"""Append-only runs.jsonl logger with automatic secret redaction."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline.env_loader import active_secret_values


def redact_secrets(text: str) -> str:
    """Scrub any loaded secret value from strings before writing logs."""
    cleaned = text
    for secret in active_secret_values():
        if secret and secret in cleaned:
            cleaned = cleaned.replace(secret, "[REDACTED]")
    return cleaned


def _redact_obj(obj: Any) -> Any:
    if isinstance(obj, str):
        return redact_secrets(obj)
    if isinstance(obj, dict):
        return {k: _redact_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact_obj(v) for v in obj]
    return obj


def log_run(
    runs_path: Path,
    *,
    stage: str,
    shot_id: str,
    model: str,
    parameters: dict[str, Any] | None = None,
    seed: int | None = None,
    latency_ms: int | None = None,
    cost_or_quota: str = "free_tier",
    cache_hit: bool = False,
    status: str = "ok",
    input_hash: str | None = None,
    output_path: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """Immediately append one structured record to runs.jsonl."""
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "shot_id": shot_id,
        "model": model,
        "parameters": _redact_obj(parameters or {}),
        "seed": seed,
        "latency_ms": latency_ms,
        "cost_or_quota": cost_or_quota,
        "cache_hit": cache_hit,
        "status": status,
        "input_hash": input_hash,
        "output_path": output_path,
        "error": redact_secrets(error) if error else None,
    }
    runs_path.parent.mkdir(parents=True, exist_ok=True)
    with runs_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record
