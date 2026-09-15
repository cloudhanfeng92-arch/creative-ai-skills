#!/usr/bin/env python3
"""Inspect video/audio streams and optionally enforce the Skill master contract."""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import sys


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("media", nargs="+", type=Path)
    result.add_argument("--strict-master", action="store_true")
    result.add_argument("--expected-duration", type=float)
    result.add_argument("--expected-frames", type=int)
    result.add_argument("--duration-tolerance", type=float, default=0.10)
    result.add_argument("--ffprobe-bin")
    return result


def probe(ffprobe: str, path: Path) -> dict:
    command = [
        ffprobe,
        "-v",
        "error",
        "-count_frames",
        "-show_entries",
        (
            "format=duration:stream=index,codec_type,codec_name,width,height,"
            "pix_fmt,sample_aspect_ratio,sample_rate,channels,r_frame_rate,nb_read_frames"
        ),
        "-of",
        "json",
        str(path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or "ffprobe failed")
    return json.loads(completed.stdout)


def as_rate(value: str | None) -> float | None:
    if not value or value == "0/0":
        return None
    try:
        return float(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return None


def validate_master(
    payload: dict,
    expected_duration: float | None,
    expected_frames: int | None,
    tolerance: float,
) -> list[str]:
    errors: list[str] = []
    streams = payload.get("streams", [])
    videos = [item for item in streams if item.get("codec_type") == "video"]
    audios = [item for item in streams if item.get("codec_type") == "audio"]
    forbidden = [
        item
        for item in streams
        if item.get("codec_type") in {"subtitle", "data", "attachment"}
    ]
    if len(videos) != 1:
        errors.append(f"expected one video stream, found {len(videos)}")
    if len(audios) != 1:
        errors.append(f"expected one audio stream, found {len(audios)}")
    if forbidden:
        errors.append("subtitle/data/attachment streams are forbidden")

    if videos:
        video = videos[0]
        if (video.get("width"), video.get("height")) != (1280, 720):
            errors.append("video must be 1280x720")
        if video.get("codec_name") != "h264":
            errors.append("video codec must be H.264")
        if video.get("pix_fmt") != "yuv420p":
            errors.append("pixel format must be yuv420p")
        if video.get("sample_aspect_ratio") != "1:1":
            errors.append("sample aspect ratio must be 1:1")
        rate = as_rate(video.get("r_frame_rate"))
        if rate is None or abs(rate - 30.0) > 0.001:
            errors.append("frame rate must be exactly 30 fps")
        if expected_frames is not None:
            raw_frames = video.get("nb_read_frames")
            try:
                actual_frames = int(raw_frames)
            except (TypeError, ValueError):
                errors.append("ffprobe did not return a readable frame count")
            else:
                if actual_frames != expected_frames:
                    errors.append(
                        f"expected {expected_frames} frames, found {actual_frames}"
                    )

    if audios:
        audio = audios[0]
        if audio.get("codec_name") != "aac":
            errors.append("audio codec must be AAC")
        if str(audio.get("sample_rate")) != "48000":
            errors.append("audio sample rate must be 48000 Hz")
        if int(audio.get("channels") or 0) != 2:
            errors.append("audio must be stereo")

    if expected_duration is not None:
        try:
            duration = float(payload.get("format", {}).get("duration"))
        except (TypeError, ValueError):
            errors.append("container duration is unavailable")
        else:
            if abs(duration - expected_duration) > tolerance:
                errors.append(
                    f"expected {expected_duration:.3f}s, found {duration:.3f}s"
                )
    return errors


def main() -> int:
    args = parser().parse_args()
    ffprobe = args.ffprobe_bin or shutil.which("ffprobe")
    if not ffprobe:
        print("ffprobe executable was not found.", file=sys.stderr)
        return 127
    exit_code = 0
    reports = []
    for raw_path in args.media:
        path = raw_path.expanduser().resolve()
        if not path.is_file():
            reports.append({"path": str(path), "errors": ["file does not exist"]})
            exit_code = 1
            continue
        try:
            payload = probe(ffprobe, path)
        except (RuntimeError, json.JSONDecodeError) as exc:
            reports.append({"path": str(path), "errors": [str(exc)]})
            exit_code = 1
            continue
        errors = []
        if args.strict_master:
            errors = validate_master(
                payload,
                args.expected_duration,
                args.expected_frames,
                args.duration_tolerance,
            )
            if errors:
                exit_code = 1
        reports.append({"path": str(path), "probe": payload, "errors": errors})
    print(json.dumps(reports, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
