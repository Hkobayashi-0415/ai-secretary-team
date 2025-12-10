import base64
import os

from starlette.testclient import TestClient

from app.main import app


def test_llm_text_endpoint_mock(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with TestClient(app) as tc:
        res = tc.post("/api/v1/llm/text", json={"prompt": "Hello endpoint"})
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "mock"
        assert "Hello endpoint" in data["text"]


def test_llm_text_endpoint_stream_flag_400(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with TestClient(app) as tc:
        res = tc.post("/api/v1/llm/text", json={"prompt": "Hello endpoint", "stream": True})
        assert res.status_code == 400
        assert res.json()["detail"] == "stream=true is not supported on REST. Use WS."


def test_llm_text_endpoint_gemini(monkeypatch):
    async def fake_generate_text(prompt: str, model=None, thinking=None):
        return ("stubbed", None, model or "gemini-3-pro-preview")

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setattr("app.services.llm.generate_gemini_text", fake_generate_text)

    with TestClient(app) as tc:
        res = tc.post("/api/v1/llm/text", json={"prompt": "Hello endpoint", "model": "gemini-3-pro-preview"})
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "gemini"
        assert data["text"] == "stubbed"
        assert data["model"] == "gemini-3-pro-preview"


def test_llm_text_endpoint_thinking_params(monkeypatch):
    captured = {}

    async def fake_generate_text(prompt: str, model=None, thinking=None):
        captured["model"] = model
        captured["thinking"] = thinking
        return ("stubbed-think", "thoughts", model or "gemini-3-pro-preview")

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setattr("app.services.llm.generate_gemini_text", fake_generate_text)

    payload = {
        "prompt": "Hello",
        "model": "gemini-3-pro-preview",
        "thinking_level": "high",
        "thinking_budget": 1024,
        "include_thoughts": True,
    }
    with TestClient(app) as tc:
        res = tc.post("/api/v1/llm/text", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["text"] == "stubbed-think"
        assert data["thoughts"] == "thoughts"
        assert captured["model"] == "gemini-3-pro-preview"
        tcfg = captured["thinking"]
        assert tcfg is not None
        assert tcfg.thinking_level == "high"
        assert tcfg.thinking_budget == 1024
        assert tcfg.include_thoughts is True


def test_llm_text_endpoint_invalid_model(monkeypatch):
    async def fake_generate_text(prompt: str, model=None, thinking=None, **kwargs):
        raise RuntimeError("model not found")

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setattr("app.services.llm.generate_gemini_text", fake_generate_text)
    monkeypatch.setattr("app.api.v1.endpoints.llm.generate_text", fake_generate_text)

    with TestClient(app) as tc:
        res = tc.post("/api/v1/llm/text", json={"prompt": "hi", "model": "invalid-model"})
        assert res.status_code == 500
        assert "model not found" in res.text


def test_llm_text_endpoint_gemini_fallback(monkeypatch):
    calls = {"count": 0}

    async def fake_generate_text(prompt: str, model=None, thinking=None):
        calls["count"] += 1
        raise RuntimeError("gemini failure")

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setattr("app.services.llm.generate_gemini_text", fake_generate_text)

    with TestClient(app) as tc:
        res = tc.post("/api/v1/llm/text", json={"prompt": "hi"})
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "mock"
        assert "You said: hi" in data["text"]
        assert calls["count"] == 1


def test_llm_image_endpoint_mock(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with TestClient(app) as tc:
        res = tc.post("/api/v1/llm/image", json={"prompt": "logo"})
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "mock"
        raw = base64.b64decode(data["data_base64"])
        assert len(raw) > 10


def test_llm_image_endpoint_gemini(monkeypatch):
    async def fake_generate_image(prompt: str, model=None, provider_override=None):
        return {
            "mime_type": "image/png",
            "data": b"1234",
            "provider": "gemini",
            "model": model or "imagen-3.0-generate-001",
        }

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setattr("app.services.llm.generate_image", fake_generate_image)
    monkeypatch.setattr("app.api.v1.endpoints.llm.generate_image", fake_generate_image)

    with TestClient(app) as tc:
        res = tc.post("/api/v1/llm/image", json={"prompt": "cat", "model": "imagen-3.0-generate-001"})
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "gemini"
        assert base64.b64decode(data["data_base64"]) == b"1234"


def test_llm_image_endpoint_invalid_model(monkeypatch):
    async def fake_generate_image(prompt: str, model=None, provider_override=None):
        raise RuntimeError("invalid model")

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setattr("app.services.llm.generate_image", fake_generate_image)
    monkeypatch.setattr("app.api.v1.endpoints.llm.generate_image", fake_generate_image)

    with TestClient(app) as tc:
        res = tc.post("/api/v1/llm/image", json={"prompt": "cat", "model": "invalid-model"})
        assert res.status_code == 500
        assert "invalid model" in res.text
