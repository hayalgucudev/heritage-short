# The Heritage Short — Explained Simply

## Stage 1: Building the Factory Foundation & Smoke Tests
- **Why we started here:** Before painting frames or recording voices, we built the factory's safety checklist (`validate.py`), fingerprint memory (`cache.py`), and flight recorder (`logger.py` writing to `runs.jsonl`).
- **The fingerprint cache (`cache.py`):** Think of a SHA-256 hash like a wax seal made from the exact ingredients of a shot (prompt + seed + model + reference image). If you change Shot 3's prompt, only Shot 3's seal changes — Shots 1, 2, 4, and the music keep their old seals and don't waste quota rebuilding.
- **Secret protection (`env_loader.py` + `logger.py`):** API keys stay in `.env` (which Git ignores) and are read only in memory; our logger automatically replaces any key string with `[REDACTED]` if an error ever tries to print it.
- **Why smoke tests come first:** Calling each AI provider once with a tiny test checks if model names changed and lets you hear Amharic TTS quality before we generate the whole film.
- **What Stage 1 smoke tests showed:** Live verification caught that `gemini-3.8-flash-lite` is missing (`gemini-3.5-flash-lite` exists), `@cf/black-forest-labs/flux-2-klein-4b` (Apache 2.0) generates painterly frames cleanly via `multipart/form-data` in ~8.8s, `gemini-3.8-flash-tts` generates Amharic audio in ~5.1s, and `gemini-3.8-flash` hit a temporary HTTP 503 high-demand outage even after 3 retries — proving why exponential backoff and logging failures immediately matter.
- **Controlled TTS experiments (EXP-001 to EXP-003):** Changing one variable at a time showed that removing the English style prefix from the spoken prompt (`--no-wrapper`) shrank the single-sentence clip from `14.32 s` down to `5.20 s` (while `Kore` was `7.08 s` and `gemini-3.8-flash-lite-tts` was `6.00 s`), proving how prompt phrasing directly changes pacing and timing.

## Stage 2: Drafting `storyboard.json` (Single Source of Truth)
- **Why one JSON file controls everything:** `storyboard.json` holds every Amharic line, English subtitle, image prompt, seed, motion prompt, and music spec in one place so code never invents prompts on the fly.
- **What broke & how we solved it:** Preview models (`3.8-flash`, `3.7-flash`) hit HTTP 503 high demand, `2.5-flash` was retired for new keys (HTTP 404), and `3.5-flash` timed out at our hard `60 s` cap due to a heavy server-side `responseSchema`. Dropping `responseSchema` in favor of plain JSON mode + local `validate.py` checking let `gemini-3.6-flash` draft all 10 shots cleanly in `33.9 s`.
