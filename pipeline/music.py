"""Stage 5: ACE-Step 1.5 music score spec export, candidate import, and hash caching."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from pipeline.cache import compute_stage_hash, update_manifest
from pipeline.logger import log_run
from pipeline.narration import probe_duration_sec
from pipeline.validate import validate_storyboard


def compute_music_hash(sb: dict[str, Any]) -> str:
    """Compute deterministic hash for the storyboard music section."""
    m = sb["music"]
    return compute_stage_hash(
        stage="music",
        model=sb["models"]["music"],
        prompt=m["caption"],
        seed=int(m["seed"]),
        params={
            "style": m["style"],
            "mood": m["mood"],
            "instruments": m["instruments"],
            "texture": m["texture"],
            "tempo_bpm": int(m["tempo_bpm"]),
            "key": m["key"],
            "duration_sec": float(m["duration_sec"]),
            "num_candidates": 3,
        },
    )


def run_music_stage(
    project_root: Path,
    storyboard_path: Path,
    schema_path: Path,
    runs_path: Path,
    manifest_path: Path,
    *,
    import_dir: Path | None = None,
) -> dict[str, Any]:
    """Export music spec for Kaggle or register/cache downloaded ACE-Step candidates."""
    sb = validate_storyboard(storyboard_path, schema_path)
    music_dir = project_root / "outputs" / "music"
    music_dir.mkdir(parents=True, exist_ok=True)
    music_hash = compute_music_hash(sb)

    if import_dir is not None:
        if not import_dir.exists():
            raise FileNotFoundError(f"Music import directory not found: {import_dir}")
        for wav in sorted(import_dir.glob("*.wav")):
            shutil.copy2(wav, music_dir / wav.name)
        meta_src = import_dir / "music_run_metadata.json"
        if meta_src.exists():
            shutil.copy2(meta_src, music_dir / "music_run_metadata.json")

    spec_path = music_dir / "music_job.json"
    spec_payload = {
        "input_hash": music_hash,
        "model": sb["models"]["music"],
        "music": sb["music"],
        "notebook": "notebooks/acestep_music.ipynb",
    }
    spec_path.write_text(json.dumps(spec_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    wavs = sorted(music_dir.glob("candidate_*.wav"))
    if not wavs:
        return {
            "status": "pending_kaggle",
            "input_hash": music_hash,
            "job_spec": spec_path.relative_to(project_root).as_posix(),
            "notebook": "notebooks/acestep_music.ipynb",
            "instructions": (
                "Upload notebooks/acestep_music.ipynb to Kaggle (GPU T4 x2, Internet On), "
                "run all cells, and extract the zip into outputs/music/."
            ),
        }

    meta_file = music_dir / "music_run_metadata.json"
    meta_by_name: dict[str, dict[str, Any]] = {}
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        for item in meta.get("candidates", []):
            meta_by_name[item.get("file_name", "")] = item

    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else {"artifacts": {}}
    )
    artifacts = manifest.get("artifacts", {})

    registered: list[dict[str, Any]] = []
    for wav in wavs:
        rel_wav = wav.relative_to(project_root).as_posix()
        cand_meta = meta_by_name.get(wav.name, {})
        seed = cand_meta.get("seed")
        cand_hash = compute_stage_hash(
            stage="music_candidate",
            model=sb["models"]["music"],
            prompt=sb["music"]["caption"],
            seed=seed,
            params={"music_hash": music_hash, "file_name": wav.name},
        )
        duration_sec = probe_duration_sec(wav)
        cached = artifacts.get(rel_wav, {})
        if cached.get("input_hash") == cand_hash and cached.get("status") == "ok":
            log_run(
                runs_path,
                stage="music",
                shot_id=cand_meta.get("candidate_id", wav.stem),
                model=sb["models"]["music"],
                parameters={"duration_sec": duration_sec, "bpm": sb["music"]["tempo_bpm"], "key": sb["music"]["key"]},
                seed=seed,
                latency_ms=0,
                cost_or_quota="0_cache_hit",
                cache_hit=True,
                status="ok",
                input_hash=cand_hash,
                output_path=rel_wav,
            )
            registered.append({"file": rel_wav, "duration_sec": duration_sec, "seed": seed, "cache_hit": True})
            continue

        latency_ms = cand_meta.get("latency_ms")
        update_manifest(
            manifest_path,
            output_file=wav,
            project_root=project_root,
            stage="music",
            shot_id=cand_meta.get("candidate_id", wav.stem),
            input_hash=cand_hash,
        )
        log_run(
            runs_path,
            stage="music",
            shot_id=cand_meta.get("candidate_id", wav.stem),
            model=sb["models"]["music"],
            parameters={"duration_sec": duration_sec, "bpm": sb["music"]["tempo_bpm"], "key": sb["music"]["key"]},
            seed=seed,
            latency_ms=latency_ms,
            cost_or_quota="1_kaggle_acestep_call",
            cache_hit=False,
            status="ok",
            input_hash=cand_hash,
            output_path=rel_wav,
        )
        registered.append({"file": rel_wav, "duration_sec": duration_sec, "seed": seed, "cache_hit": False})

    return {
        "status": "candidates_ready",
        "input_hash": music_hash,
        "selected_candidate": sb["music"].get("selected_candidate"),
        "candidates": registered,
    }
