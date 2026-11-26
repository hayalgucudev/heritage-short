# Design & Audience Log

## Creative Brief (Locked at Gate 1)
- **Story lock (director, 2026-11-25):** `"story locked"`. The 10-shot storyboard text, Amharic narration, English subtitles, seeds and shot order are now fixed. The visual realism wording was resolved on 2026-11-25 (option A of EXP-012, see line 12); no new narration text is to be invented without asking the director. The separate checkpoint gates for reference sheet, keyframes, clips, score and final edit still require explicit approval before generation.
- **Story:** A warm, stylized tribute to `"Grandmother"` in `"the village"` (fictionalized, no real-person likeness).
- **Audience & Platforms:**
  - Family & community on mobile (WhatsApp, TikTok — **9:16** vertical, safe-area English subtitles).
  - Classmates & reviewers on desktop (**16:9** widescreen).
- **Target Ending Feeling:** Quiet gratitude and warmth.
- **Language:** Amharic narration with burned-in English subtitles (2 lines max, ~40 chars/line).
- **Narration Craft & Voice Tone (FINAL, 2026-11-26):** `gemini-3.8-flash-tts` (`Kore`, pure Amharic text with `--no-wrapper`) for **all ten shots**. Shots `07`–`10` were temporarily on `gemini-3.8-flash-lite-tts` because of the 10/day cap and were rejected by the listener (`EXP-006`); they were regenerated on the correct model on 2026-11-26 with 4 approved calls (3,214 / 3,375 / 2,805 / 4,309 ms). Both exports were rebuilt with no `--allow-stale-narration` flag and `stale_narration: []`. The `PROVISIONAL` marker is removed.
- **Visual Style Block (Updated, 2026-11-25):** `"candid 35mm documentary photograph, natural soft morning light, muted warm earth tones, photoreal skin with visible pores and fine wrinkles, authentic woven cotton fabric texture, subtle film grain, shallow depth of field, imperfect unposed moment, Ethiopian highland village, no text or watermarks, no illustration or painting"`. Director chose option A in EXP-012; this one shared block was changed in 11 places and all 10 keyframes regenerated. Switched from the earlier painterly gouache/oil style (`ref_seed1024.png` kept for `EXP-007` comparison) because painterly frames looked too visibly AI-generated.

## User Tests
*(To be recorded verbatim with timestamps and resulting pipeline/edit changes.)*

- **Sample-size caveat (recorded honestly, 2026-11-25):** the brief asks for at least three people from the intended audience at **each** of the two tests. Test 1 currently records **one** viewer and Test 2 records **the director**. This gap is not hidden; if more people watch the cut, their exact words and the resulting changes will be appended below with timestamps.

### How to collect the remaining three responses (director, 2026-11-25)
- Show **(1)** `outputs/final/radio_cut.mp4` and **(2)** `outputs/final/film_9x16.mp4` (add `film_16x9.mp4` if they watch on a desktop) to three people from the intended audience — family/community or classmates.
- Ask these four questions and write the answers **verbatim**, with a timestamp and a first name or role only (no private family details):
  1. "What did you understand the story to be?"
  2. "Where, if anywhere, did you stop listening or lose the thread?"
  3. "What did you feel at the end?"
  4. "What is one thing you would change?"
- For the near-final picture also ask: "Can you read every subtitle line on a phone?" and "What do you think the last three seconds say?"
- Send the exact words to the coding agent. They will be appended below with timestamps, plus any storyboard or edit change that resulted. **Do not record a real person's face or voice into the repository.**

### Ready-to-paste response slots — ADDITIONAL VIEWERS, NOT YET COLLECTED
**Every bracket below is an empty placeholder. Nothing in this section is a real response until you replace it with the viewer's exact words.** The brief needs at least three viewers per test; Test 1 currently has one and Test 2 has the director, so two more each are the minimum. Three slots per test give margin.

#### Test 1 — radio cut (show `outputs/final/radio_cut.mp4`)
- **Additional viewer 1 — NOT YET COLLECTED**
  - Role or first name only: `[NOT YET COLLECTED]`
  - Timestamp/date: `[NOT YET COLLECTED]`
  - Q1 "What did you understand the story to be?" — verbatim: `[NOT YET COLLECTED]`
  - Q2 "Where, if anywhere, did you stop listening or lose the thread?" — verbatim: `[NOT YET COLLECTED]`
  - Q3 "What did you feel at the end?" — verbatim: `[NOT YET COLLECTED]`
  - Q4 "What is one thing you would change?" — verbatim: `[NOT YET COLLECTED]`
  - Q5 "Can you read every subtitle line on a phone?" — verbatim: `[NOT YET COLLECTED]`
  - Q6 "What do you think the last three seconds say?" — verbatim: `[NOT YET COLLECTED]`
  - What changed because of this response: `[NOT YET COLLECTED]`

- **Additional viewer 2 — NOT YET COLLECTED**
  - Role or first name only: `[NOT YET COLLECTED]`
  - Timestamp/date: `[NOT YET COLLECTED]`
  - Q1 "What did you understand the story to be?" — verbatim: `[NOT YET COLLECTED]`
  - Q2 "Where, if anywhere, did you stop listening or lose the thread?" — verbatim: `[NOT YET COLLECTED]`
  - Q3 "What did you feel at the end?" — verbatim: `[NOT YET COLLECTED]`
  - Q4 "What is one thing you would change?" — verbatim: `[NOT YET COLLECTED]`
  - Q5 "Can you read every subtitle line on a phone?" — verbatim: `[NOT YET COLLECTED]`
  - Q6 "What do you think the last three seconds say?" — verbatim: `[NOT YET COLLECTED]`
  - What changed because of this response: `[NOT YET COLLECTED]`

- **Additional viewer 3 — NOT YET COLLECTED**
  - Role or first name only: `[NOT YET COLLECTED]`
  - Timestamp/date: `[NOT YET COLLECTED]`
  - Q1 "What did you understand the story to be?" — verbatim: `[NOT YET COLLECTED]`
  - Q2 "Where, if anywhere, did you stop listening or lose the thread?" — verbatim: `[NOT YET COLLECTED]`
  - Q3 "What did you feel at the end?" — verbatim: `[NOT YET COLLECTED]`
  - Q4 "What is one thing you would change?" — verbatim: `[NOT YET COLLECTED]`
  - Q5 "Can you read every subtitle line on a phone?" — verbatim: `[NOT YET COLLECTED]`
  - Q6 "What do you think the last three seconds say?" — verbatim: `[NOT YET COLLECTED]`
  - What changed because of this response: `[NOT YET COLLECTED]`

#### Test 2 — visual cut (show `outputs/final/film_9x16.mp4`)
- **Additional viewer 1 — NOT YET COLLECTED**
  - Role or first name only: `[NOT YET COLLECTED]`
  - Timestamp/date: `[NOT YET COLLECTED]`
  - Q1 "What did you understand the story to be?" — verbatim: `[NOT YET COLLECTED]`
  - Q2 "Where, if anywhere, did you stop listening or lose the thread?" — verbatim: `[NOT YET COLLECTED]`
  - Q3 "What did you feel at the end?" — verbatim: `[NOT YET COLLECTED]`
  - Q4 "What is one thing you would change?" — verbatim: `[NOT YET COLLECTED]`
  - Q5 "Can you read every subtitle line on a phone?" — verbatim: `[NOT YET COLLECTED]`
  - Q6 "What do you think the last three seconds say?" — verbatim: `[NOT YET COLLECTED]`
  - What changed because of this response: `[NOT YET COLLECTED]`

- **Additional viewer 2 — NOT YET COLLECTED**
  - Role or first name only: `[NOT YET COLLECTED]`
  - Timestamp/date: `[NOT YET COLLECTED]`
  - Q1 "What did you understand the story to be?" — verbatim: `[NOT YET COLLECTED]`
  - Q2 "Where, if anywhere, did you stop listening or lose the thread?" — verbatim: `[NOT YET COLLECTED]`
  - Q3 "What did you feel at the end?" — verbatim: `[NOT YET COLLECTED]`
  - Q4 "What is one thing you would change?" — verbatim: `[NOT YET COLLECTED]`
  - Q5 "Can you read every subtitle line on a phone?" — verbatim: `[NOT YET COLLECTED]`
  - Q6 "What do you think the last three seconds say?" — verbatim: `[NOT YET COLLECTED]`
  - What changed because of this response: `[NOT YET COLLECTED]`

- **Additional viewer 3 — NOT YET COLLECTED**
  - Role or first name only: `[NOT YET COLLECTED]`
  - Timestamp/date: `[NOT YET COLLECTED]`
  - Q1 "What did you understand the story to be?" — verbatim: `[NOT YET COLLECTED]`
  - Q2 "Where, if anywhere, did you stop listening or lose the thread?" — verbatim: `[NOT YET COLLECTED]`
  - Q3 "What did you feel at the end?" — verbatim: `[NOT YET COLLECTED]`
  - Q4 "What is one thing you would change?" — verbatim: `[NOT YET COLLECTED]`
  - Q5 "Can you read every subtitle line on a phone?" — verbatim: `[NOT YET COLLECTED]`
  - Q6 "What do you think the last three seconds say?" — verbatim: `[NOT YET COLLECTED]`
  - What changed because of this response: `[NOT YET COLLECTED]`

---
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
- **Status / Follow-up (answered 2026-11-25):** The viewer's answer to *"What exactly was wrong after shot 7 — the voices, the story, the text, or the gaps?"* was: **`"Voices"`**. This **confirms hypothesis 1** (mixed TTS models) and rules out the story, subtitle text and silence gaps as the viewer's stated problem. **No story or storyboard text was changed.** The correction was carried out on 2026-11-26: shots `07`–`10` were regenerated on `gemini-3.8-flash-tts` with four approved calls and both exports were rebuilt with `stale_narration: []` (EXP-022). The other items remain untested hypotheses, not findings.

### User Test 2 (Provisional Visual Cut, 2026-11-25)
- **Director's instruction:** render a provisional cut **now** with the still-stale voices, so the visual and subtitle work can be judged early. Flag recorded as `--allow-stale-narration`; the export hash still uses the expected narration hashes, so fixing the TTS later forces a rebuild.
- **Status (2026-11-25 ~15:50 EAT):** The director had not watched it when first asked, so exact paths were given. After opening `film_9x16.mp4`, the director reported verbatim: **"the voice is not available after the first shot"**. This was a real technical defect, not a taste judgement: measured slot levels showed shots 09 and 10 at **-50.7 dB / -91.0 dB** in the delivered MP4 although all ten narration WAVs were healthy. Root cause was an FFmpeg filter-graph bug (voice label reused without `asplit=2`); fixed and re-rendered. All ten slots now measure **-21.3 to -16.2 dB** in the delivered MP4. No story or narration text changed. See `FAILURES.md` 022 and `EXPERIMENTS.md` EXP-016.
- **Result of the fix (director, 2026-11-25 ~15:54 EAT):** asked *"Is the voice now present all the way to the end?"*, the director answered **"Yes, all through"**. User Test 2 is therefore a **pass on the audio defect**; no subtitle, end-card or framing complaint was reported. What changed because of the test: the FFmpeg graph, `code_version: 2`, both rebuilt exports and the evidence in `FAILURES.md` 022 / `EXPERIMENTS.md` EXP-016. The separate mixed-voice issue (shots 07-10) was fixed on 2026-11-26 (EXP-022) and both finals rebuilt; no stale-flag export remains.

## Ceiling projects chosen by the director (2026-11-25)
- The director picked exactly **two**, to be planned now and **built only after the floor is finished**: **(a) the same film in a second language** and **(e) packaging the pipeline as a CLI others can use**.
- Second language: **Afaan Oromo**, chosen by the director on 2026-11-25. The director consented to sending only the locked fictional story text to Gemini; no real family details are included. Hypothesis and measurement plan go in `EXPERIMENTS.md` (EXP-017); model failures go in `FAILURES.md`. **Closed as failed by the director on 2026-11-26** after four failed translation calls (028, 030, 031); no `_om` export exists. The native-speaker check was ruled **moot** by the director because no translated text was ever produced. **No Afaan Oromo variant will be published.**
- CLI packaging: the working `run.py` becomes a reusable command-line tool with documented arguments and a clean-clone test. Hypothesis: a stranger can rebuild both exports from `storyboard.json` without reading the source code.
- Deliberately **not** chosen for now: lyrics/lyric video, open-vs-frontier benchmark, LoRA consistency experiment and post-publication audience measurement.

## Publication plan (decided 2026-11-25, nothing published yet)
- **Showcase (optional, NOT published):** the Space files are committed but the handle placeholder was replaced by a **"not published (optional)"** marker; no Space was created and nothing was uploaded. `py run.py showcase` copies the two MP4s, storyboard, cost report and keyframe sheet into `space/` locally; the command never reads `HF_TOKEN` and uploads nothing. Do not spend time on this before the deadline.
- **Public post:** the director chose **YouTube** after the final film is approved. Draft caption (not yet posted): *"The Heritage Short — an AI-generated film. A quiet fictional tribute to a grandmother in the Ethiopian highlands. Amharic narration with English subtitles; images, voice and music made with generative models; directed and edited by a human. AI-generated film."*
- **AI label wording:** **"AI-generated film"**, matching the disclosure printed in the Space. The film's own end card says "Made with AI · A fictional tribute to quiet morning hands" and was approved earlier.
- **Gate:** the director approved the **final edit on 2026-11-25**. No upload and no public post until the director also approves the actual account/handle to use and gives an explicit "publish" instruction. The Afaan Oromo ceiling is closed as failed; **no Oromo variant exists and none will be published**. The Hugging Face Space remains optional and unpublished.

## Final visual gate (2026-11-26) — director's decisions
- The director reviewed exported frames at 43, 45, 47 and 48.5 s and found the shot_07 prop and pour wrong, and the shot_10 outfit/stray hand wrong. Eight shot_07 and seven shot_10 FLUX candidates were generated and rejected; the consented jebena reference did not fix the pouring hand (`EXP-026`, `EXP-028`).
- **Director's final choice for shot_07:** keep the original keyframe. The terracotta jug and the stream that misses the cups remain; this is an accepted unresolved defect (`FAILURES.md` 032/035), not a claim of success.
- **Director's final choice for shot_10:** use seed 1113, the head-and-shoulders crop with no visible hands, so the four-finger problem is avoided by framing rather than by another model call.
- **Director's choice of method:** abandon image editing after the only available image-edit model returned `Invalid credential` twice (`FAILURES.md` 034). No edited image exists and no `runs.jsonl` row was invented.
- **What changed because of these tests:** the 9:16 subtitle `MarginV` moved from 180 to 340 so the two-line block sits higher, the end-card tribute text was enlarged and brightened, and both exports were re-rendered. Whether the subtitles clear the cups is the director's visual check; the assistant cannot view images.
- No publication. The user-test viewer slots earlier in this file remain untouched and unfilled.

### Final one-command verification (2026-11-26)
- After the visual decisions, I ran `py run.py film` once on `demo`. It logged 33 cache-hit rows with zero model calls and left both exports byte-identical (EXP-030). This is the recorded proof for the walkthrough; no further visual change has been made since.
- The six empty viewer slots earlier in this file remain untouched. `REPORT.pdf` is still intentionally stale and must not be submitted before the real viewer words are added and the report is re-rendered.
