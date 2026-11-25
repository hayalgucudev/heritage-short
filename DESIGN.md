# Design & Audience Log

## Creative Brief (Locked at Gate 1)
- **Story lock (director, 2026-11-25):** `"story locked"`. The 10-shot storyboard text, Amharic narration, English subtitles, seeds and shot order are now fixed. Only the visual realism wording remains to be decided (EXP-012); no new narration text is to be invented without asking the director. The separate checkpoint gates for reference sheet, keyframes, clips, score and final edit still require explicit approval before generation.
- **Story:** A warm, stylized tribute to `"Grandmother"` in `"the village"` (fictionalized, no real-person likeness).
- **Audience & Platforms:**
  - Family & community on mobile (WhatsApp, TikTok — **9:16** vertical, safe-area English subtitles).
  - Classmates & reviewers on desktop (**16:9** widescreen).
- **Target Ending Feeling:** Quiet gratitude and warmth.
- **Language:** Amharic narration with burned-in English subtitles (2 lines max, ~40 chars/line).
- **Narration Craft & Voice Tone (`PROVISIONAL`):** `gemini-3.8-flash-tts` (`Kore`, pure Amharic text with `--no-wrapper`). Shots `01`–`06` use `gemini-3.8-flash-tts`; shots `07`–`10` were temporarily generated with `gemini-3.8-flash-lite-tts` due to the 10/day free-tier cap and sound unnatural (`EXP-006`). Narration is marked **PROVISIONAL** until shots `07`–`10` are retried on `gemini-3.8-flash-tts` after `11:00 EAT` on 2026-11-26 (4 calls).
- **Visual Style Block (Updated, 2026-11-25):** `"candid 35mm documentary photograph, natural soft morning light, muted warm earth tones, photoreal skin with visible pores and fine wrinkles, authentic woven cotton fabric texture, subtle film grain, shallow depth of field, imperfect unposed moment, Ethiopian highland village, no text or watermarks, no illustration or painting"`. Director chose option A in EXP-012; this one shared block was changed in 11 places and all 10 keyframes regenerated. Switched from the earlier painterly gouache/oil style (`ref_seed1024.png` kept for `EXP-007` comparison) because painterly frames looked too visibly AI-generated.

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
- **Status / Follow-up (answered 2026-11-25):** The viewer's answer to *"What exactly was wrong after shot 7 — the voices, the story, the text, or the gaps?"* was: **`"Voices"`**. This **confirms hypothesis 1** (mixed TTS models) and rules out the story, subtitle text and silence gaps as the viewer's stated problem. **No story or storyboard text was changed.** The planned correction is to regenerate shots `07`–`10` on `gemini-3.8-flash-tts` after the 10/day quota resets at ~`11:00 EAT` on 2026-11-26, then rebuild both exports. The other items remain untested hypotheses, not findings.

### User Test 2 (Provisional Visual Cut, 2026-11-25)
- **Director's instruction:** render a provisional cut **now** with the still-stale voices, so the visual and subtitle work can be judged early. Flag recorded as `--allow-stale-narration`; the export hash still uses the expected narration hashes, so fixing the TTS later forces a rebuild.
- **Status (2026-11-25 ~15:50 EAT):** The director had not watched it when first asked, so exact paths were given. After opening `film_9x16.mp4`, the director reported verbatim: **"the voice is not available after the first shot"**. This was a real technical defect, not a taste judgement: measured slot levels showed shots 09 and 10 at **-50.7 dB / -91.0 dB** in the delivered MP4 although all ten narration WAVs were healthy. Root cause was an FFmpeg filter-graph bug (voice label reused without `asplit=2`); fixed and re-rendered. All ten slots now measure **-20.3 to -16.2 dB** in the delivered MP4. No story or narration text changed. See `FAILURES.md` 022 and `EXPERIMENTS.md` EXP-016.
