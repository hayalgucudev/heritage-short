"""Stage 2: Draft storyboard.json via Gemini structured JSON output and validate against schema."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from pipeline.cache import compute_stage_hash, update_manifest
from pipeline.env_loader import load_env, require_env
from pipeline.logger import log_run, redact_secrets
from pipeline.smoke import _post_with_retry
from pipeline.validate import validate_storyboard

FIXED_STYLE_BLOCK = (
    "warm painterly storybook gouache and soft oil illustration, rich golden-hour amber and "
    "terracotta light, gentle natural shadows, timeless East African village folktale mood, "
    "centered framing for 9:16 and 16:9 crops, no text or watermarks"
)

CHARACTER_DESCRIPTION = (
    "an elderly East African grandmother in her seventies with warm weathered brown skin, "
    "kind dark eyes, silver-white hair tucked neatly under a cream-colored woven cotton headwrap, "
    "wearing a simple white handwoven cotton dress and shawl with subtle earth-toned border trim"
)

STORYBOARD_DRAFT_PROMPT = f"""You are drafting the production storyboard JSON for a 65-75 second animated heritage short film titled "The Morning Hands" (የማለዳ እጆች).

STRICT RULES (must obey every single one):
1. Story & Privacy: A fictionalized, stylized tribute to "Grandmother" in "the village". NEVER invent or include real people's names, real village/city names, addresses, phone numbers, or private family details. Only use "Grandmother" (አያቴ) and "the village" (መንደሩ).
2. Ending feeling: Quiet gratitude and warmth — showing how small daily acts of care (waking early, lighting the hearth, roasting and pouring morning coffee, baking injera, tending the courtyard, welcoming neighbors, blessing the day) quietly hold a family together across generations.
3. Shot count & timing: Create EXACTLY 10 shots (shot_01 through shot_10), each 6.0 to 7.5 seconds long, so shots + 3.0s end_card = 65 to 75 seconds total.
4. Narration (Amharic): Write natural, idiomatic Amharic in VERY SHORT, SIMPLE sentences (about 5 to 9 words per shot, max 2 short sentences), using simple punctuation only (። and ፣ — no exclamation marks, colons, or English words). Short sentences keep the synthetic voice calm, warm, and unhurried instead of robotic.
5. Subtitles (English): Faithful, warm English meaning of each shot's Amharic narration. Maximum 2 lines (use \\n between lines), and EVERY line MUST be <= 38 characters so it fits safely inside mobile 9:16 margins.
6. Character & Style consistency:
   - Use this exact `style_block`: "{FIXED_STYLE_BLOCK}"
   - Use this exact `character.description`: "{CHARACTER_DESCRIPTION}"
   - Whenever Grandmother appears in a shot's `image_prompt`, reuse her description verbatim, state subject + action + setting + centered composition + warm light, and append the exact `style_block` at the end. No text inside images.
7. Video motion prompts (`video_motion_prompt`): ONLY describe gentle motion and camera (one simple idea, one slow movement, ~5 seconds, e.g. "Slow gentle push-in as rising steam drifts upward from the clay coffee pot"). Never contradict camera directions.
8. `story_reason`: For each shot, explain in one clear sentence why this shot belongs in the arc and how it builds quiet gratitude.
9. `sfx_ambience`: Short sound design note (quiet village ambience or subtle foley like charcoal crackle, coffee pouring, morning birds).
10. Seeds: Use deterministic integer seeds: `image_seed` 101..110, `video_seed` 201..210, `character.reference_seed` 1024, `music.seed` 777.
11. `models`: Set `script` to "gemini-3.8-flash", `tts` to "gemini-3.8-flash-tts", `keyframes` to "@cf/black-forest-labs/flux-2-klein-4b", `video` to "Wan-AI/Wan2.2-TI2V-5B", `music` to "ACE-Step/ACE-Step-v1.5".
12. `end_card`: `{{"text": "Made with AI · A fictional tribute to quiet morning hands", "duration_sec": 3.0}}`.
13. `music`: Warm instrumental Ethiopian-inspired acoustic folk score (`tempo_bpm`: 72, `key`: "D major", `duration_sec`: 75, `style`: "acoustic folk instrumental", `mood`: "warm, grateful, unhurried, nostalgic", `instruments`: "krar plucked strings, gentle bamboo flute, soft felt piano", `texture`: "warm organic acoustic", `caption`: "Warm acoustic Ethiopian-inspired folk instrumental with gentle krar strings, soft bamboo flute, and subtle felt piano, unhurried morning courtyard mood, organic warm texture, no vocals").

Return ONE JSON object with these exact top-level keys:
`version`, `title`, `language`, `audience`, `ending_feeling`, `aspect_ratios`, `models`, `style_block`, `character`, `music`, `end_card`, `shots`.
Each item in `shots` (10 items: `shot_01`..`shot_10`) must have ONLY these exact keys:
`id`, `duration_sec`, `narration`, `subtitle_en`, `tts_style`, `image_prompt`, `image_seed`, `video_motion_prompt`, `video_seed`, `sfx_ambience`, `story_reason`.
Set `audience` to "Family and community on WhatsApp/TikTok (9:16), classmates and reviewers on desktop (16:9)", `ending_feeling` to "Quiet gratitude and warmth", `version` to "1.0", `language` to "amharic", `aspect_ratios` to ["9:16", "16:9"], `character.name` to "Grandmother", `character.reference_seed` to 1024, `music.seed` to 777, and `tts_style` on each shot to "Aoede, no English wrapper in spoken text".
"""

# Gemini responseSchema matching schema/storyboard.schema.json
GEMINI_STORYBOARD_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "required": [
        "version",
        "title",
        "language",
        "audience",
        "ending_feeling",
        "aspect_ratios",
        "models",
        "style_block",
        "character",
        "music",
        "end_card",
        "shots",
    ],
    "properties": {
        "version": {"type": "STRING"},
        "title": {"type": "STRING"},
        "language": {"type": "STRING"},
        "audience": {"type": "STRING"},
        "ending_feeling": {"type": "STRING"},
        "aspect_ratios": {"type": "ARRAY", "items": {"type": "STRING"}},
        "models": {
            "type": "OBJECT",
            "required": ["script", "tts", "keyframes", "video", "music"],
            "properties": {
                "script": {"type": "STRING"},
                "tts": {"type": "STRING"},
                "keyframes": {"type": "STRING"},
                "video": {"type": "STRING"},
                "music": {"type": "STRING"},
            },
        },
        "style_block": {"type": "STRING"},
        "character": {
            "type": "OBJECT",
            "required": ["name", "description", "reference_seed"],
            "properties": {
                "name": {"type": "STRING"},
                "description": {"type": "STRING"},
                "reference_seed": {"type": "INTEGER"},
            },
        },
        "music": {
            "type": "OBJECT",
            "required": [
                "caption",
                "style",
                "mood",
                "instruments",
                "texture",
                "tempo_bpm",
                "key",
                "duration_sec",
                "seed",
            ],
            "properties": {
                "caption": {"type": "STRING"},
                "style": {"type": "STRING"},
                "mood": {"type": "STRING"},
                "instruments": {"type": "STRING"},
                "texture": {"type": "STRING"},
                "tempo_bpm": {"type": "INTEGER"},
                "key": {"type": "STRING"},
                "duration_sec": {"type": "NUMBER"},
                "seed": {"type": "INTEGER"},
            },
        },
        "end_card": {
            "type": "OBJECT",
            "required": ["text", "duration_sec"],
            "properties": {
                "text": {"type": "STRING"},
                "duration_sec": {"type": "NUMBER"},
            },
        },
        "shots": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "required": [
                    "id",
                    "duration_sec",
                    "narration",
                    "subtitle_en",
                    "tts_style",
                    "image_prompt",
                    "image_seed",
                    "video_motion_prompt",
                    "video_seed",
                    "sfx_ambience",
                    "story_reason",
                ],
                "properties": {
                    "id": {"type": "STRING"},
                    "duration_sec": {"type": "NUMBER"},
                    "narration": {"type": "STRING"},
                    "subtitle_en": {"type": "STRING"},
                    "tts_style": {"type": "STRING"},
                    "image_prompt": {"type": "STRING"},
                    "image_seed": {"type": "INTEGER"},
                    "video_motion_prompt": {"type": "STRING"},
                    "video_seed": {"type": "INTEGER"},
                    "sfx_ambience": {"type": "STRING"},
                    "story_reason": {"type": "STRING"},
                },
            },
        },
    },
}


def _append_fallback_failure(failures_path: Path, primary: str, fallback: str, error_msg: str) -> None:
    """Append an honest fallback entry to FAILURES.md once fallback succeeds."""
    entry = (
        f"\n## Fallback — `{primary}` failed in Stage 2; switched to `{fallback}`\n"
        f"- **What broke:** `{primary}` failed after 3 retries during storyboard drafting (`{error_msg[:180]}`).\n"
        f"- **What we tried:** 3 exponential-backoff attempts against `{primary}`.\n"
        f"- **What fixed it:** Used approved fallback `{fallback}` and logged both attempts in `runs.jsonl`.\n"
    )
    existing = failures_path.read_text(encoding="utf-8") if failures_path.exists() else ""
    if f"`{primary}` failed in Stage 2; switched to `{fallback}`" not in existing:
        failures_path.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")


def draft_storyboard(
    project_root: Path,
    storyboard_path: Path,
    schema_path: Path,
    runs_path: Path,
    manifest_path: Path,
    *,
    primary_model: str = "gemini-3.8-flash",
    fallback_model: str | None = "gemini-3.7-flash",
    force: bool = False,
) -> dict[str, Any]:
    """Draft storyboard.json using Gemini structured JSON output with approved fallback."""
    load_env(project_root)
    gemini_key = require_env("GEMINI_API_KEY")

    input_hash = compute_stage_hash(
        stage="script_draft",
        model=primary_model,
        prompt=STORYBOARD_DRAFT_PROMPT,
        params={"fallback_model": fallback_model, "schema_version": "1.0"},
        reference_files=[schema_path],
    )

    if not force and storyboard_path.exists():
        manifest = (
            json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest_path.exists()
            else {"artifacts": {}}
        )
        entry = manifest.get("artifacts", {}).get("storyboard.json", {})
        if entry.get("input_hash") == input_hash and entry.get("status") == "ok":
            sb = validate_storyboard(storyboard_path, schema_path)
            log_run(
                runs_path,
                stage="script",
                shot_id="all",
                model=sb["models"]["script"],
                parameters={"cache": True},
                latency_ms=0,
                cost_or_quota="0_cache_hit",
                cache_hit=True,
                status="ok",
                input_hash=input_hash,
                output_path="storyboard.json",
            )
            return sb

    candidates = [primary_model]
    if fallback_model and fallback_model != primary_model:
        candidates.append(fallback_model)

    used_model = primary_model
    raw_json_text = ""
    primary_err: str | None = None
    for idx, candidate_model in enumerate(candidates):
        t0 = time.perf_counter()
        try:
            resp = _post_with_retry(
                f"https://generativelanguage.googleapis.com/v1beta/models/{candidate_model}:generateContent",
                headers={"x-goog-api-key": gemini_key, "Content-Type": "application/json"},
                json_body={
                    "contents": [{"parts": [{"text": STORYBOARD_DRAFT_PROMPT}]}],
                    "generationConfig": {
                        "temperature": 0.4,
                        "responseMimeType": "application/json",
                    },
                },
                max_total_sec=60.0,
            )
            latency_ms = int((time.perf_counter() - t0) * 1000)
            raw_json_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            used_model = candidate_model
            if idx > 0 and primary_err:
                _append_fallback_failure(
                    project_root / "FAILURES.md", primary_model, candidate_model, primary_err
                )
            log_run(
                runs_path,
                stage="script",
                shot_id="all",
                model=candidate_model,
                parameters={"temperature": 0.4, "structured_json": True},
                latency_ms=latency_ms,
                cost_or_quota="1_gemini_script_call",
                cache_hit=False,
                status="ok",
                input_hash=input_hash,
                output_path="storyboard.json",
            )
            break
        except Exception as exc:  # noqa: BLE001
            latency_ms = int((time.perf_counter() - t0) * 1000)
            err_msg = redact_secrets(str(exc))
            if idx == 0:
                primary_err = err_msg
            log_run(
                runs_path,
                stage="script",
                shot_id="all",
                model=candidate_model,
                parameters={"temperature": 0.4, "structured_json": True},
                latency_ms=latency_ms,
                cost_or_quota="1_gemini_script_call_failed",
                cache_hit=False,
                status="error",
                input_hash=input_hash,
                error=err_msg,
            )
            if idx < len(candidates) - 1:
                continue
            raise

    sb_data = json.loads(raw_json_text)
    # Enforce exact locked constants so prompt drift cannot alter approved specs
    sb_data["language"] = "amharic"
    sb_data["aspect_ratios"] = ["9:16", "16:9"]
    sb_data["style_block"] = FIXED_STYLE_BLOCK
    sb_data["character"]["name"] = "Grandmother"
    sb_data["character"]["description"] = CHARACTER_DESCRIPTION
    sb_data["character"]["selected_reference_image"] = None
    sb_data["music"]["selected_candidate"] = None
    sb_data["models"]["script"] = used_model
    sb_data["models"]["tts"] = "gemini-3.8-flash-tts"
    sb_data["models"]["keyframes"] = "@cf/black-forest-labs/flux-2-klein-4b"

    storyboard_path.write_text(
        json.dumps(sb_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    validated = validate_storyboard(storyboard_path, schema_path)
    update_manifest(
        manifest_path,
        output_file=storyboard_path,
        project_root=project_root,
        stage="script",
        shot_id="all",
        input_hash=input_hash,
    )
    return validated
