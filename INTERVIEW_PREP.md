# AI Interview Prep — Plain-Language Talking Points

## Stage 1: Foundation, Caching & Secret Hygiene
1. **Why hash inputs (`cache.py`)?** Every stage output is keyed by a SHA-256 hash of its exact inputs (prompt, seed, model, params, and upstream files), so editing one shot only invalidates that shot and its downstream dependencies.
2. **Why validate before calling models (`validate.py`)?** Checking `storyboard.json` against `storyboard.schema.json` (plus subtitle length and 60–90s total timing) catches mistakes locally at zero quota cost before hitting rate-limited APIs.
3. **How are secrets and logs handled?** Secrets live only in `.env` (gitignored), are never printed or committed, and `logger.py` writes every call immediately to `runs.jsonl` while scrubbing any secret values out of error text.
