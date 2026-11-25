"""Dry-run planner: predict cache hits/misses without calling any model."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline import contracts
from pipeline.assemble import ASPECTS
from pipeline.validate import validate_storyboard


DEPENDENCY_MAP = [
    "shot N image_prompt / image_seed / style_block -> keyframe N -> clip N -> both final exports",
    "shot N narration / tts_style / models.tts -> narration N -> timing + subtitles -> both final exports",
    "music.caption / tempo_bpm / key / seed -> score -> ducking -> both final exports",
    "shot N video_motion_prompt / video_seed -> clip N -> both final exports",
    "end_card.text / duration_sec -> end card -> both final exports",
]


def _status(
    path: Path,
    manifest: dict[str, Any],
    rel: str,
    expected_hash: str,
) -> tuple[bool, str]:
    if not path.exists():
        return False, "output file missing"
    entry = manifest.get("artifacts", {}).get(rel, {})
    if not entry:
        return False, "not registered in outputs/manifest.json"
    if entry.get("status") != "ok":
        return False, f"last status was '{entry.get('status')}'"
    if entry.get("input_hash") != expected_hash:
        return False, "input hash changed (prompt, seed, params or an upstream file)"
    return True, "cache hit"


def build_plan(
    project_root: Path,
    storyboard_path: Path,
    schema_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    """Return a complete dry-run plan. Reads files only; writes nothing."""
    sb = validate_storyboard(storyboard_path, schema_path)
    manifest = contracts.load_manifest(manifest_path)
    items: list[dict[str, Any]] = []

    def add(item: str, shot_id: str, model: str, hit: bool, reason: str, quota: str) -> None:
        items.append(
            {
                "stage": item,
                "shot_id": shot_id,
                "model": model,
                "cache_hit": hit,
                "reason": reason,
                "quota_if_regenerated": quota,
            }
        )

    # Reference sheet: experimental candidates, not needed for --no-ref production.
    for i in range(3):
        seed = int(sb["character"]["reference_seed"]) + i
        rel = f"outputs/keyframes/ref_real_seed{seed}.png"
        hit, reason = _status(
            project_root / rel, manifest, rel, contracts.reference_sheet_hash(sb, seed)
        )
        add("reference_sheet", f"seed_{seed}", sb["models"]["keyframes"], hit, reason, "1_cloudflare_flux_call")

    # Narration uses the storyboard model; shots 07-10 were made on flash-lite.
    for shot in sb["shots"]:
        sid = shot["id"]
        rel = f"outputs/narration/{sid}.wav"
        hit, reason = _status(
            project_root / rel, manifest, rel, contracts.narration_hash(sb, shot)
        )
        add("narration", sid, sb["models"]["tts"], hit, reason, "1_gemini_tts_call")

    radio_hash, radio_total = contracts.radio_cut_hash(sb, project_root)
    rel = "outputs/final/radio_cut.mp4"
    hit, reason = _status(project_root / rel, manifest, rel, radio_hash)
    add("radio_cut", "all", "ffmpeg-9.1", hit, reason, "0_local_ffmpeg")

    # Production keyframes used --no-ref; using the default would give false misses.
    for shot in sb["shots"]:
        sid = shot["id"]
        rel = f"outputs/keyframes/{sid}.png"
        hit, reason = _status(
            project_root / rel,
            manifest,
            rel,
            contracts.keyframe_hash(sb, shot, project_root=project_root, use_reference=False),
        )
        add("keyframes", sid, sb["models"]["keyframes"], hit, reason, "1_cloudflare_flux_call")

    # Score: job spec plus the selected candidate WAV.
    mh = contracts.music_hash(sb)
    job = project_root / "outputs" / "music" / "music_job.json"
    job_ok = job.exists()
    add(
        "music_job",
        "all",
        sb["models"]["music"],
        job_ok,
        "cache hit" if job_ok else "job spec missing",
        "0_tokens_metadata",
    )
    meta_path = project_root / "outputs" / "music" / "music_run_metadata.json"
    meta = contracts.load_manifest(meta_path)
    candidates = meta.get("candidates", [])
    selected = sb["music"].get("selected_candidate")
    match = next((c for c in candidates if c.get("candidate_id") == selected), None)
    if match is None and selected:
        match = next((c for c in candidates if c.get("file_name") == selected), None)
    if match is None:
        wavs = sorted((project_root / "outputs" / "music").glob("candidate_*.wav"))
        wav = wavs[0] if wavs else project_root / "outputs" / "music" / "MISSING.wav"
        match = {"file_name": wav.name, "seed": None}
    else:
        wav = project_root / "outputs" / "music" / match["file_name"]
    rel = wav.relative_to(project_root).as_posix() if wav.exists() else f"outputs/music/{match['file_name']}"
    hit, reason = _status(
        wav,
        manifest,
        rel,
        contracts.music_candidate_hash(sb, wav, seed=match.get("seed"), file_name=match.get("file_name")),
    )
    add("music_candidate", selected or "unselected", sb["models"]["music"], hit, reason, "1_kaggle_acestep_call")

    # Clips: keep the currently registered source (Wan import or Ken Burns fallback).
    clip_hashes: list[str] = []
    clip_paths: list[Path] = []
    for shot in sb["shots"]:
        sid = shot["id"]
        kf = project_root / "outputs" / "keyframes" / f"{sid}.png"
        kf_hash = contracts.keyframe_hash(sb, shot, project_root=project_root, use_reference=False)
        clip = project_root / "outputs" / "clips" / f"{sid}.mp4"
        rel = clip.relative_to(project_root).as_posix()
        entry = manifest.get("artifacts", {}).get(rel, {})
        wan = contracts.clip_hash(sb, shot, kf, kf_hash, source="wan_import")
        kb = contracts.clip_hash(sb, shot, kf, kf_hash, source="ken_burns")
        got = entry.get("input_hash")
        source = "wan_import" if got == wan else "ken_burns"
        hash_to_use = wan if source == "wan_import" else kb
        hit, reason = _status(clip, manifest, rel, hash_to_use)
        quota = "1_kaggle_wan_gpu_minutes" if source == "wan_import" else "0_local_ffmpeg"
        add("shots", sid, sb["models"]["video"], hit, reason, quota)
        clip_hashes.append(hash_to_use)
        clip_paths.append(clip)

    # Final exports: hash depends on every clip, narration line and the score.
    narration_hashes = [contracts.narration_hash(sb, shot) for shot in sb["shots"]]
    narration_paths = [project_root / "outputs" / "narration" / f"{s['id']}.wav" for s in sb["shots"]]
    music_input_hash = contracts.music_candidate_hash(
        sb, wav, seed=match.get("seed"), file_name=match.get("file_name")
    )
    for aspect, (width, height, _, _, _) in ASPECTS.items():
        out = project_root / "outputs" / "final" / f"film_{aspect.replace(':', 'x')}.mp4"
        rel = out.relative_to(project_root).as_posix()
        digest = contracts.assemble_hash(
            sb,
            aspect=aspect,
            width=width,
            height=height,
            clip_paths=clip_paths,
            narration_paths=narration_paths,
            music_path=wav,
            clip_input_hashes=clip_hashes,
            narration_input_hashes=narration_hashes,
            music_input_hash=music_input_hash,
        )
        hit, reason = _status(out, manifest, rel, digest)
        add("assemble", aspect, "ffmpeg-9.1", hit, reason, "0_local_ffmpeg")

    regenerating = [i for i in items if not i["cache_hit"]]
    quota: dict[str, int] = {}
    for item in regenerating:
        key = item["quota_if_regenerated"]
        quota[key] = quota.get(key, 0) + 1

    return {
        "storyboard": str(storyboard_path),
        "total_stages_checked": len(items),
        "cache_hits": len(items) - len(regenerating),
        "would_regenerate": len(regenerating),
        "estimated_quota_if_all_regenerated": quota,
        "radio_cut_total_sec": radio_total,
        "items": items,
        "dependency_map": DEPENDENCY_MAP,
        "note": "Dry run only: no model calls, no writes to runs.jsonl or outputs/manifest.json.",
    }


def format_plan(plan: dict[str, Any]) -> str:
    lines = [
        "DRY RUN - no model calls and no files written.",
        "",
        f"Checked {plan['total_stages_checked']} stage items: "
        f"{plan['cache_hits']} cache hits, {plan['would_regenerate']} would regenerate.",
        "",
        "Stage / shot                         Status      Reason                                  Quota if regenerated",
        "-" * 110,
    ]
    for item in plan["items"]:
        status = "CACHE HIT" if item["cache_hit"] else "REGENERATE"
        label = f"{item['stage']}/{item['shot_id']}"
        lines.append(
            f"{label:<36} {status:<11} {item['reason'][:44]:<44} {item['quota_if_regenerated']}"
        )
    lines.extend(["", "Estimated quota if every listed item regenerates:"])
    for key, count in sorted(plan["estimated_quota_if_all_regenerated"].items()):
        lines.append(f"  {count} x {key}")
    lines.extend(["", "What changes what (dependency map):"])
    for row in plan["dependency_map"]:
        lines.append(f"  - {row}")
    lines.extend(["", plan["note"]])
    return "\n".join(lines)
