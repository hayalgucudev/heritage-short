# 5-Minute Walkthrough Script

**Maximum 5:00. Read this aloud; do not improvise numbers.** Use a throwaway clone for the live edit so the submitted repo and exports stay untouched.

## Before recording (throwaway clone only)
```powershell
git clone . "$env:TEMP\heritage-walkthrough"
cd "$env:TEMP\heritage-walkthrough"
py run.py preflight
py run.py film
py run.py radio-cut
py run.py plan
```
The last command should print **38 cache hits / 0 regenerations**. If it does not, run `film` again; warm-up is local FFmpeg only.

## 0:00–0:40 — The film, audience, intent
Show first `outputs/final/film_9x16.mp4`, then `outputs/final/film_16x9.mp4`.

Say: *"This is The Heritage Short, a 73-second fictional tribute to a grandmother in the Ethiopian highlands. I made it for family and community on WhatsApp and TikTok in vertical 9:16, and for classmates and reviewers on desktop in 16:9. The intended ending feeling is quiet gratitude and warmth. Amharic narration is carried by burned-in English subtitles, and a 3-second end card says it was made with AI. The motion is FFmpeg Ken Burns over approved AI-generated stills — I do not claim AI-generated video, because the Wan 2.2 GPU stage never produced a clip."*

## 0:40–1:50 — Architecture and the five stages
Show `storyboard.json`, `ARCHITECTURE.md`, then `py run.py plan`.

Exact commands:
```powershell
py run.py validate
py run.py plan
```

Say: *"`storyboard.json` is the single contract: every prompt, seed, duration, model and narration line lives there, not in code. Stage one, narration, turns each spoken line into one Gemini TTS WAV. Stage two, keyframes, makes one FLUX still per shot. Stage three, shots, makes a local Ken Burns clip from each still; a Wan clip can be imported, but none was produced. Stage four, music, registers the approved ACE-Step score. Stage five, assembly, mixes the score under the voice with sidechain compression, loudness-normalises to about minus 14 LUFS, burns subtitles and writes both exports. Each stage hashes all inputs and upstream hashes into `outputs/manifest.json`; `plan` uses the same recipe book, so it can tell me exactly what would rebuild without spending quota."*

## 1:50–2:50 — One hard decision from the real history
Show `FAILURES.md` 022 and `EXPERIMENTS.md` EXP-016.

Say: *"The hardest decision was trusting measurements over a successful FFmpeg exit. The director said the voice vanished after the first shot. FFmpeg had exited cleanly, but slot 09 measured minus 50.7 dB and slot 10 minus 91 dB in the delivered MP4 although the source WAVs were healthy. I ran a three-way A/B at fixed inputs: slot 09 measured minus 21.4, minus 21.4 and minus 67.3 dB; slot 10 measured minus 22.5, minus 22.5 and minus 91.0 dB. The failing graph reused one voice label without `asplit=2`. I chose the version with explicit split, rebuilt both exports and made a ten-slot loudness check mandatory. That changed my definition of 'the pipeline succeeded'."*

## 2:50–4:20 — Live: change one narration line
**Do this in the throwaway clone only.** A working `.env` is required for the one TTS call. Never show `.env` or any key on screen.

Back up and change exactly one line:
```powershell
Copy-Item storyboard.json storyboard.backup.json
py -c "import json,pathlib; p=pathlib.Path('storyboard.json'); d=json.loads(p.read_text(encoding='utf-8')); d['shots'][1]['narration'] += ' '; p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')"
py run.py plan
```

Say: *"Before the change, `plan` was 38 hits and zero regenerations. After adding one trailing space to shot 2's narration, it is 35 hits and 3 regenerations: one Gemini TTS call and the two local final exports. The keyframe, clip and score are untouched."*

Run and inspect:
```powershell
py run.py film
Get-Content runs.jsonl | Select-Object -Last 1
Get-Content runs.jsonl | Select-String '"stage": "narration"' | Select-Object -Last 1
py run.py radio-cut
py run.py plan
```

Say: *"There is exactly one new Gemini narration row in `runs.jsonl`; final reassembly is expected and local. After rebuilding the radio cut, `plan` returns to 38 hits and zero regenerations."*

If no `.env` is available, **do not fake a row**. Show the real rehearsal in `EXPERIMENTS.md` EXP-032 and say plainly: *"I cannot repeat the paid call in this session because no key is configured; the recorded rehearsal shows one new row, and the dry run here confirms the same invalidation."*

Restore before closing:
```powershell
Move-Item storyboard.backup.json storyboard.json -Force
```

## 4:20–5:00 — What broke, what I learned, what’s next
Show `DESIGN.md`, `REPORT.md` and `git status -sb` in the real repo.

Say: *"The free TTS tier capped at ten calls a day, so shots 7 to 10 temporarily used a different model; a viewer said 'Voices'. I regenerated those four voices on the correct model and rebuilt both exports. Feedback also recorded image inconsistency, a jebena shown as a different vessel, and a break around 00:33; I logged those as open criticism and did not pretend to fix them. The Afaan Oromo ceiling failed four times at translation and is closed. The direct MP4 links are live under `rahmetullah/heritage-film`, but the Space page UI defect is logged in `FAILURES.md` 037 and YouTube is still an unposted draft. Next I would fix that page, then test a real Wan-versus-Ken-Burns blind comparison with five people. Nothing is published from this recording; the submitted exports are unchanged."*

## Recording checklist
- Use a throwaway clone; confirm the real repo is clean afterwards with `git status -sb`.
- Hide `.env` and all terminal autocomplete/history containing keys; never open `.env` on camera.
- Enlarge terminal font to 14–16 pt and use a 1280×720 or larger capture.
- Open tabs: `storyboard.json`, `runs.jsonl`, `ARCHITECTURE.md`, `FAILURES.md`, `DESIGN.md`.
- Back up `storyboard.json` before the live change; restore it immediately after.
- Do not claim a latency from this run unless it is actually in `runs.jsonl`.
- Stop at 5:00.
