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
- **What fixed it / Status:** `gemini-3.8-flash-tts` and `@cf/black-forest-labs/flux-2-klein-4b` both succeeded; `gemini-3.8-flash` remains marked for retry or user-approved fallback (`gemini-3.7-flash` or `gemini-2.5-flash`) before Stage 2 storyboard drafting.



