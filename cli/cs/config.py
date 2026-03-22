from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import tomllib


DEFAULT_API_URL = "http://localhost:8000"
CONFIG_ENV_VAR = "CS_CONFIG_PATH"


@dataclass(slots=True)
class CSConfig:
    api_url: str = DEFAULT_API_URL
    token: str | None = None


def get_config_path() -> Path:
    custom_path = os.getenv(CONFIG_ENV_VAR)
    if custom_path:
        return Path(custom_path).expanduser()
    return Path.home() / ".cs" / "config.toml"


def load_config(path: Path | None = None) -> CSConfig:
    config_path = path or get_config_path()
    if not config_path.exists():
        return CSConfig()

    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    default_section = data.get("default", {})
    api_url = default_section.get("api_url") or DEFAULT_API_URL
    token = default_section.get("token")
    return CSConfig(api_url=api_url, token=token)


def save_config(config: CSConfig, path: Path | None = None) -> Path:
    config_path = path or get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    lines = ["[default]", f'api_url = "{_escape(config.api_url)}"']
    if config.token is not None:
        lines.append(f'token = "{_escape(config.token)}"')
    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return config_path


def resolve_api_url(config: CSConfig, override: str | None = None) -> str:
    return override or os.getenv("CS_API_URL") or config.api_url or DEFAULT_API_URL


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
