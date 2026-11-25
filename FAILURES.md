# Failures & Fixes Log

Honest log of retired/changed models, API errors, pronunciation issues, Python compatibility snags, and what fixed them.

## 001 — Global Python `externally-managed-environment` (PEP 668) on Windows
- **What broke:** Running `py -m pip install -r requirements.txt` globally failed with `error: externally-managed-environment` because system Python 3.14.6 is managed by `uv`.
- **What we tried:** Created a project-local virtual environment (`py -m venv .venv`, already listed in `.gitignore`) and installed into `.venv`.
- **What fixed it:** Installing into `.venv` (`.\.venv\Scripts\python.exe -m pip install -r requirements.txt`) worked cleanly without `--break-system-packages`, and keeps clean-clone setup isolated for any reviewer.

