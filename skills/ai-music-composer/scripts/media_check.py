#!/usr/bin/env python3
"""Inspect media duration and compare it to a requested target using ffprobe."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def probe(path: Path) -> tuple[float, dict]:
    if shutil.which("ffprobe") is None:
        raise RuntimeError("ffprobe is not installed or not on PATH")
    command = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration:format=format_name",
        "-of", "json", str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "ffprobe could not inspect this file")
    data = json.loads(result.stdout)
    try:
        return float(data["format"]["duration"]), data
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("ffprobe did not return a readable duration") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path, help="audio or video file to inspect")
    parser.add_argument("--target", type=float, help="target duration in seconds")
    parser.add_argument("--tolerance", type=float, default=0.10, help="allowed deviation in seconds (default: 0.10)")
    args = parser.parse_args()

    if not args.media.is_file():
        parser.error(f"media file not found: {args.media}")
    if args.tolerance < 0:
        parser.error("tolerance must be non-negative")

    try:
        duration, data = probe(args.media)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result = {"path": str(args.media.resolve()), "duration_seconds": round(duration, 6), "format": data.get("format", {}).get("format_name")}
    if args.target is not None:
        delta = duration - args.target
        result.update({"target_seconds": args.target, "delta_seconds": round(delta, 6), "tolerance_seconds": args.tolerance, "within_tolerance": abs(delta) <= args.tolerance})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("within_tolerance", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
