"""Stage 6: import Wan 2.2 clips, or fall back to deterministic FFmpeg Ken Burns."""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from pipeline import contracts
from pipeline.cache import update_manifest
from pipeline.logger import log_run
from pipeline.narration import probe_duration_sec
from pipeline.validate import validate_storyboard


def _wan_metadata(import_dir: Path | None) -> dict[str, dict[str, Any]]:
    if import_dir is None:
        return {}
    meta_path = import_dir / "wan_run_metadata.json"
    if not meta_path.exists():
        return {}
    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    return {
        item["shot_id"]: item
        for item in payload.get("candidates", [])
        if item.get("shot_id")
    }


def _ken_burns(keyframe: Path, out_path: Path, duration_sec: float, fps: int = 24) -> None:
    """Local, deterministic fallback: gentle centred zoom over the clean still."""
    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-framerate",
        str(fps),
        "-t",
        f"{duration_sec:.3f}",
        "-i",
        str(keyframe),
        "-vf",
        (
            "scale=960:960:force_original_aspect_ratio=increase,"
            "crop=960:960,"
            "zoompan=z='min(zoom+0.00045,1.10)':"
            "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d=1:s=480x480:fps={fps},format=yuv420p"
        ),
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(fps),
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def run_shots_stage(
    project_root: Path,
    storyboard_path: Path,
    schema_path: Path,
    runs_path: Path,
    manifest_path: Path,
    *,
    import_dir: Path | None = None,
    only_shot: str | None = None,
    force: bool = False,
) -> list[dict[str, Any]]:
    """Register imported Wan clips or generate Ken Burns fallbacks, one shot at a time."""
    sb = validate_storyboard(storyboard_path, schema_path)
    manifest = contracts.load_manifest(manifest_path)
    artifacts = manifest.get("artifacts", {})
    wan_meta = _wan_metadata(import_dir)
    clips_dir = project_root / "outputs" / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for shot in sb["shots"]:
        sid = shot["id"]
        if only_shot and sid != only_shot:
            continue

        keyframe = project_root / "outputs" / "keyframes" / f"{sid}.png"
        if not keyframe.exists():
            raise FileNotFoundError(
                f"Missing keyframe for {sid}: {keyframe}. Run keyframes stage first."
            )
        kf_hash = contracts.keyframe_hash(
            sb, shot, project_root=project_root, steps=4, use_reference=False
        )
        if artifacts.get(keyframe.relative_to(project_root).as_posix(), {}).get("input_hash") != kf_hash:
            raise ValueError(
                f"Keyframe {sid} is stale for the current storyboard. Regenerate keyframes before clips."
            )

        imported_src = import_dir / f"{sid}.mp4" if import_dir is not None else None
        source = "wan_import" if imported_src is not None and imported_src.exists() else "ken_burns"
        clip_path = clips_dir / f"{sid}.mp4"
        rel_clip = clip_path.relative_to(project_root).as_posix()
        input_hash = contracts.clip_hash(
            sb, shot, keyframe, kf_hash, source=source
        )

        cached = artifacts.get(rel_clip, {})
        if not force and cached.get("input_hash") == input_hash and cached.get("status") == "ok" and clip_path.exists():
            log_run(
                runs_path,
                stage="shots",
                shot_id=sid,
                model=sb["models"]["video"],
                parameters={"source": source, "duration_sec": float(shot["duration_sec"])},
                seed=int(shot["video_seed"]),
                latency_ms=0,
                cost_or_quota="0_cache_hit",
                cache_hit=True,
                status="ok",
                input_hash=input_hash,
                output_path=rel_clip,
            )
            results.append(
                {
                    "shot_id": sid,
                    "source": source,
                    "file": rel_clip,
                    "cache_hit": True,
                    "latency_ms": 0,
                    "input_hash": input_hash,
                }
            )
            continue

        t0 = time.perf_counter()
        if source == "wan_import":
            shutil.copy2(imported_src, clip_path)
            latency_ms = wan_meta.get(sid, {}).get("latency_ms")
            quota = "1_kaggle_wan_call"
        else:
            _ken_burns(keyframe, clip_path, float(shot["duration_sec"]))
            latency_ms = int((time.perf_counter() - t0) * 1000)
            quota = "0_local_ffmpeg"

        update_manifest(
            manifest_path,
            output_file=clip_path,
            project_root=project_root,
            stage="shots",
            shot_id=sid,
            input_hash=input_hash,
        )
        log_run(
            runs_path,
            stage="shots",
            shot_id=sid,
            model=sb["models"]["video"],
            parameters={"source": source, "duration_sec": float(shot["duration_sec"])},
            seed=int(shot["video_seed"]),
            latency_ms=latency_ms,
            cost_or_quota=quota,
            cache_hit=False,
            status="ok",
            input_hash=input_hash,
            output_path=rel_clip,
        )
        results.append(
            {
                "shot_id": sid,
                "source": source,
                "file": rel_clip,
                "cache_hit": False,
                "latency_ms": latency_ms,
                "duration_sec": probe_duration_sec(clip_path),
                "input_hash": input_hash,
            }
        )

    return results


def export_clips_job(
    project_root: Path,
    storyboard_path: Path,
    schema_path: Path,
    *,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    """Package a Kaggle-uploadable job: subset storyboard + 10 keyframes + README."""
    sb = validate_storyboard(storyboard_path, schema_path)
    job_dir = out_dir or (project_root / "outputs" / "wan_job")
    job_dir.mkdir(parents=True, exist_ok=True)
    keyframes_dir = job_dir / "keyframes"
    keyframes_dir.mkdir(parents=True, exist_ok=True)

    shots: list[dict[str, Any]] = []
    for shot in sb["shots"]:
        sid = shot["id"]
        src = project_root / "outputs" / "keyframes" / f"{sid}.png"
        if not src.exists():
            raise FileNotFoundError(f"Missing keyframe for {sid}: {src}")
        shutil.copy2(src, keyframes_dir / f"{sid}.png")
        shots.append(
            {
                "id": sid,
                "video_motion_prompt": shot["video_motion_prompt"],
                "video_seed": int(shot["video_seed"]),
                "duration_sec": float(shot["duration_sec"]),
                "keyframe": f"keyframes/{sid}.png",
            }
        )

    job = {
        "model": sb["models"]["video"],
        "fps": 24,
        "width": 480,
        "height": 480,
        "num_frames_rule": "4n+1, round(duration_sec * fps) then adjust to 4n+1",
        "negative_prompt": (
            "low quality, blurry, distorted hands, extra fingers, fused fingers, "
            "deformed face, text, watermark, subtitles, oversaturated, static frame"
        ),
        "shots": shots,
    }
    (job_dir / "wan_job.json").write_text(
        json.dumps(job, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (job_dir / "README.txt").write_text(
        "Upload this folder as a Kaggle dataset. In the Wan notebook set "
        "KAGGLE_DATASET_NAME to the dataset slug, run the smoke cell first, "
        "check the clip, then run the remaining shots. Return the zip with "
        "shot_01.mp4 ... shot_10.mp4 and wan_run_metadata.json.\n",
        encoding="utf-8",
    )
    zip_path = shutil.make_archive(str(job_dir), "zip", job_dir)
    return {
        "job_dir": job_dir.relative_to(project_root).as_posix(),
        "zip": Path(zip_path).relative_to(project_root).as_posix(),
        "shots": len(shots),
    }
