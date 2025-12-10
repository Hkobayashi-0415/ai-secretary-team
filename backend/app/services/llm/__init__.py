import os
from typing import AsyncIterator, Optional

from .gemini import (
    ThinkingConfig,
    build_mock_image,
    generate_gemini_image,
    generate_gemini_text,
    stream_gemini_reply,
)
from .mock_llm import stream_mock_reply


def _resolve_provider(provider_override: Optional[str] = None) -> str:
    provider = (provider_override or os.getenv("LLM_PROVIDER") or "").strip().lower()
    if not provider:
        provider = "gemini" if os.getenv("GEMINI_API_KEY") else "mock"
    return provider


async def stream_reply(
    user_text: str,
    *,
    model: Optional[str] = None,
    thinking_level: Optional[str] = None,
    thinking_budget: Optional[int] = None,
    include_thoughts: bool = False,
    provider_override: Optional[str] = None,
) -> AsyncIterator[str]:
    """
    Stream reply from the selected LLM provider.

    Priority:
    1. If LLM_PROVIDER=mock (or override) -> mock
    2. If LLM_PROVIDER=gemini (or unset but GEMINI_API_KEY is present) -> Gemini with mock fallback
    3. Otherwise -> mock
    """
    provider = _resolve_provider(provider_override)
    thinking_cfg = ThinkingConfig(
        include_thoughts=include_thoughts,
        thinking_level=thinking_level,
        thinking_budget=thinking_budget,
    )

    if provider == "gemini":
        try:
            async for token in stream_gemini_reply(user_text, model=model, thinking=thinking_cfg):
                yield token
            return
        except Exception:
            # Fall back to mock for robustness (tests/offline/dev).
            pass

    # default: mock echo
    async for token in stream_mock_reply(user_text):
        yield token


async def generate_text(
    prompt: str,
    *,
    model: Optional[str] = None,
    thinking_level: Optional[str] = None,
    thinking_budget: Optional[int] = None,
    include_thoughts: bool = False,
    provider_override: Optional[str] = None,
) -> dict:
    """
    Non-stream text generation with optional thinking config.
    Returns dict: {text, thoughts?, provider, model}
    """
    provider = _resolve_provider(provider_override)
    thinking_cfg = ThinkingConfig(
        include_thoughts=include_thoughts,
        thinking_level=thinking_level,
        thinking_budget=thinking_budget,
    )

    if provider == "gemini":
        try:
            text, thoughts, used_model = await generate_gemini_text(
                prompt, model=model, thinking=thinking_cfg
            )
            return {
                "text": text,
                "thoughts": thoughts,
                "provider": "gemini",
                "model": used_model,
            }
        except Exception as exc:
            # Surface likely configuration/model errors; otherwise fall back to mock.
            msg = str(exc).lower()
            if "model" in msg and ("not found" in msg or "invalid" in msg):
                raise
            # fallback to mock below

    # mock fallback
    return {
        "text": f"You said: {prompt}",
        "thoughts": None,
        "provider": "mock",
        "model": "mock",
    }


async def generate_image(
    prompt: str,
    *,
    model: Optional[str] = None,
    provider_override: Optional[str] = None,
) -> dict:
    """
    Image generation. Falls back to placeholder PNG for mock/offline.
    Returns dict: {mime_type, data_bytes, provider, model}
    """
    provider = _resolve_provider(provider_override)
    if provider == "gemini":
        try:
            mime, data, used_model = await generate_gemini_image(prompt, model=model)
            return {
                "mime_type": mime,
                "data": data,
                "provider": "gemini",
                "model": used_model,
            }
        except Exception as exc:
            msg = str(exc).lower()
            if "model" in msg and ("not found" in msg or "invalid" in msg):
                raise
            # fallback to mock below

    mime, data = build_mock_image(prompt)
    return {"mime_type": mime, "data": data, "provider": "mock", "model": "mock"}
