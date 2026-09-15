#!/usr/bin/env python3
"""Inspect a media file with ffprobe and enforce optional delivery checks."""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import sys


def probe(path: Path) -> dict:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("ffprobe is not installed or not on PATH")
    command = [
        ffprobe,
        "-v",
        "error",
        "-count_frames",
        "-show_entries",
        "format=duration,format_name:stream=index,codec_type,codec_name,width,height,"
        "r_frame_rate,avg_frame_rate,nb_frames,nb_read_frames,sample_rate,channels",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "ffprobe could not inspect the file")
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    parser.add_argument("--target", type=float, help="Expected duration in seconds")
    parser.add_argument("--tolerance", type=float, default=0.10)
    parser.add_argument("--expected-width", type=int)
    parser.add_argument("--expected-height", type=int)
    parser.add_argument("--expected-fps", type=float)
    parser.add_argument("--expected-frames", type=int)
    parser.add_argument("--expect-audio", choices=("any", "yes", "no"), default="any")
    args = parser.parse_args()

    media = args.media.expanduser().resolve()
    if not media.is_file():
        parser.error(f"media file not found: {media}")
    if args.tolerance < 0:
        parser.error("--tolerance must be non-negative")

    try:
        data = probe(media)
        duration = float(data.get("format", {}).get("duration"))
    except (RuntimeError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    streams = data.get("streams", [])
    videos = [stream for stream in streams if stream.get("codec_type") == "video"]
    audios = [stream for stream in streams if stream.get("codec_type") == "audio"]
    video = videos[0] if videos else {}
    frame_rate_text = video.get("avg_frame_rate") or video.get("r_frame_rate")
    try:
        frame_rate = float(Fraction(frame_rate_text)) if frame_rate_text else None
    except (ValueError, ZeroDivisionError):
        frame_rate = None
    frame_count_text = video.get("nb_read_frames") or video.get("nb_frames")
    try:
        frame_count = int(frame_count_text) if frame_count_text not in (None, "N/A") else None
    except (TypeError, ValueError):
        frame_count = None
    failures: list[str] = []

    report = {
        "path": str(media),
        "format": data.get("format", {}).get("format_name"),
        "duration_seconds": round(duration, 6),
        "video": {
            "present": bool(videos),
            "codec": video.get("codec_name"),
            "width": video.get("width"),
            "height": video.get("height"),
            "frame_rate": frame_rate_text,
            "frame_rate_decimal": round(frame_rate, 6) if frame_rate is not None else None,
            "frames": frame_count,
        },
        "audio": {
            "present": bool(audios),
            "codec": audios[0].get("codec_name") if audios else None,
            "sample_rate": audios[0].get("sample_rate") if audios else None,
            "channels": audios[0].get("channels") if audios else None,
        },
    }

    if args.target is not None:
        delta = duration - args.target
        report["duration_check"] = {
            "target_seconds": args.target,
            "delta_seconds": round(delta, 6),
            "tolerance_seconds": args.tolerance,
            "pass": abs(delta) <= args.tolerance,
        }
        if abs(delta) > args.tolerance:
            failures.append("duration")
    if args.expected_width is not None and video.get("width") != args.expected_width:
        failures.append("width")
    if args.expected_height is not None and video.get("height") != args.expected_height:
        failures.append("height")
    if args.expected_fps is not None and (
        frame_rate is None or abs(frame_rate - args.expected_fps) > 0.001
    ):
        failures.append("frame_rate")
    if args.expected_frames is not None and frame_count != args.expected_frames:
        failures.append("frame_count")
    if args.expect_audio == "yes" and not audios:
        failures.append("missing_audio")
    if args.expect_audio == "no" and audios:
        failures.append("unexpected_audio")

    report["pass"] = not failures
    report["failures"] = failures
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
