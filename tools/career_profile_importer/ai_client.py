from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Protocol


class AIModelClient(Protocol):
    def generate_structured(self, *, user_text: str, system_prompt: str, model: str, dry_run: bool = False) -> str:
        ...


@dataclass
class GeminiClient:
    api_key: str | None = None

    def __post_init__(self) -> None:
        if not self.api_key:
            self.api_key = os.getenv("GEMINI_API_KEY")

    def generate_structured(self, *, user_text: str, system_prompt: str, model: str, dry_run: bool = False) -> str:
        """
        Minimal Gemini call wrapper. In dry_run mode it returns a canned JSON string.
        """
        if dry_run:
            return json.dumps(
                {
                    "type": "project",
                    "title": "Sample Project",
                    "period": "2023-04 ~ 2024-03",
                    "role": "PM",
                    "client_industry": "製薬",
                    "team_size": 10,
                    "environment": ["AWS", "Python", "FastAPI"],
                    "responsibilities": ["要件定義からリリースまでPMを担当"],
                    "achievements": ["工数20%削減"],
                    "tags": ["#project", "#role/PM", "#skill/生成AI"],
                    "summary": "サンプル概要",
                }
            )

        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not set; use --dry-run or set the key.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": system_prompt},
                        {"text": user_text},
                    ],
                }
            ]
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:  # noqa: S310 - explicit API call
            body = resp.read()
            parsed = json.loads(body)

        # Gemini text response structure
        try:
            text = parsed["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"Gemini response missing text field: {parsed}") from exc
        return text
