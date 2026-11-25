"""Deterministic input hashing, manifest tracking, and exponential backoff retries."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def sha256_bytes(data: bytes) -> str:
    """Return hex SHA-256 digest for raw bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Return hex SHA-256 digest of a file on disk."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_stage_hash(
    *,
    stage: str,
    model: str,
    prompt: str = "",
    seed: int | None = None,
    params: dict[str, Any] | None = None,
    reference_files: list[Path] | None = None,
    upstream_hashes: dict[str, str] | None = None,
) -> str:
    """Compute a deterministic fingerprint from every input a stage depends on."""
    file_hashes: dict[str, str] = {}
    for ref in sorted(reference_files or [], key=lambda p: str(p)):
        if ref.exists():
            file_hashes[ref.as_posix()] = sha256_file(ref)
        else:
            file_hashes[ref.as_posix()] = "MISSING"

    payload = {
        "stage": stage,
        "model": model,
        "prompt": prompt,
        "seed": seed,
        "params": params or {},
        "reference_files": file_hashes,
        "upstream_hashes": upstream_hashes or {},
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return sha256_bytes(canonical)


def update_manifest(
    manifest_path: Path,
    *,
    output_file: Path,
    project_root: Path,
    stage: str,
    shot_id: str,
    input_hash: str,
    status: str = "ok",
) -> None:
    """Record generated artifact metadata in outputs/manifest.json."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        data = {"artifacts": {}}

    rel_path = output_file.resolve().relative_to(project_root.resolve()).as_posix()
    data.setdefault("artifacts", {})[rel_path] = {
        "file_name": output_file.name,
        "stage": stage,
        "shot_id": shot_id,
        "input_hash": input_hash,
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def retry_with_backoff(
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    base_delay_sec: float = 2.0,
) -> T:
    """Run fn with exponential backoff up to max_attempts before re-raising."""
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt >= max_attempts:
                break
            delay = base_delay_sec * (2 ** (attempt - 1))
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc
