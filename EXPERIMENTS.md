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
- **Decision:** *Pending director listening check comparing `shot_06.wav` (`3.8-flash-tts`) and `shot_07.wav` (`3.8-flash-lite-tts`).*





