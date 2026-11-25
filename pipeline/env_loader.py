"""Environment variable loader that never prints or logs secret values."""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

SECRET_ENV_VARS = (
    "GEMINI_API_KEY",
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_API_TOKEN",
    "HF_TOKEN",
)


def load_env(project_root: Path) -> None:
    """Load .env into process environment without printing any values."""
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)


def require_env(name: str) -> str:
    """Return a required environment variable or raise a clear non-secret error."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{name}'. "
            "Set it in your .env file (see .env.example) before running API stages."
        )
    return value


def active_secret_values() -> list[str]:
    """Return non-empty secret strings solely for in-memory log redaction."""
    values: list[str] = []
    for key in SECRET_ENV_VARS:
        val = os.environ.get(key, "").strip()
        if val:
            values.append(val)
    return values
