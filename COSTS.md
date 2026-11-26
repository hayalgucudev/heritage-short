# Costs & Quota Report

*(Auto-generated from `runs.jsonl` by `py run.py report-costs` once pipeline runs are logged.)*

## Quota availability note (logged 2026-11-25)
- The previous coding agent (**Antigravity CLI**, starter quota) exhausted its quota on **both** accounts.
- Its message said the **baseline quota refreshes on 2 December 2026**.
- I did **not** rotate accounts to get around the limit.
- I moved to **OpenCode with a free model**; this changed the coding tool, not the film pipeline or its measured costs.
- Consequence: do not rely on that starter quota before 2026-12-02. Continue to protect quota with cache hits, cheap drafts and the free tiers recorded in `FAILURES.md`; every figure in the tables below still comes from `runs.jsonl`.

## Measured totals (from `runs.jsonl`)

- Real logged records: **152**
- Non-cache model/FFmpeg calls: **104**
- Failed calls: **7**
- Total logged latency: **967,733 ms** (16.1 min)

### By stage

| Stage | Calls | Cache hits | Failures | Latency (ms) | Cost / quota tags |
| --- | --- | --- | --- | --- | --- |
| assemble | 16 | 2 | 0 | 87,220 | 0_cache_hit x2, 0_local_ffmpeg x16 |
| keyframes | 27 | 10 | 0 | 316,453 | 0_cache_hit x10, 1_cloudflare_flux_call x27 |
| music | 1 | 2 | 0 | 0 | 0_cache_hit x2, 1_kaggle_acestep_call x1 |
| narration | 22 | 15 | 2 | 82,071 | 0_cache_hit x15, 1_gemini_tts_call x20, 1_gemini_tts_call_failed x2 |
| radio_cut | 2 | 0 | 0 | 5,580 | 0_local_ffmpeg x2 |
| reference_sheet | 9 | 0 | 0 | 98,266 | 1_cloudflare_flux_call x9 |
| script | 5 | 0 | 4 | 316,424 | 1_gemini_script_call x1, 1_gemini_script_call_failed x4 |
| shots | 13 | 19 | 0 | 18,775 | 0_cache_hit x19, 0_local_ffmpeg x13 |
| smoke_flux | 1 | 0 | 0 | 8,846 | 1_cloudflare_flux_call x1 |
| smoke_text | 1 | 0 | 1 | 13,533 | 1_gemini_text_call_failed x1 |
| smoke_tts | 1 | 0 | 0 | 5,093 | 1_gemini_tts_call x1 |
| smoke_tts_experiment | 4 | 0 | 0 | 14,506 | 1_gemini_tts_call x4 |
| verify_models | 2 | 0 | 0 | 966 | 0_neurons_metadata x1, 0_tokens_metadata x1 |

### By model

| Model | Calls | Latency (ms) |
| --- | --- | --- |
| @cf/black-forest-labs/flux-2-klein-4b | 37 | 423,565 |
| gemini-3.8-flash | 2 | 213,444 |
| ffmpeg-9.1 | 18 | 92,800 |
| gemini-3.8-flash-tts | 22 | 87,491 |
| gemini-3.5-flash | 1 | 60,356 |
| gemini-3.6-flash | 1 | 33,900 |
| gemini-3.7-flash | 1 | 21,871 |
| Wan-AI/Wan2.2-TI2V-5B | 13 | 18,775 |
| gemini-3.8-flash-lite-tts | 5 | 14,179 |
| cloudflare-models-search | 1 | 558 |
| gemini-models-list | 1 | 408 |
| gemini-2.5-flash | 1 | 386 |
| ACE-Step/ACE-Step-v1.5 | 1 | 0 |

### By stage and shot

| Stage | Shot | Calls | Latency (ms) |
| --- | --- | --- | --- |
| assemble | 16:9 | 8 | 44,870 |
| assemble | 9:16 | 8 | 42,350 |
| keyframes | shot_01 | 1 | 10,233 |
| keyframes | shot_02 | 5 | 48,359 |
| keyframes | shot_03 | 2 | 22,779 |
| keyframes | shot_04 | 1 | 7,737 |
| keyframes | shot_05 | 1 | 8,849 |
| keyframes | shot_06 | 1 | 11,896 |
| keyframes | shot_07 | 7 | 97,605 |
| keyframes | shot_08 | 1 | 8,118 |
| keyframes | shot_09 | 1 | 9,656 |
| keyframes | shot_10 | 7 | 91,221 |
| music | candidate_01 | 1 | 0 |
| narration | shot_01 | 2 | 6,403 |
| narration | shot_02 | 3 | 9,252 |
| narration | shot_03 | 2 | 6,647 |
| narration | shot_04 | 2 | 9,590 |
| narration | shot_05 | 2 | 7,637 |
| narration | shot_06 | 2 | 10,403 |
| narration | shot_07 | 3 | 13,728 |
| narration | shot_08 | 2 | 5,992 |
| narration | shot_09 | 2 | 5,258 |
| narration | shot_10 | 2 | 7,161 |
| radio_cut | all | 2 | 5,580 |
| reference_sheet | ref_01 | 1 | 9,064 |
| reference_sheet | ref_02 | 1 | 10,286 |
| reference_sheet | ref_03 | 1 | 9,296 |
| reference_sheet | ref_real_seed_01 | 2 | 21,547 |
| reference_sheet | ref_real_seed_02 | 2 | 23,143 |
| reference_sheet | ref_real_seed_03 | 2 | 24,930 |
| script | all | 5 | 316,424 |
| shots | shot_01 | 1 | 1,417 |
| shots | shot_02 | 3 | 4,321 |
| shots | shot_03 | 1 | 1,428 |
| shots | shot_04 | 1 | 1,456 |
| shots | shot_05 | 1 | 1,434 |
| shots | shot_06 | 1 | 1,419 |
| shots | shot_07 | 1 | 1,464 |
| shots | shot_08 | 1 | 1,473 |
| shots | shot_09 | 1 | 1,417 |
| shots | shot_10 | 2 | 2,946 |
| smoke_flux | smoke | 1 | 8,846 |
| smoke_text | smoke | 1 | 13,533 |
| smoke_tts | smoke | 1 | 5,093 |
| smoke_tts_experiment | smoke | 4 | 14,506 |
| verify_models | smoke | 2 | 966 |

## Evidence rule

Every number above is computed from `runs.jsonl` at generation time. No cost or latency is estimated or invented. Rebuild with `py run.py report-costs`.
