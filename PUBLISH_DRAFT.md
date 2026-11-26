# Publication draft — DRAFT, NOT PUBLISHED

**Status: nothing has been uploaded, posted or made public.** This file contains ready-to-use text for the director to approve. Publishing requires an explicit "publish" instruction and the account/handle decision. Do not paste this into a live platform before the three additional viewer responses per test are recorded in `DESIGN.md`.

## YouTube public post (Assignment 2, 20 marks)

### Title
**The Heritage Short — an AI-generated film (Amharic, 73 s)**

### Description — paste as-is
```
AI-generated film. A quiet, fictional tribute to a grandmother in the Ethiopian highlands, told in Amharic with burned-in English subtitles and an original AI-composed score.

Both cuts are in one video: vertical 9:16 first, then widescreen 16:9. No real person's face or voice was used; the character and village are fictional.

Made and directed by a human. Generative models were used for images (FLUX), motion (local FFmpeg Ken Burns camera moves), voice (Gemini TTS) and music (ACE-Step). The end card discloses that the film was made with AI.

The complete pipeline, storyboard, cost tables and failure log are public in the repository: https://github.com/hayalgucudev/heritage-short

Suggested platform setting: turn on YouTube's "Altered or synthetic content" disclosure for this upload.

#AIGeneratedFilm #ShortFilm #Amharic
```

### Upload checklist
- Privacy: **Unlisted** until the remaining viewer tests are recorded, then change to Public only on the director's instruction.
- Confirm the "AI-generated film" label appears in the title/description and the 3-second "Made with AI" end card in both cuts.
- No family names, no real person's likeness, no private details appear anywhere in the post.

## Five-minute walkthrough caption

> In five minutes: what the film is, the one locked `storyboard.json`, the dependency map, and one live regeneration. I delete only the derived clip for shot_02 — `plan` then shows three local rebuilds and zero quota — and one FFmpeg call in 1.4 seconds returns the repo to 38 cache hits. The hard decision: FFmpeg reported success while two slots were silent, so a ten-slot loudness check is now mandatory. Full evidence in `DESIGN.md`, `EXPERIMENTS.md`, `FAILURES.md` and `REPORT.pdf`.

The timed script, recording checklist and three-line memory notes are in `INTERVIEW_PREP.md`. Do not show `.env` or any key value on camera.

## Hugging Face Space (static showcase)

The files are prepared in `space/` — `index.html`, `README.md`, `storyboard.json`, `costs.md`, `keyframes.html` and both MP4s. **Nothing has been uploaded.** The Space is **optional and NOT published**; the `YOUR_USERNAME` placeholder was replaced by a "not published (optional)" marker in `space/README.md` and `DESIGN.md`. Publishing is not planned before the deadline. The page already carries the "AI-generated film" tag and an AI disclosure paragraph.

## Gates before anything goes live

- [ ] Three additional viewers per user test give verbatim responses recorded in `DESIGN.md`. **PARTIAL on 2026-11-26:** the director supplied six answers from one additional Test 2 viewer, relayed further visual criticisms, and states that more than three people gave feedback in total. The supplied words are in `DESIGN.md` and `REPORT.md` §2, but no per-test breakdown was supplied, so the three-per-test threshold is NOT claimed as evidenced.
- [ ] The walkthrough video is recorded and under five minutes.
- [ ] The director explicitly says "publish" and names the account/handle.
- [ ] The platform AI-disclosure setting is enabled.
- [x] `REPORT.pdf` re-rendered from `REPORT.md` after the supplied viewer words were added (2026-11-26).
- [x] Oromo ceiling CLOSED AS FAILED, native-speaker check MOOT: no variant exists and none will be published.
- [ ] Optional Wan 2.2 clips are not claimed: no Wan clip or GPU latency exists.
