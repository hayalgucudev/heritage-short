# Experiments Log

Target: **>= 10 controlled experiments** (changing ONE variable at a time, recording Hypothesis, Change, Result, and Decision).

## EXP-001 — Prebuilt Voice Comparison for Amharic TTS (`Aoede` vs `Kore`)
- **Hypothesis:** Changing only the prebuilt voice from `Aoede` to `Kore` on `gemini-3.8-flash-tts` will improve Amharic cadence and reduce the bloated `14.32 s` single-sentence duration.
- **Change:** `voiceName`: `Aoede` -> `Kore` (identical model `gemini-3.8-flash-tts`, identical prompt & Amharic sentence).
- **Result:** *Pending execution (`outputs/smoke/amharic_tts_kore.wav`).*
- **Decision:** *Pending director listening verdict.*

## EXP-002 — TTS Model Variant for Amharic (`gemini-3.8-flash-tts` vs `gemini-3.8-flash-lite-tts`)
- **Hypothesis:** Switching only the TTS model from `gemini-3.8-flash-tts` to `gemini-3.8-flash-lite-tts` (keeping `voiceName=Aoede` and identical prompt) may alter pronunciation accuracy and latency.
- **Change:** `model`: `gemini-3.8-flash-tts` -> `gemini-3.8-flash-lite-tts` (identical voice `Aoede`, identical prompt & Amharic sentence).
- **Result:** *Pending execution (`outputs/smoke/amharic_tts_lite.wav`).*
- **Decision:** *Pending director listening verdict.*

