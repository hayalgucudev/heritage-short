# The Heritage Short — Codebase and Report

**Draft for submission (Markdown; rendered as `REPORT.pdf`).** Every number below comes from `runs.jsonl`, `COSTS.md`, `DESIGN.md`, `EXPERIMENTS.md` or `FAILURES.md` in this repository. Nothing is estimated or invented. Prepared 2026-11-25 and updated 2026-11-26 after the four voice re-takes; the Afaan Oromo run was attempted three times and failed each time at translation; those failures are recorded as failures, not results.

---

## 1. What I set out to make, and for whom

I set out to make a 60–90 second short film about a grandmother in the Ethiopian highlands, told as a warm fictional tribute rather than a documentary about a named real person. The story was locked by the director on 2026-11-25 and has ten shots. The intended audience is family and community watching on a phone (vertical 9:16, WhatsApp/TikTok) and classmates and reviewers watching on a desktop (16:9). The intended ending feeling is quiet gratitude and warmth. The narration is Amharic with burned-in English subtitles of at most two lines.

The second deliverable is the studio that makes it: a repository where `storyboard.json` is the single contract, and `py run.py film` rebuilds both MP4s from it. The one-command requirement mattered more to me than any individual shot: a stranger must be able to clone the repository and get a film without a key, a GPU or a manual edit.

Delivered state: all ten shots now use `gemini-3.8-flash-tts`; both exports are **73.0 s**, H.264 + AAC at 48 kHz stereo, 24 fps constant frame rate; measured **−14.02 LUFS / −0.98 dBTP**; ten narration slots all audible (−21.3 to −16.2 dB); a 3-second end card saying "Made with AI". The floor uses ten local Ken Burns clips because the optional Wan 2.2 GPU stage was never successfully run. `py run.py plan` reports **38 cache hits / 0 regenerations** (EXP-022).

## 2. What I learned from the audience

I recorded feedback verbatim in `DESIGN.md` rather than paraphrasing it into a conclusion I liked.

- **Radio-cut test:** a viewer said *"it is good, but the shots after 7 are not good"*. When asked what exactly was wrong, they answered *"Voices"*. That ruled out my hypotheses about the story, the subtitle text and the empty gaps inside each slot. It confirmed that shots 07–10 sounded different because they had been generated with `gemini-3.8-flash-lite-tts` while shots 01–06 used `gemini-3.8-flash-tts`. **No story or narration text was changed.** The change was operational: four pre-approved calls on the correct model on 2026-11-26 (3,214 / 3,375 / 2,805 / 4,309 ms), with the hash chain invalidating only those shots, the two finals and the radio cut.
- **Visual-cut test:** the director reported *"the voice is not available after the first shot"*. This was a real defect, not a taste judgement: shots 09 and 10 measured −50.7 dB and −91.0 dB in the delivered MP4 even though all ten source WAVs were healthy. Asked again after the fix, the director said *"Yes, all through"*.

**Honest limitation:** the brief asks for at least three people from the intended audience at each test. Test 1 has one viewer and Test 2 has the director. I recorded this gap explicitly in `DESIGN.md` instead of implying a sample I did not have. The director is gathering three more viewers before submission; their exact words will be appended there.

The largest effect of audience feedback was therefore not a creative change but a **measurement habit**: after the silent-tail bug I made a ten-slot loudness check mandatory before calling any export finished (`EXPERIMENTS.md` EXP-016, `FAILURES.md` 022). A successful FFmpeg exit had looked like success while two shots were effectively silent.

## 3. The hardest problem and how I solved it

The hardest problem was the silent last two shots. The narration WAVs, the score and the subtitles were all present, and FFmpeg exited with code 0, so there was no error to read. I isolated it with a three-way A/B test at fixed inputs and seeds: (A) a plain audio mix, (B) an explicit `asplit=2` of the voice before sidechaining, and (C) the original graph that reused one voice label. Slot 09 measured −21.4 / −21.4 / −67.3 dB and slot 10 −22.5 / −22.5 / −91.0 dB for A/B/C. The cause was that reusing one label made FFmpeg stop the shared stream early, so the sidechain mix ran out of voice before the final slots. Version 2 of the assembly settings applied the winning graph, which forced a rebuild, and a ten-slot measurement became part of verification. This changed my mind about what "the pipeline succeeded" means.

The second-hardest problem was quota, not engineering. Gemini TTS allows ten requests per day on this free tier, and the tenth was spent before shots 07–10 were made on the correct model. I did not rotate accounts. Those four shots stayed provisional and were logged as such on the earlier assemble rows; on 2026-11-26 four approved calls regenerated them and the cache hash forced both exports to rebuild with `stale_narration: []`. The AAC mix bug that produced a 3.72-second soundtrack (`FAILURES.md` 020) and two seek/timestamp bugs in the second-language split (`FAILURES.md` 023) were found the same way: measure the artifact, isolate one variable, fix the recipe, bump the hash.

## 4. A suggested practice that helped, and one that did not

**Helped: a JSON contract with hash-based caching and a dry-run plan.** `storyboard.json` holds every prompt, seed, duration and model choice; no prompt is hidden in code. Each stage hashes all of its inputs, including upstream output hashes, and writes the result to `outputs/manifest.json`. `py run.py plan` reads the same hashes and prints exactly what would regenerate and why, with no model calls. Evidence: after changing one shot's prompt in an experiment, only that keyframe, its clip and the two finals regenerated; after fixing the reference portraits, `plan` moved from 29 hits / 9 regenerations to 34 hits / 4 regenerations while the approved finals stayed cache hits. This beat my instinct because my first instinct was to re-run "the film" after every change; the plan showed that was unnecessary and expensive.

**Did not help: conditioning every keyframe on the character reference sheet.** This was a practice suggested in the brief, and I tried it honestly. `input_image_0` preserved the reference pose but produced a different face in an action shot; adding a pose-override phrase did not fix it (`EXPERIMENTS.md` EXP-009, option C **rejected** by the director because the face changed). A no-reference frame using the verbatim character description was accepted (`EXP-011`, *"the others seem okay"*). The production rule became: repeat the character description word-for-word and the fixed style block in every prompt, generate with `--no-ref`, and check faces and hands before spending GPU time. We still generated and kept a reference sheet, but it is not the conditioning source for these shots. The lesson is that a plausible practice is not a universal one; the evidence was one rejected image, not a theory.

## 5. Ceiling work

Two ceiling items were chosen by the director, and a small polish item was added after the floor was stable.

- **Second language (Afaan Oromo).** `pipeline/second_language.py` translates the ten locked fictional lines with one Gemini text call, makes **one** long Gemini TTS call, splits the result locally at detected silences (with a word-count fallback), and reuses the same clips and English subtitles for both aspect ratios. A local smoke test with a synthetic WAV and **zero model calls** produced both `_om` exports at 73.0 s with all ten slots audible, and exposed two real FFmpeg seek/timestamp bugs that were fixed. The approved run was attempted three times on 2026-11-26: two read timeouts on `gemini-3.8-flash` (54.2 s and 46.2 s) and one HTTP 503 high-demand on `gemini-3.6-flash`; the pipeline stopped before the TTS call each time (`FAILURES.md` 028, 030). A free DNS/TCP/TLS probe then showed the endpoint reachable in ~200 ms, so a network fault was ruled out; the configured `gemini-3.8-flash` text model has never succeeded in this repo, while `gemini-3.6-flash` once succeeded in 33.9 s (`FAILURES.md` 029, EXP-023). **No translation-quality or native-speaker result exists yet**; a family/community member will check names and places, and the variant will not be published unless that check is recorded in `ETHICS.md`.
- **Reusable CLI.** `run.py` exposes `validate`, `preflight`, `plan`, `film` and each stage separately, with documented PowerShell commands in `README.md`. A clean clone with no `.env` passed `preflight` and rebuilt both MP4s with zero model calls. On 2026-11-26 a fresh clone of `5bd6adf` with **no `.env`** passed `preflight` and ran plain `py run.py film` with **no flags**: 21 cache-hit rows and 13 local FFmpeg rows, zero paid calls, both MP4s byte-identical to the delivered files (EXP-018 complete).
- **Sound and legibility polish.** A measured, deterministic room tone at about −40 dB mean, subtitles 10 % larger in Arial Bold with margins widened so the longest 33-character line still fits (587 px in a 608 px frame), and a restyled 3-second end card. My first ambience gain measured −54.1 dB mean — inaudible — so it was raised and re-measured (`EXP-019`). This cost zero quota.

## 6. Failures, experiments and measurement

`FAILURES.md` holds 30 real entries, including provider 503/404 responses, a 60-second schema timeout, the ten-call TTS cap, the silent-tail bug, three FFmpeg audio/video bugs, and real Kaggle/Colab notebook tracebacks. `EXPERIMENTS.md` holds 24 entries with a hypothesis, change, result and decision. `COSTS.md` is regenerated from `runs.jsonl` by `py run.py report-costs` and currently reads 94 logged records, 88 non-cache calls, 7 failures and 786,841 ms of logged latency. Free-tier limits and API changes are recorded rather than assumed. The optional notebooks were repaired from the director's pasted errors and validated as JSON and Python locally. The director then reran the **Colab** ACE-Step notebook on a real T4: DiT load 10.1 s, 5.9 GB used, three candidates in 13,842 / 7,113 / 6,965 ms, metadata written; only the browser-download helper failed and that cell was fixed. The director also reran the **Wan 2.2** notebook on Kaggle: the pin fix is GPU-verified (`WanImageToVideoPipeline import: OK`) and the new guards refused to generate clips without a mounted job, instead of cascading `NameError`s. The blocker was a workflow gap — `outputs/wan_job.zip` had never been exported — so I ran `py run.py clips-export` locally (zero quota, 10 shots, 7,796,471-byte zip). **No Wan clip or GPU latency exists yet**; the film still uses the local Ken Burns fallback, and the Kaggle ACE-Step twin remains compiled locally only.

## 7. What I would build next

1. Keep the clean-clone evidence current after any future change, and run the recorded walkthrough for Assignment 2.
2. Complete the native-speaker check and, if it passes, publish the Afaan Oromo variant as a second public cut; if it fails, keep it private and document exactly which words failed.
3. Run the Wan 2.2 notebook from a fresh Kaggle session and compare one clip against the Ken Burns fallback in a blind preference test with at least five people. That would turn the fallback from a workaround into a measured choice.
4. For a longer project, build the small family-facing web app so a relative who does not code can supply their own storyboard and get a film back — with the same consent gate in front of any real likeness or voice.

## 8. Where the evidence lives

| Claim | File |
| :--- | :--- |
| Audience, intent, verbatim quotes, sample-size caveat | `DESIGN.md` |
| Stage contracts, caching and the dependency map | `ARCHITECTURE.md` |
| Twenty-four hypothesis/change/result experiments | `EXPERIMENTS.md` |
| Thirty real failures and their fixes | `FAILURES.md` |
| Measured latency, quota and list-price notes | `COSTS.md` (`py run.py report-costs`) |
| Consent, AI disclosure and model licences | `ETHICS.md` |
| One line per model or FFmpeg call | `runs.jsonl` |
| Plain-language walkthrough of every decision | `EXPLAINED.md`, `INTERVIEW_PREP.md` |
