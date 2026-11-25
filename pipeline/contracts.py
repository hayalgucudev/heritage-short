"""Shared hash recipes for every stage.

The real stage modules and the dry-run planner both call these functions. If a
recipe changes here, both sides change together, so `py run.py plan` cannot
silently disagree with what a stage actually caches.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.cache import compute_stage_hash
from pipeline.narration import probe_duration_sec


def _selected_reference(sb: dict[str, Any], project_root: Path) -> Path | None:
    rel = sb.get("character", {}).get("selected_reference_image")
    if not rel:
        return None
    path = Path(rel)
    return path if path.is_absolute() else project_root / path


def reference_sheet_hash(sb: dict[str, Any], seed: int, *, steps: int = 4) -> str:
    """Exact hash used by generate_reference_sheet()."""
    prompt = (
        f"Candid documentary portrait of {sb['character']['description']}, "
        "gentle natural expression, relaxed posture, hands resting naturally holding a simple clay coffee cup near her lap, "
        f"plain mud-plaster courtyard wall background, centered framing for 9:16 and 16:9 crops, {sb['style_block']}"
    )
    return compute_stage_hash(
        stage="reference_sheet",
        model=sb["models"]["keyframes"],
        prompt=prompt,
        seed=int(seed),
        params={"steps": steps},
    )


def keyframe_hash(
    sb: dict[str, Any],
    shot: dict[str, Any],
    *,
    project_root: Path,
    steps: int = 4,
    use_reference: bool = False,
) -> str:
    """Exact hash used by generate_keyframes().

    Production keyframes were generated with --no-ref, so plan defaults to
    use_reference=False to avoid falsely invalidating all ten stills.
    """
    shot_ref = None
    if use_reference and "grandmother" in shot["image_prompt"].lower():
        shot_ref = _selected_reference(sb, project_root)
    refs = [shot_ref] if shot_ref is not None else []
    return compute_stage_hash(
        stage="keyframes",
        model=sb["models"]["keyframes"],
        prompt=shot["image_prompt"],
        seed=int(shot["image_seed"]),
        params={"steps": steps, "style_block": sb["style_block"]},
        reference_files=refs,
    )


def narration_hash(
    sb: dict[str, Any],
    shot: dict[str, Any],
    *,
    tts_model_override: str | None = None,
    voice_override: str | None = None,
) -> str:
    """Exact hash used by generate_narration()."""
    voice = voice_override or shot.get("tts_style", "Kore").split(",", 1)[0].strip()
    return compute_stage_hash(
        stage="narration",
        model=tts_model_override or sb["models"]["tts"],
        prompt=shot["narration"].strip(),
        params={"voice": voice, "no_wrapper": True},
    )


def radio_cut_hash(sb: dict[str, Any], project_root: Path) -> tuple[str, float]:
    """Exact hash used by build_radio_cut(); returns (hash, total_seconds)."""
    shot_wavs: list[Path] = []
    upstream: dict[str, str] = {}
    total = float(sb["end_card"]["duration_sec"])
    for shot in sb["shots"]:
        wav = project_root / "outputs" / "narration" / f"{shot['id']}.wav"
        measured = probe_duration_sec(wav) if wav.exists() else 0.0
        slot = max(float(shot["duration_sec"]), measured)
        total += slot
        shot_wavs.append(wav)
        upstream[shot["id"]] = compute_stage_hash(
            stage="radio_slot",
            model="ffmpeg",
            params={"slot_sec": slot},
            reference_files=[wav],
        )
    total = round(total, 3)
    digest = compute_stage_hash(
        stage="radio_cut",
        model="ffmpeg-9.1",
        params={"total_sec": total, "end_card_sec": float(sb["end_card"]["duration_sec"])},
        reference_files=shot_wavs,
        upstream_hashes=upstream,
    )
    return digest, total


def music_hash(sb: dict[str, Any]) -> str:
    """Exact hash used by run_music_stage()."""
    from pipeline.music import compute_music_hash

    return compute_music_hash(sb)


def music_candidate_hash(
    sb: dict[str, Any], wav: Path, *, seed: int | None, file_name: str | None = None
) -> str:
    """Exact hash used by run_music_stage() for a downloaded candidate."""
    return compute_stage_hash(
        stage="music_candidate",
        model=sb["models"]["music"],
        prompt=sb["music"]["caption"],
        seed=seed,
        params={"music_hash": music_hash(sb), "file_name": file_name or wav.name},
    )


def clip_hash(
    sb: dict[str, Any],
    shot: dict[str, Any],
    keyframe_path: Path,
    keyframe_input_hash: str,
    *,
    source: str,
) -> str:
    """Hash for a moving clip, whether from Wan import or Ken Burns fallback."""
    if source not in {"wan_import", "ken_burns"}:
        raise ValueError(f"Unknown clip source: {source}")
    return compute_stage_hash(
        stage="shots",
        model=sb["models"]["video"],
        prompt=shot["video_motion_prompt"],
        seed=int(shot["video_seed"]),
        params={
            "duration_sec": float(shot["duration_sec"]),
            "resolution": "480p",
            "source": source,
            "fps": 24,
        },
        reference_files=[keyframe_path],
        upstream_hashes={"keyframes": keyframe_input_hash},
    )


ASSEMBLE_SETTINGS: dict[str, Any] = {
    # Bump when the FFmpeg filter graph changes even if storyboard inputs do not.
    # v2 adds asplit=2 so the voice sidechain cannot truncate the final 2 slots.
    # v3: +10% Arial Bold subtitles, restyled 3 s end card, quiet seeded room tone.
    "code_version": 3,
    "subtitle_bold": True,
    "subtitle_size_scale": 1.10,
    "endcard_style_version": 2,
    "ambience": {
        "source": "local_anoisesrc_pink",
        "seed": 20261126,
        "lowpass_hz": 1400,
        "gain": 0.06,
    },
    "fps": 24,
    "sidechain_threshold": 0.02,
    "sidechain_ratio": 6,
    "sidechain_attack_ms": 300,
    "sidechain_release_ms": 1500,
    "loudnorm_i": -14,
    "loudnorm_tp": -1,
    "loudnorm_lra": 11,
    "output_sample_rate": 48000,
}


def assemble_hash(
    sb: dict[str, Any],
    *,
    aspect: str,
    width: int,
    height: int,
    clip_paths: list[Path],
    narration_paths: list[Path],
    music_path: Path,
    clip_input_hashes: list[str],
    narration_input_hashes: list[str],
    music_input_hash: str,
    variant: str = "",
) -> str:
    """Hash for one final aspect-ratio export."""
    upstream = {
        **{f"clip_{i}": h for i, h in enumerate(clip_input_hashes)},
        **{f"narration_{i}": h for i, h in enumerate(narration_input_hashes)},
        "music": music_input_hash,
    }
    return compute_stage_hash(
        stage="assemble",
        model="ffmpeg-9.1",
        prompt=sb["end_card"]["text"],
        params={
            "aspect": aspect,
            "width": width,
            "height": height,
            "end_card_sec": float(sb["end_card"]["duration_sec"]),
            "variant": variant,
            "settings": ASSEMBLE_SETTINGS,
        },
        reference_files=clip_paths + narration_paths + [music_path],
        upstream_hashes=upstream,
    )


def manifest_hash(manifest: dict[str, Any], rel_path: str) -> str | None:
    """Return a manifest input_hash, or None when the artifact is untracked."""
    return manifest.get("artifacts", {}).get(rel_path, {}).get("input_hash")


def is_cached(manifest: dict[str, Any], path: Path, expected_hash: str) -> bool:
    """House cache rule: file exists, manifest hash matches, status is ok."""
    if not path.exists():
        return False
    entry = manifest.get("artifacts", {}).get(str(path), {})
    return entry.get("input_hash") == expected_hash and entry.get("status") == "ok"


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.exists():
        return {"artifacts": {}}
    return json.loads(manifest_path.read_text(encoding="utf-8"))
