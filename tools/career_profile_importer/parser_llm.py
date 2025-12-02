from __future__ import annotations

import json
from typing import Any, Dict

from .ai_client import AIModelClient

PROMPT = """You are a career analyst. Read the provided job history text and emit JSON only.
Required keys:
- type (always "project")
- title
- period (e.g., "2023-04 ~ 2024-03")
- role
- client_industry
- team_size (integer)
- environment (array of strings)
- tags (array of strings)
Optional keys: client_type, employment_type, work_style, responsibilities (array), achievements (array), summary (string).
Respond with JSON only."""


def parse_project(text: str, client: AIModelClient, model: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Invoke LLM (or dry-run stub) to get structured project data.
    """
    raw = client.generate_structured(user_text=text, system_prompt=PROMPT, model=model, dry_run=dry_run)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: wrap raw string if model responded with plain text
        return {
            "type": "project",
            "title": "Unparsed Project",
            "period": "",
            "role": "",
            "client_industry": "",
            "team_size": 0,
            "environment": [],
            "tags": [],
            "summary": raw,
        }
