"""Live model ID verification and 1-call provider smoke tests."""

from __future__ import annotations

import base64
import subprocess
import time
import wave
from pathlib import Path
from typing import Any

import requests

from pipeline.cache import compute_stage_hash, retry_with_backoff, update_manifest
from pipeline.env_loader import load_env, require_env
from pipeline.logger import log_run, redact_secrets

# Generic, non-personal Amharic test line about Grandmother and the village courtyard morning.
SMOKE_AMHARIC_TEXT = "አያቴ በጠዋት በመንደሩ ግቢ ውስጥ ትኩስ ቡና እና እንጀራ ታዘጋጃለች።"
SMOKE_AMHARIC_ENGLISH = (
    "In the morning, Grandmother prepares fresh coffee and injera in the village courtyard."
)
SMOKE_IMAGE_PROMPT = (
    "An elderly East African grandmother in a simple white woven shawl pouring morning coffee "
    "from a clay pot in a sunlit village courtyard, centered composition, warm golden-hour light, "
    "painterly storybook gouache texture, warm amber and terracotta palette, no text."
)


class NonRetryableHTTPError(RuntimeError):
    """HTTP error (such as 400/401/403/404) that should not be retried."""


def _post_with_retry(
    url: str,
    *,
    headers: dict[str, str],
    json_body: dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
    timeout: int | tuple[int, int] = (10, 50),
    max_total_sec: float = 60.0,
) -> requests.Response:
    """POST with retries on transient 429/5xx HTTP errors within a hard 60s per-call cap."""
    deadline = time.monotonic() + max_total_sec

    def _do_post() -> requests.Response:
        remaining = deadline - time.monotonic()
        if remaining <= 1.0:
            raise TimeoutError(f"Hard {max_total_sec:.0f}s call timeout reached before attempt.")
        req_timeout = (min(10.0, remaining), max(1.0, remaining))
        resp = requests.post(
            url, headers=headers, json=json_body, files=files, timeout=req_timeout
        )
        if resp.status_code in (429, 500, 502, 503, 504):
            raise requests.HTTPError(
                f"HTTP {resp.status_code}: {resp.text[:300]}", response=resp
            )
        if resp.status_code >= 400:
            raise NonRetryableHTTPError(
                f"HTTP {resp.status_code}: {resp.text[:500]}"
            )
        return resp

    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            return _do_post()
        except NonRetryableHTTPError:
            raise
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt >= 3:
                break
            delay = 2.0 * (2 ** (attempt - 1))
            if time.monotonic() + delay >= deadline:
                break
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc


def verify_live_models(project_root: Path, runs_path: Path) -> dict[str, Any]:
    """Query live Gemini and Cloudflare Workers AI endpoints to check current model IDs."""
    load_env(project_root)
    gemini_key = require_env("GEMINI_API_KEY")
    cf_account = require_env("CLOUDFLARE_ACCOUNT_ID")
    cf_token = require_env("CLOUDFLARE_API_TOKEN")

    results: dict[str, Any] = {"gemini": [], "cloudflare_flux": []}

    # 1. Gemini models list
    t0 = time.perf_counter()
    try:
        def _get_gemini() -> requests.Response:
            r = requests.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                headers={"x-goog-api-key": gemini_key},
                params={"pageSize": 100},
                timeout=30,
            )
            r.raise_for_status()
            return r

        resp = retry_with_backoff(_get_gemini)
        latency_ms = int((time.perf_counter() - t0) * 1000)
        models = resp.json().get("models", [])
        relevant = [
            {
                "name": m.get("name", "").replace("models/", ""),
                "displayName": m.get("displayName", ""),
                "supportedGenerationMethods": m.get("supportedGenerationMethods", []),
            }
            for m in models
            if any(
                k in m.get("name", "").lower()
                for k in ("flash", "tts", "gemini-2", "gemini-3")
            )
        ]
        results["gemini"] = relevant
        log_run(
            runs_path,
            stage="verify_models",
            shot_id="smoke",
            model="gemini-models-list",
            parameters={"count": len(relevant)},
            latency_ms=latency_ms,
            cost_or_quota="0_tokens_metadata",
            status="ok",
        )
    except Exception as exc:  # noqa: BLE001
        latency_ms = int((time.perf_counter() - t0) * 1000)
        log_run(
            runs_path,
            stage="verify_models",
            shot_id="smoke",
            model="gemini-models-list",
            latency_ms=latency_ms,
            status="error",
            error=redact_secrets(str(exc)),
        )
        raise

    # 2. Cloudflare Workers AI FLUX models search
    t1 = time.perf_counter()
    try:
        def _get_cf() -> requests.Response:
            r = requests.get(
                f"https://api.cloudflare.com/client/v4/accounts/{cf_account}/ai/models/search",
                headers={"Authorization": f"Bearer {cf_token}"},
                params={"search": "flux"},
                timeout=30,
            )
            r.raise_for_status()
            return r

        cf_resp = retry_with_backoff(_get_cf)
        latency_ms = int((time.perf_counter() - t1) * 1000)
        cf_models = [
            {
                "name": m.get("name"),
                "task": (m.get("task") or {}).get("name"),
                "description": (m.get("description") or "")[:120],
            }
            for m in cf_resp.json().get("result", [])
        ]
        results["cloudflare_flux"] = cf_models
        log_run(
            runs_path,
            stage="verify_models",
            shot_id="smoke",
            model="cloudflare-models-search",
            parameters={"count": len(cf_models)},
            latency_ms=latency_ms,
            cost_or_quota="0_neurons_metadata",
            status="ok",
        )
    except Exception as exc:  # noqa: BLE001
        latency_ms = int((time.perf_counter() - t1) * 1000)
        log_run(
            runs_path,
            stage="verify_models",
            shot_id="smoke",
            model="cloudflare-models-search",
            latency_ms=latency_ms,
            status="error",
            error=redact_secrets(str(exc)),
        )
        raise

    return results


def _write_pcm_to_wav(pcm_bytes: bytes, out_path: Path, sample_rate: int = 24000) -> None:
    """Save 16-bit mono PCM bytes to a standard WAV file."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)


def run_smoke_tests(
    project_root: Path,
    runs_path: Path,
    manifest_path: Path,
    *,
    gemini_model: str,
    tts_model: str,
    flux_model: str,
    tts_voice: str = "Aoede",
) -> dict[str, Any]:
    """Run one smoke test per provider using explicitly verified model IDs."""
    load_env(project_root)
    gemini_key = require_env("GEMINI_API_KEY")
    cf_account = require_env("CLOUDFLARE_ACCOUNT_ID")
    cf_token = require_env("CLOUDFLARE_API_TOKEN")

    smoke_dir = project_root / "outputs" / "smoke"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {}

    # 1. FFmpeg local check
    ff_res = subprocess.run(
        ["ffmpeg", "-version"], capture_output=True, text=True, check=True
    )
    summary["ffmpeg"] = ff_res.stdout.splitlines()[0]

    # 2. Gemini text JSON check
    text_prompt = (
        "Return a JSON object with keys 'status' ('ok') and 'note' "
        "(a 5-word warm greeting about morning coffee)."
    )
    text_hash = compute_stage_hash(stage="smoke_text", model=gemini_model, prompt=text_prompt)
    t0 = time.perf_counter()
    try:
        text_resp = _post_with_retry(
            f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent",
            headers={"x-goog-api-key": gemini_key, "Content-Type": "application/json"},
            json_body={
                "contents": [{"parts": [{"text": text_prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            },
            timeout=45,
        )
        latency_text = int((time.perf_counter() - t0) * 1000)
        text_out = text_resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        log_run(
            runs_path,
            stage="smoke_text",
            shot_id="smoke",
            model=gemini_model,
            parameters={"responseMimeType": "application/json"},
            latency_ms=latency_text,
            cost_or_quota="1_gemini_text_call",
            status="ok",
            input_hash=text_hash,
        )
        summary["gemini_text"] = {
            "model": gemini_model,
            "latency_ms": latency_text,
            "reply": text_out,
        }
    except Exception as exc:  # noqa: BLE001
        latency_text = int((time.perf_counter() - t0) * 1000)
        err_msg = redact_secrets(str(exc))
        log_run(
            runs_path,
            stage="smoke_text",
            shot_id="smoke",
            model=gemini_model,
            parameters={"responseMimeType": "application/json"},
            latency_ms=latency_text,
            cost_or_quota="1_gemini_text_call_failed",
            status="error",
            input_hash=text_hash,
            error=err_msg,
        )
        summary["gemini_text"] = {"model": gemini_model, "status": "error", "error": err_msg}

    # 3. Gemini TTS Amharic sample
    tts_instruction = (
        f"Speak in a calm, warm, unhurried storytelling voice in Amharic: {SMOKE_AMHARIC_TEXT}"
    )
    tts_hash = compute_stage_hash(
        stage="smoke_tts",
        model=tts_model,
        prompt=tts_instruction,
        params={"voice": tts_voice},
    )
    wav_path = smoke_dir / "amharic_tts_test.wav"
    t1 = time.perf_counter()
    try:
        tts_resp = _post_with_retry(
            f"https://generativelanguage.googleapis.com/v1beta/models/{tts_model}:generateContent",
            headers={"x-goog-api-key": gemini_key, "Content-Type": "application/json"},
            json_body={
                "contents": [{"parts": [{"text": tts_instruction}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {"voiceName": tts_voice}
                        }
                    },
                },
            },
            timeout=60,
        )
        latency_tts = int((time.perf_counter() - t1) * 1000)
        inline = tts_resp.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
        audio_bytes = base64.b64decode(inline["data"])
        mime = inline.get("mimeType", "")
        if "wav" in mime.lower():
            wav_path.write_bytes(audio_bytes)
        else:
            _write_pcm_to_wav(audio_bytes, wav_path, sample_rate=24000)

        update_manifest(
            manifest_path,
            output_file=wav_path,
            project_root=project_root,
            stage="smoke_tts",
            shot_id="smoke",
            input_hash=tts_hash,
        )
        log_run(
            runs_path,
            stage="smoke_tts",
            shot_id="smoke",
            model=tts_model,
            parameters={"voice": tts_voice, "mimeType": mime},
            latency_ms=latency_tts,
            cost_or_quota="1_gemini_tts_call",
            status="ok",
            input_hash=tts_hash,
            output_path=wav_path.relative_to(project_root).as_posix(),
        )
        summary["gemini_tts"] = {
            "model": tts_model,
            "latency_ms": latency_tts,
            "file": wav_path.relative_to(project_root).as_posix(),
            "amharic_text": SMOKE_AMHARIC_TEXT,
            "english_meaning": SMOKE_AMHARIC_ENGLISH,
        }
    except Exception as exc:  # noqa: BLE001
        latency_tts = int((time.perf_counter() - t1) * 1000)
        err_msg = redact_secrets(str(exc))
        log_run(
            runs_path,
            stage="smoke_tts",
            shot_id="smoke",
            model=tts_model,
            parameters={"voice": tts_voice},
            latency_ms=latency_tts,
            cost_or_quota="1_gemini_tts_call_failed",
            status="error",
            input_hash=tts_hash,
            error=err_msg,
        )
        summary["gemini_tts"] = {"model": tts_model, "status": "error", "error": err_msg}

    # 4. Cloudflare Workers AI FLUX smoke test (handles multipart/form-data for flux-2-klein)
    flux_seed = 42
    flux_hash = compute_stage_hash(
        stage="smoke_flux",
        model=flux_model,
        prompt=SMOKE_IMAGE_PROMPT,
        seed=flux_seed,
        params={"steps": 4},
    )
    img_path = smoke_dir / "flux_test.png"
    t2 = time.perf_counter()
    try:
        cf_url = f"https://api.cloudflare.com/client/v4/accounts/{cf_account}/ai/run/{flux_model}"
        cf_headers = {"Authorization": f"Bearer {cf_token}"}
        if "flux-2" in flux_model:
            cf_resp = _post_with_retry(
                cf_url,
                headers=cf_headers,
                files={
                    "prompt": (None, SMOKE_IMAGE_PROMPT),
                    "seed": (None, str(flux_seed)),
                    "steps": (None, "4"),
                },
                timeout=60,
            )
        else:
            cf_resp = _post_with_retry(
                cf_url,
                headers=cf_headers,
                json_body={"prompt": SMOKE_IMAGE_PROMPT, "seed": flux_seed, "steps": 4},
                timeout=60,
            )
        latency_flux = int((time.perf_counter() - t2) * 1000)
        content_type = cf_resp.headers.get("Content-Type", "")
        if "application/json" in content_type:
            img_b64 = cf_resp.json()["result"]["image"]
            img_path.write_bytes(base64.b64decode(img_b64))
        else:
            img_path.write_bytes(cf_resp.content)

        update_manifest(
            manifest_path,
            output_file=img_path,
            project_root=project_root,
            stage="smoke_flux",
            shot_id="smoke",
            input_hash=flux_hash,
        )
        log_run(
            runs_path,
            stage="smoke_flux",
            shot_id="smoke",
            model=flux_model,
            parameters={"steps": 4},
            seed=flux_seed,
            latency_ms=latency_flux,
            cost_or_quota="1_cloudflare_flux_call",
            status="ok",
            input_hash=flux_hash,
            output_path=img_path.relative_to(project_root).as_posix(),
        )
        summary["cloudflare_flux"] = {
            "model": flux_model,
            "latency_ms": latency_flux,
            "file": img_path.relative_to(project_root).as_posix(),
        }
    except Exception as exc:  # noqa: BLE001
        latency_flux = int((time.perf_counter() - t2) * 1000)
        err_msg = redact_secrets(str(exc))
        log_run(
            runs_path,
            stage="smoke_flux",
            shot_id="smoke",
            model=flux_model,
            parameters={"steps": 4},
            seed=flux_seed,
            latency_ms=latency_flux,
            cost_or_quota="1_cloudflare_flux_call_failed",
            status="error",
            input_hash=flux_hash,
            error=err_msg,
        )
        summary["cloudflare_flux"] = {"model": flux_model, "status": "error", "error": err_msg}

    return summary


def run_tts_sample(
    project_root: Path,
    runs_path: Path,
    manifest_path: Path,
    *,
    tts_model: str,
    tts_voice: str,
    out_rel_path: str,
    text: str = SMOKE_AMHARIC_TEXT,
    stage_name: str = "smoke_tts_experiment",
    no_wrapper: bool = False,
) -> dict[str, Any]:
    """Generate one TTS test WAV (1-variable controlled experiment)."""
    load_env(project_root)
    gemini_key = require_env("GEMINI_API_KEY")

    tts_instruction = (
        text
        if no_wrapper
        else f"Speak in a calm, warm, unhurried storytelling voice in Amharic: {text}"
    )
    tts_hash = compute_stage_hash(
        stage=stage_name,
        model=tts_model,
        prompt=tts_instruction,
        params={"voice": tts_voice, "no_wrapper": no_wrapper},
    )
    wav_path = project_root / out_rel_path
    wav_path.parent.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    try:
        tts_resp = _post_with_retry(
            f"https://generativelanguage.googleapis.com/v1beta/models/{tts_model}:generateContent",
            headers={"x-goog-api-key": gemini_key, "Content-Type": "application/json"},
            json_body={
                "contents": [{"parts": [{"text": tts_instruction}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {"voiceName": tts_voice}
                        }
                    },
                },
            },
            timeout=60,
        )
        latency_tts = int((time.perf_counter() - t0) * 1000)
        inline = tts_resp.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
        audio_bytes = base64.b64decode(inline["data"])
        mime = inline.get("mimeType", "")
        if "wav" in mime.lower():
            wav_path.write_bytes(audio_bytes)
        else:
            _write_pcm_to_wav(audio_bytes, wav_path, sample_rate=24000)

        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(wav_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        duration_sec = round(float(probe.stdout.strip()), 3)

        update_manifest(
            manifest_path,
            output_file=wav_path,
            project_root=project_root,
            stage=stage_name,
            shot_id="smoke",
            input_hash=tts_hash,
        )
        log_run(
            runs_path,
            stage=stage_name,
            shot_id="smoke",
            model=tts_model,
            parameters={
                "voice": tts_voice,
                "no_wrapper": no_wrapper,
                "mimeType": mime,
                "duration_sec": duration_sec,
            },
            latency_ms=latency_tts,
            cost_or_quota="1_gemini_tts_call",
            status="ok",
            input_hash=tts_hash,
            output_path=wav_path.relative_to(project_root).as_posix(),
        )
        return {
            "model": tts_model,
            "voice": tts_voice,
            "latency_ms": latency_tts,
            "duration_sec": duration_sec,
            "file": wav_path.relative_to(project_root).as_posix(),
            "amharic_text": text,
        }
    except Exception as exc:  # noqa: BLE001
        latency_tts = int((time.perf_counter() - t0) * 1000)
        err_msg = redact_secrets(str(exc))
        log_run(
            runs_path,
            stage=stage_name,
            shot_id="smoke",
            model=tts_model,
            parameters={"voice": tts_voice},
            latency_ms=latency_tts,
            cost_or_quota="1_gemini_tts_call_failed",
            status="error",
            input_hash=tts_hash,
            error=err_msg,
        )
        raise
