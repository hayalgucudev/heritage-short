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

## 008 — HTTP 429 quota exceeded on `gemini-3.8-flash-tts` at `shot_06`
- **What broke:** While generating `Aoede` narration back-to-back (`shot_01`–`shot_05` succeeded in 17 seconds), `shot_06` failed with `HTTP 429` (`You exceeded your current quota`). Error truncation at `300` chars in `_post_with_retry` hid the exact quota metric name (`PerMinute` vs `PerDay`).
- **What we tried:** Preserved `shot_01`–`shot_05` (`Aoede`) in `outputs/narration_aoede/`, expanded HTTP error capture in `pipeline/smoke.py` to `1,200` chars, and added pacing delay between TTS calls in `pipeline/narration.py`.
- **What fixed it:** `shot_01` (`Kore`) succeeded after >1 minute pause (`3,131 ms`), confirming the 429 was a per-minute RPM limit (~5 RPM). Added `--delay-sec 13.0` default pacing between live TTS calls in `pipeline/narration.py`.

## 009 — Language-quality finding: Gemini Amharic draft used unnatural verbs (`shot_02`, `shot_07`)
- **What broke:** Native Amharic speaker review of `storyboard.json` (drafted by `gemini-3.6-flash`) caught unnatural verb choices in two lines: `shot_02` used `ታንድዳለች` instead of natural `ታነዳለች` ("lights the fire"), and `shot_07` used `አጥልላ ታፈሳለች` instead of natural `በቀስታ ትቀዳለች` ("slowly pours").
- **What we tried:** Replaced those exact lines and updated their English subtitles in `storyboard.json`, while holding `shot_09` for a revised line matching the updated solo-Grandmother framing.
- **What fixed it / Lesson:** Even fluent-looking low-resource script output from an LLM requires native-speaker verification before locking TTS audio; per-shot hash caching ensured only the modified shots regenerate.

## 010 — `gemini-3.8-flash-tts` Free Tier daily cap is 10 requests/day (`RESOURCE_EXHAUSTED`)
- **What broke:** After completing `Kore` narration for `shot_01`–`shot_06` (`3.56 s`–`4.64 s` each), `shot_07` failed with `HTTP 429 RESOURCE_EXHAUSTED`: `Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 10, model: gemini-3.8-flash-tts, description: Generate content requests per day limit exceeded on Free Tier. Please retry in 23h47m25s.`
- **What we learned:** The free tier on `gemini-3.8-flash-tts` allows only **10 requests per day** (the earlier `shot_06` 429 was hitting this rolling/daily quota ceiling, not just RPM).
- **What we fixed in code:** Updated `_post_with_retry` in `pipeline/smoke.py` to treat `"per day"` / `PerDay` 429 quota errors as non-retryable so we fail fast instead of burning retries.
- **Status:** `shot_01`–`shot_06` (`Kore`) are saved and cached; paused at `shot_07` awaiting director choice between testing `gemini-3.8-flash-lite-tts` / `gemini-3.1-flash-tts-preview` or proceeding with keyframes/character sheet today while waiting for tomorrow's 24h reset.

## 011 — Windows Store Python alias blocking `python` outside `.venv`
- **What broke:** Running `python` in PowerShell outside an activated `.venv` hit the Windows Microsoft Store app execution alias instead of the installed Python interpreter.
- **What we tried:** Verified `py` launcher and explicit `.venv` interpreter path.
- **What fixed it:** Use `py` (for bootstrapping `.venv`) or `.\.venv\Scripts\python.exe` directly in PowerShell commands and documentation.

## 012 — `Media.SoundPlayer` relative-path error in PowerShell
- **What broke:** Playing `.wav` narration files via `.NET` `System.Media.SoundPlayer` with a relative path failed because `.NET` resolves relative paths against the process working directory rather than PowerShell's current location.
- **What we tried:** Switched from relative paths to resolved full file paths.
- **What fixed it:** Pass `Resolve-Path` / absolute Windows paths (e.g., `(Resolve-Path .\outputs\narration\shot_01.wav).Path`) to `SoundPlayer`, or play via standard media player / `ffplay`.

## 013 — First AI session hit assistant quota cutoff mid-project
- **What broke:** The initial AI coding session exhausted its assistant quota after completing Stages 0–3 (`smoke`, `storyboard.json`, and 10 per-shot narration WAVs).
- **What we tried:** Resumed in a new session using the repo's written state (`runs.jsonl`, `outputs/manifest.json`, `EXPLAINED.md`, `FAILURES.md`, `EXPERIMENTS.md`) and adopted concise, targeted file reads.
- **What fixed it / Lesson:** Keeping all state on disk (`storyboard.json`, `manifest.json`, `runs.jsonl`, markdown logs) allowed seamless handoff across sessions with zero lost work.

## 014 — FFmpeg `-map [10:v]` bracket syntax error in `build_radio_cut`
- **What broke:** Running `py run.py radio-cut` failed with FFmpeg exit code `-22` (`Invalid argument`): `Output with label '10:v' does not exist in any defined filter graph`.
- **What we tried:** Captured FFmpeg `stderr` directly and inspected the `-map` flag in `pipeline/narration.py`.
- **What fixed it:** Changed `-map [10:v]` (which looks for a named filtergraph output pad) to `-map 10:v` (raw input stream 10 video), and `radio-cut` succeeded cleanly.

## 015 — Second language-quality & visual-alignment finding (`shot_09` narration)
- **What broke:** After revising `shot_09`'s visual to show only Grandmother holding out a coffee cup toward the camera (no neighbours in frame), the old narration (`"ጎረቤቶች ወደ ቤት ገብተው፣ ሰላምታ ይለዋወጣሉ።"` / *"Neighbours come in and exchange greetings."*) described neighbours entering and conversing instead of matching the solo frame, and sounded stiff.
- **What we tried:** Replaced the `shot_09` line with natural Amharic aligned to the visual (`"ጎረቤቶቿን ቡና ትጋብዛለች።"` / *"She invites the neighbours\nto share coffee."*).
- **What fixed it / Status:** `storyboard.json` updated and re-validated. Only `shot_09.wav` is invalidated by its input hash; regeneration of `shot_09` (along with `shot_07`, `shot_08`, `shot_10`) is deferred until `gemini-3.8-flash-tts` daily quota resets after `11:00 EAT` on 2026-11-26.

## 016 — Previous coding agent (Antigravity CLI) exhausted starter quota on both accounts
- **What broke:** The previous coding agent (**Antigravity CLI**, **starter quota**) ran out of quota on **both** of its accounts. Its message said the **baseline quota refreshes on 2 December 2026**.
- **What we did NOT do:** I did **not** rotate accounts to get around the quota limit.
- **What changed instead:** I moved to **OpenCode with a free model** and continued the project from the on-disk state (`storyboard.json`, `outputs/manifest.json`, `runs.jsonl`, and the markdown logs).
- **Status / Lesson:** This is a tooling/quota handoff, not a model-output failure. Do not budget on the Antigravity starter quota before 2026-12-02; keep using cache hits, small drafts, and the free tiers already logged in this file. All cost numbers remain sourced from `runs.jsonl` only.

## 017 — ACE-Step 1.5 dependency conflict and false "Models initialized." success on Kaggle
- **What broke:** A fresh Kaggle session could not load ACE-Step 1.5. `transformers 5.20.2` was installed, which is **outside the repo's declared `>=4.51,<4.58` range**. Downgrading `transformers` alone then broke `diffusers 0.42.0`, because that version imports `resolve_revision`, a symbol added in `huggingface_hub 1.26.0`; but `transformers 4.57.x` requires `huggingface_hub` **below 1.0**. Three mutually incompatible constraints.
- **What we tried:** `pip install -e .` (editable install of the ACE-Step repo) **failed twice**; we abandoned it instead of retrying a third time.
- **What fixed it:** Pinned **`transformers==4.57.6` + `huggingface_hub==0.36.2` + `diffusers==0.35.2`**, and put the cloned repo on `sys.path` instead of installing it. Verified with `from diffusers.models import AutoencoderOobleck` (the import that had broken). The director reported the Kaggle run then worked.
- **Second bug:** The old notebook printed `"Models initialized."` unconditionally, even when loading had failed — a false success signal. It now asserts `dit_handler.model is not None` before printing anything, and treats the optional language-model planner as non-fatal (`llm_handler = None` when it fails; `generate_music` skips the LM when `llm_initialized` is false).
- **Measured on the successful run (reported by the director, not re-run locally here):** T4 detected at **14.6 GB**; about **7.6 GB** GPU memory used after loading; **10.1 GB** model download in about **22 s**; three 60 s candidates in **12.6 s**, **6.0 s** and **6.0 s**; `llm_initialized=False` and generation still worked.
- **Files changed:** `notebooks/acestep_music.ipynb` (one-pass fresh-session install + assertions + real `run_info` in metadata) and new `notebooks/acestep_music_colab.ipynb` (same pinned contract with `/content` paths and `files.download`).
- **Status / Lesson:** The notebooks are written to match the verified pins but were **not executed in this local session** (no GPU here); the numbers above are the director's Kaggle measurements, not invented ones. Lesson: pin the *whole* dependency triangle, and never print success without checking the loaded object.

## 018 — Hand-anatomy failure in `shot_02_noref.png` (EXP-008 follow-up)
- **What broke:** Director's visual check of `outputs/keyframes/shot_02_noref.png` (generated with `seed=102`, no reference) found **only 4 fingers on one hand**. This is a real anatomy defect, not a style preference.
- **Director's decision:** Option C — keep testing reference conditioning, but add a measurement; regenerate the no-reference version with **another seed** and compare.
- **Hands policy adopted for all future keyframes:** hands must be **holding an object, partly in shadow, or out of frame**; **max 3 attempts** per shot; after 3 failures **change the framing**; final fallback is deterministic **FFmpeg Ken Burns pan/zoom over the clean still** rather than spending more GPU quota.
- **What was generated (EXP-009 follow-up):** (1) `shot_02` conditioned on `ref_real_seed1025.png`, `seed=102`, pose-override instruction; (2) `shot_02` no-reference with a new seed and object-in-hand/shadow phrasing; (3) `shot_03` no-reference with its original prompt and `seed=103` for an honest face comparison. All are test files with distinct names; `storyboard.json` was not changed.
- **Director's verdict (2026-11-25):** EXP-009 (`shot_02_exp009_ref.png`) had a **different face**, so the pose-override + reference approach failed identity preservation; EXP-010 and EXP-011 were `"okay"`. The adopted production rule is verbatim description + `--no-ref` for action shots; `input_image_0` is not used to hold identity on `flux-2-klein-4b` on this evidence.
- **Status:** Generation and latencies are logged in `runs.jsonl`. This assistant did not visually inspect the PNGs; finger counts and face comparisons above are the director's observations. Director also asked to "make it more realistic"; scope of that change is pending a decision (EXP-012).

## 019 — ACE-Step download arrived without notebook run metadata
- **What broke:** The downloaded score file (`outputs/music/download (1).wav`) had no `music_run_metadata.json` beside it, so seed, latency and candidate id could not be proven. The notebook had been updated in entry 017 but this earlier download predates that fix.
- **What we did:** Did **not** guess a seed or latency. Wrote metadata with `seed=null`, `latency_ms=null` and an explicit `seed_note` explaining that `candidate_01_seed777.wav` uses the storyboard base seed as a filename label only. Registered the WAV through `py run.py music`, which logged a real 60.0 s duration from `ffprobe`.
- **Status / Lesson:** Director approved this single candidate as the floor score (EXP-013). Future notebook runs must keep `music_run_metadata.json` in the exported zip so costs and latencies stay real.

## 020 — Three FFmpeg assembly bugs found in a local smoke test (2026-11-25)
- **Bug A, fontconfig crash:** `drawtext=font=Arial` made FFmpeg exit with `Fontconfig error: Cannot load default config file`. The build has fontconfig compiled in but this Windows machine has no fontconfig config. Tried and rejected: `fontfile=C:/Windows/Fonts/arial.ttf` and `fontfile=C\:/...` — both produced `No option name near ...` because the drive colon is a filtergraph delimiter. **Fix:** resolve a real font file and emit `fontfile='C\:/Windows/Fonts/arial.ttf':` (quoted plus escaped colon), verified with a one-frame drawtext test.
- **Bug B, subtitle scale:** Generating an SRT and using `force_style` left libass using its default 288-unit PlayRes, so a measured `MarginV=210` would have placed subtitles ~73% up a 9:16 frame. **Fix:** write a per-aspect ASS file with `PlayResX/PlayResY` set to the real export size, so FontSize and MarginV are real pixels.
- **Bug C, silent 3.72 s soundtrack:** The audio mix looked successful but probed as **3.72 s instead of 73 s**. Step-by-step isolation showed the padded narration concat was 73.0 s, `sidechaincompress` output was only 60 s because the score WAV is 60 s, and `amix=inputs=2:duration=first` then stopped at 3.72 s. **Fix:** `apad=whole_dur=73` the score before ducking and use `amix=duration=longest`; the mix then probed 73.0 s.
- **Verification:** Temporary-only smoke render (no deliverable, no `runs.jsonl` writes) produced 9:16 and 16:9 MP4s, both 73.0 s; measured final audio **-14.32 LUFS, -0.97 dBTP**. Production code now raises with FFmpeg stderr instead of hiding it.
- **Status / Lesson:** These were real failures, not hypothetical ones. This assistant cannot view PNG/video frames in this session; text placement and the end card still need the director's visual check.

## 021 — No Wan clip output found when asked about the clips gate (2026-11-25)
- **What happened:** Asked whether to run the Wan Kaggle job, the director replied *"I already saved the kaggle output in music/"*. I checked `outputs/music/` and found only `candidate_01_seed777.wav`, `music_job.json` and `music_run_metadata.json` — the ACE-Step score, not video clips. `outputs/clips/` did not exist and no Wan zip was in Downloads.
- **What I did:** Did not guess a clip source or invent a Wan result. Recorded the ambiguity here, treated it as **no Wan clips available**, and used the local Ken Burns fallback for the provisional cut. The Wan notebook remains prepared but unrun.
- **Director's clarification (2026-11-25):** They confirmed the file they meant was **`candidate_01_seed777` in `outputs/music`** — the ACE-Step score, not Wan video. So no Wan clip output exists. Decision: **use the local Ken Burns fallback for the final film**; the Wan notebook stays prepared as evidence but unrun.
- **Status:** Closed for the floor. If Wan clips are generated later, `py run.py shots --import-dir <folder>` replaces only the 10 clips and both finals; everything else stays cached.

## 022 — Voice disappears after the first shot in the rendered film (2026-11-25)
- **What happened:** The director opened the provisional cut and said verbatim: *"the voice is not available after the first shot"*. This was a real defect, not a preference.
- **How it was measured (no fabrication):** `volumedetect` on each 7 s slot of the delivered MP4 gave mean levels `-18.7, -19.7, -18.8, -18.3, -16.2, -16.6, -14.6, -20.2, -50.7, -91.0` dB. Every individual narration WAV measured `-17.5` to `-15.0` dB, so the source audio was fine. The concatenated voice track alone was healthy in all ten slots; the ducked and mixed output went silent in slots 9 and 10.
- **Root cause:** The voice filter label `[voice]` was consumed **twice** — once as the `sidechaincompress` trigger and once in the final `amix`. FFmpeg allowed the graph to build but silently truncated the second consumer to about 3.7 s of usable signal, which progressively killed the tail. A 3-way A/B isolated it: plain `amix` = all 10 slots audible; `asplit=2` then duck = all 10 audible; the original reused label = slots 9/10 at `-67.3 / -91.0` dB.
- **Fix:** `concat -> [voice_raw] -> asplit=2 -> [voice_side] (sidechain) + [voice] (mix)`, and the sidechain now reads `[voice_side]`. Because the storyboard inputs did not change, a code-only fix would have been treated as a cache hit; added `code_version: 2` to `ASSEMBLE_SETTINGS` so the change invalidates and rebuilds both exports.
- **Verification:** Both re-rendered MP4s are 73.0 s, H.264/AAC 48 kHz stereo, 24 fps CFR; slot means `-20.3` to `-16.2` dB in all ten; measured **-14.01 LUFS / -0.99 dBTP**. Render latencies 8,147 ms (9:16) and 4,896 ms (16:9), zero model calls.
- **Lesson:** Silence is not an exception — FFmpeg exited successfully on the broken mix. Never trust a render without measuring the actual delivered file, slot by slot, after the director reports a problem.






