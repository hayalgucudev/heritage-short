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

## 023 — Two FFmpeg split bugs in the one-call second-language smoke test (2026-11-25)
- **What happened:** In a temp clone, the synthetic long WAV was split into 10 shot WAVs, but shots 03-10 were 78-byte empty headers, so assembly failed with `could not convert string to float: 'N/A'`.
- **Bug A, timestamps:** Seeking with `-ss` *after* `-i` left filter timestamps starting at 12.3 s, so `atrim=duration=7.000` cut everything. Tried adding `asetpts=PTS-STARTPTS` before the trim; still empty.
- **Bug B, `-t` measured from input start:** With `-ss` after the input, `-t 7` limited output to the first 7 s of the *source*, before the 12.3 s seek point. **Fix:** put `-ss` **before** `-i`, keep `-t` after the input, and reset timestamps before `apad`/`atrim`. Verified one command produced 7.000 s / 336,078 bytes.
- **Cache consequence:** The split hash did not include the code version, so broken files would have been treated as cached. Added `code_version: 2` to the split hash so the fix invalidates them.
- **Verification:** Re-ran in the temp clone with no model calls: both `film_9x16_om.mp4` and `film_16x9_om.mp4` rendered 73.0 s (latencies 7,769 ms and 8,836 ms); all ten slots measured `-20.3` to `-16.2 dB`. No Afaan Oromo model call has been made yet.

## 024 — ACE-Step Colab run: missing `vector_quantize_pytorch`, then NameError cascade (2026-11-25)
- **What the director ran:** `notebooks/acestep_music_colab.ipynb` on a Colab T4. The pinned trio installed, 28 model files (~9 GB) downloaded in about 40 s, but the DiT load failed.
- **Real error:** `ImportError: This modeling file requires the following packages that were not found in your environment: vector_quantize_pytorch. Run 'pip install vector_quantize_pytorch'`; the assertion correctly stopped with `AssertionError: DiT model failed to load (dit_handler.model is None). Do not print 'Models initialized.' when loading failed.` Later cells then gave `NameError: name 'llm_handler' is not defined` and `NameError: name 'run_info' is not defined`.
- **Root cause:** The downloaded `modeling_acestep_v15_turbo.py` imports `ResidualFSQ` from `vector_quantize_pytorch`; the install cell only listed the pinned trio plus soundfile/accelerate/einops/loguru/safetensors. Upstream `requirements.txt` confirms `vector-quantize-pytorch>=1.27.15`. The NameErrors were a cascade: cell 4 aborted before defining those variables, and the director ran cells 5 and 6 anyway.
- **What fixed it:** Install cell now adds `vector-quantize-pytorch>=1.27.15`; cell 2 imports `ResidualFSQ` so a missing package fails at the check, not 9 GB later; cell 3 sets `MODEL_READY = False`, `llm_handler = None`, `records = []`, `run_info = {}` before any model call; cell 4 sets `MODEL_READY = True` only after the assertion; cells 5 and 6 raise a clear `RuntimeError` instead of a confusing `NameError`. Applied to both `acestep_music.ipynb` and `acestep_music_colab.ipynb`.
- **Non-fatal warning left alone:** pip reported that pre-installed `gradio-client 2.7.2` / `gradio 6.30.0` want `huggingface-hub>=1.16` while our pin is `0.36.2` (and pillow 13 vs their `<13`). The imported modules (`acestep/__init__.py`, `handler.py`, `inference.py`, `llm_inference.py`) do not import gradio, and upstream pins gradio 6.2.0 which accepts hub 0.36.2. Changing gradio was not worth a new dependency conflict in a path we do not use; this is recorded rather than hidden.
- **Verification status (updated 2026-11-25 with the director's real Colab run):** the director reran `acestep_music_colab.ipynb` on a fresh Colab T4. The pinned trio and `vector-quantize-pytorch` installed; the compatibility check printed `transformers: 4.57.6`, `huggingface_hub: 0.36.2`, `diffusers: 0.35.2` and `Compatibility check passed: AutoencoderOobleck and ResidualFSQ import.` The DiT loaded in **10.1 s** using **5.9 GB** on a Tesla T4 (14.6 GB), `llm_initialized = False`, and all three candidates generated in **13,842 / 7,113 / 6,965 ms** with `music_run_metadata.json` written. Entry 024 is therefore **verified on GPU for Colab**. The Kaggle twin is still only locally compiled; no claim is made for it.

## 025 — Wan Kaggle notebook: placeholder slug, unpinned `-U`, then NameError cascade (2026-11-25)
- **What the director ran:** `notebooks/wan_clips_kaggle.ipynb` on Kaggle. Cell 1 stopped at `AssertionError: wan_job.json not found. Upload outputs/wan_job.zip as a Kaggle dataset and set KAGGLE_DATASET_NAME to the slug shown in the Kaggle sidebar.` Cell 2 then failed with `RuntimeError: Failed to import diffusers.pipelines.wan.pipeline_wan_i2v ... cannot import name 'divide_to_patches' from 'transformers.image_transforms'`. Cells 3-6 cascaded into `NameError: name 'AutoencoderKLWan' is not defined`, `NameError: name 'job' is not defined`, and `AssertionError: Run the smoke cell first (and only once).`
- **Root causes:** (a) `KAGGLE_DATASET_NAME` was still the literal placeholder and no `wan_job.zip` dataset was mounted; (b) `pip install -q -U diffusers transformers ...` pulled transformers 5.x, whose `image_transforms` module removed `divide_to_patches`, breaking the Wan pipeline import — the same dependency-skew family as entry 017; (c) every later cell assumed earlier cells had succeeded.
- **What fixed it:** The install cell now pins `transformers==4.57.6`, `huggingface_hub==0.36.2`, `diffusers==0.35.2` and asserts those versions (checked against upstream tag v0.35.2: `WanImageToVideoPipeline`, `AutoencoderKLWan` and `export_to_video` are all exported there). Cell 1 auto-detects the slug when exactly one `wan_job.json` exists under `/kaggle/input`. Cells 1 and 3 define `JOB_READY`, `MODEL_READY`, `records` and `load_sec` before any GPU call, set the flags only after success, and cells 3, 5 and 6 raise clear `RuntimeError`s if a prerequisite failed.
- **Verification status (updated 2026-11-25 with the director's real Kaggle run):** cell 1 still stopped at `AssertionError: wan_job.json not found`, but cell 2 **now passes on GPU** — it printed `transformers 4.57.6`, `huggingface_hub 0.36.2`, `diffusers 0.35.2` and `WanImageToVideoPipeline import: OK`. That verifies the pin fix; the old `divide_to_patches` import error is gone. Cells 3, 5 and 6 then raised the new clear `RuntimeError`s (`JOB_READY`/`MODEL_READY` false) instead of cascading `NameError`s, so the guards also work. **No Wan clip was generated and no GPU latency was measured**, because no job dataset was mounted. Cell 1 now prints what `/kaggle/input` actually contains and names `py run.py clips-export` in its error. The floor remains the local Ken Burns fallback; nothing in `outputs/final` depends on this notebook.

## 026 — Colab ACE-Step run succeeded, but the browser download helper failed (2026-11-25)
- **What the director ran:** the repaired `notebooks/acestep_music_colab.ipynb` on a fresh Colab T4. Cells 2–5 all succeeded (see entry 024 for the real latencies and GPU memory). Cell 6 printed `Downloaded zip: extract into outputs/music/ in the repo. /content/heritage_music_candidates.zip`, listed all three candidates and the run info, then ended with `Javascript Error: download is not defined`.
- **Root cause:** `files.download()` calls a browser-side JavaScript helper that is absent in this Colab runtime. It has nothing to do with model generation or the zip: `shutil.make_archive` had already written a complete zip to `/content/heritage_music_candidates.zip`.
- **What fixed it:** cell 6 now prints a manual-download instruction **before** attempting `files.download()`, and wraps the call in `try/except Exception` so a missing JS helper is reported as "Browser auto-download unavailable" rather than appearing as a failed generation. The notebook still validates as JSON and all code cells compile. The director can also download the zip directly from the Colab file browser.
- **Status:** the generation itself is verified on GPU; only the convenience download was broken. **No new candidate has been imported into `outputs/music/`**, so the director-approved score and both delivered MP4s are unchanged.

## 027 — Wan job zip had never been exported locally (2026-11-25)
- **What broke:** after the pin fix, the director's Kaggle run still stopped in cell 1 with `wan_job.json not found`. The auto-detect could not help because nothing matching `wan_job.json` existed under `/kaggle/input`.
- **Root cause:** `outputs/wan_job.zip` did not exist in the repository or on disk. The notebook README had said to run `py run.py clips-export` first, but that local step had never been executed, so there was nothing to upload as a Kaggle dataset. This is a workflow gap, not a model failure.
- **What fixed it:** ran `py run.py clips-export` locally (zero quota; copies the 10 committed keyframes and writes `wan_job.json`, `README.txt` and `outputs/wan_job.zip`). Result: **10 shots, 7,796,471-byte zip**. The zip stays gitignored (`*.zip`) and the staging folder `outputs/wan_job/` was added to `.gitignore`; a clean clone regenerates it with the same one command. Cell 1's error now names that command and prints the visible `/kaggle/input` entries.
- **Status:** the director chose on 2026-11-25 to **defer the Wan rerun until after tomorrow's scheduled TTS and Oromo jobs**, because Wan is optional and the floor already works. The zip is ready locally. **No Wan clip or GPU latency exists yet**; the film still uses the local Ken Burns fallback.


## 028 — Afaan Oromo translation call timed out (2026-11-26)
- **What I ran:** `py run.py second-language` at 12:11 EAT on 2026-11-26, after confirming the TTS fix had succeeded (`plan`: 38 cache hits / 0 regenerations; both assemble rows `stale_narration: []`). This was the director-approved spend of exactly two model calls.
- **What broke:** the **first** call — Gemini text translation of the ten locked fictional lines — failed with `requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='generativelanguage.googleapis.com', port=443): Read timed out. (read timeout=54.21401089988649)`. `pipeline/smoke.py::_post_with_retry` retries transient errors inside a hard 60 s per-call cap; the last attempt consumed 54.2 s and no further attempt was made.
- **What did NOT happen:** no translation JSON was produced, the Gemini TTS call was **never made**, `outputs/second_language/` stayed empty, and no `outputs/narration_om/`, `film_9x16_om.mp4` or `film_16x9_om.mp4` exists. Nothing was published. `runs.jsonl` has **no row** for this failed call because `pipeline/second_language.py` logs only after a successful response — a real logging gap, not evidence that no request was attempted.
- **Second attempt (director approved on 2026-11-26):** reran the same `second-language` command with the same 2-call budget. The translation call failed again, this time with `requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='generativelanguage.googleapis.com', port=443): Read timed out. (read timeout=46.191618899814785)`. Two consecutive timeouts on the same endpoint initially suggested a connectivity/endpoint issue; entry 029 shows that hypothesis was **disproved** by a free network probe.
- **What fixed it / status:** nothing yet. After the second failure I stopped; no third call, no model switch and no invented fallback. `runs.jsonl` still has no row for either failed call because the pipeline logs only successful responses. No translation, TTS output or `_om` MP4 exists; nothing is published. No claim about translation quality, native-speaker checking or viewer comprehension is made.


## 029 — Free connectivity probe rules out a network fault (2026-11-26)
- **What I ran:** a Python `socket`/`ssl` probe at 09:35:09 UTC (12:35 EAT) — DNS resolution, TCP connect to port 443 and a full TLS handshake against `generativelanguage.googleapis.com`, plus `github.com` as a control. **No API key, no HTTP request to a model path, no model call, zero quota.** Proxy variables were checked by presence only, never printed.
- **Measured result:** Gemini DNS **11.4 ms** (8 IPv4 addresses), TCP connect **78.9 ms** to `172.217.115.4`, TLS handshake **113.2 ms** (`TLSv1.3`, `TLS_AES_256_GCM_SHA384`). Control `github.com`: DNS **5.8 ms**, TCP **95.4 ms**, TLS **104.9 ms**. No proxy variables set except `NO_PROXY` (presence only). The endpoint is fully reachable; a network-level block is ruled out.
- **Corroborating log evidence:** the four TTS calls on that same hostname succeeded at 09:06-09:07 UTC, roughly 25 minutes before the first translation timeout. `runs.jsonl` also shows `gemini-3.8-flash` (the configured `text_model`) has **never succeeded** in this repo: smoke text `HTTP 503 high demand` at 13,533 ms (25 Nov 07:31), script `HTTP 503 high demand` at 199,911 ms (25 Nov 07:49), then the two read timeouts (54.2 s, 46.2 s). The only successful script text call used `gemini-3.6-flash` at **33,900 ms**; `gemini-3.5-flash` timed out at 60,356 ms and `gemini-2.5-flash` returned 404 "no longer available to new users".
- **What this means, and its limit:** the evidence points to the **configured text model / 60 s retry cap**, not connectivity. Request size is small (868 prompt characters, ~929-byte JSON body), so payload size is not an obvious cause. This is a diagnosis from logs and a transport probe, **not** a measured root cause — I have not made a successful translation call to prove which change fixes it.
- **Status:** stopped. No third attempt, no model change and no timeout change has been made; any of those needs a director decision about quota. Nothing published.


## 030 — gemini-3.6-flash translation also failed (2026-11-26)
- **What I ran:** with director approval, changed only `translations/afaan_oromo.json` `text_model` from `gemini-3.8-flash` to `gemini-3.6-flash`, then ran `py run.py second-language` once at 12:38 EAT. The budget was one translation + one TTS call.
- **What broke:** the translation call returned `requests.exceptions.HTTPError: HTTP 503: {"error": {"code": 503, "message": "This model is currently experiencing high demand...", "status": "UNAVAILABLE"}}`. `_post_with_retry` exhausted its retry window on the same 503. This is the **third** distinct text-model failure pattern in the repo: 3.8-flash gave two 503s and two read timeouts, 3.6-flash gave a 503 even though it succeeded once on 25 Nov in 33,900 ms.
- **What did NOT happen:** no translation JSON, no TTS call, no split WAVs, no `_om` MP4s. `outputs/second_language/` is still empty and `runs.jsonl` still ends at the 09:08 UTC radio-cut row, because the pipeline logs only successful responses. Nothing published; no translation-quality or native-speaker claim.
- **Status / decision:** stopped as instructed. A single historical success does not make a model reliable enough for a quota-limited stage. I did not try a third model, raise the timeout or write my own translation — those are new director decisions. The config keeps `gemini-3.6-flash` with its rationale updated to include this failure so the file cannot mislead a future reader.


## 031 — Fourth translation failure after key change (2026-11-26)
- **What I ran:** the director reported changing the API and asked for a retry, so I ran `py run.py second-language` once at 12:44 EAT with the existing `gemini-3.6-flash` config. I did not read, print or log any key value.
- **What broke:** the translation call again returned `HTTP 503: This model is currently experiencing high demand ... UNAVAILABLE` after retries. This is the fourth consecutive failed translation attempt and the second 503 from `gemini-3.6-flash`.
- **What did NOT happen:** no translation JSON, no TTS call, no split WAVs, no `_om` MP4s and no new `runs.jsonl` row. Nothing published.
- **Status:** stopped. The evidence now points to model capacity on the free tier rather than the credential or the network: DNS/TCP/TLS were healthy (029), both configured text models failed (028, 030), and a credential change did not help. I did not try a fifth call. The Oromo ceiling item remains an honest failure; the native-speaker check and publication stay blocked.
