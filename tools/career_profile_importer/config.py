from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict
import tomllib


@dataclass
class VaultConfig:
    path: Path
    projects_subdir: str = "projects"
    skills_subdir: str = "skills"

    def projects_path(self) -> Path:
        return self.path / self.projects_subdir


@dataclass
class DefaultsConfig:
    vault: str = "career"
    input_dir: Path = Path("./input")
    model: str = "gemini-pro"


@dataclass
class AppConfig:
    defaults: DefaultsConfig
    vaults: Dict[str, VaultConfig]

    def get_vault(self, name: str | None) -> VaultConfig:
        key = name or self.defaults.vault
        if key not in self.vaults:
            raise KeyError(f"Vault '{key}' is not defined in config.toml")
        return self.vaults[key]


def _load_dict(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    return tomllib.loads(path.read_text(encoding="utf-8"))


def load_config(path: Path | str | None = None) -> AppConfig:
    """
    Load config.toml. When not present, fall back to a minimal in-memory config.
    """
    if path:
        data = _load_dict(Path(path))
    else:
        # Minimal default that matches the provided Vault path
        data = {
            "defaults": {
                "vault": "career",
                "input_dir": "./input",
                "model": "gemini-pro",
            },
            "vaults": {
                "career": {
                    "path": r"C:\Users\sugar\OneDrive\デスクトップ\Obsidian",
                    "projects_subdir": "projects",
                    "skills_subdir": "skills",
                }
            },
        }

    defaults_raw = data.get("defaults", {})
    defaults = DefaultsConfig(
        vault=defaults_raw.get("vault", "career"),
        input_dir=Path(defaults_raw.get("input_dir", "./input")),
        model=defaults_raw.get("model", "gemini-pro"),
    )

    vaults: Dict[str, VaultConfig] = {}
    for name, cfg in data.get("vaults", {}).items():
        vaults[name] = VaultConfig(
            path=Path(cfg["path"]),
            projects_subdir=cfg.get("projects_subdir", "projects"),
            skills_subdir=cfg.get("skills_subdir", "skills"),
        )

    return AppConfig(defaults=defaults, vaults=vaults)
