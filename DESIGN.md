# Design & Audience Log

## Creative Brief (Locked at Gate 1)
- **Story:** A warm, stylized tribute to `"Grandmother"` in `"the village"` (fictionalized, no real-person likeness).
- **Audience & Platforms:**
  - Family & community on mobile (WhatsApp, TikTok — **9:16** vertical, safe-area English subtitles).
  - Classmates & reviewers on desktop (**16:9** widescreen).
- **Target Ending Feeling:** Quiet gratitude and warmth.
- **Language:** Amharic narration with burned-in English subtitles (2 lines max, ~40 chars/line).
- **Narration Craft & Voice Tone (`PROVISIONAL`):** `gemini-3.8-flash-tts` (`Kore`, pure Amharic text with `--no-wrapper`). Shots `01`–`06` use `gemini-3.8-flash-tts`; shots `07`–`10` were temporarily generated with `gemini-3.8-flash-lite-tts` due to the 10/day free-tier cap and sound unnatural (`EXP-006`). Narration is marked **PROVISIONAL** until shots `07`–`10` are retried on `gemini-3.8-flash-tts` after `11:00 EAT` on 2026-11-26 (4 calls).
- **Visual Style Block (Updated):** Realistic 35mm documentary film still (`"cinematic 35mm film still, natural soft window light, muted warm earth tones, visible skin texture and fine wrinkles, subtle film grain, shallow depth of field, documentary realism, slightly imperfect and unposed, Ethiopian highland village, no text or watermarks"`). Switched from the earlier painterly gouache/oil style (`ref_seed1024.png` kept for `EXP-007` comparison) because painterly frames looked too visibly AI-generated.

## User Tests
*(To be recorded verbatim with timestamps and resulting pipeline/edit changes.)*

### User Test 1 (Floor Draft — Provisional Radio Cut)
- **Viewer feedback (verbatim):** `"it is good, but the shots after 7 are not good"`
- **Context at time of test:**
  - Shots `07`, `08`, and `10` used `gemini-3.8-flash-lite-tts` (`Kore`), a different TTS model from shots `01`–`06` (`gemini-3.8-flash-tts`, `Kore`).
  - The tested `radio_cut.mp4` still contained the old `shot_09` narration line (`"ጎረቤቶች ወደ ቤት ገብተው፣ ሰላምታ ይለዋወጣሉ።"`), before the solo-Grandmother narration fix.
- **Hypotheses to investigate:**
  1. Voice model difference (`gemini-3.8-flash-lite-tts` sounding unnatural next to `gemini-3.8-flash-tts`).
  2. Stale `shot_09` text misaligned with the intended scene.
  3. Weaker second half of the story arc.
  4. Empty silence gaps (~`2.4 s`–`3.5 s` of padding inside each `7.0 s` slot).
- **Status / Follow-up:** **STILL PENDING as of 2026-11-25.** The viewer has not yet answered the follow-up question: *"What exactly was wrong after shot 7 — the voices, the story, the text, or the gaps?"* No story or storyboard text change has been made on the basis of this test. The known context (mixed TTS models, stale `shot_09` line and 2.4–3.5 s padding gaps) remains a list of **hypotheses only**, not a confirmed finding.

### User Test 2 (Polished Cut)
- *Pending Quality completion.*
