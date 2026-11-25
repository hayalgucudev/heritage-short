# The Heritage Short

A 60–90 second AI-made short film plus a reproducible pipeline. A stranger with Python, FFmpeg and `.env` keys can clone this repo and rebuild both film formats from `storyboard.json` with one command.

## Requirements
- Windows PowerShell; Python 3.14 (`py`) or a Python 3.12 `.venv` if a package fails.
- FFmpeg 9.1 full build (`ffmpeg` and `ffprobe` on `PATH`).
- API keys in `.env` (never committed). Copy `.env.example` and fill it in.

## Setup (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Fill in keys in .env
.\.venv\Scripts\python.exe run.py verify-models
```
Use `.\.venv\Scripts\python.exe run.py ...` if the virtual environment is not activated. Global `py -m pip` fails on this machine (PEP 668); see `FAILURES.md`.

## The one-command build
```powershell
.\.venv\Scripts\python.exe run.py film
```
It validates the storyboard, then runs narration, keyframes, music, clips and assembly in order. Every stage checks its own hash cache first, so a second run is mostly cache hits. Outputs land in `outputs/final/`:
- `film_9x16.mp4` — 608×1080, H.264 + AAC, 24 fps CFR.
- `film_16x9.mp4` — 1280×720, H.264 + AAC, 24 fps CFR.

Both have burned-in English subtitles, the ACE-Step score ducked under Amharic narration, and a 3 s AI disclosure end card.

## Other commands
| Command | What it does |
| :--- | :--- |
| `validate` | Check `storyboard.json` against the schema before any quota call. |
| `plan` | Dry run: print exactly what would regenerate, why, and the quota estimate. No model calls. |
| `narration --shot shot_07 --tts-model gemini-3.8-flash-tts` | Regenerate one narration line. |
| `keyframes --shot shot_03 --no-ref` | Regenerate one keyframe. |
| `clips-export` | Package keyframes + motion prompts for the Kaggle Wan notebook. |
| `shots --import-dir <folder>` | Import Wan clips from Kaggle; without it, make local Ken Burns clips. |
| `music --import-dir <folder>` | Register downloaded ACE-Step candidates. |
| `radio-cut` | Rebuild the provisional narration-only cut. |
| `assemble` | Rebuild the two final exports from cached inputs. |
| `report-costs` | Rebuild `COSTS.md` tables from real `runs.jsonl` rows. |

`film` also accepts `--skip-narration`, `--skip-keyframes`, `--skip-music`, `--skip-shots`, `--import-dir`, `--steps` and `--delay-sec`. Both `assemble` and `film` accept `--allow-stale-narration` for a director-approved provisional cut; without it, stale narration fails loudly.

## Gates and heavy jobs
The director must explicitly approve the story, storyboard, radio cut, reference sheet, keyframes, clips, score and final edit. The Wan 2.2 Kaggle notebook (`notebooks/wan_clips_kaggle.ipynb`) is prepared but is **not run automatically**; the floor works with local Ken Burns clips. No real person's face or voice is used — see `ETHICS.md`.

## Evidence
`DESIGN.md`, `ARCHITECTURE.md`, `EXPERIMENTS.md`, `FAILURES.md`, `COSTS.md`, `EXPLAINED.md` and `INTERVIEW_PREP.md` contain the real decisions, measurements and failure records. `runs.jsonl` is the source of truth for every model call.
