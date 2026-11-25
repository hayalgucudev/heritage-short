# The Heritage Short

A 60–90 second AI-made heritage short film and reproducible production pipeline built for Windows PowerShell (`py run.py ...`).

## Requirements
- Python 3.14 (or Python 3.12 virtual environment if any dependency fails)
- FFmpeg 9.1 full build (`ffmpeg` and `ffprobe` on `PATH`)
- API keys in `.env` (never committed; copy `.env.example` to `.env`)

## Quick Start (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
# Fill in keys in .env, then verify live models:
py run.py verify-models
```

## Main Commands
- `py run.py validate` — Validate `storyboard.json` against `schema/storyboard.schema.json`.
- `py run.py verify-models` — Query live model IDs from Gemini and Cloudflare Workers AI.
- `py run.py smoke --gemini-model <id> --tts-model <id> --flux-model <id>` — Run 1-call smoke tests.
- `py run.py plan` — Dry-run input hash check (upcoming Polish stage).
- `py run.py film` — Full end-to-end build into `outputs/final/` (upcoming Floor stages).
- `py run.py report-costs` — Build `COSTS.md` from `runs.jsonl` (upcoming Polish stage).
