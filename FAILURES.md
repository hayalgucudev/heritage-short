# Failures & Fixes Log

Honest log of retired/changed models, API errors, pronunciation issues, Python compatibility snags, and what fixed them.

## 001 — Global Python `externally-managed-environment` (PEP 668) on Windows
- **What broke:** Running `py -m pip install -r requirements.txt` globally failed with `error: externally-managed-environment` because system Python 3.14.6 is managed by `uv`.
- **What we tried:** Created a project-local virtual environment (`py -m venv .venv`, already listed in `.gitignore`) and installed into `.venv`.
- **What fixed it:** Installing into `.venv` (`.\.venv\Scripts\python.exe -m pip install -r requirements.txt`) worked cleanly without `--break-system-packages`, and keeps clean-clone setup isolated for any reviewer.

## 002 — `gemini-3.8-flash-lite` missing from live Gemini model list
- **What broke:** Running `py run.py verify-models` showed `gemini-3.8-flash` and `gemini-3.8-flash-tts` are live, but `gemini-3.8-flash-lite` was **not** present in `v1beta/models`.
- **What we tried:** Inspected the full live `v1beta/models` response for Flash-Lite alternatives.
- **What fixed it:** Use `gemini-3.8-flash` for primary script/storyboard/translation calls, and `gemini-3.5-flash-lite` (confirmed live) when a lighter/bulk model is needed.

## 003 — `gemini-3.8-flash` returned HTTP 503 (`UNAVAILABLE`) on smoke test
- **What broke:** During `run.py smoke`, `gemini-3.8-flash` returned HTTP 503 (`This model is currently experiencing high demand`) across all 3 exponential-backoff attempts (and our first attempt before fixing `smoke.py` to call `raise_for_status()` inside the retry wrapper).
- **What we tried:** Fixed `_post_with_retry` in `pipeline/smoke.py` so HTTP 429/5xx raises inside the retry loop (2s, 4s backoff), and logged the error to `runs.jsonl` without crashing the remaining TTS and FLUX smoke tests.
- **What fixed it / Status:** `gemini-3.8-flash-tts` and `@cf/black-forest-labs/flux-2-klein-4b` both succeeded; `gemini-3.8-flash` remains marked for retry, with director pre-approval (`2B`) to fall back automatically to `gemini-3.7-flash` if `gemini-3.8-flash` returns 503 after 3 retries (logged to `FAILURES.md` and `runs.jsonl`).

## 004 — Baseline Amharic TTS (`gemini-3.8-flash-tts`, voice `Aoede`) bloated by English style wrapper
- **What broke:** Sending `"Speak in a calm, warm, unhurried storytelling voice in Amharic: <text>"` inside `contents` caused the TTS model to stumble over / absorb the English prefix, bloating a single 10-word sentence to `14.32 s` with awkward pacing.
- **What we tried:** Tested `Kore` (`EXP-001`: `7.08 s`), `gemini-3.8-flash-lite-tts` (`EXP-002`: `6.00 s`), and removing the English wrapper completely (`EXP-003`: `5.20 s`) since Gemini's `speechConfig.voiceConfig` has no separate style field.
- **What fixed it:** Sending **pure Amharic text only** (`--no-wrapper`) fixed word accuracy and natural pacing (`5.20 s`), though the director noted the voice still sounds slightly robotic — so scripts will use short sentences and simple punctuation, and warmth will be tested directly in the radio-cut audience test.

## 005 — Both `gemini-3.8-flash` and `gemini-3.7-flash` returned HTTP 503 (`UNAVAILABLE`) in Stage 2
- **What broke:** During `run.py draft-storyboard`, `gemini-3.8-flash` failed after 3 exponential-backoff attempts (`199,911 ms`, `HTTP 503: high demand`), and the pre-approved fallback `gemini-3.7-flash` also failed after 3 attempts (`21,871 ms`, `HTTP 503: high demand`). The `90 s` per-attempt timeout allowed `gemini-3.8-flash` retries to block for over 3 minutes.
- **What we tried:** Verified both errors in `runs.jsonl` and stopped without silently substituting another model.
- **What fixed it:** Added a hard `60 s` wall-clock timeout cap per call (`max_total_sec=60.0` in `pipeline/smoke.py` `_post_with_retry`) so overloaded models cannot stall for minutes.

## 006 — `gemini-2.5-flash` returned HTTP 404 (`NOT_FOUND` for new users)
- **What broke:** Even though `gemini-2.5-flash` appeared in `v1beta/models` during `verify-models`, calling it in `draft-storyboard` returned HTTP 404 (`386 ms`): `"This model models/gemini-2.5-flash is no longer available to new users. Please update your code to use models/gemini-3.8-flash"`.
- **What we tried:** Verified the error in `runs.jsonl` and removed `gemini-2.5-flash` from candidate models.
- **Status:** Logged as a live-tier retirement discrepancy (`verify-models` still lists retired models for existing users while blocking new keys).

## 007 — `gemini-3.5-flash` hit the 60s hard read timeout on nested `responseSchema`
- **What broke:** Fallback `gemini-3.5-flash` timed out cleanly at `60,356 ms` (`ReadTimeoutError`, confirming the 60s hard cap works) when generating the 10-shot storyboard with a large nested `responseSchema`.
- **What we tried:** Replaced the heavy server-side `responseSchema` constraint with `responseMimeType: "application/json"` plus explicit JSON structure in the prompt, relying on local `validate.py` (`jsonschema`) to enforce exact schema compliance.
- **What fixed it:** `gemini-3.6-flash` succeeded in `33,900 ms` with the lighter JSON-only request and passed `validate.py` cleanly (`10 shots`).



