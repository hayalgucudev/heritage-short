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
4. **Why mark narration PROVISIONAL and still build the Radio Cut?** Every shot sits cleanly inside its 7.0s slot (`3.52s`–`4.64s`), so building `radio_cut.mp4` locally let us lock pacing on 25 Nov while waiting for the 10/day quota reset. On 26 Nov shots 07-10 were regenerated on the main model and the marker was removed.

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
3. **What did the local assembly smoke test prove?** With temporary files only, both exports rendered 73.0 s at 24 fps, and measured audio was **-14.32 LUFS / -0.97 dBTP (HISTORICAL smoke-test value; final delivery measured -14.02 LUFS / -0.98 dBTP)**, matching the target at that stage; no final deliverable was rendered before the director's gate.

## Provisional cut — be able to explain this
1. **Why did the film once have two voices?** The director confirmed the User Test 1 problem was voices. Shots 07-10 were made on flash-lite TTS because of a 10/day cap; on 26 Nov they were regenerated on `gemini-3.8-flash-tts` with 4 calls (3,214 / 3,375 / 2,805 / 4,309 ms). The provisional cut existed only so visual feedback could happen early; old log rows still name the four stale shots.
2. **Why does using stale audio not break caching?** The export hash is computed from the *expected* narration hashes, not the stale files' hashes. When the correct TTS is generated, its hash matches the expected one and the finals rebuild automatically; nothing else does.
3. **What was measured on the delivered provisional files (before the audio fix)?** Both MP4s: 73.0 s, H.264/AAC 48 kHz stereo, 24 fps CFR, **-14.32 LUFS / -0.95 dBTP (HISTORICAL provisional-cut value, not the delivered film)**. Ten local Ken Burns clips took 1,417-1,473 ms each, with zero model calls.

## The missing-voice bug — be able to explain this
1. **How did I find it?** The director said "the voice is not available after the first shot". I measured the volume of each 7 s slot in the delivered MP4: shots 09 and 10 were at -50.7 and -91.0 dB. The source WAVs were all normal, so I compared three filter graphs: plain mix, split-then-duck, and the original.
2. **What was the fix?** The voice label was consumed twice by FFmpeg without `asplit=2`, which silently truncated the second consumer. After the split, all ten slots measure -20.3 to -16.2 dB and the film then measured **-14.01 LUFS / -0.99 dBTP (HISTORICAL; final delivery measured -14.02 LUFS / -0.98 dBTP)**. I bumped `code_version` to 2 so the cache rebuilt the exports.
3. **What did this change about my process?** FFmpeg returned success on a broken mix. From now on, a render is not "verified" until the delivered file's own audio is measured slot by slot, not just its length and codec.

## CLI packaging — be able to explain this
1. **Why track 1.88 MB of narration WAVs?** A clean clone then has every cached input and can rebuild the film without API keys or model calls; this was the director's choice. The regenerated WAVs 07-10 are force-added so this stays true.
2. **What does `preflight` prove?** It checks tools and required files and reports booleans only — it never prints `.env` values. In a clone with no `.env`, it returned `ready: true` and `missing_files: []`.
3. **What happened with the clean clone?** The earlier clone needed `--skip-narration --allow-stale-narration`. After the voices were fixed, a fresh clone of `5bd6adf` with no `.env` ran plain `py run.py film` with no flags: 21 cache-hit rows and 13 local FFmpeg rows, zero paid calls, and both MP4s byte-identical to the delivered ones. EXP-018 is complete.

## Second-language ceiling — be able to explain this
1. **Why one TTS call instead of ten?** The 10/day cap and the 4-call voice fix leave only 6 calls before the deadline. One long narration call plus local splitting fits, at the cost of a timing-alignment risk that must be measured.
2. **How are the 10 shot files made?** FFmpeg detects pauses in the long WAV and cuts at the nine longest ones; if that fails it falls back to word-count proportions. Each piece is padded to its 7-second slot. A smoke test with a synthetic WAV produced 10 audible slots and both 73.0 s exports.
3. **What did not happen?** Four Afaan Oromo **translation** calls were made on 2026-11-26 and all four failed; no TTS call and no `_om` film exist. The director closed the ceiling as failed and ruled the native-speaker check **moot**; no Oromo variant will be published.

## Showcase and post — be able to explain this
1. **Why keep the Space folder but ignore its copies?** The HTML and metadata are stable; the MP4s and cost table change after the final voice fix. `py run.py showcase` refreshes them, so the Space cannot silently show an old film.
2. **Did the pipeline publish anything?** No. The showcase command reads no keys and uploads nothing; YouTube and Hugging Face publication both wait for the director's explicit approval.
3. **What is the agreed disclosure?** "AI-generated film" in the post and Space, plus the film's own "Made with AI" end card. No real person's face or voice appears.

## Reproduction notebooks — be able to explain this
1. **Why fix notebooks that `film` never calls?** Because a stranger cloning the repo may try the optional GPU stages. The director's real Kaggle/Colab errors showed two missing pins; `FAILURES.md` 024 and 025 quote the errors and the fixes. The one-command floor itself needs no GPU, no key and no notebook.
2. **What exactly broke?** ACE-Step's model file imports `ResidualFSQ` from `vector_quantize_pytorch`, which we had not installed; Wan's `-U` install pulled transformers 5.x, whose `image_transforms` lacks `divide_to_patches`. In both cases later cells then threw `NameError`s because an earlier cell had aborted. Now all three notebooks pin the tested trio, assert the model actually loaded, and set safe flags before any model call.
3. **How do I know the fix works?** Honestly: I first validated JSON and compiled each code cell locally. Then the director reran the **Colab** notebook on a real T4: DiT loaded in 10.1 s using 5.9 GB, and all three candidates generated in 13,842 / 7,113 / 6,965 ms with metadata written (`FAILURES.md` 024). The final cell's `files.download` hit a browser-JS error, fixed in entry 026 — the zip was already on disk. The director then ran the **Wan** notebook on Kaggle: the pins worked on GPU (`WanImageToVideoPipeline import: OK`) and the guards stopped cells 3–6 instead of cascading errors, but no job dataset was mounted. I ran `py run.py clips-export` locally (zero quota) to create `outputs/wan_job.zip` for upload. **No Wan clip exists and the Kaggle ACE-Step twin is still only compiled locally**, so the approved film is unchanged.

## Sound and subtitle polish — be able to explain this
1. **What changed and why?** Arial Bold subtitles 10% larger, a restyled but still 3-second AI end card, and a seeded pink-noise room tone at about -40 dB mean. It serves the film criteria (clear narration, readable subtitles, careful mix) and cost zero quota.
2. **What did the measurement teach me?** My first ambience gain measured -54.1 dB mean — technically present but inaudible. I raised it to -40.2 dB and re-measured the exports: **-14.04 LUFS / -0.99 dBTP (HISTORICAL polish-stage value; final delivery measured -14.02 LUFS / -0.98 dBTP)**, all ten slots audible. EXP-019 records both numbers.
3. **What is still unverified?** I cannot view frames in this session, so I have not judged the subtitle placement or the end-card design by eye. The director must check both before the final-edit gate is approved.

## 5-minute walkthrough script (strict narration-line demo; rehearsed 2026-11-26)
**Recording rule:** the whole live section runs in a **throwaway clone** of commit `1a5989a`. The submitted repo, film, cache and `runs.jsonl` are never edited. The rehearsal spent **one approved free Gemini TTS call** in the clone; live timestamp and latency will differ, but the pattern must be one model call and only dependent stages regenerated.

**Before recording, not on camera — prepare the clone and warm local derived outputs:**
```powershell
$demo = "$env:TEMP\opencode\heritage-walkthrough-demo"
if (Test-Path $demo) { Remove-Item $demo -Recurse -Force }
git clone --quiet https://github.com/hayalgucudev/heritage-short.git $demo
Copy-Item 'C:\Users\Rahmetulaha\heritage-short\.env' "$demo\.env"
Push-Location $demo
$py = 'C:\Users\Rahmetulaha\heritage-short\.venv\Scripts\python.exe'
& $py run.py film | Out-Null
& $py run.py radio-cut | Out-Null
& $py run.py plan | Select-String 'Checked'
```
Say before starting: *"This clone is disposable. Copying `.env` only lets the live TTS call authenticate; no key value is shown and the clone is deleted after recording."*

**0:00–0:25 — Intro.** Open the clone folder and say: *"This is The Heritage Short. The story is locked in `storyboard.json`. One command, `py run.py film`, rebuilds both films. Every stage checks a hash of its inputs, so only changed things regenerate."*

**0:25–1:10 — Architecture and one hard decision.** Open `ARCHITECTURE.md` and point to the dependency map. Say: *"A storyboard field flows to a stage, then an output, then downstream stages. Changing one narration line invalidates that WAV, the radio cut and both exports — not the keyframes or clips."* Then say: *"The hardest decision was measurement: FFmpeg reported success while the last two voices were silent. I now measure every seven-second slot, so a successful exit code is never treated as proof."*

**1:10–1:45 — Safe baseline.**
```powershell
& $py run.py preflight
& $py run.py plan | Select-String 'Checked'
```
Say: *"Preflight checks tools and committed inputs without keys. The dry run makes no model calls and reports 38 cache hits and 0 regenerations after the clone was warmed."*

**1:45–2:20 — Show the source of truth and change one narration line.** Open `storyboard.json` shot_02, then run:
```powershell
& $py -c "from pathlib import Path; p=Path('storyboard.json'); s=p.read_text(encoding='utf-8'); old='አያቴ በማለዳ ተነስታ፣ እሳቱን ታነዳለች።'; new='አያቴ በማለዳ ተነስታ፣ እሳቱን በጥንቃቄ ታነዳለች።'; assert s.count(old)==1; p.write_text(s.replace(old,new),encoding='utf-8')"
```
Say: *"I changed only one narration field. I added 'carefully', a word already used in shot_03, so this tests caching, not a new story fact. The prompt, seed, keyframe and clip are untouched."*

**2:20–2:50 — Dry run before spending quota.**
```powershell
& $py run.py plan | Select-String -Pattern 'Checked|REGENERATE|  [0-9]+ x'
```
Rehearsal result: *"Checked 38 stage items: 35 cache hits, 3 would regenerate"* — `narration/shot_02`, `assemble/9:16` and `assemble/16:9`; quota estimate *"1 x 1_gemini_tts_call, 2 x 0_local_ffmpeg"*. Say: *"The dry run proves one model call is needed; no keyframes, clips or music are touched."*

**2:50–3:35 — Rerun the pipeline and show the single model call.**
```powershell
$before = (Get-Content runs.jsonl).Count
& $py run.py film | Out-Null
& $py run.py radio-cut | Out-Null
Get-Content runs.jsonl | Select-Object -Skip $before | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $_.cost_or_quota -eq '1_gemini_tts_call' } | Select-Object timestamp,shot_id,model,latency_ms,cache_hit,status,input_hash | Format-List
```
Rehearsal produced one row: `shot_02`, `gemini-3.8-flash-tts`, `latency_ms 3937`, `cache_hit false`, `status ok`, `input_hash 39bb1814a11f8453759c656033bfdbcc922695f514808d3ed285daf3dcf6374e`, measured voice `4.77 s` and `fits true`. Say: *"One new model call. The two export rebuilds and the radio cut are local FFmpeg, not model quota."*

**3:35–4:10 — Show the restored cache.**
```powershell
& $py run.py plan | Select-String 'Checked'
```
Say: *"The plan is back to 38 cache hits and 0 regenerations. Only shot_02's narration and its dependent exports changed in this clone. The keyframes, clips, score and all other voices were cache hits."*

**4:10–4:40 — Show the submitted film is untouched.** Switch to the real repo and run:
```powershell
Push-Location C:\Users\Rahmetulaha\heritage-short
Get-FileHash outputs\final\film_9x16.mp4 -Algorithm SHA256 | Select-Object -ExpandProperty Hash
Get-FileHash outputs\final\film_16x9.mp4 -Algorithm SHA256 | Select-Object -ExpandProperty Hash
Pop-Location
```
Say: *"The demo exports live in the throwaway clone. The submitted vertical hash starts 375467a8 and the horizontal hash starts 03697d27; neither changed. Both are 73 seconds, 24 fps, H.264/AAC, measured -14.02 LUFS / -0.98 dBTP, with burned-in subtitles and a 3-second 'Made with AI' end card. The motion is FFmpeg Ken Burns over AI stills, not AI-generated video."*

**4:40–5:00 — Close.** Say: *"The four voices were fixed on 26 Nov and both finals rebuilt. The optional Afaan Oromo ceiling is closed as failed after four translation calls; it spends no more quota and will not be published. The viewer words supplied on 26 Nov are in DESIGN.md and REPORT.pdf has been re-rendered; the director confirmed at least three viewers per cut. Nothing is published until I approve the account and give an explicit publish instruction."*

### Recording checklist (keep the video under five minutes)
- Record at 1280×720 or higher with **PowerShell + the throwaway clone folder** visible; never show `.env` or any key value.
- The clone must be warmed with `film` and `radio-cut` before recording so the baseline plan is 38/0. This warm-up is local FFmpeg only.
- Have these files open in tabs so switching is quick: `storyboard.json` (shot_02), `runs.jsonl`, `ARCHITECTURE.md`, `DESIGN.md`.
- The live step changes **one line in `storyboard.json`**; it does not delete a clip. If it fails, the clone is deleted and the submitted film is unaffected.
- Show the one new `runs.jsonl` row after filtering; do not claim a latency that appears only in the rehearsal.
- Delete the throwaway clone after recording and confirm the real repo is still clean with `git status -sb`.
- Stop at 5:00. The walkthrough is graded on the architecture, one hard decision and one live regeneration — not on extra polish.


### Diagnosing the Oromo timeout (three lines to memorise)
Say: *"A free DNS, TCP and TLS probe showed the Gemini endpoint answers in about 200 ms, so the network was never the problem."*
Say: *"`runs.jsonl` shows `gemini-3.8-flash` failed every time — two 503s and two timeouts — while `gemini-3.6-flash` once succeeded in 33.9 seconds."*
Say: *"I stopped after the fourth failed attempt; the director closed the ceiling as failed, so there is no more call, no model switch and no Oromo film."*


### The second-language ceiling, honestly
Say: *"I tried the translation four times — twice on 3.8-flash and twice on 3.6-flash, the last after a key change; all failed with timeouts or 503."*
Say: *"The endpoint was reachable in about 200 ms, so I did not blame the network — I recorded the model failures instead of inventing a translation."*
Say: *"No Oromo film exists and nothing was published; the native-speaker check is moot, the ceiling is closed as failed, and the floor film is unaffected."*


### The submitted report (three lines to memorise)
Say: *"`REPORT.pdf` is rendered from `REPORT.md`, so there is only one source of truth for the numbers."*
Say: *"Every figure traces back to `runs.jsonl`, `COSTS.md`, `DESIGN.md`, `EXPERIMENTS.md` or `FAILURES.md`."*
Say: *"REPORT.md is the source of truth; REPORT.pdf was stale before 26 Nov and was re-rendered from it after the supplied viewer words were added."*


### Strict live step — three lines to memorise
Say: *"Before recording I show plan: 38 cache hits, zero regenerations in a warmed throwaway clone."*
Say: *"I change one shot_02 narration line in storyboard.json; plan becomes 35 hits and 3 regenerations: one TTS call and two local exports."*
Say: *"One new Gemini TTS row appears, local FFmpeg rebuilds the exports and radio cut, and plan returns to 38 hits with the submitted film untouched."*


### Strict walkthrough rehearsal — three lines to memorise
Say: *"I rehearsed the strict demo in a throwaway clone and spent one approved free Gemini TTS call."*
Say: *"The dry run showed 35 hits and 3 regenerations: one TTS call plus two local exports; the log showed exactly one new model row."*
Say: *"The submitted hashes stayed 375467a8... and 03697d27..., and the clone was deleted after the evidence was captured."*


### Space publication failure — three lines to memorise
Say: *"I prepared the static Space and the director approved publishing to hayalgucudev/heritage-short, but Hugging Face returned 403 because the token cannot create under that namespace."*
Say: *"No Space was created and no MP4 was uploaded; whoami showed the token belongs to an account without rights over that namespace, and I never printed the token."*
Say: *"FAILURES.md 036 records the block; the staged package is ready for an approved handle, a different token, or a decision to skip the Space."*


### Publication status — three lines to memorise
Say: *"The Afaan Oromo ceiling was closed as failed after four translation calls; no Oromo film exists and no quality claim was made."*
Say: *"PUBLISH_DRAFT.md contains the YouTube and Space text with the AI-generated film label, but nothing has been uploaded."*
Say: *"I publish only after you approve the account and the AI label; the director confirmed at least three viewers per cut."*


### Final audit — three lines to memorise
Say: *"Both exports are 73 seconds, 24 fps, H.264/AAC, measured -14.02 LUFS and -0.98 dBTP."*
Say: *"The 152 log rows, 104 non-cache calls, 7 failures and 967,733 ms in COSTS.md match runs.jsonl exactly."*
Say: *"plan reports 38 cache hits and zero regenerations; nothing upstream would be rebuilt."*

### Documentation cleanup — three lines to memorise
Say: *"The Oromo ceiling is closed as failed after four translation calls; the native-speaker check is moot and no Oromo film exists."*
Say: *"Older -14.01, -14.04 and -14.32 readings are labelled historical; the delivered film measures -14.02 LUFS / -0.98 dBTP."*
Say: *"That stale-PDF note was written before the viewer words arrived; REPORT.pdf has since been re-rendered from REPORT.md."*

### Final visual gate — three lines to memorise
Say: *"shot_07 stayed original after eight candidates failed; I logged the pouring defect as unresolved instead of claiming fixed."*
Say: *"shot_10 uses seed 1113, a head-and-shoulders crop with no hands, after the image-edit fallback failed on credentials."*
Say: *"The strict demo changes shot_02 narration in a throwaway clone; the submitted exports are 73 s at -14.02 LUFS / -0.98 dBTP and remain untouched."*

### One-command reproducibility — three lines to memorise
Say: *"The final `py run.py film` logged 33 rows — 10 narration, 10 keyframes, 1 music, 10 shots, 2 exports — every one a cache hit."*
Say: *"No model or TTS call was made and both MP4 hashes were unchanged: that is the one-command regeneration proof."*
Say: *"COSTS.md now reads 152 records, 104 non-cache calls, 7 failures and 967,733 ms, all computed from runs.jsonl."*

### Final clean-clone proof — three lines to memorise
Say: *"I cloned final `main` at 05a8b81 with no `.env`, installed only requirements.txt, and `preflight` said ready."*
Say: *"Plain `run.py film` gave 21 cache hits and 12 local FFmpeg rows with zero model calls, and both MP4 hashes matched."*
Say: *"The earlier clone proof was from an older commit; EXP-031 proves the exact code being submitted."*


### The supplied viewer feedback — three lines to memorise
Say: *"I pasted the director's six answers verbatim into DESIGN.md and rewrote REPORT.md section 2 from those exact words."*
Say: *"I added formal summaries beside the quotes, but I did not rewrite the viewers' words or invent names and timestamps."*
Say: *"The pronunciation and visual criticisms are recorded as open issues; nothing was regenerated, and I record the director's confirmation of at least three viewers per cut without inventing quotes."*


### Corrected viewer count — three lines to memorise
Say: *"The director first corrected the count to more than three people, then confirmed at least three viewers at each cut; both statements are in DESIGN.md and REPORT.md."*
Say: *"The audience threshold is met by the director's confirmation; I did not invent names, timestamps or quotes that were not supplied."*
Say: *"The PDF was re-rendered again from REPORT.md, so the written evidence and the submitted report say the same thing."*


### Per-cut audience confirmation — three lines to memorise
Say: *"The director confirmed that at least three people watched each of the two cuts, so the audience-count threshold is met."*
Say: *"The written record still contains only the exact words supplied; I did not invent names, timestamps or extra quotes."*
Say: *"I changed only DESIGN.md, REPORT.md, the PDF and the supporting notes; the film, cache and logs were untouched."*


### The strict walkthrough script — three lines to memorise
Say: *"The strict five-minute script is near the top of INTERVIEW_PREP.md; it shows preflight, the storyboard line change, the dry run, one model log row and both submitted hashes."*
Say: *"Changing shot_02 narration moves plan from 38/0 to 35/3: one Gemini TTS call and two local exports; local radio cut then returns it to 38/0."*
Say: *"I state the true specs and admit the film is Ken Burns over AI stills; the supplied viewer words are logged and re-rendered, publication is still pending."*
