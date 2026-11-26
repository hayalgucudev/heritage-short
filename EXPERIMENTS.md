# Experiments Log

Target: **>= 10 controlled experiments** (changing ONE variable at a time, recording Hypothesis, Change, Result, and Decision).

## EXP-001 — Prebuilt Voice Comparison for Amharic TTS (`Aoede` vs `Kore`)
- **Hypothesis:** Changing only the prebuilt voice from `Aoede` to `Kore` on `gemini-3.8-flash-tts` will improve Amharic cadence and reduce the bloated `14.32 s` single-sentence duration.
- **Change:** `voiceName`: `Aoede` -> `Kore` (identical model `gemini-3.8-flash-tts`, identical prompt & Amharic sentence).
- **Result:** Succeeded in `3,771 ms` (`outputs/smoke/amharic_tts_kore.wav`), duration **`7.08 s`** (down from `14.32 s`, `-50.6%`; `Aoede` baseline was `5,093 ms`).
- **Decision:** Not selected — shorter than baseline, but superseded by `EXP-003` (`--no-wrapper`).

## EXP-002 — TTS Model Variant for Amharic (`gemini-3.8-flash-tts` vs `gemini-3.8-flash-lite-tts`)
- **Hypothesis:** Switching only the TTS model from `gemini-3.8-flash-tts` to `gemini-3.8-flash-lite-tts` (keeping `voiceName=Aoede` and identical prompt) may alter pronunciation accuracy and latency.
- **Change:** `model`: `gemini-3.8-flash-tts` -> `gemini-3.8-flash-lite-tts` (identical voice `Aoede`, identical prompt & Amharic sentence).
- **Result:** Succeeded in `3,290 ms` (`outputs/smoke/amharic_tts_lite.wav`), duration **`6.00 s`** (faster latency than `5,093 ms` baseline and `8.32 s` shorter audio).
- **Decision:** Not selected — `EXP-003` gave better pronunciation and more natural pacing.

## EXP-003 — Removing English Instruction Wrapper from TTS Input
- **Hypothesis:** Removing the English style instruction (`"Speak in a calm, warm, unhurried storytelling voice in Amharic: "`) from `contents` (note: Gemini `speechConfig.voiceConfig` has no separate style-instruction field) will eliminate English bleed/extra pauses and drop single-sentence duration from `14.32 s` to natural length (~3–6 s).
- **Change:** Prompt text: stripped English prefix, sending only the raw Amharic sentence (identical model `gemini-3.8-flash-tts`, identical voice `Aoede`).
- **Result:** Succeeded in `3,930 ms` (`outputs/smoke/amharic_tts_nowrapper.wav`), duration **`5.20 s`** (most natural single-sentence length: `9.12 s` shorter than the `14.32 s` baseline with the exact same voice and model). Director listened and confirmed: *"no English, correct words, natural pace, but a bit robotic."*
- **Decision:** Adopted `--no-wrapper` pure Amharic text permanently for all narration (see `EXP-004` for voice selection).

## EXP-004 — Voice Warmth Check Without Wrapper (`Aoede` vs `Kore`, `--no-wrapper`)
- **Hypothesis:** Testing `Kore` with `--no-wrapper` (no English instruction) may sound warmer than `Aoede` while keeping natural ~5 s single-sentence pacing.
- **Change:** `voiceName`: `Aoede` -> `Kore` (identical model `gemini-3.8-flash-tts`, identical `--no-wrapper` raw Amharic text).
- **Result:** Succeeded in `3,515 ms` (`outputs/smoke/amharic_tts_kore_nowrapper.wav`), duration **`5.04 s`** (slightly faster latency and `0.16 s` shorter than `Aoede` `--no-wrapper` at `5.20 s`). Director listened to both and confirmed `Kore` sounded better.
- **Decision:** **Winner / Production voice.** Switched all 10 shots in `storyboard.json` to `Kore` (`gemini-3.8-flash-tts`, no English wrapper). The 5 earlier `Aoede` clips (`shot_01`–`shot_05`) were archived in `outputs/narration_aoede/` for the record.

## EXP-005 — Voice Continuity Check After 10/Day Quota (`gemini-3.8-flash-tts` vs `gemini-3.8-flash-lite-tts`, `Kore`)
- **Hypothesis:** After `gemini-3.8-flash-tts` hit its 10/day free-tier limit at `shot_07`, generating `shot_07` with `gemini-3.8-flash-lite-tts` using the same `Kore` voice and `--no-wrapper` prompt will match `shot_01`–`shot_06` closely enough to finish Stage 3 today without audible speaker mismatch.
- **Change:** `tts_model`: `gemini-3.8-flash-tts` -> `gemini-3.8-flash-lite-tts` on `shot_07` (`Kore`, `--no-wrapper`).
- **Result:** Succeeded in `2,967 ms` (`outputs/narration/shot_07.wav`), duration **`3.92 s`** (vs `7.00 s` slot).
- **Decision:** Superseded by `EXP-006` after listening to all 10 shots (`shot_07`–`shot_10` flagged unnatural).

## EXP-006 — Full 10-Shot Voice Continuity Review (`gemini-3.8-flash-tts` 01–06 vs `gemini-3.8-flash-lite-tts` 07–10)
- **Hypothesis:** Using `gemini-3.8-flash-lite-tts` (`Kore`, `--no-wrapper`) for `shot_07`–`shot_10` would blend seamlessly with `shot_01`–`shot_06` (`gemini-3.8-flash-tts`, `Kore`) in a full listen-through.
- **Change:** Generated `shot_07`–`shot_10` on `gemini-3.8-flash-lite-tts` (`2.45 s`–`2.97 s` latency; `3.52 s`–`4.52 s` audio durations) while keeping `shot_01`–`shot_06` on `gemini-3.8-flash-tts`.
- **Result:** Director listening check found that `shot_07`–`shot_10` sound unnatural compared to `shot_01`–`shot_06`.
- **Decision (resolved 2026-11-26):** **Narration marked `PROVISIONAL`** until the quota reset; the provisional radio cut let pacing be checked early. All four shots were then regenerated on `gemini-3.8-flash-tts` (EXP-022); the `PROVISIONAL` marker is now removed. The hypothesis that flash-lite would blend was **rejected** by the listener's ears, and the fix was worth four calls.

## EXP-007 — Visual Style Pivot: Painterly Illustration vs. 35mm Documentary Realism
- **Hypothesis:** Replacing the painterly gouache/oil style (`ref_seed1024.png`) with a realistic 35mm documentary film style (`ref_real_seed1024.png`–`1026.png`) will make the film feel less visibly AI-generated and more grounded for family and classmate audiences.
- **Change:** Replaced `style_block` in `storyboard.json` (and removed gouache/oil illustration wording across all shot prompts) with `"cinematic 35mm film still, natural soft window light, muted warm earth tones, visible skin texture and fine wrinkles, subtle film grain, shallow depth of field, documentary realism, slightly imperfect and unposed, Ethiopian highland village, no text or watermarks"`, keeping fixed seeds `1024, 1025, 1026` on `@cf/black-forest-labs/flux-2-klein-4b` and shifting hands to a relaxed, simple pose holding a clay cup.
- **Result:** *Planned director viewing of `ref_real_seed1024..1026.png` vs `ref_seed1024.png`, plus a blind preference check with 3 people.* **Not run; no viewing result and no blind preference result exist.**
- **Trade-off Risk & Mitigation:** Realistic human skin, eyes, and hands tend to drift or warp more noticeably in `Wan 2.2 TI2V-5B` at `480p` than stylized illustration. If any animated clip shows facial or hand artifacts, our plan uses the deterministic FFmpeg Ken Burns (`zoompan`) fallback over the clean FLUX keyframe for those shots.

## EXP-008 — `shot_02` Single-Variable Reference Conditioning Test (`--no-ref` vs `input_image_0`)
- **Hypothesis:** Conditioning `flux-2-klein-4b` on `ref_real_seed1025.png` via `input_image_0` (holding prompt, `seed=102`, and `steps=4` fixed) will keep Grandmother's face consistent while placing her beside the hearth tending embers.
- **Change:** Generated `shot_02` twice with identical `image_prompt` and `seed=102`: once without reference (`outputs/keyframes/shot_02_noref.png`, `11,053 ms`) and once with `input_image_0=ref_real_seed1025.png` (`outputs/keyframes/shot_02_ref.png`, `8,418 ms`).
- **Result (Visual & Anatomy Inspection):**
  - `shot_02_noref.png`: Clean face (3/4 downward gaze) and natural hands tending embers over the clay hearth; matches the shot action and clothing/style description accurately.
  - `shot_02_ref.png`: Clean face and hands, **100% facial/outfit consistency** — **however**, `flux-2-klein-4b`'s `input_image_0` behaved like an image-to-image edit, preserving her front-facing pose and clay cup from `ref_real_seed1025.png` and placing the hearth fire behind her instead of showing her tending the embers.
- **Decision:** *Pending director verdict* (whether to generate action shots with verbatim description + `--no-ref`, reserve `input_image_0` only for front-facing/close-up shots, or test pose-override phrasing in `input_image_0`).

## EXP-009 — `shot_02` pose-override instruction with reference conditioning (EXP-008 option C)
- **Hypothesis:** Adding an explicit pose override ("now kneeling in profile…, no cup in her hands") while keeping `input_image_0=ref_real_seed1025.png` will keep Grandmother's identity **and** let her perform the hearth action, fixing EXP-008's frozen cup pose.
- **Change:** Only the prompt changed versus EXP-008's `shot_02_ref` test — verbatim instruction `"the same woman as in the reference image, now kneeling in profile beside a clay hearth, tending glowing embers, no cup in her hands"` plus the fixed style block. Model `@cf/black-forest-labs/flux-2-klein-4b`, `seed=102`, `steps=4`, and the same reference PNG were held constant.
- **Prompt rationale (one line):** the phrase names the reference for identity but explicitly cancels its front-facing cup pose, so the model should keep the face while changing the action.
- **Result:** `outputs/keyframes/shot_02_exp009_ref.png`, latency **`9,038 ms`** (`cache_hit=false`, `1_cloudflare_flux_call`). `storyboard.json` was not edited; a temporary copy of the storyboard supplied the test prompt.
- **Visual result:** *Pending director verdict.* This assistant cannot inspect PNG content, so it does not claim any finger count or pose match it did not see. The images were opened in the browser for the director.
- **Decision (director, 2026-11-25):** **Rejected.** The conditioned image shows a **different face**, so `input_image_0` did **not** preserve identity even with the pose-override phrase. Reference conditioning is therefore not reliable for action shots on this evidence; use verbatim description + `--no-ref` unless a future experiment proves otherwise.

## EXP-010 — `shot_02` re-seeded no-reference with hands-protecting phrasing
- **Hypothesis:** Changing only the seed and adding an object-in-hand/partial-shadow instruction will remove the **4-finger hand defect** the director found in `shot_02_noref.png`.
- **Change:** `seed=102 -> 112`; prompt adds "holding a short wooden stirrer above the coals and partly in shadow, relaxed fingers"; no reference image. Model and `steps=4` held constant. This is attempt 2 of 3 under the hands policy in FAILURES.md entry 018.
- **Prompt rationale (one line):** a held object plus shadow gives the model an excuse to hide individual fingers, which is safer than asking for an open, fully visible hand.
- **Result:** `outputs/keyframes/shot_02_seed112_noref.png`, latency **`9,927 ms`** (`cache_hit=false`, `1_cloudflare_flux_call`).
- **Visual result (director, 2026-11-25):** `"the others seem okay"` — accepted; no 4-finger defect reported in this image.
- **Decision:** **Accepted** as the working `shot_02` look. Attempt 3 and the Ken Burns fallback are not needed for this shot on the director's check. Overall "make it more realistic" request is tracked separately below.

## EXP-011 — `shot_03` no-reference face comparison against the locked reference
- **Hypothesis:** A no-reference keyframe using the verbatim character description may match the locked reference face well enough to avoid `input_image_0` pose-freezing on action shots.
- **Change:** `shot_03` generated with `use_reference=False`, unchanged `image_seed=103` and unchanged original prompt; compared by the director against `ref_real_seed1025.png`.
- **Result:** `outputs/keyframes/shot_03_noref_seed103.png`, latency **`11,439 ms`** (`cache_hit=false`, `1_cloudflare_flux_call`).
- **Visual result (director, 2026-11-25):** `"the others seem okay"` — accepted; no face complaint about this no-reference image.
- **Decision:** **Accepted.** Together with EXP-009's rejected face, this supports the rule: generate action shots from the verbatim character description with `--no-ref`; do not use `input_image_0` on this model to preserve identity.

## EXP-012 — Tighter global style block for realism (director chose option A, 2026-11-25)
- **Hypothesis:** Turning one shared dial — replacing "cinematic 35mm film still" with "candid 35mm documentary photograph" and adding "photoreal skin with visible pores and fine wrinkles, authentic woven cotton fabric texture, no illustration or painting" — will make all shots read as real photography without breaking consistency across the film.
- **Change:** Edited **11 occurrences** in `storyboard.json`: the global `style_block` plus the same wording copied at the end of all 10 `image_prompt`s. Seeds `101`–`110`, model `@cf/black-forest-labs/flux-2-klein-4b`, `steps=4`, and every story/narration line were held constant. Generated with `--no-ref` (per EXP-009/011 decision).
- **Prompt rationale (one line):** "photograph" instead of "film still" plus pores/weave/no-illustration pushes the model toward a real camera look; no living artist is named and the palette/light block stays fixed.
- **Result:** 10/10 `status=ok`, `cache_hit=false`, `1_cloudflare_flux_call` each; latencies `10233, 9923, 11340, 7737, 8849, 11896, 10735, 8118, 9656, 10237` ms; **total 98,724 ms (~98.7 s)**. Files `outputs/keyframes/shot_01.png` … `shot_10.png`; hashes and rows written to `outputs/manifest.json` and `runs.jsonl`. Validation passed before any call.
- **Visual result:** *Pending director's keyframes-gate verdict.* All 10 PNGs were opened in the browser; this assistant cannot see PNG content and makes no finger/face/realism claim it did not observe.
- **Decision (resolved 2026-11-25):** the director chose option A and the 10 regenerated keyframes were accepted (`DESIGN.md` 11–12). The hands policy adopted for later shots: object in hand, shadow or out of frame; max 3 attempts, then change framing, then FFmpeg Ken Burns over the clean still. **No Wan 2.2 video clip has ever been produced; the film uses Ken Burns motion over generated stills. The ACE-Step GPU job did run on Colab and produced the approved score.**

## EXP-013 — Register the downloaded ACE-Step WAV as the score (director approved, 2026-11-25)
- **Hypothesis:** The single downloaded 60.0 s stereo WAV can serve as the floor score even though the 3-candidate notebook metadata was not downloaded with it.
- **Change:** Renamed `outputs/music/download (1).wav` to `outputs/music/candidate_01_seed777.wav` **without processing the audio**; wrote `music_run_metadata.json` with `seed=null` and an explicit note that the filename's `777` is an ordering convention, not a measured seed; set `storyboard.json -> music.selected_candidate = "candidate_01"`. Ran `py run.py music` to hash and log it.
- **Result:** `candidates_ready`, 1 candidate, measured `60.0 s` (`pcm_s16le`, 48 kHz, stereo), `input_hash=40539b99…`, `cache_hit=false`, one `1_kaggle_acestep_call` row in `runs.jsonl` with `latency_ms=null` (not measured, so not invented).
- **Decision:** Approved by director for the floor. If the 3-candidate Kaggle zip is imported later, only the score/mix/final assembly depend on that change.

## EXP-014 — Local smoke test of the two-pass loudnorm and dual export (2026-11-25)
- **Hypothesis:** A single unnormalised sidechained mix plus FFmpeg two-pass `loudnorm=I=-14:TP=-1:LRA=11` can hit the deliverable loudness target in both aspect ratios without model calls.
- **Change:** No model calls and no deliverables. Temporary files only: 10 Ken Burns clips from the approved keyframes, one 73.0 s ducked mix, per-aspect ASS subtitles, then both exports. Three bugs were found and fixed (see `FAILURES.md` 020).
- **Result:** Pass-1 measurement `input_i=-22.55`, `input_tp=-1.37`, `input_lra=12.90`. Measured on the rendered exports: **-14.32 LUFS, -0.97 dBTP (HISTORICAL smoke-render value; final delivery measured -14.02 LUFS / -0.98 dBTP)** for both 9:16 and 16:9; both 73.0 s at 24 fps. Render latency 6,485 ms (9:16) and 7,835 ms (16:9), locally measured.
- **Decision:** The audio chain is accepted for the floor. Visual subtitle placement and end-card text remain unverified by this assistant (no image input) and need the director's check on a real frame; no final film has been rendered behind the final-edit gate.

## EXP-015 — Director-approved provisional visual cut (2026-11-25)
- **Hypothesis:** A provisional cut with the still-stale voices is useful enough to get early visual/subtitle feedback, even though shots 07-10 will be replaced after the TTS quota resets.
- **Change:** Added an explicit `assemble --allow-stale-narration` flag (default off). Built 10 local Ken Burns clips (`py run.py shots`, 10 x `0_local_ffmpeg`, latencies 1,417-1,473 ms) and rendered both finals. The export hash still uses the *expected* narration hashes, so a later TTS fix invalidates both exports automatically.
- **Result:** `outputs/final/film_9x16.mp4` (608x1080) and `film_16x9.mp4` (1280x720), both H.264 + AAC 48 kHz stereo, 24 fps CFR, **73.0 s**. Measured audio **-14.32 LUFS / -0.95 dBTP (HISTORICAL provisional-cut value; final delivery measured -14.02 LUFS / -0.98 dBTP)**. `runs.jsonl` records `stale_narration=[shot_07, shot_08, shot_09, shot_10]` on both rows. `plan` now reports 31 cache hits and 7 regenerations.
- **Decision:** Provisional only; it served its purpose for User Test 2. The voices were fixed on 2026-11-26 (EXP-022) and the flag is no longer needed. No story text changed.

## EXP-016 — Isolating the missing-voice bug with a three-way A/B (2026-11-25)
- **Hypothesis:** The silence in shots 09-10 is caused by reusing one FFmpeg audio label for both the sidechain and the final mix, not by the narration files or the score.
- **Change:** Fixed seeds and inputs; three temporary filter graphs only: (A) plain `amix` with no ducking, (B) `asplit=2` then sidechain + `amix`, (C) original reused label. Then applied the winning graph to production code with `code_version: 2` so cache invalidation occurred.
- **Result:** Slot mean dB for A/B/C respectively: shot 09 `-21.4 / -21.4 / -67.3`, shot 10 `-22.5 / -22.5 / -91.0`; all earlier slots normal in A and B. Production re-render: 10/10 slots audible (`-20.3` to `-16.2` dB), **-14.01 LUFS / -0.99 dBTP (HISTORICAL A/B-test value; final delivery measured -14.02 LUFS / -0.98 dBTP)**, 73.0 s, 24 fps CFR.
- **Decision:** Hypothesis confirmed; B is now the production graph. This changed my mind about a hidden risk: a successful FFmpeg exit is not proof of a correct mix, so slot-level measurement is now a mandatory verification step (logged in `FAILURES.md` 022).

## Ceiling plans (chosen 2026-11-25, NOT started — floor first)
- **EXP-017 (CLOSED AS FAILED, 2026-11-26) — second-language remake.** Hypothesis: a stranger can understand the story without Amharic when the same 10 shots are narrated in a second language, but at least one model failure will need an honest workaround. Director chose **Afaan Oromo**, one long TTS call split locally, and consented to sending the fictional story text to Gemini; a family/community member had been named to check names and places (name withheld). The director ruled that check **MOOT on 2026-11-26**: the ceiling failed at translation, so no text exists to check and no Oromo film will be published.
  - **Change so far:** added `translations/afaan_oromo.json` (prompt, models, voice) and `pipeline/second_language.py`, plus a `py run.py second-language` command. The locked `storyboard.json` was **not** edited. `assemble_film` gained an optional narration directory, output suffix and per-shot hash override so the alternate film reuses the same clips and English subtitles.
  - **Result so far (local smoke only, 2026-11-25):** with a synthetic long WAV in a temp clone and **zero model calls**, the split produced 10 shot WAVs and both `_om` exports rendered at **73.0 s** (7,769 ms / 8,836 ms); all ten audio slots measured `-20.3` to `-16.2 dB`. Two real seek/timestamp bugs were found and fixed (`FAILURES.md` 023).
  - **Result on 2026-11-26:** preconditions passed (TTS fix done, `plan` 38 hits / 0 regenerations), so the approved run was attempted. The **first** call, Gemini text translation, failed with a `ReadTimeout` of **54.2 s** against `generativelanguage.googleapis.com` after the retry helper's 60 s cap (`FAILURES.md` 028). No translation, no TTS call, no `_om` export. A director-approved retry failed the same way (read timeout **46.2 s** on the same endpoint). A director-approved model switch to `gemini-3.6-flash` then failed too — HTTP 503 high demand (`FAILURES.md 030`); a fourth attempt after the director changed the API credential returned the same 503 (`FAILURES.md 031`). The TTS call was never reached in either attempt. **Decision — CLOSED AS FAILED by the director on 2026-11-26:** four translation attempts failed (two read timeouts, two HTTP 503s, the last after a credential change). No claim about translation quality, native speakers or comprehension, and nothing published. This changed my mind about treating a ceiling item as 'pending': it is now a finished negative result, and the remaining time belongs to the human-graded work. **No Oromo variant will be published.**
- **EXP-018 (COMPLETE, 2026-11-26) — reusable CLI.** Hypothesis: a stranger can regenerate both MP4s from `storyboard.json` using documented commands without reading the Python source.
  - **Change so far:** added `py run.py preflight`, which checks FFmpeg, the schema, the 10 keyframes, the 10 narration WAVs, the score WAV and the manifest, and reports only booleans about `.env` (never values). Committed all 20 cached WAVs so a clone needs no keys for a cached rebuild.
  - **Result so far (2026-11-25):** cloned HEAD `d5fc95a` to a temp folder with **no `.env`**; `preflight` reported `ready: true`, `env_file_present: false`, `missing_files: []`. `plan` reported 18 cache hits / 20 regenerations (the 4 stale TTS clips plus missing clips/exports). `film --skip-narration --allow-stale-narration` rendered both 9:16 and 16:9 MP4s, **73.0 s, H.264/AAC, 24 fps CFR**, with **zero model calls**; clip latencies 1,367-1,450 ms. Two manual flags were needed because shots 07-10 are still stale.
  - **Final measurement (2026-11-26):** cloned HEAD `5bd6adf` to a temp folder with **no `.env`**. `preflight`: `ready: true`, `env_file_present: false`, `missing_files: []`. Before the build `plan` showed 25 hits / 13 regenerations, **all** `0_local_ffmpeg` because the derived clips/exports are gitignored, not because inputs were stale. Plain `py run.py film` with **no flags** succeeded: all 10 narration WAVs, 10 keyframes and the score were cache hits; it rebuilt 10 Ken Burns clips (1,419–1,557 ms) and both finals (4,781 / 5,680 ms) with `stale_narration: []`. The clone's `runs.jsonl` gained **34 rows: 21 `0_cache_hit` + 13 `0_local_ffmpeg`, zero paid model calls, all `ok`**. After `radio-cut` (2,925 ms) the clone's `plan` was **38 hits / 0 regenerations**. Both clone MP4s are **byte-identical** to the delivered ones (SHA-256 `73C5205D…92381` and `8F34DA3C…30756`).
  - **Known limitation recorded, not fixed:** cache keys are not portable across clone paths. `contracts.clip_hash` passes an absolute keyframe path and `compute_stage_hash` uses `ref.as_posix()` as a dict key, so a clone at a different path computes different `input_hash` values and rebuilds the 12 local FFmpeg outputs. Rendered bytes are identical, so the cost is local CPU only. I did not change this because it would invalidate every cached clip without a director decision.
  - **Decision:** EXP-018 **complete** — a stranger can regenerate both MP4s from `storyboard.json` with one command, no keys and no model calls.

## EXP-019 — Quiet room tone, bolder subtitles and a restyled end card (2026-11-25)
- **Hypothesis:** A very quiet, deterministic room tone plus slightly larger Arial Bold subtitles and a simpler two-line end card will make the film feel finished without moving the measured mix off target. All of it can be done locally with FFmpeg, so the cost is zero quota.
- **Change:** `pipeline/assemble.py`: subtitle sizes 32->35 px (9:16) and 40->44 px (16:9), with ASS side margins 24->8 px so the longest 33-character line still fits (measured 587 px in a 608 px frame); end card kept at exactly 3 s but split on "·" into a bold `arialbd.ttf` headline and a quieter tribute, with a bronze rule on a warm near-black field; a seeded pink-noise room tone (`seed=20261126`, lowpass 1400 Hz) mixed in as a third input. `contracts.ASSEMBLE_SETTINGS` bumped to `code_version: 3` so both finals invalidate automatically.
- **Result:** The first ambience gain (`0.012`) measured **-54.1 dB mean / -42.1 dB peak** in isolation — effectively inaudible, so the hypothesis failed at that value. Raised to `0.06`: **-40.2 dB mean / -28.2 dB peak**, a gentle bed. Rebuilt both finals: 73.0 s, H.264/AAC 48 kHz stereo, 24 fps CFR, **-14.04 LUFS / -0.99 dBTP (HISTORICAL polish-stage value; final delivery measured -14.02 LUFS / -0.98 dBTP)**, all ten slot means **-20.2 to -16.1 dB**. FFmpeg latencies 4,325 ms and 5,396 ms, both `0_local_ffmpeg`, logged in `runs.jsonl` at 13:36 UTC.
- **Decision:** Kept the polished version; it changed my mind about "quiet ambience" — a number that looks small in code can be far below audibility after filtering, so the layer is now measured in isolation before judging it. Subtitle legibility and end-card appearance still need the director's eyes (this session cannot view frames); no visual claim is made here.

## EXP-020 — Clearing stale reference portraits (2026-11-25)
- **Hypothesis:** Regenerating the three unused reference portraits against the locked style block will make `plan` clean without changing the director-approved final edit.
- **Change:** `py run.py ref-sheet` with the three original seeds (1024, 1025, 1026). Director explicitly approved this 3-call Cloudflare Flux spend; production keyframes use `--no-ref`, so no clip depends on these images.
- **Result:** Three real calls, cache miss, latencies **13,044 / 11,721 / 14,496 ms**. `plan` went from 29 hits / 9 regenerations to **34 hits / 4 regenerations** — only the four known TTS shots remain. Both finals stayed cache hits, so the approved edit was untouched.
- **Decision:** Kept. This is a quota-cleanliness fix, not a visual change; it makes the clean-clone one-command test predictable. No new keyframe, clip or export was generated.

## EXP-021 — Verifying the notebook repairs on real GPUs (2026-11-25)
- **Hypothesis:** The notebook fixes made from pasted tracebacks will hold on a fresh GPU session: pinned versions will let Wan import, guards will fail loudly instead of cascading, and the ACE-Step Colab run will make all three candidates.
- **Change:** The director reran `acestep_music_colab.ipynb` on Colab and `wan_clips_kaggle.ipynb` on Kaggle; I patched only the download cell and cell 1's error message afterward. I also ran `py run.py clips-export` locally to create the missing job zip.
- **Result:** Colab ACE-Step succeeded on a T4: DiT load **10.1 s**, **5.9 GB** used, three candidates in **13,842 / 7,113 / 6,965 ms**, metadata written; only `files.download` failed (browser JS). Kaggle Wan printed the three pinned versions and **`WanImageToVideoPipeline import: OK`** (the pin fix works), and cells 3/5/6 raised the intended clear errors. Cell 1 still failed because no job dataset was mounted; `clips-export` produced a **7,796,471-byte** zip. No Wan clip, no GPU latency for Wan, no new score imported.
- **Decision:** Keep the pins and guards — they changed my mind about "locally compiled" being enough; a real run distinguishes a dependency fix from a plausible-looking patch. The Wan job zip is gitignored and rebuilt by one local command. The delivered film is unchanged.

## EXP-022 — Final voice continuity: four re-takes on the correct model (2026-11-26)
- **Hypothesis:** Regenerating only shots 07–10 on `gemini-3.8-flash-tts` after the daily quota reset will remove the voice mismatch the listener heard, and the hash chain will invalidate only those shots plus the finals and radio cut.
- **Change:** Four separate pre-approved calls with the locked storyboard text and `Kore` / `--no-wrapper`: `run.py narration --shot shot_0N --tts-model gemini-3.8-flash-tts`. No story or subtitle text changed. Then `run.py assemble` with **no** `--allow-stale-narration` flag, plus a zero-quota `radio-cut` rebuild.
- **Result:** Four real cache misses on `gemini-3.8-flash-tts`, latencies **3,214 / 3,375 / 2,805 / 4,309 ms**, durations **3.86 / 4.46 / 2.91 / 4.17 s**, all inside their 7.0 s slots. `plan` went from 34 hits / 4 stale regenerations to 38 hits / 0 regenerations after assembly (4,604 / 5,300 ms) and radio cut (2,613 ms). Both delivered MP4s: **73.0 s**, H.264 608x1080 / 1280x720, AAC 48 kHz stereo, `r_frame_rate` and `avg_frame_rate` both **24/1**; measured **−14.02 LUFS / −0.98 dBTP**, ten slot means **−21.3 to −16.2 dB** — all ten carry voice. `stale_narration: []` on both assemble rows in `runs.jsonl`.
- **Decision:** Accepted as the final cut; the listener's "Voices" complaint is closed at the source rather than by tweaking the mix. It changed my mind about accepting a free-tier fallback as "good enough" — the operationally cheap shortcut cost a second quota window and a full rebuild, so model continuity is now treated as a release gate. No visual change was made and no new quota spend is planned for Wan.


## EXP-023 — Is the Afaan Oromo failure a network block?
- **Hypothesis:** the two translation read timeouts were caused by loss of connectivity to `generativelanguage.googleapis.com`.
- **Change:** no code or model change. A free DNS + TCP + TLS probe was run locally, with `github.com` as a control, and `runs.jsonl` was checked for earlier calls to the same text model. Zero model calls and zero quota.
- **Result:** Gemini DNS 11.4 ms, TCP 78.9 ms, TLS 113.2 ms (`TLSv1.3`); control DNS 5.8 ms, TCP 95.4 ms, TLS 104.9 ms. Four TTS calls on the same host had succeeded ~25 minutes earlier. The configured `gemini-3.8-flash` text model has no success in 95 logged rows — two HTTP 503 "high demand" errors plus the two timeouts — while `gemini-3.6-flash` succeeded once in 33.9 s.
- **Decision:** hypothesis **rejected**; the fault is request/model-side, not network-side. It changed my mind about blaming the endpoint. I did not spend quota on a third blind retry. **The director closed the ceiling as failed on 2026-11-26 after four translation attempts; no further call or model switch will be made without a new decision.**


## EXP-024 — Switch the translation model to the one that once worked
- **Hypothesis:** `gemini-3.6-flash` will translate the ten lines successfully because `runs.jsonl` records a 33,900 ms success for it, while `gemini-3.8-flash` has never succeeded.
- **Change:** one field in `translations/afaan_oromo.json` (`text_model`); no prompts, story text, TTS model or code changed. One approved run of `run.py second-language`.
- **Result:** HTTP 503 "This model is currently experiencing high demand" after retries. No translation JSON, no TTS call, no `_om` exports, no new `runs.jsonl` row.
- **Decision:** hypothesis **rejected** — a single past success is not a reliable capacity guarantee on a free tier. This changed my mind about "pick the model with a historical success". I stopped rather than cycling models again; the remaining time goes to the finished floor, user tests and submission.


## EXP-025 — Walkthrough rehearsal: what does deleting one derived clip invalidate?
- **Hypothesis:** deleting `outputs/clips/shot_02.mp4` will invalidate only that clip and the downstream exports, never an upstream model stage.
- **Change:** deleted just that derived MP4, ran `py run.py shots --shot shot_02`, then re-ran `plan`. No prompts, seeds, keyframes, narration or score changed; zero quota.
- **Result:** `plan` moved from **38 hits / 0 regenerations** to **35 hits / 3 regenerations**: `shots/shot_02` plus the two finals and the radio cut, all labelled `0_local_ffmpeg`. Regeneration took **1,420 ms** and produced one `runs.jsonl` row (`cache_hit: false`, `status: ok`, same `input_hash` `d017039b…c5a9d`). ffprobe confirmed H.264, 480x480, 24 fps, 7.000000 s. `plan` returned to **38 hits / 0 regenerations**.
- **Decision:** this is the live step for the recorded walkthrough. It proves the dependency map visually in a few seconds and costs nothing; the director can safely show it on camera.
## EXP-026 — Fix the shot_07 prop and pouring stream from the delivered frames (2026-11-26)
- **Hypothesis:** naming the jebena's exact parts and tying it to "the same black pot as in shot_05", plus "the stream clearly landing in the cups" and "her eyes on the cups", will remove the terracotta-jug substitution and the stream falling down her body.
- **Change:** only `shot_07.image_prompt` and `image_seed` in `storyboard.json`; the fixed style block is appended verbatim and all narration, music, video-motion prompts and locks are untouched. Three `--no-ref` FLUX calls at seeds `1070`, `1071`, `1072`.
- **Result:** 3/3 `status=ok`, `cache_hit=false`, latencies `9,987 / 10,350 / 11,319` ms; files `outputs/keyframes/shot_07_seed1070.png` (746,389 B), `shot_07_seed1071.png` (763,145 B), `shot_07_seed1072.png` (770,375 B). `runs.jsonl` grew from 95 to 101 rows. **Director review is pending; no visual success is claimed and no export has been made.**
- **Decision:** pending the director's seed choice. Alternative considered: one generated image and accept it on prompt text alone; rejected because I cannot view images and this defect was found by the director's eye.

## EXP-027 — Fix the shot_10 outfit and stray hand (2026-11-26)
- **Hypothesis:** stating the outfit as "ONLY a plain white handwoven cotton dress and a white cotton shawl", adding explicit no-striped-cloak/no-green-or-brown negatives, and asking for one open hand with the other out of frame will remove the green/brown striped cloak and the partial hand at the left edge.
- **Change:** only `shot_10.image_prompt` and `image_seed` in `storyboard.json` (seed `110` -> `1110`, `1111`, `1112`); the approved character description and style block stay verbatim.
- **Result:** 3/3 `status=ok`, `cache_hit=false`, latencies `13,518 / 11,132 / 9,905` ms; files `outputs/keyframes/shot_10_seed1110.png` (742,096 B), `shot_10_seed1111.png` (774,127 B), `shot_10_seed1112.png` (745,210 B). **Director review is pending; no export has been made.**
- **Decision:** pending the director's seed choice; max three attempts, then change framing to head-and-shoulders if none pass.
