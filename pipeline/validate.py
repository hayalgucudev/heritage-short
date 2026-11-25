"""Schema and semantic validation for storyboard.json before any quota call."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def validate_storyboard(storyboard_path: Path, schema_path: Path) -> dict[str, Any]:
    """Validate storyboard.json against schema and check subtitle/duration constraints."""
    if not storyboard_path.exists():
        raise FileNotFoundError(
            f"Storyboard not found at {storyboard_path}. Create or draft storyboard.json first."
        )
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found at {schema_path}.")

    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(storyboard), key=lambda e: list(e.path))
    if errors:
        formatted = "\n".join(
            f"  - {'/'.join(str(p) for p in err.path) or '<root>'}: {err.message}"
            for err in errors
        )
        raise ValueError(f"storyboard.json failed schema validation:\n{formatted}")

    semantic_errors: list[str] = []
    seen_ids: set[str] = set()
    total_duration = float(storyboard["end_card"]["duration_sec"])

    for shot in storyboard["shots"]:
        sid = shot["id"]
        if sid in seen_ids:
            semantic_errors.append(f"Duplicate shot id: {sid}")
        seen_ids.add(sid)
        total_duration += float(shot["duration_sec"])

        lines = shot["subtitle_en"].splitlines()
        if len(lines) > 2:
            semantic_errors.append(
                f"{sid}: subtitle_en has {len(lines)} lines (max 2 lines allowed)."
            )
        for idx, line in enumerate(lines, start=1):
            if len(line) > 42:
                semantic_errors.append(
                    f"{sid}: subtitle_en line {idx} is {len(line)} chars (target <= 40-42 chars)."
                )

    if total_duration < 55.0 or total_duration > 95.0:
        semantic_errors.append(
            f"Total planned duration is {total_duration:.1f}s (target 60-90s including end card)."
        )

    if semantic_errors:
        raise ValueError(
            "storyboard.json failed semantic checks:\n"
            + "\n".join(f"  - {msg}" for msg in semantic_errors)
        )

    return storyboard
