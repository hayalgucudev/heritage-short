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





