"""Build COSTS.md tables from real runs.jsonl records only."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

HANDWRITTEN_MARKER = "## Production keyframes run"


def _records(runs_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not runs_path.exists():
        return rows
    for line in runs_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(out)


def render_costs_md(records: list[dict[str, Any]], preserved_header: str) -> str:
    by_stage: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"calls": 0, "hits": 0, "failures": 0, "latency": 0, "quota": defaultdict(int)}
    )
    by_model: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"calls": 0, "latency": 0}
    )
    by_shot: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"calls": 0, "latency": 0})

    for rec in records:
        stage = str(rec.get("stage", "unknown"))
        model = str(rec.get("model", "unknown"))
        shot = str(rec.get("shot_id", "all"))
        calls = 1 if not rec.get("cache_hit") else 0
        latency = int(rec.get("latency_ms") or 0)
        bucket = by_stage[stage]
        bucket["calls"] += calls
        bucket["hits"] += 1 if rec.get("cache_hit") else 0
        bucket["failures"] += 1 if rec.get("status") != "ok" else 0
        bucket["latency"] += latency
        bucket["quota"][str(rec.get("cost_or_quota", "unspecified"))] += 1
        by_model[model]["calls"] += calls
        by_model[model]["latency"] += latency
        by_shot[(stage, shot)]["calls"] += calls
        by_shot[(stage, shot)]["latency"] += latency

    total_calls = sum(v["calls"] for v in by_stage.values())
    total_latency = sum(v["latency"] for v in by_stage.values())
    total_failures = sum(v["failures"] for v in by_stage.values())

    stage_rows = []
    for stage, v in sorted(by_stage.items()):
        quota_text = ", ".join(f"{k} x{n}" for k, n in sorted(v["quota"].items()))
        stage_rows.append(
            [stage, v["calls"], v["hits"], v["failures"], f"{v['latency']:,}", quota_text]
        )

    model_rows = [
        [model, v["calls"], f"{v['latency']:,}"]
        for model, v in sorted(by_model.items(), key=lambda kv: -kv[1]["latency"])
    ]
    shot_rows = [
        [stage, shot, v["calls"], f"{v['latency']:,}"]
        for (stage, shot), v in sorted(by_shot.items())
    ]

    parts = [
        preserved_header.rstrip(),
        "",
        "## Measured totals (from `runs.jsonl`)",
        "",
        f"- Real logged records: **{len(records)}**",
        f"- Non-cache model/FFmpeg calls: **{total_calls}**",
        f"- Failed calls: **{total_failures}**",
        f"- Total logged latency: **{total_latency:,} ms** ({total_latency / 60000:.1f} min)",
        "",
        "### By stage",
        "",
        _table(["Stage", "Calls", "Cache hits", "Failures", "Latency (ms)", "Cost / quota tags"], stage_rows),
        "",
        "### By model",
        "",
        _table(["Model", "Calls", "Latency (ms)"], model_rows),
        "",
        "### By stage and shot",
        "",
        _table(["Stage", "Shot", "Calls", "Latency (ms)"], shot_rows),
        "",
        "## Evidence rule",
        "",
        "Every number above is computed from `runs.jsonl` at generation time. "
        "No cost or latency is estimated or invented. Rebuild with `py run.py report-costs`.",
        "",
    ]
    return "\n".join(parts)


def build_cost_report(runs_path: Path, costs_path: Path) -> dict[str, Any]:
    records = _records(runs_path)
    existing = costs_path.read_text(encoding="utf-8") if costs_path.exists() else "# Costs & Quota Report\n"
    if HANDWRITTEN_MARKER in existing:
        preserved = existing.split(HANDWRITTEN_MARKER, 1)[0]
    else:
        preserved = existing
    rendered = render_costs_md(records, preserved)
    costs_path.write_text(rendered, encoding="utf-8")
    return {
        "runs_file": runs_path.name,
        "costs_file": costs_path.name,
        "records_read": len(records),
        "preserved_handwritten_note": HANDWRITTEN_MARKER in existing,
    }
