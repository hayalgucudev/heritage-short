"""Ceiling item: one-call Afaan Oromo narration, split locally into shot WAVs.

The locked Amharic storyboard is never edited. The translation prompt, models and
voice live in translations/afaan_oromo.json, not in this file.
"""

from __future__ import annotations

import base64
import json
import re
import subprocess
import time
import wave
from pathlib import Path
from typing import Any

from pipeline.assemble import assemble_film
from pipeline.cache import compute_stage_hash, update_manifest
from pipeline.env_loader import load_env, require_env
from pipeline.logger import log_run
from pipeline.narration import probe_duration_sec
from pipeline.smoke import _post_with_retry
from pipeline.validate import validate_storyboard


def _run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return proc.stdout


def _extract_json_array(text: str) -> list[str]:
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        raise ValueError("Gemini did not return a JSON array for the translation.")
    data = json.loads(match.group(0))
    if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
        raise ValueError("Translation must be a JSON array of strings.")
    return data


def _translate(
    project_root: Path,
    config: dict[str, Any],
    source_lines: list[str],
    runs_path: Path,
) -> tuple[list[str], str, bool]:
    out_dir = project_root / "outputs" / "second_language"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "translation.json"
    text = config["translation_prompt"].replace(
        "{lines}", "\n".join(f"{i + 1}. {line}" for i, line in enumerate(source_lines))
    )
    digest = compute_stage_hash(
        stage="second_language_translate",
        model=config["text_model"],
        prompt=text,
        params={"language": config["language"], "source_field": config["source_field"]},
    )
    if out_path.exists():
        cached = json.loads(out_path.read_text(encoding="utf-8"))
        if cached.get("input_hash") == digest and len(cached.get("lines", [])) == len(source_lines):
            log_run(
                runs_path,
                stage="second_language_translate",
                shot_id="all",
                model=config["text_model"],
                parameters={"language": config["language"], "lines": len(source_lines)},
                latency_ms=0,
                cost_or_quota="0_cache_hit",
                cache_hit=True,
                status="ok",
                input_hash=digest,
                output_path=out_path.relative_to(project_root).as_posix(),
            )
            return cached["lines"], digest, True

    load_env(project_root)
    key = require_env("GEMINI_API_KEY")
    t0 = time.perf_counter()
    resp = _post_with_retry(
        f"https://generativelanguage.googleapis.com/v1beta/models/{config['text_model']}:generateContent",
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        json_body={"contents": [{"parts": [{"text": text}]}]},
        max_total_sec=60.0,
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    lines = _extract_json_array(raw_text)
    if len(lines) != len(source_lines):
        raise ValueError(f"Expected {len(source_lines)} translated lines, got {len(lines)}.")
    out_path.write_text(
        json.dumps(
            {
                "language": config["language"],
                "model": config["text_model"],
                "input_hash": digest,
                "lines": lines,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    log_run(
        runs_path,
        stage="second_language_translate",
        shot_id="all",
        model=config["text_model"],
        parameters={"language": config["language"], "lines": len(lines)},
        latency_ms=latency_ms,
        cost_or_quota="1_gemini_text_call",
        cache_hit=False,
        status="ok",
        input_hash=digest,
        output_path=out_path.relative_to(project_root).as_posix(),
    )
    return lines, digest, False


def _write_pcm_wav(pcm: bytes, out_path: Path, sample_rate: int = 24000) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)


def _silence_boundaries(raw: Path, count: int) -> list[float]:
    proc = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(raw),
            "-af",
            "silencedetect=noise=-38dB:d=0.25",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", proc.stderr)]
    pairs = []
    for start, end in zip(starts, ends):
        if end > start:
            pairs.append(((start + end) / 2.0, end - start))
    pairs.sort(key=lambda p: -p[1])
    chosen = sorted(p[0] for p in pairs[:count])
    return chosen if len(chosen) == count else []


def _word_boundaries(lines: list[str], duration: float, count: int) -> list[float]:
    weights = [max(1, len(line.split())) for line in lines]
    total = sum(weights)
    points: list[float] = []
    running = 0.0
    for w in weights[:-1]:
        running += w / total
        points.append(round(duration * running, 3))
    return points


def _split_and_register(
    project_root: Path,
    raw: Path,
    lines: list[str],
    durations: list[float],
    tts_hash: str,
    runs_path: Path,
    manifest_path: Path,
) -> list[str]:
    out_dir = project_root / "outputs" / "narration_om"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_duration = probe_duration_sec(raw)
    boundaries = _silence_boundaries(raw, len(lines) - 1)
    method = "silence" if boundaries else "word_count_fallback"
    if not boundaries:
        boundaries = _word_boundaries(lines, raw_duration, len(lines))
    edges = [0.0, *boundaries, raw_duration]
    t0 = time.perf_counter()
    hashes: list[str] = []
    for i, line in enumerate(lines):
        planned = durations[i]
        digest = compute_stage_hash(
            stage="second_language_split",
            model="ffmpeg-9.1",
            prompt=line,
            params={
                "code_version": 2,
                "index": i,
                "source_tts_hash": tts_hash,
                "duration_sec": planned,
                "method": method,
            },
        )
        out = out_dir / f"shot_{i + 1:02d}.wav"
        if not out.exists() or (
            json.loads(manifest_path.read_text(encoding="utf-8"))
            .get("artifacts", {})
            .get(out.relative_to(project_root).as_posix(), {})
            .get("input_hash")
            != digest
        ):
            _run(
                [
                    "ffmpeg",
                    "-y",
                    "-hide_banner",
                    "-ss",
                    f"{edges[i]:.3f}",
                    "-i",
                    str(raw),
                    "-t",
                    f"{edges[i + 1] - edges[i]:.3f}",
                    "-af",
                    "asetpts=PTS-STARTPTS,"
                    f"apad=whole_dur={planned:.3f},atrim=duration={planned:.3f},asetpts=PTS-STARTPTS",
                    "-ar",
                    "24000",
                    "-ac",
                    "1",
                    "-c:a",
                    "pcm_s16le",
                    str(out),
                ]
            )
            update_manifest(
                manifest_path,
                output_file=out,
                project_root=project_root,
                stage="second_language_split",
                shot_id=f"shot_{i + 1:02d}",
                input_hash=digest,
            )
        hashes.append(digest)
    log_run(
        runs_path,
        stage="second_language_split",
        shot_id="all",
        model="ffmpeg-9.1",
        parameters={
            "method": method,
            "pauses_found": 0 if method == "word_count_fallback" else len(lines) - 1,
            "edges": [round(x, 3) for x in edges],
            "durations": durations,
        },
        latency_ms=int((time.perf_counter() - t0) * 1000),
        cost_or_quota="0_local_ffmpeg",
        cache_hit=False,
        status="ok",
        input_hash=tts_hash,
        output_path="outputs/narration_om/",
    )
    return hashes


def _long_tts(
    project_root: Path,
    config: dict[str, Any],
    lines: list[str],
    translation_hash: str,
    runs_path: Path,
    manifest_path: Path,
) -> tuple[Path, str, bool]:
    out_dir = project_root / "outputs" / "second_language"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = out_dir / "long_narration.wav"
    joined = config["tts_joiner"].join(lines)
    digest = compute_stage_hash(
        stage="second_language_tts",
        model=config["tts_model"],
        prompt=joined,
        params={"voice": config["voice"], "upstream_translation": translation_hash},
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    got = manifest.get("artifacts", {}).get(raw.relative_to(project_root).as_posix(), {}).get("input_hash")
    if raw.exists() and got == digest:
        log_run(
            runs_path,
            stage="second_language_tts",
            shot_id="all",
            model=config["tts_model"],
            parameters={"voice": config["voice"], "lines": len(lines), "chars": len(joined)},
            latency_ms=0,
            cost_or_quota="0_cache_hit",
            cache_hit=True,
            status="ok",
            input_hash=digest,
            output_path=raw.relative_to(project_root).as_posix(),
        )
        return raw, digest, True

    load_env(project_root)
    key = require_env("GEMINI_API_KEY")
    t0 = time.perf_counter()
    resp = _post_with_retry(
        f"https://generativelanguage.googleapis.com/v1beta/models/{config['tts_model']}:generateContent",
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        json_body={
            "contents": [{"parts": [{"text": joined}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": config["voice"]}}
                },
            },
        },
        max_total_sec=120.0,
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    inline = resp.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
    audio = base64.b64decode(inline["data"])
    mime = inline.get("mimeType", "")
    if "wav" in mime.lower():
        raw.write_bytes(audio)
    else:
        _write_pcm_wav(audio, raw)
    duration = probe_duration_sec(raw)
    update_manifest(
        manifest_path,
        output_file=raw,
        project_root=project_root,
        stage="second_language_tts",
        shot_id="all",
        input_hash=digest,
    )
    log_run(
        runs_path,
        stage="second_language_tts",
        shot_id="all",
        model=config["tts_model"],
        parameters={
            "voice": config["voice"],
            "lines": len(lines),
            "chars": len(joined),
            "mimeType": mime,
            "duration_sec": duration,
        },
        latency_ms=latency_ms,
        cost_or_quota="1_gemini_tts_call",
        cache_hit=False,
        status="ok",
        input_hash=digest,
        output_path=raw.relative_to(project_root).as_posix(),
    )
    return raw, digest, False


def run_second_language(
    project_root: Path,
    storyboard_path: Path,
    schema_path: Path,
    runs_path: Path,
    manifest_path: Path,
    config_path: Path,
) -> dict[str, Any]:
    """Translate, make one TTS call, split locally, then build both variants."""
    sb = validate_storyboard(storyboard_path, schema_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    source_lines = [shot[config["source_field"]].replace("\n", " ") for shot in sb["shots"]]
    lines, translation_hash, translation_cached = _translate(
        project_root, config, source_lines, runs_path
    )
    raw, tts_hash, tts_cached = _long_tts(
        project_root, config, lines, translation_hash, runs_path, manifest_path
    )
    durations = [float(shot["duration_sec"]) for shot in sb["shots"]]
    narration_hashes = _split_and_register(
        project_root, raw, lines, durations, tts_hash, runs_path, manifest_path
    )
    exports = assemble_film(
        project_root,
        storyboard_path,
        schema_path,
        runs_path,
        manifest_path,
        narration_dir=project_root / "outputs" / "narration_om",
        output_suffix="_om",
        narration_hashes_override=narration_hashes,
    )
    return {
        "language": config["language"],
        "translation_cache_hit": translation_cached,
        "tts_cache_hit": tts_cached,
        "model_calls": 0 if translation_cached and tts_cached else 2,
        "translated_lines": lines,
        "native_speaker_check": config["native_speaker_check"],
        "exports": exports,
    }
