# Costs & Quota Report

*(Auto-generated from `runs.jsonl` by `py run.py report-costs` once pipeline runs are logged.)*

## Quota availability note (logged 2026-11-25)
- The previous coding agent (**Antigravity CLI**, starter quota) exhausted its quota on **both** accounts.
- Its message said the **baseline quota refreshes on 2 December 2026**.
- I did **not** rotate accounts to get around the limit.
- I moved to **OpenCode with a free model**; this changed the coding tool, not the film pipeline or its measured costs.
- Consequence: do not rely on that starter quota before 2026-12-02. Continue to protect quota with cache hits, cheap drafts and the free tiers recorded in `FAILURES.md`; every figure in the tables below still comes from `runs.jsonl`.

## Production keyframes run (measured from `runs.jsonl`, 2026-11-25)
- Stage `keyframes`, model `@cf/black-forest-labs/flux-2-klein-4b`, 10 shots (`shot_01`–`shot_10`): **10 calls**, each `1_cloudflare_flux_call`, **0 cache hits**, all `status=ok`.
- Latencies: **98,724 ms total (~98.7 s)**; fastest `7,737 ms` (`shot_04`), slowest `11,896 ms` (`shot_06`). Full per-shot table is in `EXP-012` in `EXPERIMENTS.md`; `py run.py report-costs` will aggregate all logged stages when that command is built.
