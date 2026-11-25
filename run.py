"""Single CLI entrypoint for The Heritage Short (PowerShell replacement for Makefile)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pipeline.narration import build_radio_cut, generate_narration
from pipeline.script import draft_storyboard
from pipeline.smoke import run_smoke_tests, run_tts_sample, verify_live_models
from pipeline.validate import validate_storyboard

PROJECT_ROOT = Path(__file__).resolve().parent
STORYBOARD_PATH = PROJECT_ROOT / "storyboard.json"
SCHEMA_PATH = PROJECT_ROOT / "schema" / "storyboard.schema.json"
RUNS_PATH = PROJECT_ROOT / "runs.jsonl"
MANIFEST_PATH = PROJECT_ROOT / "outputs" / "manifest.json"


def cmd_validate(_args: argparse.Namespace) -> int:
    sb = validate_storyboard(STORYBOARD_PATH, SCHEMA_PATH)
    print(f"OK: {STORYBOARD_PATH.name} valid ({len(sb['shots'])} shots).")
    return 0


def cmd_verify_models(_args: argparse.Namespace) -> int:
    info = verify_live_models(PROJECT_ROOT, RUNS_PATH)
    print(json.dumps(info, indent=2, ensure_ascii=False))
    return 0


def cmd_smoke(args: argparse.Namespace) -> int:
    summary = run_smoke_tests(
        PROJECT_ROOT,
        RUNS_PATH,
        MANIFEST_PATH,
        gemini_model=args.gemini_model,
        tts_model=args.tts_model,
        flux_model=args.flux_model,
        tts_voice=args.tts_voice,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def cmd_smoke_tts(args: argparse.Namespace) -> int:
    summary = run_tts_sample(
        PROJECT_ROOT,
        RUNS_PATH,
        MANIFEST_PATH,
        tts_model=args.tts_model,
        tts_voice=args.tts_voice,
        out_rel_path=args.out,
        no_wrapper=args.no_wrapper,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def cmd_draft_storyboard(args: argparse.Namespace) -> int:
    sb = draft_storyboard(
        PROJECT_ROOT,
        STORYBOARD_PATH,
        SCHEMA_PATH,
        RUNS_PATH,
        MANIFEST_PATH,
        primary_model=args.model,
        fallback_model=args.fallback_model,
        force=args.force,
    )
    print(f"Drafted and validated {STORYBOARD_PATH.name} ({len(sb['shots'])} shots, model={sb['models']['script']}).")
    return 0


def cmd_narration(args: argparse.Namespace) -> int:
    skip = {s.strip() for s in args.skip_shots.split(",") if s.strip()} if args.skip_shots else None
    rows = generate_narration(
        PROJECT_ROOT,
        STORYBOARD_PATH,
        SCHEMA_PATH,
        RUNS_PATH,
        MANIFEST_PATH,
        voice=args.voice,
        only_shot=args.shot,
        skip_shots=skip,
        pacing_delay_sec=args.delay_sec,
    )
    print(json.dumps(rows, indent=2, ensure_ascii=False))
    return 0


def cmd_radio_cut(_args: argparse.Namespace) -> int:
    info = build_radio_cut(
        PROJECT_ROOT,
        STORYBOARD_PATH,
        SCHEMA_PATH,
        RUNS_PATH,
        MANIFEST_PATH,
    )
    print(json.dumps(info, indent=2, ensure_ascii=False))
    return 0


def cmd_not_yet(name: str) -> int:
    print(
        f"Command '{name}' is scaffolded and will be implemented in its upcoming stage.",
        file=sys.stderr,
    )
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="py run.py",
        description="Reproducible pipeline runner for The Heritage Short.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="Validate storyboard.json against schema.")
    p_val.set_defaults(func=cmd_validate)

    p_vm = sub.add_parser("verify-models", help="List live Gemini and Cloudflare FLUX models.")
    p_vm.set_defaults(func=cmd_verify_models)

    p_sm = sub.add_parser("smoke", help="Run 1-call smoke tests with verified model IDs.")
    p_sm.add_argument("--gemini-model", required=True)
    p_sm.add_argument("--tts-model", required=True)
    p_sm.add_argument("--flux-model", required=True)
    p_sm.add_argument("--tts-voice", default="Aoede")
    p_sm.set_defaults(func=cmd_smoke)

    p_stts = sub.add_parser("smoke-tts", help="Run a single controlled TTS sample test.")
    p_stts.add_argument("--tts-model", required=True)
    p_stts.add_argument("--tts-voice", required=True)
    p_stts.add_argument("--out", required=True)
    p_stts.add_argument(
        "--no-wrapper",
        action="store_true",
        help="Send only the raw narration text without the English style prefix.",
    )
    p_stts.set_defaults(func=cmd_smoke_tts)

    p_ds = sub.add_parser("draft-storyboard", help="Draft storyboard.json via Gemini structured JSON.")
    p_ds.add_argument("--model", default="gemini-3.8-flash")
    p_ds.add_argument("--fallback-model", default="gemini-3.7-flash")
    p_ds.add_argument("--force", action="store_true", help="Ignore cache and regenerate storyboard.json.")
    p_ds.set_defaults(func=cmd_draft_storyboard)

    p_narr = sub.add_parser("narration", help="Generate per-shot TTS narration WAVs.")
    p_narr.add_argument("--voice", default=None, help="Optional voice override (defaults to storyboard tts_style).")
    p_narr.add_argument("--shot", default=None, help="Optional single shot id (e.g. shot_03).")
    p_narr.add_argument("--skip-shots", default="", help="Comma-separated shot ids to hold/skip (e.g. shot_09).")
    p_narr.add_argument("--delay-sec", type=float, default=13.0, help="Pause between live TTS calls to respect RPM limits.")
    p_narr.set_defaults(func=cmd_narration)

    p_rc = sub.add_parser("radio-cut", help="Assemble narration over placeholder tone on black video.")
    p_rc.set_defaults(func=cmd_radio_cut)

    p_plan = sub.add_parser("plan", help="Dry-run hash check showing what would regenerate.")
    p_plan.set_defaults(func=lambda _a: cmd_not_yet("plan"))

    p_film = sub.add_parser("film", help="Run full film pipeline from storyboard.json.")
    p_film.set_defaults(func=lambda _a: cmd_not_yet("film"))

    p_costs = sub.add_parser("report-costs", help="Generate COSTS.md tables from runs.jsonl.")
    p_costs.set_defaults(func=lambda _a: cmd_not_yet("report-costs"))

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
