"""Stage 4: Character reference sheet and keyframe generation via Cloudflare FLUX."""

from __future__ import annotations

import base64
import json
import time
from pathlib import Path
from typing import Any

from pipeline.cache import compute_stage_hash, update_manifest
from pipeline.env_loader import load_env, require_env
from pipeline.logger import log_run, redact_secrets
from pipeline.smoke import _post_with_retry
from pipeline.validate import validate_storyboard


def _call_cloudflare_flux(
    cf_account: str,
    cf_token: str,
    flux_model: str,
    *,
    prompt: str,
    seed: int,
    steps: int = 4,
    input_image_path: Path | None = None,
) -> bytes:
    """Call Cloudflare Workers AI FLUX endpoint and return raw PNG bytes."""
    cf_url = f"https://api.cloudflare.com/client/v4/accounts/{cf_account}/ai/run/{flux_model}"
    cf_headers = {"Authorization": f"Bearer {cf_token}"}

    if "flux-2" in flux_model:
        files: dict[str, tuple[str | None, Any, str] | tuple[None, str]] = {
            "prompt": (None, prompt),
            "seed": (None, str(seed)),
            "steps": (None, str(steps)),
        }
        if input_image_path is not None:
            img_bytes = input_image_path.read_bytes()
            files["input_image_0"] = (input_image_path.name, img_bytes, "image/png")
        resp = _post_with_retry(
            cf_url,
            headers=cf_headers,
            files=files,
            timeout=60,
            max_total_sec=90.0,
        )
    else:
        resp = _post_with_retry(
            cf_url,
            headers=cf_headers,
            json_body={"prompt": prompt, "seed": seed, "steps": steps},
            timeout=60,
            max_total_sec=90.0,
        )

    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
        img_b64 = resp.json()["result"]["image"]
        return base64.b64decode(img_b64)
    return resp.content


def generate_reference_sheet(
    project_root: Path,
    storyboard_path: Path,
    schema_path: Path,
    runs_path: Path,
    manifest_path: Path,
    *,
    count: int = 3,
    steps: int = 4,
    file_prefix: str = "ref_real_seed",
) -> list[dict[str, Any]]:
    """Generate candidate character reference portraits for director selection."""
    sb = validate_storyboard(storyboard_path, schema_path)
    flux_model = sb["models"]["keyframes"]
    base_seed = int(sb["character"]["reference_seed"])
    ref_prompt = (
        f"Candid documentary portrait of {sb['character']['description']}, "
        "gentle natural expression, relaxed posture, hands resting naturally holding a simple clay coffee cup near her lap, "
        f"plain mud-plaster courtyard wall background, centered framing for 9:16 and 16:9 crops, {sb['style_block']}"
    )

    out_dir = project_root / "outputs" / "keyframes"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else {"artifacts": {}}
    )
    artifacts = manifest.get("artifacts", {})

    cf_account: str | None = None
    cf_token: str | None = None
    results: list[dict[str, Any]] = []

    for i in range(count):
        seed = base_seed + i
        cand_id = f"{file_prefix}_{i + 1:02d}"
        img_path = out_dir / f"{file_prefix}{seed}.png"
        rel_img = img_path.relative_to(project_root).as_posix()

        input_hash = compute_stage_hash(
            stage="reference_sheet",
            model=flux_model,
            prompt=ref_prompt,
            seed=seed,
            params={"steps": steps},
        )
        cached = artifacts.get(rel_img, {})
        if (
            img_path.exists()
            and cached.get("input_hash") == input_hash
            and cached.get("status") == "ok"
        ):
            log_run(
                runs_path,
                stage="reference_sheet",
                shot_id=cand_id,
                model=flux_model,
                parameters={"steps": steps},
                seed=seed,
                latency_ms=0,
                cost_or_quota="0_cache_hit",
                cache_hit=True,
                status="ok",
                input_hash=input_hash,
                output_path=rel_img,
            )
            results.append({"id": cand_id, "seed": seed, "file": rel_img, "cache_hit": True, "latency_ms": 0})
            continue

        if cf_account is None or cf_token is None:
            load_env(project_root)
            cf_account = require_env("CLOUDFLARE_ACCOUNT_ID")
            cf_token = require_env("CLOUDFLARE_API_TOKEN")

        t0 = time.perf_counter()
        try:
            png_bytes = _call_cloudflare_flux(
                cf_account,
                cf_token,
                flux_model,
                prompt=ref_prompt,
                seed=seed,
                steps=steps,
            )
            latency_ms = int((time.perf_counter() - t0) * 1000)
            img_path.write_bytes(png_bytes)

            update_manifest(
                manifest_path,
                output_file=img_path,
                project_root=project_root,
                stage="reference_sheet",
                shot_id=cand_id,
                input_hash=input_hash,
            )
            log_run(
                runs_path,
                stage="reference_sheet",
                shot_id=cand_id,
                model=flux_model,
                parameters={"steps": steps},
                seed=seed,
                latency_ms=latency_ms,
                cost_or_quota="1_cloudflare_flux_call",
                cache_hit=False,
                status="ok",
                input_hash=input_hash,
                output_path=rel_img,
            )
            results.append({"id": cand_id, "seed": seed, "file": rel_img, "cache_hit": False, "latency_ms": latency_ms})
        except Exception as exc:  # noqa: BLE001
            latency_ms = int((time.perf_counter() - t0) * 1000)
            err_msg = redact_secrets(str(exc))
            log_run(
                runs_path,
                stage="reference_sheet",
                shot_id=cand_id,
                model=flux_model,
                parameters={"steps": steps},
                seed=seed,
                latency_ms=latency_ms,
                cost_or_quota="1_cloudflare_flux_call_failed",
                cache_hit=False,
                status="error",
                input_hash=input_hash,
                error=err_msg,
            )
            raise

    return results


def generate_keyframes(
    project_root: Path,
    storyboard_path: Path,
    schema_path: Path,
    runs_path: Path,
    manifest_path: Path,
    *,
    only_shot: str | None = None,
    steps: int = 4,
    use_reference: bool = True,
) -> list[dict[str, Any]]:
    """Generate per-shot keyframes conditioned on storyboard style and approved reference."""
    sb = validate_storyboard(storyboard_path, schema_path)
    flux_model = sb["models"]["keyframes"]
    sel_ref_rel = sb["character"].get("selected_reference_image")
    ref_path: Path | None = None
    if use_reference:
        if not sel_ref_rel:
            raise ValueError(
                "character.selected_reference_image is null in storyboard.json. "
                "Approve a reference candidate before generating keyframes."
            )
        ref_path = project_root / sel_ref_rel
        if not ref_path.exists():
            raise FileNotFoundError(f"Selected reference image not found: {ref_path}")

    out_dir = project_root / "outputs" / "keyframes"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else {"artifacts": {}}
    )
    artifacts = manifest.get("artifacts", {})

    cf_account: str | None = None
    cf_token: str | None = None
    results: list[dict[str, Any]] = []

    for shot in sb["shots"]:
        sid = shot["id"]
        if only_shot and sid != only_shot:
            continue

        prompt = shot["image_prompt"]
        seed = int(shot["image_seed"])
        img_path = out_dir / f"{sid}.png"
        rel_img = img_path.relative_to(project_root).as_posix()

        # Condition character shots on selected reference; shot_01 (village landscape) can omit ref if desired.
        shot_ref = ref_path if (ref_path is not None and "grandmother" in prompt.lower()) else None
        refs = [shot_ref] if shot_ref is not None else []

        input_hash = compute_stage_hash(
            stage="keyframes",
            model=flux_model,
            prompt=prompt,
            seed=seed,
            params={"steps": steps, "style_block": sb["style_block"]},
            reference_files=refs,
        )
        cached = artifacts.get(rel_img, {})
        if (
            img_path.exists()
            and cached.get("input_hash") == input_hash
            and cached.get("status") == "ok"
        ):
            log_run(
                runs_path,
                stage="keyframes",
                shot_id=sid,
                model=flux_model,
                parameters={"steps": steps, "conditioned": shot_ref is not None},
                seed=seed,
                latency_ms=0,
                cost_or_quota="0_cache_hit",
                cache_hit=True,
                status="ok",
                input_hash=input_hash,
                output_path=rel_img,
            )
            results.append({"shot_id": sid, "seed": seed, "file": rel_img, "cache_hit": True, "latency_ms": 0})
            continue

        if cf_account is None or cf_token is None:
            load_env(project_root)
            cf_account = require_env("CLOUDFLARE_ACCOUNT_ID")
            cf_token = require_env("CLOUDFLARE_API_TOKEN")

        t0 = time.perf_counter()
        try:
            png_bytes = _call_cloudflare_flux(
                cf_account,
                cf_token,
                flux_model,
                prompt=prompt,
                seed=seed,
                steps=steps,
                input_image_path=shot_ref,
            )
            latency_ms = int((time.perf_counter() - t0) * 1000)
            img_path.write_bytes(png_bytes)

            update_manifest(
                manifest_path,
                output_file=img_path,
                project_root=project_root,
                stage="keyframes",
                shot_id=sid,
                input_hash=input_hash,
            )
            log_run(
                runs_path,
                stage="keyframes",
                shot_id=sid,
                model=flux_model,
                parameters={"steps": steps, "conditioned": shot_ref is not None},
                seed=seed,
                latency_ms=latency_ms,
                cost_or_quota="1_cloudflare_flux_call",
                cache_hit=False,
                status="ok",
                input_hash=input_hash,
                output_path=rel_img,
            )
            results.append({"shot_id": sid, "seed": seed, "file": rel_img, "cache_hit": False, "latency_ms": latency_ms})
        except Exception as exc:  # noqa: BLE001
            latency_ms = int((time.perf_counter() - t0) * 1000)
            err_msg = redact_secrets(str(exc))
            log_run(
                runs_path,
                stage="keyframes",
                shot_id=sid,
                model=flux_model,
                parameters={"steps": steps, "conditioned": shot_ref is not None},
                seed=seed,
                latency_ms=latency_ms,
                cost_or_quota="1_cloudflare_flux_call_failed",
                cache_hit=False,
                status="error",
                input_hash=input_hash,
                error=err_msg,
            )
            raise

    return results
