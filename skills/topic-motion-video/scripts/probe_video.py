#!/usr/bin/env python3
"""Inspect local video metadata and optionally decode it to check stream errors.

Python 3.9+, FFprobe; optional FFmpeg for --decode. No third-party Python packages.
Does not validate scene meaning, subtitles, constant frame rate, or listening quality.
Exit 0 = requested automatic checks passed; 1 = failed; 2 = inspection unavailable.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import shutil
import subprocess
from typing import Any, Optional


def numeric(value: Any) -> Optional[float]:
    try:
        result = float(Fraction(str(value)))
        return result if math.isfinite(result) else None
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def positive_number(text: str) -> float:
    value = numeric(text)
    if value is None or value <= 0:
        raise argparse.ArgumentTypeError("Expected a positive number or fraction")
    return value


def positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Expected a positive integer") from exc
    if value <= 0:
        raise argparse.ArgumentTypeError("Expected a positive integer")
    return value


def write_report(report: dict[str, Any], output: Optional[Path]) -> None:
    content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    print(content, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--width", type=positive_int)
    parser.add_argument("--height", type=positive_int)
    parser.add_argument("--fps", type=positive_number)
    parser.add_argument("--fps-tolerance", type=positive_number, default=0.02)
    parser.add_argument("--duration", type=positive_number)
    parser.add_argument("--duration-tolerance", type=positive_number, default=0.2)
    parser.add_argument("--require-audio", action="store_true")
    parser.add_argument("--video-codec", help="For example: h264")
    parser.add_argument("--pixel-format", help="For example: yuv420p")
    parser.add_argument("--decode", action="store_true")
    parser.add_argument("--decode-timeout", type=positive_number, default=300)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    path = args.video.expanduser().resolve()
    report: dict[str, Any] = {
        "file": str(path), "status": "not_checked", "checks": [],
        "not_checked": ["Visual quality and intended black frames", "Facts and chart correctness",
                        "Text, glyphs and subtitle timing", "Listening quality and audio sync",
                        "Constant frame rate from per-frame timestamps"],
    }
    if not path.is_file():
        report["error"] = "Input is not an existing local file"
        write_report(report, args.out)
        return 2
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        report["error"] = "ffprobe is not available on PATH"
        write_report(report, args.out)
        return 2

    command = [ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)]
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)
        if proc.returncode != 0:
            report.update({"status": "failed", "error": "ffprobe could not inspect the file",
                           "details": proc.stderr[-2000:]})
            write_report(report, args.out)
            return 1
        data = json.loads(proc.stdout)
        if not isinstance(data, dict):
            raise ValueError("ffprobe output was not a JSON object")
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        report["error"] = str(exc)
        write_report(report, args.out)
        return 2

    streams = data.get("streams", [])
    videos = [s for s in streams if s.get("codec_type") == "video"
              and not s.get("disposition", {}).get("attached_pic", 0)]
    audios = [s for s in streams if s.get("codec_type") == "audio"]
    checks = report["checks"]

    def check(name: str, passed: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "status": "passed" if passed else "failed",
                       "actual": actual, "expected": expected})

    check("video_stream_present", bool(videos), len(videos), ">= 1 (not cover art)")
    if videos:
        video = videos[0]
        fps = numeric(video.get("avg_frame_rate")) or numeric(video.get("r_frame_rate"))
        duration = numeric(video.get("duration"))
        if duration is None:
            duration = numeric(data.get("format", {}).get("duration"))
        metadata = {"width": video.get("width"), "height": video.get("height"),
                    "fps": fps, "avg_frame_rate": video.get("avg_frame_rate"),
                    "video_duration_sec": duration, "video_codec": video.get("codec_name"),
                    "pixel_format": video.get("pix_fmt"), "audio_stream_count": len(audios),
                    "audio_codecs": [a.get("codec_name") for a in audios],
                    "audio_durations_sec": [numeric(a.get("duration")) for a in audios],
                    "container_duration_sec": numeric(data.get("format", {}).get("duration")),
                    "size_bytes": path.stat().st_size}
        report["metadata"] = metadata
        check("video_duration_positive", duration is not None and duration > 0, duration, "> 0")
        for key in ("width", "height"):
            expected = getattr(args, key)
            if expected is not None:
                check(key, video.get(key) == expected, video.get(key), expected)
        if args.fps is not None:
            check("fps_metadata", fps is not None and abs(fps - args.fps) <= args.fps_tolerance,
                  fps, {"value": args.fps, "tolerance": args.fps_tolerance})
        if args.duration is not None:
            check("duration", duration is not None and abs(duration - args.duration) <= args.duration_tolerance,
                  duration, {"value": args.duration, "tolerance": args.duration_tolerance})
        if args.video_codec:
            check("video_codec", video.get("codec_name") == args.video_codec,
                  video.get("codec_name"), args.video_codec)
        if args.pixel_format:
            check("pixel_format", video.get("pix_fmt") == args.pixel_format,
                  video.get("pix_fmt"), args.pixel_format)
    if args.require_audio:
        check("audio_stream_present", bool(audios), len(audios), ">= 1")

    unavailable = False
    if args.decode:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            checks.append({"name": "decode", "status": "not_checked", "reason": "ffmpeg unavailable"})
            unavailable = True
        else:
            decode_command = [ffmpeg, "-nostdin", "-v", "error", "-xerror", "-i", str(path),
                              "-map", "0:v:0?", "-map", "0:a?", "-f", "null", "-"]
            try:
                decoded = subprocess.run(decode_command, capture_output=True, text=True,
                                         timeout=args.decode_timeout, check=False)
                check("decode", decoded.returncode == 0,
                      {"exit_code": decoded.returncode, "stderr": decoded.stderr[-2000:]},
                      "Full decode without a fatal stream error")
            except (OSError, subprocess.TimeoutExpired) as exc:
                checks.append({"name": "decode", "status": "not_checked", "reason": str(exc)})
                unavailable = True
    else:
        report["not_checked"].append("Full stream decode (run --decode to check)")

    failed = any(c["status"] == "failed" for c in checks)
    report["status"] = "failed" if failed else ("not_checked" if unavailable else "passed")
    write_report(report, args.out)
    return 1 if failed else (2 if unavailable else 0)


if __name__ == "__main__":
    raise SystemExit(main())
