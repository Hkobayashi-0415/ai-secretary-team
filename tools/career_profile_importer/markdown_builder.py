from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable

from .config import VaultConfig


def _fmt_list(items: Iterable[str]) -> str:
    return "\n".join(f"  - {item}" for item in items)


def build_markdown(data: Dict[str, Any]) -> str:
    """
    Build Markdown string with front matter + basic sections.
    """
    environment = data.get("environment", [])
    tags = data.get("tags", [])
    responsibilities = data.get("responsibilities", [])
    achievements = data.get("achievements", [])

    front_matter_lines = [
        f"type: {data.get('type', 'project')}",
        f"title: {data.get('title', '')}",
        f"period: {data.get('period', '')}",
        f"role: {data.get('role', '')}",
        f"client_industry: {data.get('client_industry', '')}",
        f"client_type: {data.get('client_type', '')}",
        f"employment_type: {data.get('employment_type', '')}",
        f"work_style: {data.get('work_style', '')}",
        f"team_size: {data.get('team_size', '')}",
        "environment:",
        _fmt_list(environment),
        "responsibilities:",
        _fmt_list(responsibilities),
        "achievements:",
        _fmt_list(achievements),
        "tags:",
        _fmt_list(tags),
    ]

    summary = data.get("summary", "")
    body = [
        "---",
        "\n".join(front_matter_lines),
        "---",
        "### 概要",
        summary or "",
        "### 担当業務",
        *(f"- {item}" for item in responsibilities) or ["- "],
        "### 実績・工夫",
        *(f"- {item}" for item in achievements) or ["- "],
    ]
    return "\n".join(body) + "\n"


def write_project_markdown(data: Dict[str, Any], vault: VaultConfig, output_dir: Path | None = None) -> Path:
    """
    Write Markdown under the vault's projects directory. Returns the written path.
    """
    target_dir = Path(output_dir) if output_dir else vault.projects_path()
    target_dir.mkdir(parents=True, exist_ok=True)
    slug = _slugify(data.get("title") or "project")
    period = (data.get("period") or "").replace(" ", "").replace("~", "-") or "period"
    filename = f"PJ_{period}_{slug}.md"
    path = target_dir / filename
    path.write_text(build_markdown(data), encoding="utf-8")
    return path


def _slugify(text: str) -> str:
    safe = "".join(ch if ch.isalnum() else "_" for ch in text)
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_").lower() or "project"
