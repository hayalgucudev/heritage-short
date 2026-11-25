# AI Interview Prep — Plain-Language Talking Points

## Stage 1: Foundation, Caching & Secret Hygiene
1. **Why hash inputs (`cache.py`)?** Every stage output is keyed by a SHA-256 hash of its exact inputs (prompt, seed, model, params, and upstream files), so editing one shot only invalidates that shot and its downstream dependencies.
2. **Why validate before calling models (`validate.py`)?** Checking `storyboard.json` against `storyboard.schema.json` (plus subtitle length and 60–90s total timing) catches mistakes locally at zero quota cost before hitting rate-limited APIs.
3. **How are secrets and logs handled?** Secrets live only in `.env` (gitignored), are never printed or committed, and `logger.py` writes every call immediately to `runs.jsonl` while scrubbing any secret values out of error text.

## Stage 2: Storyboard Drafting & Resilience
1. **Why keep prompts and seeds in `storyboard.json` instead of Python?** Separating data from code makes the pipeline declarative and reproducible — changing one line in `storyboard.json` updates only dependent downstream stages.
2. **How did we prevent API stalls during failures?** After a 3-minute hang on HTTP 503, we added a hard 60-second wall-clock cap per call and switched from server-side `responseSchema` to plain JSON mode + local `jsonschema` validation.
3. **How do we keep visual & narrative consistency?** A single `style_block` and verbatim `character.description` are reused across shots, with centered framing so both 9:16 and 16:9 crops work cleanly.

## Stage 3: Per-Shot Narration & Radio Cut
1. **Why generate one WAV per shot instead of one long audio file?** Generating per shot lets us fingerprint each shot independently so a single line fix rebuilds only that shot, and lets us pad/align each clip to its exact visual slot.
2. **Why make a Radio Cut before visuals?** If the story doesn't land emotionally with voice and pacing alone on a black screen, pictures won't save it — and measuring `ffprobe` durations early prevents rushed cuts.
3. **Why did we strip the English style prefix from TTS calls?** Our controlled experiment (`EXP-003`) proved an English prefix bloated a 5.2s sentence to 14.32s, so pure Amharic text with short sentences and simple punctuation drives natural pacing.
4. **Why mark narration PROVISIONAL and still build the Radio Cut?** Every shot sits cleanly inside its 7.0s slot (`3.52s`–`4.64s`), so building `radio_cut.mp4` locally lets us lock pacing today while waiting for tomorrow's 10/day quota reset to regenerate only `shot_07`–`shot_10` on the main TTS model.

## Stage 4 & 5 Prep: Reference Sheet & Parallel Kaggle Music
1. **Why generate a character reference sheet before shot keyframes?** Conditioning all character shots on one approved portrait (plus verbatim `character.description` and `style_block`) keeps Grandmother's face and clothing consistent across scenes; switching from painterly to 35mm realism (`EXP-007`) before generating any shot keyframes invalidated zero downstream assets.
2. **What did the `shot_02` conditioning experiment (`EXP-008`) prove?** Running `seed=102` with and without `input_image_0` proved that `flux-2-klein-4b` treats `input_image_0` as a strong pose-preserving image edit (locking the face and cup pose from `ref_real_seed1025.png`), whereas `--no-ref` with verbatim `character.description` performs the prompted action (`tending glowing red embers`).
2. **Why run ACE-Step 1.5 on Kaggle instead of locally?** Music generation needs GPU acceleration; keeping a standalone Kaggle notebook (`notebooks/acestep_music.ipynb`) that exports `music_run_metadata.json` lets `pipeline/music.py` hash, cache, and log Kaggle outputs into `runs.jsonl` just like local stages.

## Stage 4 (Final): Production keyframes — be able to explain this
1. **Why one global style block instead of ten prompt rewrites?** One shared text dial keeps all shots visually consistent; after the director chose "more realistic" we edited 11 places in `storyboard.json` (the block plus its 10 copies) so every frame changed together with zero story or narration changes.
2. **Why no reference image on the 10 shots?** EXP-009 showed `input_image_0` gave a different face on an action pose, while EXP-010/011 no-reference images were accepted; therefore all production keyframes used `--no-ref` with the verbatim character description.
3. **What did the run prove about caching and quota?** Schema validation passed locally before any call, all 10 calls were logged as `ok`/`cache_hit=false` in `runs.jsonl` (98.7 s total), and the 10 stills are the only assets invalidated by the style change — a later tweak to one shot prompt would regenerate only that shot.

## Stage 6 & 7: Clips, plan and assembly — be able to explain this
1. **Why share hash recipes between the stages and `plan`?** If the dry run used its own copy of the cache formulas it could claim a hit when the stage would actually regenerate; one `contracts.py` makes the promise true by construction.
2. **What does a Ken Burns fallback do?** It is a deterministic FFmpeg zoom over the approved still — real motion with no extra GPU cost, used if Wan is skipped or fails after 3 attempts, so the film can still be finished.
3. **What did the local assembly smoke test prove?** With temporary files only, both exports rendered 73.0 s at 24 fps, and measured audio was **-14.32 LUFS / -0.97 dBTP**, matching the target; no final deliverable was rendered before the director's gate.

## Provisional cut — be able to explain this
1. **Why did the final film still have two voices?** The director confirmed the User Test 1 problem was voices. Shots 07-10 were made on flash-lite TTS because of a 10/day cap; the fix needs 4 calls after ~11:00 EAT on 26 Nov. The provisional cut exists only so visual feedback could happen early, and every log row names the four stale shots.
2. **Why does using stale audio not break caching?** The export hash is computed from the *expected* narration hashes, not the stale files' hashes. When the correct TTS is generated, its hash matches the expected one and the finals rebuild automatically; nothing else does.
3. **What was measured on the delivered provisional files (before the audio fix)?** Both MP4s: 73.0 s, H.264/AAC 48 kHz stereo, 24 fps CFR, **-14.32 LUFS / -0.95 dBTP**. Ten local Ken Burns clips took 1,417-1,473 ms each, with zero model calls.

## The missing-voice bug — be able to explain this
1. **How did I find it?** The director said "the voice is not available after the first shot". I measured the volume of each 7 s slot in the delivered MP4: shots 09 and 10 were at -50.7 and -91.0 dB. The source WAVs were all normal, so I compared three filter graphs: plain mix, split-then-duck, and the original.
2. **What was the fix?** The voice label was consumed twice by FFmpeg without `asplit=2`, which silently truncated the second consumer. After the split, all ten slots measure -20.3 to -16.2 dB and the film measures **-14.01 LUFS / -0.99 dBTP**. I bumped `code_version` to 2 so the cache rebuilt the exports.
3. **What did this change about my process?** FFmpeg returned success on a broken mix. From now on, a render is not "verified" until the delivered file's own audio is measured slot by slot, not just its length and codec.

## CLI packaging — be able to explain this
1. **Why track 1.88 MB of narration WAVs?** A clean clone then has every cached input and can rebuild the film without API keys or model calls; this was the director's choice. Re-generated WAVs 07-10 will be force-added after the TTS fix.
2. **What does `preflight` prove?** It checks tools and required files and reports booleans only — it never prints `.env` values. In a clone with no `.env`, it returned `ready: true` and `missing_files: []`.
3. **What is still pending?** The clean clone needed `--skip-narration --allow-stale-narration` because four voices are provisional. After tomorrow's scheduled TTS fix, plain `py run.py film` must succeed with no flags; that is the final CLI measurement.

## Second-language ceiling — be able to explain this
1. **Why one TTS call instead of ten?** The 10/day cap and the 4-call voice fix leave only 6 calls before the deadline. One long narration call plus local splitting fits, at the cost of a timing-alignment risk that must be measured.
2. **How are the 10 shot files made?** FFmpeg detects pauses in the long WAV and cuts at the nine longest ones; if that fails it falls back to word-count proportions. Each piece is padded to its 7-second slot. A smoke test with a synthetic WAV produced 10 audible slots and both 73.0 s exports.
3. **What has not happened yet?** No real Afaan Oromo translation or TTS call has been made, and the family/community native-speaker check is pending. The alternate film must not be published until that check is recorded.

## Showcase and post — be able to explain this
1. **Why keep the Space folder but ignore its copies?** The HTML and metadata are stable; the MP4s and cost table change after the final voice fix. `py run.py showcase` refreshes them, so the Space cannot silently show an old film.
2. **Did the pipeline publish anything?** No. The showcase command reads no keys and uploads nothing; YouTube and Hugging Face publication both wait for the director's explicit approval.
3. **What is the agreed disclosure?** "AI-generated film" in the post and Space, plus the film's own "Made with AI" end card. No real person's face or voice appears.

## 5-minute walkthrough script (rehearsed 2026-11-25, shot_02)
**0:00–0:30 — Intro.** Open the repo and say: *"This is The Heritage Short. The story is locked in `storyboard.json`. One command, `py run.py film`, rebuilds both films. Every stage checks a hash of its inputs, so only changed things regenerate."*

**0:30–1:15 — Prove the environment is safe.**
```powershell
.\.venv\Scripts\python.exe run.py preflight
.\.venv\Scripts\python.exe run.py plan
```
Say: *"Preflight checks FFmpeg and committed inputs without keys. The dry run makes no model calls; it currently reports 31 cache hits and 7 regenerations — the four provisional voices plus outputs that only exist after tomorrow's fix."*

**1:15–2:00 — Show the source of truth.** Open `storyboard.json` shot_02 and say: *"Prompt, seed 102, motion prompt and duration live here, not in Python. Changing this one prompt would change only shot_02's keyframe, clip and the two finals."*

**2:00–3:00 — Live regeneration (zero quota).**
```powershell
Remove-Item outputs\clips\shot_02.mp4 -Force
.\.venv\Scripts\python.exe run.py shots --shot shot_02
```
Expected real output from rehearsal: `cache_hit: false`, `source: ken_burns`, `duration_sec: 7.0`, `latency_ms: 1452`, `input_hash: d017039b9cbbe22513dea62644e52b48d82909df5dc754aacd9fc3e6a73c5a9d`. Say: *"I deleted one derived clip. The stage rebuilt only that clip from the approved still, with local FFmpeg — no model call, no quota."*

**3:00–3:45 — Show the evidence.**
```powershell
Get-Content runs.jsonl -Tail 1
.\.venv\Scripts\python.exe run.py plan | Select-String 'shots/shot_02'
```
Say: *"The log row has a timestamp, stage, model `ffmpeg-9.1`, latency, cache flag and hash. The plan now calls shot_02 a cache hit, which proves the manifest agrees with the file."*

**3:45–4:30 — Show the result.** Open `outputs\final\film_9x16.mp4` at shot 2 and the end card. Say: *"Both exports are 73 seconds, 24 fps, H.264/AAC 48 kHz, measured -14.01 LUFS / -0.99 dBTP, with all ten voices audible after the mix fix."*

**4:30–5:00 — Close.** Say: *"Tomorrow's scheduled job replaces only four voice files and rebuilds the finals; the Afaan Oromo version then spends one translation call and one TTS call. Nothing is published until I approve it."*
