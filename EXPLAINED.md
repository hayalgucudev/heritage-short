# The Heritage Short — Explained Simply

## Stage 1: Building the Factory Foundation & Smoke Tests
- **Why we started here:** Before painting frames or recording voices, we built the factory's safety checklist (`validate.py`), fingerprint memory (`cache.py`), and flight recorder (`logger.py` writing to `runs.jsonl`).
- **The fingerprint cache (`cache.py`):** Think of a SHA-256 hash like a wax seal made from the exact ingredients of a shot (prompt + seed + model + reference image). If you change Shot 3's prompt, only Shot 3's seal changes — Shots 1, 2, 4, and the music keep their old seals and don't waste quota rebuilding.
- **Secret protection (`env_loader.py` + `logger.py`):** API keys stay in `.env` (which Git ignores) and are read only in memory; our logger automatically replaces any key string with `[REDACTED]` if an error ever tries to print it.
- **Why smoke tests come first:** Calling each AI provider once with a tiny test checks if model names changed and lets you hear Amharic TTS quality before we generate the whole film.
- **What Stage 1 smoke tests showed:** Live verification caught that `gemini-3.8-flash-lite` is missing (`gemini-3.5-flash-lite` exists), `@cf/black-forest-labs/flux-2-klein-4b` (Apache 2.0) generates painterly frames cleanly via `multipart/form-data` in ~8.8s, `gemini-3.8-flash-tts` generates Amharic audio in ~5.1s, and `gemini-3.8-flash` hit a temporary HTTP 503 high-demand outage even after 3 retries — proving why exponential backoff and logging failures immediately matter.
