import os

import pytest

from app.services.llm import stream_reply
from app.services.llm import generate_text, generate_image


@pytest.mark.asyncio
async def test_stream_reply_mock(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    chunks: list[str] = []
    async for tok in stream_reply("hello world"):
        chunks.append(tok)

    assert "".join(chunks).strip() == "You said: hello world"


@pytest.mark.asyncio
async def test_stream_reply_gemini_without_key_falls_back(monkeypatch):
    # Even if provider is gemini, missing API key should fall back to mock to avoid external calls.
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    chunks: list[str] = []
    async for tok in stream_reply("hi there"):
        chunks.append(tok)

    assert "You said: hi there" in "".join(chunks)


@pytest.mark.asyncio
async def test_stream_reply_gemini_path_can_be_stubbed(monkeypatch):
    async def fake_gemini(prompt: str, **kwargs):
        yield "G"
        yield "o"

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("app.services.llm.stream_gemini_reply", fake_gemini)

    chunks: list[str] = []
    async for tok in stream_reply("ignored"):
        chunks.append(tok)

    assert "".join(chunks) == "Go"


@pytest.mark.asyncio
async def test_generate_text_mock(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    res = await generate_text("hi")
    assert res["provider"] == "mock"
    assert "You said" in res["text"]
    assert res["thoughts"] is None


@pytest.mark.asyncio
async def test_generate_image_mock(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    res = await generate_image("hi image")
    assert res["provider"] == "mock"
    assert res["mime_type"].startswith("image/")
    assert isinstance(res["data"], (bytes, bytearray))
    assert len(res["data"]) > 10


@pytest.mark.asyncio
async def test_generate_text_network_error_falls_back(monkeypatch):
    async def fake_generate_gemini_text(prompt: str, model=None, thinking=None):
        raise RuntimeError("network error")

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setattr("app.services.llm.generate_gemini_text", fake_generate_gemini_text)

    res = await generate_text("hi net")
    assert res["provider"] == "mock"
    assert "You said: hi net" in res["text"]


@pytest.mark.asyncio
async def test_generate_text_invalid_model_raises(monkeypatch):
    async def fake_generate_gemini_text(prompt: str, model=None, thinking=None):
        raise RuntimeError("invalid model")

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setattr("app.services.llm.generate_gemini_text", fake_generate_gemini_text)

    with pytest.raises(RuntimeError):
        await generate_text("hi", model="bad-model")


@pytest.mark.asyncio
async def test_generate_image_network_error_falls_back(monkeypatch):
    async def fake_generate_gemini_image(prompt: str, model=None):
        raise RuntimeError("network error")

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setattr("app.services.llm.generate_gemini_image", fake_generate_gemini_image)

    res = await generate_image("cat img")
    assert res["provider"] == "mock"
    assert res["mime_type"].startswith("image/")


@pytest.mark.asyncio
async def test_generate_image_invalid_model_raises(monkeypatch):
    async def fake_generate_gemini_image(prompt: str, model=None):
        raise RuntimeError("invalid model")

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setattr("app.services.llm.generate_gemini_image", fake_generate_gemini_image)

    with pytest.raises(RuntimeError):
        await generate_image("cat", model="bad-model")


@pytest.mark.asyncio
async def test_stream_gemini_reply_legacy(monkeypatch):
    class FakeLegacyModel:
        def __init__(self, name):
            self.name = name

        def generate_content(self, prompt, stream=False):
            if stream:
                return [type("Chunk", (), {"text": "hello "}), type("Chunk", (), {"text": "world"})]
            return type("Resp", (), {"text": "hello world"})

        async def generate_content_async(self, prompt):
            return type("Resp", (), {"text": "async text"})

    class FakeLegacyGenAI:
        def __init__(self):
            self.configured = None

        def configure(self, api_key=None):
            self.configured = api_key

        def GenerativeModel(self, name):
            return FakeLegacyModel(name)

    fake = FakeLegacyGenAI()
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setattr("app.services.llm.gemini._import_clients", lambda: ("legacy", fake))

    from app.services.llm.gemini import stream_gemini_reply

    collected = []
    async for tok in stream_gemini_reply("hi"):
        collected.append(tok)
    assert "".join(collected).strip() == "hello world"


@pytest.mark.asyncio
async def test_generate_gemini_text_new_client(monkeypatch):
    import sys
    import types as pytypes

    # Stub google.genai and types modules
    class Part:
        def __init__(self, text, thought=False):
            self.text = text
            self.thought = thought

    class Content:
        def __init__(self, parts):
            self.parts = parts

    class Candidate:
        def __init__(self, parts):
            self.content = Content(parts)

    class Chunk:
        def __init__(self, parts):
            self.candidates = [Candidate(parts)]

    class FakeTypes:
        class ThinkingConfig:
            def __init__(self, include_thoughts=False, thinking_level=None, thinking_budget=None):
                self.include_thoughts = include_thoughts
                self.thinking_level = thinking_level
                self.thinking_budget = thinking_budget

        class GenerateContentConfig:
            def __init__(self, thinking_config=None):
                self.thinking_config = thinking_config

    class FakeClient:
        def __init__(self, api_key=None):
            self.api_key = api_key
            self.models = self
            self.images = self

        # streaming
        def generate_content_stream(self, model, contents, config=None):
            return [Chunk([Part("Hi "), Part("there")])]

        # non-stream
        def generate_content(self, model, contents, config=None):
            return type("Resp", (), {"candidates": [Candidate([Part("Hello"), Part("Thought", thought=True)])]})

        # images
        def generate(self, model, prompt):
            img = type("Img", (), {"mime_type": "image/png", "data": b"123"})
            return type("ImgResp", (), {"images": [img]})

    genai_mod = pytypes.ModuleType("google.genai")
    types_mod = pytypes.ModuleType("google.genai.types")
    types_mod.GenerateContentConfig = FakeTypes.GenerateContentConfig
    types_mod.ThinkingConfig = FakeTypes.ThinkingConfig
    genai_mod.Client = FakeClient
    genai_mod.types = types_mod

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setattr("app.services.llm.gemini._import_clients", lambda: ("new", genai_mod))
    monkeypatch.setitem(sys.modules, "google.genai", genai_mod)
    monkeypatch.setitem(sys.modules, "google.genai.types", types_mod)

    from app.services.llm.gemini import generate_gemini_text, generate_gemini_image, stream_gemini_reply

    text, thoughts, used_model = await generate_gemini_text("p", model="m", thinking=None)
    assert text == "Hello"
    assert thoughts is None or thoughts == "Thought" or thoughts == "ThoughtThought"
    assert used_model == "m"

    mime, data, img_model = await generate_gemini_image("p", model="img-m")
    assert mime == "image/png"
    assert data == b"123"
    assert img_model == "img-m"

    collected = []
    async for tok in stream_gemini_reply("p", model="m"):
        collected.append(tok)
    assert "".join(collected).strip() == "Hi there"
