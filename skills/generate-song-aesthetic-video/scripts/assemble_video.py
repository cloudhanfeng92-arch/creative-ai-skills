#!/usr/bin/env python3
"""Normalize and concatenate approved native clips without changing duration.

Every input clip is retained from its first video frame through its last. The
helper standardizes delivery dimensions, frame rate, codecs, and audio layout;
it never selects a shorter narrative interval or applies a speed change.
Creative order and transition choices must already have user approval.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def ffprobe_data(path: Path, ffprobe: str) -> dict:
    command = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,width,height,duration,nb_frames,avg_frame_rate",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"ffprobe failed for {path}")
    return json.loads(result.stdout)


def video_stream(data: dict) -> dict:
    return next(
        (stream for stream in data.get("streams", []) if stream.get("codec_type") == "video"),
        {},
    )


def readable_duration(data: dict, path: Path) -> float:
    stream = video_stream(data)
    candidates = (stream.get("duration"), data.get("format", {}).get("duration"))
    for value in candidates:
        try:
            duration = float(value)
        except (TypeError, ValueError):
            continue
        if duration > 0:
            return duration
    raise RuntimeError(f"No readable positive video duration for {path}")


def duration_and_audio(path: Path, ffprobe: str) -> tuple[float, bool]:
    data = ffprobe_data(path, ffprobe)
    duration = readable_duration(data, path)
    has_audio = any(stream.get("codec_type") == "audio" for stream in data.get("streams", []))
    return duration, has_audio


def integer_frames(data: dict) -> int | None:
    value = video_stream(data).get("nb_frames")
    try:
        return int(value) if value not in (None, "N/A") else None
    except (TypeError, ValueError):
        return None


def run(command: list[str], dry_run: bool, commands: list[list[str]]) -> None:
    commands.append(command)
    if dry_run:
        return
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        message = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise RuntimeError(message)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clip", action="append", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument(
        "--audio-tail-fade",
        type=float,
        default=0.08,
        help="Short audio-only fade at each clean cut to prevent clicks",
    )
    parser.add_argument(
        "--audio-mode",
        choices=("preserve", "none"),
        default="preserve",
        help="Preserve ambience/dialogue (fill a missing track with silence) or remove all audio",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.width <= 0 or args.height <= 0 or args.fps <= 0:
        parser.error("width, height, and fps must be positive")
    if args.audio_tail_fade < 0:
        parser.error("--audio-tail-fade must not be negative")

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        print("ERROR: ffmpeg and ffprobe are both required", file=sys.stderr)
        return 127

    clips = [path.expanduser().resolve() for path in args.clip]
    output = args.out.expanduser().resolve()
    for path in clips:
        if not path.is_file():
            parser.error(f"input file not found: {path}")
        if path == output:
            parser.error("output path must not replace an input file")
    if output.exists() and not args.overwrite:
        parser.error("output already exists; pass --overwrite only after confirming replacement")
    if not args.dry_run:
        output.parent.mkdir(parents=True, exist_ok=True)

    commands: list[list[str]] = []
    try:
        clip_info = [duration_and_audio(path, ffprobe) for path in clips]
        source_durations = [duration for duration, _ in clip_info]
        source_total = sum(source_durations)
        if source_total <= 0:
            raise RuntimeError("total source duration is zero")
        for clip, duration in zip(clips, source_durations):
            if args.audio_tail_fade > duration:
                raise RuntimeError(
                    f"audio fade {args.audio_tail_fade:.3f}s exceeds video duration "
                    f"{duration:.3f}s for {clip}"
                )

        with tempfile.TemporaryDirectory(prefix="song-video-") as temp_name:
            temp_dir = Path(temp_name)
            normalized: list[Path] = []
            normalized_durations: list[float] = []
            normalized_frames: list[int | None] = []
            # Reset only the time origin so concat starts each clip at zero.
            # Inter-frame PTS intervals are never multiplied or divided.
            video_filter = (
                "setpts=PTS-STARTPTS,"
                f"scale={args.width}:{args.height}:force_original_aspect_ratio=decrease,"
                f"pad={args.width}:{args.height}:(ow-iw)/2:(oh-ih)/2:color=black,"
                f"setsar=1,fps={args.fps},format=yuv420p"
            )

            for index, (clip, (source_duration, has_audio)) in enumerate(
                zip(clips, clip_info), 1
            ):
                normalized_path = temp_dir / f"clip-{index:03d}.mp4"
                normalized.append(normalized_path)
                common = [
                    "-c:v",
                    "libx264",
                    "-preset",
                    "medium",
                    "-crf",
                    "18",
                ]

                if args.audio_mode == "none":
                    command = [
                        ffmpeg,
                        "-y",
                        "-i",
                        str(clip),
                        "-map",
                        "0:v:0",
                        "-vf",
                        video_filter,
                        *common,
                        "-an",
                        "-movflags",
                        "+faststart",
                        str(normalized_path),
                    ]
                elif has_audio:
                    audio_filters = [
                        "aresample=48000",
                        "asetpts=PTS-STARTPTS",
                    ]
                    if args.audio_tail_fade > 0:
                        fade_start = max(0.0, source_duration - args.audio_tail_fade)
                        audio_filters.append(
                            f"afade=t=out:st={fade_start:.6f}:d={args.audio_tail_fade:.6f}"
                        )
                    audio_filters.append("apad")
                    command = [
                        ffmpeg,
                        "-y",
                        "-i",
                        str(clip),
                        "-map",
                        "0:v:0",
                        "-map",
                        "0:a:0",
                        "-vf",
                        video_filter,
                        "-af",
                        ",".join(audio_filters),
                        "-shortest",
                        *common,
                        "-c:a",
                        "aac",
                        "-b:a",
                        "192k",
                        "-ar",
                        "48000",
                        "-ac",
                        "2",
                        "-movflags",
                        "+faststart",
                        str(normalized_path),
                    ]
                else:
                    command = [
                        ffmpeg,
                        "-y",
                        "-i",
                        str(clip),
                        "-f",
                        "lavfi",
                        "-i",
                        "anullsrc=r=48000:cl=stereo",
                        "-map",
                        "0:v:0",
                        "-map",
                        "1:a:0",
                        "-vf",
                        video_filter,
                        "-shortest",
                        *common,
                        "-c:a",
                        "aac",
                        "-b:a",
                        "192k",
                        "-ar",
                        "48000",
                        "-ac",
                        "2",
                        "-movflags",
                        "+faststart",
                        str(normalized_path),
                    ]
                run(command, args.dry_run, commands)

                if not args.dry_run:
                    normalized_data = ffprobe_data(normalized_path, ffprobe)
                    normalized_durations.append(readable_duration(normalized_data, normalized_path))
                    normalized_frames.append(integer_frames(normalized_data))

            combined = temp_dir / "combined.mp4"
            if len(normalized) == 1:
                commands.append(["copy", str(normalized[0]), str(combined)])
                if not args.dry_run:
                    shutil.copy2(normalized[0], combined)
            else:
                inputs: list[str] = []
                labels: list[str] = []
                for index, path in enumerate(normalized):
                    inputs.extend(["-i", str(path)])
                    if args.audio_mode == "preserve":
                        labels.append(f"[{index}:v:0][{index}:a:0]")
                    else:
                        labels.append(f"[{index}:v:0]")
                if args.audio_mode == "preserve":
                    concat_filter = "".join(labels) + f"concat=n={len(normalized)}:v=1:a=1[v][a]"
                    command = [
                        ffmpeg,
                        "-y",
                        *inputs,
                        "-filter_complex",
                        concat_filter,
                        "-map",
                        "[v]",
                        "-map",
                        "[a]",
                        "-c:v",
                        "libx264",
                        "-preset",
                        "medium",
                        "-crf",
                        "18",
                        "-c:a",
                        "aac",
                        "-b:a",
                        "192k",
                        "-movflags",
                        "+faststart",
                        str(combined),
                    ]
                else:
                    concat_filter = "".join(labels) + f"concat=n={len(normalized)}:v=1:a=0[v]"
                    command = [
                        ffmpeg,
                        "-y",
                        *inputs,
                        "-filter_complex",
                        concat_filter,
                        "-map",
                        "[v]",
                        "-c:v",
                        "libx264",
                        "-preset",
                        "medium",
                        "-crf",
                        "18",
                        "-an",
                        "-movflags",
                        "+faststart",
                        str(combined),
                    ]
                run(command, args.dry_run, commands)

            commands.append(["copy", str(combined), str(output)])
            if not args.dry_run:
                shutil.copy2(combined, output)

        if args.dry_run:
            print(
                json.dumps(
                    {
                        "source_durations_seconds": [round(value, 6) for value in source_durations],
                        "source_total_seconds": round(source_total, 6),
                        "duration_policy": "retain every input from first video frame through last",
                        "commands": commands,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0

        final_data = ffprobe_data(output, ffprobe)
        final_duration = readable_duration(final_data, output)
        final_video = video_stream(final_data)
        final_audio = any(
            stream.get("codec_type") == "audio" for stream in final_data.get("streams", [])
        )
        expected_audio = args.audio_mode == "preserve"
        actual_frames = integer_frames(final_data)
        known_normalized_frames = [value for value in normalized_frames if value is not None]
        target_frames = (
            sum(known_normalized_frames)
            if len(known_normalized_frames) == len(normalized_frames)
            else round(source_total * args.fps)
        )
        duration_tolerance = max(0.10, len(clips) / args.fps + 0.02)
        report = {
            "output": str(output),
            "source_durations_seconds": [round(value, 6) for value in source_durations],
            "normalized_durations_seconds": [round(value, 6) for value in normalized_durations],
            "duration_seconds": round(final_duration, 6),
            "target_seconds": round(source_total, 6),
            "duration_tolerance_seconds": round(duration_tolerance, 6),
            "width": final_video.get("width"),
            "height": final_video.get("height"),
            "fps": final_video.get("avg_frame_rate"),
            "frames": actual_frames,
            "target_frames": target_frames,
            "audio_mode": args.audio_mode,
            "audio": final_audio,
            "duration_policy": "full native clip retention; no narrative interval selection or speed change",
            "pass": abs(final_duration - source_total) <= duration_tolerance
            and final_video.get("width") == args.width
            and final_video.get("height") == args.height
            and (actual_frames is None or actual_frames == target_frames)
            and final_audio == expected_audio,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["pass"] else 1
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if args.dry_run and commands:
            print(json.dumps({"commands": commands}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
