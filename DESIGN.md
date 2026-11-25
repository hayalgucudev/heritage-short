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

- **Sample-size caveat (recorded honestly, 2026-11-25):** the brief asks for at least three people from the intended audience at **each** of the two tests. Test 1 currently records **one** viewer and Test 2 records **the director**. This gap is not hidden; if more people watch the cut, their exact words and the resulting changes will be appended below with timestamps.

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
- **Result of the fix (director, 2026-11-25 ~15:54 EAT):** asked *"Is the voice now present all the way to the end?"*, the director answered **"Yes, all through"**. User Test 2 is therefore a **pass on the audio defect**; no subtitle, end-card or framing complaint was reported. What changed because of the test: the FFmpeg graph, `code_version: 2`, both rebuilt exports and the evidence in `FAILURES.md` 022 / `EXPERIMENTS.md` EXP-016. The separate mixed-voice issue (shots 07-10) remains and has its own scheduled fix.

## Ceiling projects chosen by the director (2026-11-25)
- The director picked exactly **two**, to be planned now and **built only after the floor is finished**: **(a) the same film in a second language** and **(e) packaging the pipeline as a CLI others can use**.
- Second language: **Afaan Oromo**, chosen by the director on 2026-11-25. The director consented to sending only the locked fictional story text to Gemini; no real family details are included. Hypothesis and measurement plan go in `EXPERIMENTS.md` (EXP-017); model failures go in `FAILURES.md`.
- CLI packaging: the working `run.py` becomes a reusable command-line tool with documented arguments and a clean-clone test. Hypothesis: a stranger can rebuild both exports from `storyboard.json` without reading the source code.
- Deliberately **not** chosen for now: lyrics/lyric video, open-vs-frontier benchmark, LoRA consistency experiment and post-publication audience measurement.

## Publication plan (decided 2026-11-25, nothing published yet)
- **Showcase:** the director chose a **Hugging Face Space** with placeholder handle `YOUR_USERNAME/heritage-short`. `space/index.html` and `space/README.md` are committed; `py run.py showcase` copies the two MP4s, storyboard, cost report and keyframe sheet into `space/`. The command never reads `HF_TOKEN` and uploads nothing.
- **Public post:** the director chose **YouTube** after the final film is approved. Draft caption (not yet posted): *"The Heritage Short — an AI-generated film. A quiet fictional tribute to a grandmother in the Ethiopian highlands. Amharic narration with English subtitles; images, voice and music made with generative models; directed and edited by a human. AI-generated film."*
- **AI label wording:** **"AI-generated film"**, matching the disclosure printed in the Space. The film's own end card says "Made with AI · A fictional tribute to quiet morning hands" and was approved earlier.
- **Gate:** the director approved the **final edit on 2026-11-25**. No upload and no public post until the director also approves the actual account/handle to use and gives an explicit "publish" instruction. The Afaan Oromo variant must not be published until its native-speaker check is recorded in `ETHICS.md`.
