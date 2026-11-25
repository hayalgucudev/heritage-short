"""Copy the finished film and evidence into the static Hugging Face Space folder.

No keys are read and nothing is uploaded. The director publishes the Space manually.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


def build_showcase(project_root: Path) -> dict[str, Any]:
    space = project_root / "space"
    assets = space / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    copies = {
        project_root / "outputs" / "final" / "film_9x16.mp4": assets / "film_9x16.mp4",
        project_root / "outputs" / "final" / "film_16x9.mp4": assets / "film_16x9.mp4",
        project_root / "storyboard.json": space / "storyboard.json",
        project_root / "COSTS.md": space / "costs.md",
        project_root / "outputs" / "keyframes" / "preview.html": space / "keyframes.html",
    }
    missing = [src.relative_to(project_root).as_posix() for src in copies if not src.is_file()]
    if missing:
        raise FileNotFoundError("Showcase inputs missing: " + ", ".join(missing))

    for src, dst in copies.items():
        shutil.copy2(src, dst)

    return {
        "space": space.relative_to(project_root).as_posix(),
        "files_copied": [dst.relative_to(project_root).as_posix() for dst in copies.values()],
        "uploaded": False,
        "note": "HF_TOKEN is never read here. Publish the Space manually after director approval.",
    }


def main() -> None:
    info = build_showcase(Path(__file__).resolve().parent.parent)
    print(json.dumps(info, indent=2, ensure_ascii=False))
