# Experiments Log

Target: **>= 10 controlled experiments** (changing ONE variable at a time, recording Hypothesis, Change, Result, and Decision).

## EXP-001 — Prebuilt Voice Comparison for Amharic TTS (`Aoede` vs `Kore`)
- **Hypothesis:** Changing only the prebuilt voice from `Aoede` to `Kore` on `gemini-3.8-flash-tts` will improve Amharic cadence and reduce the bloated `14.32 s` single-sentence duration.
- **Change:** `voiceName`: `Aoede` -> `Kore` (identical model `gemini-3.8-flash-tts`, identical prompt & Amharic sentence).
- **Result:** Succeeded in `3,771 ms` (`outputs/smoke/amharic_tts_kore.wav`), duration **`7.08 s`** (down from `14.32 s`, `-50.6%`; `Aoede` baseline was `5,093 ms`).
- **Decision:** *Pending director listening verdict.*

## EXP-002 — TTS Model Variant for Amharic (`gemini-3.8-flash-tts` vs `gemini-3.8-flash-lite-tts`)
- **Hypothesis:** Switching only the TTS model from `gemini-3.8-flash-tts` to `gemini-3.8-flash-lite-tts` (keeping `voiceName=Aoede` and identical prompt) may alter pronunciation accuracy and latency.
- **Change:** `model`: `gemini-3.8-flash-tts` -> `gemini-3.8-flash-lite-tts` (identical voice `Aoede`, identical prompt & Amharic sentence).
- **Result:** Succeeded in `3,290 ms` (`outputs/smoke/amharic_tts_lite.wav`), duration **`6.00 s`** (faster latency than `5,093 ms` baseline and `8.32 s` shorter audio).
- **Decision:** *Pending director listening verdict.*

## EXP-003 — Removing English Instruction Wrapper from TTS Input
- **Hypothesis:** Removing the English style instruction (`"Speak in a calm, warm, unhurried storytelling voice in Amharic: "`) from `contents` (note: Gemini `speechConfig.voiceConfig` has no separate style-instruction field) will eliminate English bleed/extra pauses and drop single-sentence duration from `14.32 s` to natural length (~3–6 s).
- **Change:** Prompt text: stripped English prefix, sending only the raw Amharic sentence (identical model `gemini-3.8-flash-tts`, identical voice `Aoede`).
- **Result:** Succeeded in `3,930 ms` (`outputs/smoke/amharic_tts_nowrapper.wav`), duration **`5.20 s`** (most natural single-sentence length: `9.12 s` shorter than the `14.32 s` baseline with the exact same voice and model).
- **Decision:** *Pending director listening verdict.*



