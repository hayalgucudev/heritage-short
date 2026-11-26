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

- **Sample-size caveat (confirmed 2026-11-26):** the director confirms **at least three people watched each cut** — the radio cut (Test 1) and the visual cut (Test 2). The brief's three-viewer threshold is therefore met by the director's confirmation. Names, timestamps and every person's exact words were not supplied, so the written record contains only what was actually given: Test 1 — **one** verbatim viewer; Test 2 — **the director**, **one additional viewer who gave all six answers**, and relayed visual comments from further people. I do not invent quotes or fill the remaining slots with imagined responses.

### Original collection instruction (director, 2026-11-25; count later confirmed 2026-11-26)
- Show **(1)** `outputs/final/radio_cut.mp4` and **(2)** `outputs/final/film_9x16.mp4` (add `film_16x9.mp4` if they watch on a desktop) to three people from the intended audience — family/community or classmates.
- Ask these four questions and write the answers **verbatim**, with a timestamp and a first name or role only (no private family details):
  1. "What did you understand the story to be?"
  2. "Where, if anywhere, did you stop listening or lose the thread?"
  3. "What did you feel at the end?"
  4. "What is one thing you would change?"
- For the near-final picture also ask: "Can you read every subtitle line on a phone?" and "What do you think the last three seconds say?"
- Send the exact words to the coding agent. They will be appended below with timestamps, plus any storyboard or edit change that resulted. **Do not record a real person's face or voice into the repository.**

### Response slots — ADDITIONAL VIEWERS (PARTIALLY FILLED 2026-11-26)
**The Test 2 / Additional viewer 1 slot below contains a real response exactly as supplied by the director. The relayed comments below are feedback from further people, but their exact words and per-person attribution were not supplied, so they are not placed into numbered slots.** The director confirms that at least three people watched each cut, so the audience-count threshold is met by that confirmation. The remaining brackets stay empty rather than being filled with invented responses.

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
- **Additional viewer 1 — real response recorded 2026-11-26**
  - Role or first name only: `[not supplied by director — no name or private detail recorded]`
  - Timestamp/date: `2026-11-26; exact clock time not supplied`
  - Q1 "What did you understand the story to be?" — verbatim: `about a lovely granny`
  - Q2 "Where, if anywhere, did you stop listening or lose the thread?" — verbatim: `on 00:33`
  - Q3 "What did you feel at the end?" — verbatim: `happy`
  - Q4 "What is one thing you would change?" — verbatim: `the amharic pronounciation is deformed`
  - Q5 "Can you read every subtitle line on a phone?" — verbatim: `yes`
  - Q6 "What do you think the last three seconds say?" — verbatim: `that it is AI produced and made to warm my morning`
  - **Formal summary (not a quote; for the report):** the viewer read the film as a warm portrait of a grandmother, felt happiness at the end, could read the subtitles on a phone, and understood the end card as an AI disclosure with a warm morning feeling. They located a break in the thread around 00:33 and asked for the Amharic pronunciation to be improved.
  - What changed because of this response: **no storyboard or edit change has been made.** The director supplied the words on 2026-11-26 and asked only that they be recorded formally. The pronunciation criticism and the 00:33 break are open issues, not claimed fixes.

- **Additional comments from further viewers (director relayed, 2026-11-26; individual attribution and exact per-person wording not supplied)**
  - Verbatim as relayed: `about the image inconsistency`; `the video being not normal (too much ai generated)`; `the jebena being something else`; `the place inconsistency`.
  - **Formal summary (not a quote; for the report):** other viewers noticed inconsistent images across shots, a visible "too AI-generated" quality to the motion, a jebena depicted as a different vessel, and inconsistent location details. These are criticisms of the delivered cut, not approved fixes.
  - What changed because of these comments: **nothing yet.** They corroborate the already-documented unresolved shot_07 prop/pour defect and the accepted Ken Burns-over-stills motion limitation (`FAILURES.md` 032–035, `EXPERIMENTS.md` EXP-026–030). No keyframe, prompt, seed or export was changed in response, and no visual success is claimed.

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

## Publication outcome (decided 2026-11-25; Space published 2026-11-26)
- **Showcase (LIVE):** the director published the static Space at **https://huggingface.co/spaces/rahmetullah/heritage-film** on 2026-11-26 and confirmed the two direct MP4 links open without login. The **showcase page does not render the film UI** and serves a stale README (`FAILURES.md` 037), so it is not claimed as evidence. The Assignment 2 public-link evidence is the two direct MP4 URLs only (in `README.md` and `PUBLISH_DRAFT.md`). `py run.py showcase` still only copies files locally and reads no keys; the upload itself was a manual director action. The earlier 403 under `hayalgucudev` is preserved in `FAILURES.md` 036.
- **Public post:** the director chose **YouTube** after final approval, but **no YouTube upload has been made**. Draft caption (still not posted): *"The Heritage Short — an AI-generated film. A quiet fictional tribute to a grandmother in the Ethiopian highlands. Amharic narration with English subtitles; images, voice and music made with generative models; directed and edited by a human. AI-generated film."* No YouTube URL is claimed.
- **AI label wording:** **"AI-generated film"**, printed in the live Space and in the draft caption. The film's own end card says "Made with AI · A fictional tribute to quiet morning hands" and was approved earlier.
- **Gate:** the director approved the **final edit on 2026-11-25** and the public handle on 2026-11-26. The Afaan Oromo ceiling is closed as failed; **no Oromo variant exists and none will be published**. Publication spent no quota and changed no output hash.

## Final visual gate (2026-11-26) — director's decisions
- The director reviewed exported frames at 43, 45, 47 and 48.5 s and found the shot_07 prop and pour wrong, and the shot_10 outfit/stray hand wrong. Eight shot_07 and seven shot_10 FLUX candidates were generated and rejected; the consented jebena reference did not fix the pouring hand (`EXP-026`, `EXP-028`).
- **Director's final choice for shot_07:** keep the original keyframe. The terracotta jug and the stream that misses the cups remain; this is an accepted unresolved defect (`FAILURES.md` 032/035), not a claim of success.
- **Director's final choice for shot_10:** use seed 1113, the head-and-shoulders crop with no visible hands, so the four-finger problem is avoided by framing rather than by another model call.
- **Director's choice of method:** abandon image editing after the only available image-edit model returned `Invalid credential` twice (`FAILURES.md` 034). No edited image exists and no `runs.jsonl` row was invented.
- **What changed because of these tests:** the 9:16 subtitle `MarginV` moved from 180 to 340 so the two-line block sits higher, the end-card tribute text was enlarged and brightened, and both exports were re-rendered. Whether the subtitles clear the cups is the director's visual check; the assistant cannot view images.
- Publication happened later on 2026-11-26 (live Space, links above); these visual decisions were made before that upload. On 2026-11-26 the director supplied six answers from one additional Test 2 viewer, relayed further visual criticisms, and later confirmed **at least three people watched each cut**. Those exact words are recorded above; the audience-count threshold is met by the director's confirmation, while missing names and quotes are not invented.

### Final one-command verification (2026-11-26)
- After the visual decisions, I ran `py run.py film` once on `demo`. It logged 33 cache-hit rows with zero model calls and left both exports byte-identical (EXP-030). This is the recorded proof for the walkthrough; no further visual change has been made since.
- The supplied viewer words were added on 2026-11-26 and `REPORT.pdf` was re-rendered from `REPORT.md`. On the same day the director confirmed **at least three viewers per cut**; the count is met by that confirmation and no names or quotes were invented. The remaining empty slots are genuinely unfilled and the written-evidence limit is stated in `REPORT.md` §2.
