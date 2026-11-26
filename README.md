# The Heritage Short

A 60–90 second AI-made short film plus a reproducible pipeline. A stranger with Python, FFmpeg and `.env` keys can clone this repo and rebuild both film formats from `storyboard.json` with one command.

## Public links (director-verified 2026-11-26, no login required)
- Main film 9:16: https://huggingface.co/spaces/rahmetullah/heritage-film/resolve/main/film_9x16.mp4
- Widescreen 16:9: https://huggingface.co/spaces/rahmetullah/heritage-film/resolve/main/film_16x9.mp4

Both MP4 links returned HTTP 200 `video/mp4` on 2026-11-26. The **showcase page** at `https://huggingface.co/spaces/rahmetullah/heritage-film` is published but **does not work for the director** (it serves the Hugging Face wrapper and a stale README, not the film UI) — see `FAILURES.md` 037. Do not present it as working evidence. The exports themselves end with a "Made with AI" card. The YouTube post is still a draft (`PUBLISH_DRAFT.md`); no YouTube URL is claimed.

## Requirements
- Windows PowerShell; Python 3.14 (`py`) or a Python 3.12 `.venv` if a package fails.
- FFmpeg 9.1 full build (`ffmpeg` and `ffprobe` on `PATH`).
- API keys in `.env` (never committed). Copy `.env.example` and fill it in.

## Setup (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py preflight
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

**Motion is not AI video:** every shot is an FFmpeg Ken Burns pan/zoom over an approved AI-generated still (keyframe). **No Wan 2.2 video clip was produced and the film contains no AI-generated video.** The Wan notebook exists but was never successfully run; the floor is deterministic local motion (see `FAILURES.md` 024–025 and `EXPERIMENTS.md` EXP-018).

### Verified final state (2026-11-26)
All ten shots now use `gemini-3.8-flash-tts` (`Kore`). Both exports are **73.0 s**, H.264 + AAC 48 kHz stereo, 24 fps CFR, measured **−14.02 LUFS / −0.98 dBTP**, with all ten 7-second slots carrying voice (−21.3 to −16.2 dB). `py run.py plan` reports **38 cache hits / 0 regenerations**; no `--allow-stale-narration` flag is needed. Evidence: `EXPERIMENTS.md` EXP-022 and `runs.jsonl`.

### Final visual gate (2026-11-26)
The director reviewed the exported frames and made two final choices: **shot_07 stays as the original** (eight replacement candidates did not fix the pouring hand and the stream; the defect is logged as unresolved in `FAILURES.md` 032/035), and **shot_10 uses seed 1113**, a head-and-shoulders crop with no visible hands. The approved image-edit fallback failed twice with `Invalid credential` and was abandoned (`FAILURES.md` 034). The 9:16 subtitle margin moved `180 -> 340` and the end-card tribute was enlarged. Only shot_10's clip and both exports rebuilt (1,485 / 4,500 / 5,633 ms); `plan` is back to **38 cache hits / 0 regenerations**. See `EXPERIMENTS.md` EXP-029. A final one-command `py run.py film` produced 33 cache-hit rows, zero model calls and byte-identical exports (EXP-030).

## Other commands
| Command | What it does |
| :--- | :--- |
| `validate` | Check `storyboard.json` against the schema before any quota call. |
| `preflight` | Check FFmpeg and all committed inputs exist; no keys or model calls. |
| `plan` | Dry run: print exactly what would regenerate, why, and the quota estimate. No model calls. |
| `narration --shot shot_07 --tts-model gemini-3.8-flash-tts` | Regenerate one narration line. |
| `keyframes --shot shot_03 --no-ref` | Regenerate one keyframe. |
| `clips-export` | Package keyframes + motion prompts for the Kaggle Wan notebook. |
| `shots --import-dir <folder>` | Import Wan clips from Kaggle; without it, make local Ken Burns clips. |
| `music --import-dir <folder>` | Register downloaded ACE-Step candidates. |
| `radio-cut` | Rebuild the provisional narration-only cut. |
| `assemble` | Rebuild the two final exports from cached inputs. |
| `report-costs` | Rebuild `COSTS.md` tables from real `runs.jsonl` rows. |
| `second-language` | Ceiling experiment: **closed as FAILED** on 2026-11-26 after four failed translation calls; no TTS call, no `_om` film, no publication. |
| `showcase` | Copy film, storyboard and costs into `space/`; publishing to Hugging Face is manual. |

`film` also accepts `--skip-narration`, `--skip-keyframes`, `--skip-music`, `--skip-shots`, `--import-dir`, `--steps` and `--delay-sec`. Both `assemble` and `film` accept `--allow-stale-narration` for a director-approved provisional cut; without it, stale narration fails loudly.

### Optional reproduction notebooks (not part of the one-command floor)
`notebooks/acestep_music.ipynb`, `notebooks/acestep_music_colab.ipynb` and `notebooks/wan_clips_kaggle.ipynb` reproduce the GPU stages on Kaggle/Colab. They are **not called by `film`**: the committed WAVs and keyframes let a clean clone rebuild both MP4s with zero model calls. All three notebooks now pin `transformers==4.57.6`, `huggingface_hub==0.36.2` and `diffusers==0.35.2` (ACE-Step also needs `vector-quantize-pytorch>=1.27.15`), assert the loaded model, and fail with clear messages instead of cascading `NameError`s. Real Kaggle/Colab failures and their fixes are in `FAILURES.md` entries 024, 025 and 026. The **Colab** ACE-Step notebook was rerun on a real T4 by the director (DiT load 10.1 s, three candidates in 13,842 / 7,113 / 6,965 ms); its browser-download error is fixed. The director also reran the **Wan** notebook on Kaggle: the pin fix is GPU-verified (`WanImageToVideoPipeline import: OK`) and the guards correctly refused to generate clips, but cell 1 found no job dataset. Run `py run.py clips-export` locally first (zero quota), then upload `outputs/wan_job.zip` as a Kaggle dataset. **No Wan clip exists yet**; the Kaggle ACE-Step twin is still only compiled locally. No new candidate was imported, so the approved score is unchanged.

## Gates and heavy jobs
The director must explicitly approve the story, storyboard, radio cut, reference sheet, keyframes, clips, score and final edit. The Wan 2.2 Kaggle notebook (`notebooks/wan_clips_kaggle.ipynb`) is prepared but is **not run automatically**; the floor works with local Ken Burns clips. No real person's face or voice is used — see `ETHICS.md`.

## Evidence
`DESIGN.md`, `ARCHITECTURE.md`, `EXPERIMENTS.md`, `FAILURES.md`, `COSTS.md`, `EXPLAINED.md`, `INTERVIEW_PREP.md` and `WALKTHROUGH.md` contain the real decisions, measurements, failure records and the timed recording script. `runs.jsonl` is the source of truth for every model call.
