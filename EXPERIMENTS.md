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
- **Decision:** **Narration marked `PROVISIONAL`.** Proceed with `radio-cut` today to verify pacing/timing, then regenerate only `shot_07`–`shot_10` (4 calls, well within the 10/day limit) on `gemini-3.8-flash-tts` after `11:00 EAT` tomorrow (2026-11-26) when the daily quota resets. Because narration is cached per shot, downstream stages can proceed in parallel and only final assembly will re-run once those 4 WAVs update.

## EXP-007 — Visual Style Pivot: Painterly Illustration vs. 35mm Documentary Realism
- **Hypothesis:** Replacing the painterly gouache/oil style (`ref_seed1024.png`) with a realistic 35mm documentary film style (`ref_real_seed1024.png`–`1026.png`) will make the film feel less visibly AI-generated and more grounded for family and classmate audiences.
- **Change:** Replaced `style_block` in `storyboard.json` (and removed gouache/oil illustration wording across all shot prompts) with `"cinematic 35mm film still, natural soft window light, muted warm earth tones, visible skin texture and fine wrinkles, subtle film grain, shallow depth of field, documentary realism, slightly imperfect and unposed, Ethiopian highland village, no text or watermarks"`, keeping fixed seeds `1024, 1025, 1026` on `@cf/black-forest-labs/flux-2-klein-4b` and shifting hands to a relaxed, simple pose holding a clay cup.
- **Result:** *Pending director viewing of `ref_real_seed1024..1026.png` vs `ref_seed1024.png`, plus a blind preference check with 3 people to be run by the director.*
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
- **Decision:** Provisional pending verdict. If any shot fails the hands policy, use at most 3 attempts, then change framing, then FFmpeg Ken Burns over the clean still. No Wan video or ACE-Step GPU job has been started.

## EXP-013 — Register the downloaded ACE-Step WAV as the score (director approved, 2026-11-25)
- **Hypothesis:** The single downloaded 60.0 s stereo WAV can serve as the floor score even though the 3-candidate notebook metadata was not downloaded with it.
- **Change:** Renamed `outputs/music/download (1).wav` to `outputs/music/candidate_01_seed777.wav` **without processing the audio**; wrote `music_run_metadata.json` with `seed=null` and an explicit note that the filename's `777` is an ordering convention, not a measured seed; set `storyboard.json -> music.selected_candidate = "candidate_01"`. Ran `py run.py music` to hash and log it.
- **Result:** `candidates_ready`, 1 candidate, measured `60.0 s` (`pcm_s16le`, 48 kHz, stereo), `input_hash=40539b99…`, `cache_hit=false`, one `1_kaggle_acestep_call` row in `runs.jsonl` with `latency_ms=null` (not measured, so not invented).
- **Decision:** Approved by director for the floor. If the 3-candidate Kaggle zip is imported later, only the score/mix/final assembly depend on that change.

## EXP-014 — Local smoke test of the two-pass loudnorm and dual export (2026-11-25)
- **Hypothesis:** A single unnormalised sidechained mix plus FFmpeg two-pass `loudnorm=I=-14:TP=-1:LRA=11` can hit the deliverable loudness target in both aspect ratios without model calls.
- **Change:** No model calls and no deliverables. Temporary files only: 10 Ken Burns clips from the approved keyframes, one 73.0 s ducked mix, per-aspect ASS subtitles, then both exports. Three bugs were found and fixed (see `FAILURES.md` 020).
- **Result:** Pass-1 measurement `input_i=-22.55`, `input_tp=-1.37`, `input_lra=12.90`. Measured on the rendered exports: **-14.32 LUFS, -0.97 dBTP** for both 9:16 and 16:9; both 73.0 s at 24 fps. Render latency 6,485 ms (9:16) and 7,835 ms (16:9), locally measured.
- **Decision:** The audio chain is accepted for the floor. Visual subtitle placement and end-card text remain unverified by this assistant (no image input) and need the director's check on a real frame; no final film has been rendered behind the final-edit gate.





