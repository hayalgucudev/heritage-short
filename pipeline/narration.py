"""Stage 3: Per-shot Gemini TTS narration with per-shot hash caching and FFmpeg radio cut."""

from __future__ import annotations

import base64
import json
import subprocess
import time
import wave
from pathlib import Path
from typing import Any

from pipeline.cache import compute_stage_hash, update_manifest
from pipeline.env_loader import load_env, require_env
from pipeline.logger import log_run, redact_secrets
from pipeline.smoke import _post_with_retry
from pipeline.validate import validate_storyboard


def _write_pcm_to_wav(pcm_bytes: bytes, out_path: Path, sample_rate: int = 24000) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)


def probe_duration_sec(media_path: Path) -> float:
    """Measure exact duration in seconds using ffprobe."""
    res = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(media_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return round(float(res.stdout.strip()), 3)


def generate_narration(
    project_root: Path,
    storyboard_path: Path,
    schema_path: Path,
    runs_path: Path,
    manifest_path: Path,
    *,
    voice: str = "Aoede",
    only_shot: str | None = None,
) -> list[dict[str, Any]]:
    """Generate one WAV file per shot with deterministic per-shot hash caching."""
    sb = validate_storyboard(storyboard_path, schema_path)
    tts_model = sb["models"]["tts"]
    out_dir = project_root / "outputs" / "narration"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else {"artifacts": {}}
    )
    artifacts = manifest.get("artifacts", {})

    gemini_key: str | None = None
    results: list[dict[str, Any]] = []

    for shot in sb["shots"]:
        sid = shot["id"]
        if only_shot and sid != only_shot:
            continue

        narration_text = shot["narration"].strip()
        planned_sec = float(shot["duration_sec"])
        wav_path = out_dir / f"{sid}.wav"
        rel_wav = wav_path.relative_to(project_root).as_posix()

        # Hash includes ONLY this shot's text, model, and voice so editing 1 line rebuilds 1 shot.
        input_hash = compute_stage_hash(
            stage="narration",
            model=tts_model,
            prompt=narration_text,
            params={"voice": voice, "no_wrapper": True},
        )

        cached_entry = artifacts.get(rel_wav, {})
        if (
            wav_path.exists()
            and cached_entry.get("input_hash") == input_hash
            and cached_entry.get("status") == "ok"
        ):
            measured_sec = probe_duration_sec(wav_path)
            log_run(
                runs_path,
                stage="narration",
                shot_id=sid,
                model=tts_model,
                parameters={"voice": voice, "no_wrapper": True, "duration_sec": measured_sec},
                latency_ms=0,
                cost_or_quota="0_cache_hit",
                cache_hit=True,
                status="ok",
                input_hash=input_hash,
                output_path=rel_wav,
            )
            results.append(
                {
                    "shot_id": sid,
                    "file": rel_wav,
                    "planned_sec": planned_sec,
                    "measured_sec": measured_sec,
                    "fits": measured_sec <= planned_sec,
                    "cache_hit": True,
                    "latency_ms": 0,
                }
            )
            continue

        if gemini_key is None:
            load_env(project_root)
            gemini_key = require_env("GEMINI_API_KEY")

        t0 = time.perf_counter()
        try:
            resp = _post_with_retry(
                f"https://generativelanguage.googleapis.com/v1beta/models/{tts_model}:generateContent",
                headers={"x-goog-api-key": gemini_key, "Content-Type": "application/json"},
                json_body={
                    "contents": [{"parts": [{"text": narration_text}]}],
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {
                            "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}
                        },
                    },
                },
                max_total_sec=60.0,
            )
            latency_ms = int((time.perf_counter() - t0) * 1000)
            inline = resp.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
            audio_bytes = base64.b64decode(inline["data"])
            mime = inline.get("mimeType", "")
            if "wav" in mime.lower():
                wav_path.write_bytes(audio_bytes)
            else:
                _write_pcm_to_wav(audio_bytes, wav_path, sample_rate=24000)

            measured_sec = probe_duration_sec(wav_path)
            update_manifest(
                manifest_path,
                output_file=wav_path,
                project_root=project_root,
                stage="narration",
                shot_id=sid,
                input_hash=input_hash,
            )
            log_run(
                runs_path,
                stage="narration",
                shot_id=sid,
                model=tts_model,
                parameters={
                    "voice": voice,
                    "no_wrapper": True,
                    "mimeType": mime,
                    "duration_sec": measured_sec,
                },
                latency_ms=latency_ms,
                cost_or_quota="1_gemini_tts_call",
                cache_hit=False,
                status="ok",
                input_hash=input_hash,
                output_path=rel_wav,
            )
            results.append(
                {
                    "shot_id": sid,
                    "file": rel_wav,
                    "planned_sec": planned_sec,
                    "measured_sec": measured_sec,
                    "fits": measured_sec <= planned_sec,
                    "cache_hit": False,
                    "latency_ms": latency_ms,
                }
            )
        except Exception as exc:  # noqa: BLE001
            latency_ms = int((time.perf_counter() - t0) * 1000)
            err_msg = redact_secrets(str(exc))
            log_run(
                runs_path,
                stage="narration",
                shot_id=sid,
                model=tts_model,
                parameters={"voice": voice, "no_wrapper": True},
                latency_ms=latency_ms,
                cost_or_quota="1_gemini_tts_call_failed",
                cache_hit=False,
                status="error",
                input_hash=input_hash,
                error=err_msg,
            )
            raise

    return results


def build_radio_cut(
    project_root: Path,
    storyboard_path: Path,
    schema_path: Path,
    runs_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    """Assemble all shot narration WAVs over a quiet placeholder tone on a black screen."""
    sb = validate_storyboard(storyboard_path, schema_path)
    narr_dir = project_root / "outputs" / "narration"
    out_dir = project_root / "outputs" / "final"
    out_dir.mkdir(parents=True, exist_ok=True)
    radio_path = out_dir / "radio_cut.mp4"

    shot_wavs: list[Path] = []
    shot_slots: list[float] = []
    upstream_hashes: dict[str, str] = {}
    for shot in sb["shots"]:
        sid = shot["id"]
        wav_path = narr_dir / f"{sid}.wav"
        if not wav_path.exists():
            raise FileNotFoundError(
                f"Missing narration WAV for {sid}: {wav_path}. Run narration stage first."
            )
        measured = probe_duration_sec(wav_path)
        slot_sec = max(float(shot["duration_sec"]), measured)
        shot_wavs.append(wav_path)
        shot_slots.append(slot_sec)
        upstream_hashes[sid] = compute_stage_hash(
            stage="radio_slot",
            model="ffmpeg",
            params={"slot_sec": slot_sec},
            reference_files=[wav_path],
        )

    end_card_sec = float(sb["end_card"]["duration_sec"])
    total_sec = round(sum(shot_slots) + end_card_sec, 3)

    radio_hash = compute_stage_hash(
        stage="radio_cut",
        model="ffmpeg-9.1",
        params={"total_sec": total_sec, "end_card_sec": end_card_sec},
        reference_files=shot_wavs,
        upstream_hashes=upstream_hashes,
    )

    rel_radio = radio_path.relative_to(project_root).as_posix()
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else {"artifacts": {}}
    )
    cached = manifest.get("artifacts", {}).get(rel_radio, {})
    if (
        radio_path.exists()
        and cached.get("input_hash") == radio_hash
        and cached.get("status") == "ok"
    ):
        log_run(
            runs_path,
            stage="radio_cut",
            shot_id="all",
            model="ffmpeg-9.1",
            parameters={"total_sec": total_sec},
            latency_ms=0,
            cost_or_quota="0_cache_hit",
            cache_hit=True,
            status="ok",
            input_hash=radio_hash,
            output_path=rel_radio,
        )
        return {"file": rel_radio, "total_sec": total_sec, "cache_hit": True}

    t0 = time.perf_counter()
    cmd: list[str] = ["ffmpeg", "-y"]
    for wav in shot_wavs:
        cmd.extend(["-i", str(wav)])

    # Add black video source and quiet warm placeholder tone (soft low sine + filtered room tone)
    cmd.extend(
        [
            "-f",
            "lavfi",
            "-i",
            f"color=c=black:s=1280x720:r=24:d={total_sec}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=110:sample_rate=48000:duration={total_sec}",
            "-f",
            "lavfi",
            "-i",
            f"anoisesrc=color=pink:sample_rate=48000:amplitude=0.015:duration={total_sec}",
        ]
    )

    n = len(shot_wavs)
    video_idx = n
    sine_idx = n + 1
    noise_idx = n + 2

    filter_parts: list[str] = []
    concat_inputs = ""
    for i, slot in enumerate(shot_slots):
        filter_parts.append(
            f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"apad=whole_dur={slot}[s{i}]"
        )
        concat_inputs += f"[s{i}]"

    # End-card silence pad + concat all voice slots
    filter_parts.append(
        f"anullsrc=r=48000:cl=stereo:d={end_card_sec}[end_sil]"
    )
    filter_parts.append(
        f"{concat_inputs}[end_sil]concat=n={n + 1}:v=0:a=1[voice]"
    )
    # Quiet warm placeholder tone (~ -32 dB)
    filter_parts.append(
        f"[{sine_idx}:a]volume=0.015[drone];"
        f"[{noise_idx}:a]lowpass=f=350,volume=0.35[room];"
        f"[drone][room]amix=inputs=2:duration=first:normalize=0[bg];"
        f"[voice][bg]amix=inputs=2:duration=first:normalize=0,"
        f"loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
    )

    cmd.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            f"[{video_idx}:v]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-r",
            "24",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(radio_path),
        ]
    )

    subprocess.run(cmd, check=True, capture_output=True, text=True)
    latency_ms = int((time.perf_counter() - t0) * 1000)

    update_manifest(
        manifest_path,
        output_file=radio_path,
        project_root=project_root,
        stage="radio_cut",
        shot_id="all",
        input_hash=radio_hash,
    )
    log_run(
        runs_path,
        stage="radio_cut",
        shot_id="all",
        model="ffmpeg-9.1",
        parameters={"total_sec": total_sec, "fps": 24, "size": "1280x720"},
        latency_ms=latency_ms,
        cost_or_quota="0_local_ffmpeg",
        cache_hit=False,
        status="ok",
        input_hash=radio_hash,
        output_path=rel_radio,
    )
    return {
        "file": rel_radio,
        "total_sec": total_sec,
        "measured_total_sec": probe_duration_sec(radio_path),
        "cache_hit": False,
        "latency_ms": latency_ms,
    }
