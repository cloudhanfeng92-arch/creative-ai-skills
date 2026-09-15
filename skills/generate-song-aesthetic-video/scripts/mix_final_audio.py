#!/usr/bin/env python3
"""Mix an exact-duration original score under a picture-locked video.

The video stream is copied unchanged. Existing dialogue, action sound, and
ambience drive a gentle side-chain reduction of the score. The helper refuses
music whose duration does not closely match picture lock, so audio generation
is fixed instead of retiming or trimming the picture.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


def probe(path: Path, ffprobe: str) -> tuple[float, bool]:
    command = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,duration",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"ffprobe failed: {path}")
    data = json.loads(result.stdout)
    duration = float(data.get("format", {}).get("duration") or 0)
    has_audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))
    if duration <= 0:
        raise RuntimeError(f"no positive duration: {path}")
    return duration, has_audio


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--picture-lock", required=True, type=Path)
    value.add_argument("--music", required=True, type=Path)
    value.add_argument("--out", required=True, type=Path)
    value.add_argument("--music-gain-db", type=float, default=-15.0)
    value.add_argument("--duration-tolerance", type=float, default=0.10)
    value.add_argument("--overwrite", action="store_true")
    value.add_argument("--dry-run", action="store_true")
    return value


def main() -> int:
    args = parser().parse_args()
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        print("ERROR: ffmpeg and ffprobe are required", file=sys.stderr)
        return 127

    picture = args.picture_lock.expanduser().resolve()
    music = args.music.expanduser().resolve()
    output = args.out.expanduser().resolve()
    for path in (picture, music):
        if not path.is_file():
            raise SystemExit(f"input not found: {path}")
    if output in (picture, music):
        raise SystemExit("output must not replace an input")
    if output.exists() and not args.overwrite:
        raise SystemExit("output exists; pass --overwrite after confirming replacement")

    picture_duration, picture_has_audio = probe(picture, ffprobe)
    music_duration, music_has_audio = probe(music, ffprobe)
    if not music_has_audio:
        raise SystemExit("music input has no audio stream")
    if abs(picture_duration - music_duration) > args.duration_tolerance:
        raise SystemExit(
            "music must match picture lock before mixing: "
            f"picture={picture_duration:.3f}s music={music_duration:.3f}s"
        )

    common = [
        ffmpeg,
        "-y",
        "-i",
        str(picture),
        "-i",
        str(music),
    ]
    if picture_has_audio:
        filter_graph = (
            "[0:a]aresample=48000,asetpts=PTS-STARTPTS[production];"
            f"[1:a]aresample=48000,asetpts=PTS-STARTPTS,volume={args.music_gain_db}dB[score];"
            "[score][production]sidechaincompress="
            "threshold=0.035:ratio=7:attack=25:release=420:makeup=1[ducked];"
            "[production][ducked]amix=inputs=2:duration=first:normalize=0,"
            "alimiter=limit=0.95[aout]"
        )
    else:
        filter_graph = (
            f"[1:a]aresample=48000,asetpts=PTS-STARTPTS,volume={args.music_gain_db}dB,"
            "alimiter=limit=0.95[aout]"
        )

    command = [
        *common,
        "-filter_complex",
        filter_graph,
        "-map",
        "0:v:0",
        "-map",
        "[aout]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-t",
        f"{picture_duration:.6f}",
        "-movflags",
        "+faststart",
        str(output),
    ]
    if args.dry_run:
        print(json.dumps(command, ensure_ascii=False))
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        print(result.stderr.strip() or "ffmpeg mix failed", file=sys.stderr)
        return result.returncode
    final_duration, final_has_audio = probe(output, ffprobe)
    if not final_has_audio or abs(final_duration - picture_duration) > args.duration_tolerance:
        print("ERROR: final mix validation failed", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "output": str(output),
                "picture_duration": picture_duration,
                "music_duration": music_duration,
                "final_duration": final_duration,
                "picture_audio_preserved": picture_has_audio,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
