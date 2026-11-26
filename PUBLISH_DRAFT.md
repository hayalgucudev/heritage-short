# Publication record — Space LIVE, YouTube still a draft

**Status (2026-11-26): the static Hugging Face Space is published and both MP4 links open without login, confirmed by the director.** The YouTube text below remains a **draft, not posted**. The Space carries the "AI-generated film" label and the film ends with a "Made with AI" card. Assignment 2's public-link evidence is the Space, not the unposted YouTube draft.

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

## Hugging Face Space (static showcase) — LIVE

Published by the director at **https://huggingface.co/spaces/rahmetullah/heritage-film** on 2026-11-26. Verified working without login:

- Main film 9:16: https://huggingface.co/spaces/rahmetullah/heritage-film/resolve/main/film_9x16.mp4
- Widescreen 16:9: https://huggingface.co/spaces/rahmetullah/heritage-film/resolve/main/film_16x9.mp4
- Showcase page: https://huggingface.co/spaces/rahmetullah/heritage-film — **NOT working for the director**; do not use as evidence (`FAILURES.md` 037).

The local `space/index.html` carries the "AI-generated film" tag and an AI disclosure paragraph, but the live Space currently serves the old README and wrapper instead; both exports end with the approved "Made with AI" card. The earlier 403 under `hayalgucudev` (`FAILURES.md` 036) was resolved by using the director-approved `rahmetullah` namespace; the original failure record is kept unchanged as evidence. Publishing involved no model call, quota spend or change to the film.

## Gates before anything goes live

- [x] At least three viewers per user test watched the cuts (director's confirmation, 2026-11-26). The verbatim words actually supplied are in `DESIGN.md` and `REPORT.md` §2; missing names and remaining quotes were not invented.
- [ ] The walkthrough video is recorded and under five minutes.
- [x] The director chose the handle and published the Hugging Face Space at `rahmetullah/heritage-film` (2026-11-26).
- [ ] YouTube upload: still a draft; no video has been posted and no YouTube URL is claimed.
- [ ] The platform AI-disclosure setting is enabled.
- [x] `REPORT.pdf` re-rendered from `REPORT.md` after the supplied viewer words were added (2026-11-26).
- [x] Oromo ceiling CLOSED AS FAILED, native-speaker check MOOT: no variant exists and none will be published.
- [ ] Optional Wan 2.2 clips are not claimed: no Wan clip or GPU latency exists.
