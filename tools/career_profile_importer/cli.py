from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from .ai_client import GeminiClient
from .config import AppConfig, load_config
from .markdown_builder import write_project_markdown
from .parser_llm import parse_project


def _collect_files(input_file: str | None, input_dir: Path) -> List[Path]:
    if input_file:
        return [Path(input_file)]
    return sorted(p for p in input_dir.glob("*") if p.suffix.lower() in {".txt", ".md"})


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Career profile importer (Gemini-first, Obsidian vault).")
    parser.add_argument("--config", type=str, default=None, help="Path to config.toml (defaults are embedded).")
    parser.add_argument("--vault", type=str, default=None, help="Vault key (defaults.vault).")
    parser.add_argument("--input-file", type=str, help="Single input file (.txt/.md).")
    parser.add_argument("--input-dir", type=str, help="Directory to scan when --input-file is not set.")
    parser.add_argument("--model", type=str, default=None, help="Model name (default: gemini-pro).")
    parser.add_argument("--output-dir", type=str, help="Optional override for output directory (else vault.projects_subdir).")
    parser.add_argument("--dry-run", action="store_true", help="Do not call the API; use canned JSON for testing.")
    return parser.parse_args()


def _resolve_config(args: argparse.Namespace) -> tuple[AppConfig, Path]:
    cfg = load_config(args.config)
    vault = cfg.get_vault(args.vault)
    input_dir = Path(args.input_dir) if args.input_dir else cfg.defaults.input_dir
    return cfg, input_dir, vault


def main() -> int:
    args = _parse_args()
    cfg, input_dir, vault = _resolve_config(args)
    files = _collect_files(args.input_file, input_dir)
    if not files:
        print(f"[warn] no input files found in {input_dir} (use --input-file or --input-dir)")
        return 1

    client = GeminiClient()
    model = args.model or cfg.defaults.model
    dry_run = bool(args.dry_run or not client.api_key)
    if dry_run:
        print("[info] dry-run mode (no API key detected or --dry-run specified)")

    for fpath in files:
        text = fpath.read_text(encoding="utf-8")
        data = parse_project(text, client=client, model=model, dry_run=dry_run)
        out_dir = Path(args.output_dir) if args.output_dir else None
        written = write_project_markdown(data, vault=vault, output_dir=out_dir)
        print(f"[ok] {fpath} -> {written}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
