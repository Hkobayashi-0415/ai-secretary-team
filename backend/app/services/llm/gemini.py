import asyncio
import base64
import os
from dataclasses import dataclass
from typing import AsyncIterator, Iterable, Optional, Tuple

# This module prefers the newer google.genai client (Gemini 2/3, thinking features).
# If unavailable, it falls back to google.generativeai for compatibility.


@dataclass
class ThinkingConfig:
    include_thoughts: bool = False
    thinking_level: Optional[str] = None  # "low" | "high" (Gemini 3) or None
    thinking_budget: Optional[int] = None  # Gemini 2.5


def _split_tokens(text: str) -> Iterable[str]:
    """Split into small chunks to simulate streaming even for non-stream responses."""
    for part in text.split(" "):
        if part:
            yield part + " "


def _import_clients():
    """
    Try new client first (google.genai). If not installed, fall back to google.generativeai.
    Returns tuple: (mode, module)
    mode: "new" | "legacy"
    """
    try:
        import google.genai as genai  # type: ignore

        return "new", genai
    except Exception:
        import google.generativeai as genai  # type: ignore

        return "legacy", genai


def _extract_text_and_thoughts_from_parts(parts) -> Tuple[str, Optional[str]]:
    text_out = []
    thoughts_out = []
    for p in parts or []:
        t = getattr(p, "text", None)
        if not t:
            continue
        if getattr(p, "thought", False):
            thoughts_out.append(t)
        else:
            text_out.append(t)
    return "".join(text_out), ("".join(thoughts_out) if thoughts_out else None)


def _extract_text_from_chunk(chunk: object) -> str:
    text = getattr(chunk, "text", None)
    if text:
        return text
    candidates = getattr(chunk, "candidates", None) or []
    if candidates:
        content = getattr(candidates[0], "content", None)
        parts = getattr(content, "parts", None) or []
        pieces = [getattr(p, "text", "") for p in parts if getattr(p, "text", "")]
        if pieces:
            return "".join(pieces)
    return ""


# ----- Text generation / streaming -----


async def stream_gemini_reply(
    user_text: str,
    *,
    model: Optional[str] = None,
    thinking: Optional[ThinkingConfig] = None,
) -> AsyncIterator[str]:
    """
    Stream tokens from Gemini API. Falls back to full generate + splitting.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    mode, genai = _import_clients()
    model_name = model or os.getenv("GEMINI_MODEL", "gemini-pro")

    if mode == "new":
        # google.genai (Gemini 2/3, thinking support)
        from google.genai import types  # type: ignore

        client = genai.Client(api_key=api_key)
        config = None
        if thinking:
            config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    include_thoughts=thinking.include_thoughts,
                    thinking_level=thinking.thinking_level,
                    thinking_budget=thinking.thinking_budget,
                )
            )
        try:
            stream = client.models.generate_content_stream(
                model=model_name,
                contents=user_text,
                config=config,
            )
            for chunk in stream:
                candidates = getattr(chunk, "candidates", None) or []
                if not candidates:
                    continue
                parts = getattr(candidates[0].content, "parts", None) or []
                for token in _split_tokens(_extract_text_and_thoughts_from_parts(parts)[0]):
                    yield token
            return
        except Exception:
            # Fall through to legacy logic
            pass

    # Legacy client
    genai.configure(api_key=api_key)
    legacy_model = genai.GenerativeModel(model_name)

    # Try streaming
    try:
        response_sync = legacy_model.generate_content(user_text, stream=True)
        for chunk in response_sync:
            text = _extract_text_from_chunk(chunk)
            for token in _split_tokens(text):
                yield token
        return
    except Exception:
        pass

    # Final fallback: non-streaming generate then split.
    full = await _generate_full_text_legacy(legacy_model, user_text)
    if not full:
        raise RuntimeError("Gemini returned empty response")
    for token in _split_tokens(full):
        yield token


async def _generate_full_text_legacy(model, prompt: str) -> str:
    """Call Gemini legacy client without streaming and return the whole text."""
    # Try async if available
    if hasattr(model, "generate_content_async"):
        try:
            resp = await model.generate_content_async(prompt)
            if getattr(resp, "text", None):
                return resp.text
        except Exception:
            pass
    # Sync fallback
    resp = model.generate_content(prompt)
    return getattr(resp, "text", "") or ""


async def generate_gemini_text(
    prompt: str,
    *,
    model: Optional[str] = None,
    thinking: Optional[ThinkingConfig] = None,
) -> Tuple[str, Optional[str], str]:
    """
    Non-streaming text generation.
    Returns (text, thoughts, provider_model_used)
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    mode, genai = _import_clients()
    model_name = model or os.getenv("GEMINI_MODEL", "gemini-pro")

    if mode == "new":
        from google.genai import types  # type: ignore

        client = genai.Client(api_key=api_key)
        config = None
        if thinking:
            config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    include_thoughts=thinking.include_thoughts,
                    thinking_level=thinking.thinking_level,
                    thinking_budget=thinking.thinking_budget,
                )
            )
        resp = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config,
        )
        candidates = getattr(resp, "candidates", None) or []
        if not candidates:
            return "", None, model_name
        parts = getattr(candidates[0].content, "parts", None) or []
        text, thoughts = _extract_text_and_thoughts_from_parts(parts)
        if not text and hasattr(resp, "text"):
            text = getattr(resp, "text", "") or ""
        return text, thoughts, model_name

    # Legacy
    genai.configure(api_key=api_key)
    legacy_model = genai.GenerativeModel(model_name)
    resp = legacy_model.generate_content(prompt)
    text = getattr(resp, "text", "") or ""
    return text, None, model_name


# ----- Image generation -----


async def generate_gemini_image(
    prompt: str,
    *,
    model: Optional[str] = None,
) -> Tuple[str, bytes, str]:
    """
    Generate an image from text prompt.
    Returns (mime_type, data_bytes, provider_model_used)
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    mode, genai = _import_clients()
    model_name = model or os.getenv("GEMINI_IMAGE_MODEL", "imagen-3.0-generate-001")

    if mode == "new":
        client = genai.Client(api_key=api_key)
        try:
            resp = client.images.generate(model=model_name, prompt=prompt)
            images = getattr(resp, "images", None) or []
            if not images:
                raise RuntimeError("Gemini returned no images")
            img = images[0]
            # google.genai returns .data (bytes) and mime_type
            mime = getattr(img, "mime_type", "image/png")
            data = getattr(img, "data", None)
            if data is None:
                raise RuntimeError("Gemini image response missing data")
            return mime, data, model_name
        except Exception as exc:
            raise RuntimeError(f"Gemini image generation failed: {exc}") from exc

    # Legacy client may not support images; return an explicit error.
    raise RuntimeError("Image generation requires google.genai client (not available)")


# ----- Helpers -----


def build_mock_image(prompt: str) -> Tuple[str, bytes]:
    """
    Build a small placeholder PNG with the prompt text.
    """
    try:
        from io import BytesIO
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (320, 200), color=(245, 246, 250))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), prompt[:80], fill=(0, 0, 0))
        buf = BytesIO()
        img.save(buf, format="PNG")
        return "image/png", buf.getvalue()
    except Exception:
        # Fallback: empty png bytes
        empty_png_base64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
            "/w8AAusB9YtBhNEAAAAASUVORK5CYII="
        )
        return "image/png", base64.b64decode(empty_png_base64)
