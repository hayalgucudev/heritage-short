"""Stage 7: assemble both final aspect ratios with burned subtitles and a ducked score."""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from pipeline import contracts
from pipeline.cache import update_manifest
from pipeline.logger import log_run
from pipeline.narration import probe_duration_sec
from pipeline.validate import validate_storyboard


# aspect: (width, height, subtitle_font_px, subtitle_margin_v_px, endcard_font_px)
ASPECTS: dict[str, tuple[int, int, int, int, int]] = {
    "9:16": (608, 1080, 32, 180, 18),
    "16:9": (1280, 720, 40, 52, 28),
}
FPS = 24


def _run_ffmpeg(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run FFmpeg and surface stderr, otherwise failures are impossible to diagnose."""
    try:
        return subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=cwd)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"FFmpeg command failed:\n{(exc.stderr or '')[-4000:]}") from exc


def _ass_time(sec: float) -> str:
    cs = int(round(sec * 100))
    h, rem = divmod(cs, 36000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _write_ass(sb: dict[str, Any], slots: list[float], path: Path, width: int, height: int, font_px: int, margin_v: int) -> None:
    """Write a per-aspect ASS file whose PlayRes equals the real video pixels.

    libass scales subtitle coordinates from PlayRes to the video. By setting
    PlayRes to the actual export size, FontSize and MarginV are real pixels,
    which makes the vertical safe area predictable instead of guessed.
    """
    style = (
        "Style: Default,Arial,"
        f"{font_px},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
        "-1,0,0,0,100,100,0,0,1,2,2,2,24,24,"
        f"{margin_v},1"
    )
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        style,
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    cursor = 0.0
    for shot, slot in zip(sb["shots"], slots):
        end = cursor + slot
        text = shot["subtitle_en"].replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\N")
        lines.append(
            f"Dialogue: 0,{_ass_time(cursor)},{_ass_time(end)},Default,,0,0,0,,{text}"
        )
        cursor = end
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _selected_music(project_root: Path, sb: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    music_dir = project_root / "outputs" / "music"
    selected = sb["music"].get("selected_candidate")
    meta_path = music_dir / "music_run_metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    candidates = meta.get("candidates", [])
    match = next((c for c in candidates if c.get("candidate_id") == selected), None)
    if match is None and selected:
        match = next((c for c in candidates if c.get("file_name") == selected), None)
    if match is None:
        wavs = sorted(music_dir.glob("candidate_*.wav"))
        if len(wavs) != 1:
            raise FileNotFoundError(
                "No unique score candidate. Set storyboard.json -> music.selected_candidate "
                "and import the ACE-Step candidate with its metadata."
            )
        match = {"file_name": wavs[0].name, "seed": None}
    path = music_dir / match["file_name"]
    if not path.exists():
        raise FileNotFoundError(f"Selected score WAV is missing: {path}")
    return path, match


def _build_audio_mix(
    project_root: Path,
    sb: dict[str, Any],
    slots: list[float],
    music_path: Path,
    out_path: Path,
) -> float:
    """Sidechain the score under voice; output one unnormalised 48 kHz stereo WAV."""
    end_sec = float(sb["end_card"]["duration_sec"])
    total = round(sum(slots) + end_sec, 3)
    narr_dir = project_root / "outputs" / "narration"
    wavs = [narr_dir / f"{shot['id']}.wav" for shot in sb["shots"]]
    for wav in wavs:
        if not wav.exists():
            raise FileNotFoundError(f"Missing narration WAV: {wav}")

    cmd: list[str] = ["ffmpeg", "-y"]
    for wav in wavs:
        cmd.extend(["-i", str(wav)])
    cmd.extend(["-i", str(music_path)])

    parts: list[str] = []
    concat_labels = ""
    for i, slot in enumerate(slots):
        parts.append(
            f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"apad=whole_dur={slot:.3f},atrim=duration={slot:.3f}[n{i}]"
        )
        concat_labels += f"[n{i}]"
    parts.append(f"anullsrc=r=48000:cl=stereo:d={end_sec:.3f}[end_sil]")
    parts.append(f"{concat_labels}[end_sil]concat=n={len(wavs) + 1}:v=0:a=1[voice]")
    music_idx = len(wavs)
    parts.append(
        f"[{music_idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
        f"atrim=duration={total:.3f},apad=whole_dur={total:.3f},"
        "asetpts=PTS-STARTPTS[music_in]"
    )
    parts.append(
        "[music_in][voice]sidechaincompress="
        "threshold=0.02:ratio=6:attack=300:release=1500[ducked]"
    )
    parts.append("[voice][ducked]amix=inputs=2:duration=longest:normalize=0[out]")

    cmd.extend(
        [
            "-filter_complex",
            ";".join(parts),
            "-map",
            "[out]",
            "-t",
            f"{total:.3f}",
            "-c:a",
            "pcm_s16le",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(out_path),
        ]
    )
    _run_ffmpeg(cmd)
    return total


def _loudnorm_measurements(audio_path: Path) -> dict[str, str]:
    """Pass 1: measure the mix so pass 2 can hit about -14 LUFS / -1 dBTP."""
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        str(audio_path),
        "-af",
        "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    matches = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", proc.stderr, re.DOTALL)
    if not matches:
        raise RuntimeError("Could not parse loudnorm pass-1 measurement from FFmpeg output.")
    data = json.loads(matches[-1])
    keys = ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")
    return {k.replace("input_", "").replace("target_", ""): str(data[k]) for k in keys}


def _loudnorm_filter(m: dict[str, str]) -> str:
    return (
        "loudnorm=I=-14:TP=-1:LRA=11:"
        f"measured_I={m['i']}:measured_TP={m['tp']}:measured_LRA={m['lra']}:"
        f"measured_thresh={m['thresh']}:offset={m['offset']}:linear=true"
    )


def _font_prefix() -> str:
    """Resolve a real font file without relying on fontconfig.

    This FFmpeg build has fontconfig enabled but no config file on the director's
    Windows machine, so `font=Arial` crashes. A fontfile path works, but the
    drive colon must be both quoted and escaped inside a filtergraph.
    """
    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for font in candidates:
        if font.exists():
            escaped = font.as_posix().replace(":", r"\:")
            return f"fontfile='{escaped}':"
    return ""


def _render_aspect(
    project_root: Path,
    sb: dict[str, Any],
    aspect: str,
    clip_paths: list[Path],
    slots: list[float],
    mix_path: Path,
    measured: dict[str, str],
    ass_path: Path,
    endcard_path: Path,
    out_path: Path,
) -> tuple[int, float]:
    width, height, _, _, end_font = ASPECTS[aspect]
    end_sec = float(sb["end_card"]["duration_sec"])

    cmd: list[str] = ["ffmpeg", "-y"]
    for clip in clip_paths:
        cmd.extend(["-i", str(clip)])
    cmd.extend(["-i", str(mix_path)])

    parts: list[str] = []
    concat_labels = ""
    for i, slot in enumerate(slots):
        parts.append(
            f"[{i}:v]fps={FPS},scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},tpad=stop_mode=clone:stop_duration=1,"
            f"trim=duration={slot:.3f},setpts=PTS-STARTPTS[v{i}]"
        )
        concat_labels += f"[v{i}]"
    parts.append(f"color=c=0x1c1713:s={width}x{height}:r={FPS}:d={end_sec:.3f}[endraw]")
    parts.append(
        f"[endraw]drawtext={_font_prefix()}textfile={endcard_path.relative_to(project_root).as_posix()}:"
        f"expansion=none:fontcolor=white:fontsize={end_font}:"
        "x=(w-text_w)/2:y=(h-text_h)/2:"
        "box=1:boxcolor=black@0.55:boxborderw=18[end]"
    )
    parts.append(f"{concat_labels}[end]concat=n={len(clip_paths) + 1}:v=1:a=0[cat]")
    parts.append(
        f"[cat]subtitles=filename={ass_path.relative_to(project_root).as_posix()}[vout]"
    )
    audio_idx = len(clip_paths)
    parts.append(f"[{audio_idx}:a]{_loudnorm_filter(measured)}[aout]")

    cmd.extend(
        [
            "-filter_complex",
            ";".join(parts),
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            "-fps_mode",
            "cfr",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(out_path),
        ]
    )
    t0 = time.perf_counter()
    _run_ffmpeg(cmd, cwd=project_root)
    return int((time.perf_counter() - t0) * 1000), probe_duration_sec(out_path)


def assemble_film(
    project_root: Path,
    storyboard_path: Path,
    schema_path: Path,
    runs_path: Path,
    manifest_path: Path,
) -> list[dict[str, Any]]:
    """Build film_9x16.mp4 and film_16x9.mp4 from cached stage outputs."""
    sb = validate_storyboard(storyboard_path, schema_path)
    manifest = contracts.load_manifest(manifest_path)
    artifacts = manifest.get("artifacts", {})
    out_dir = project_root / "outputs" / "final"
    out_dir.mkdir(parents=True, exist_ok=True)

    clip_paths: list[Path] = []
    clip_hashes: list[str] = []
    narration_paths: list[Path] = []
    narration_hashes: list[str] = []
    slots: list[float] = []
    for shot in sb["shots"]:
        sid = shot["id"]
        clip = project_root / "outputs" / "clips" / f"{sid}.mp4"
        wav = project_root / "outputs" / "narration" / f"{sid}.wav"
        if not clip.exists() or not wav.exists():
            raise FileNotFoundError(
                f"Missing inputs for {sid}: clip={clip.exists()}, narration={wav.exists()}. "
                "Run shots and narration stages first."
            )
        kf = project_root / "outputs" / "keyframes" / f"{sid}.png"
        kf_hash = contracts.keyframe_hash(sb, shot, project_root=project_root, use_reference=False)
        got = artifacts.get(clip.relative_to(project_root).as_posix(), {}).get("input_hash")
        wan_hash = contracts.clip_hash(sb, shot, kf, kf_hash, source="wan_import")
        kb_hash = contracts.clip_hash(sb, shot, kf, kf_hash, source="ken_burns")
        if got == wan_hash:
            clip_hashes.append(wan_hash)
        elif got == kb_hash:
            clip_hashes.append(kb_hash)
        else:
            raise ValueError(f"Clip {sid} is stale or unregistered. Regenerate the shots stage.")
        clip_paths.append(clip)

        n_hash = contracts.narration_hash(sb, shot)
        if artifacts.get(wav.relative_to(project_root).as_posix(), {}).get("input_hash") != n_hash:
            raise ValueError(
                f"Narration {sid} is stale. Regenerate it before the final edit "
                "(shots 07-10 are expected to be stale until the TTS quota resets)."
            )
        narration_hashes.append(n_hash)
        narration_paths.append(wav)
        slots.append(max(float(shot["duration_sec"]), probe_duration_sec(wav)))

    music_path, music_meta = _selected_music(project_root, sb)
    music_hash = contracts.music_candidate_hash(
        sb, music_path, seed=music_meta.get("seed"), file_name=music_meta.get("file_name")
    )
    if artifacts.get(music_path.relative_to(project_root).as_posix(), {}).get("input_hash") != music_hash:
        raise ValueError("Score is stale or unregistered. Run the music stage first.")

    planned: list[tuple[str, Path, str]] = []
    for aspect, (width, height, _, _, _) in ASPECTS.items():
        rel = f"outputs/final/film_{aspect.replace(':', 'x')}.mp4"
        out_path = project_root / rel
        digest = contracts.assemble_hash(
            sb,
            aspect=aspect,
            width=width,
            height=height,
            clip_paths=clip_paths,
            narration_paths=narration_paths,
            music_path=music_path,
            clip_input_hashes=clip_hashes,
            narration_input_hashes=narration_hashes,
            music_input_hash=music_hash,
        )
        planned.append((aspect, out_path, digest))

    if all(
        out.exists()
        and artifacts.get(out.relative_to(project_root).as_posix(), {}).get("input_hash") == digest
        and artifacts.get(out.relative_to(project_root).as_posix(), {}).get("status") == "ok"
        for _, out, digest in planned
    ):
        for aspect, out, digest in planned:
            rel = out.relative_to(project_root).as_posix()
            log_run(
                runs_path,
                stage="assemble",
                shot_id=aspect,
                model="ffmpeg-9.1",
                parameters={"aspect": aspect, "duration_sec": probe_duration_sec(out)},
                latency_ms=0,
                cost_or_quota="0_cache_hit",
                cache_hit=True,
                status="ok",
                input_hash=digest,
                output_path=rel,
            )
        return [
            {"aspect": a, "file": o.relative_to(project_root).as_posix(), "cache_hit": True}
            for a, o, _ in planned
        ]

    total = round(sum(slots) + float(sb["end_card"]["duration_sec"]), 3)
    endcard_path = out_dir / "endcard.txt"
    endcard_path.write_text(sb["end_card"]["text"], encoding="utf-8")
    mix_path = out_dir / "mix_unmastered.wav"
    _build_audio_mix(project_root, sb, slots, music_path, mix_path)
    measured = _loudnorm_measurements(mix_path)

    results: list[dict[str, Any]] = []
    for aspect, out_path, digest in planned:
        rel = out_path.relative_to(project_root).as_posix()
        width, height, font_px, margin_v, _ = ASPECTS[aspect]
        ass_path = out_dir / f"subtitles_{aspect.replace(':', 'x')}.ass"
        _write_ass(sb, slots, ass_path, width, height, font_px, margin_v)
        latency_ms, duration = _render_aspect(
            project_root,
            sb,
            aspect,
            clip_paths,
            slots,
            mix_path,
            measured,
            ass_path,
            endcard_path,
            out_path,
        )
        update_manifest(
            manifest_path,
            output_file=out_path,
            project_root=project_root,
            stage="assemble",
            shot_id=aspect,
            input_hash=digest,
        )
        log_run(
            runs_path,
            stage="assemble",
            shot_id=aspect,
            model="ffmpeg-9.1",
            parameters={
                "aspect": aspect,
                "duration_sec": duration,
                "loudnorm_measured": measured,
            },
            latency_ms=latency_ms,
            cost_or_quota="0_local_ffmpeg",
            cache_hit=False,
            status="ok",
            input_hash=digest,
            output_path=rel,
        )
        results.append(
            {
                "aspect": aspect,
                "file": rel,
                "cache_hit": False,
                "latency_ms": latency_ms,
                "duration_sec": duration,
                "input_hash": digest,
            }
        )
    return results
