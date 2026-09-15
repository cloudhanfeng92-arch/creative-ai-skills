#!/usr/bin/env python3
"""Join complete 4–5-second sources at original speed and verify their final frames."""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clip", action="append", required=True, type=Path)
    parser.add_argument(
        "--shot-duration",
        action="append",
        type=float,
        default=[],
        help=(
            "Optional expected complete source duration (4–5s), never an edit. "
            "Omit to detect full sources; pass once for all or once per --clip."
        ),
    )
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--crf", type=int, default=18)
    parser.add_argument("--preset", default="medium")
    parser.add_argument("--reject-missing-audio", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ffmpeg-bin")
    parser.add_argument("--ffprobe-bin")
    return parser


def run_probe(ffprobe: str, path: Path, count_frames: bool = False) -> dict:
    command = [ffprobe, "-v", "error"]
    if count_frames:
        command.append("-count_frames")
    command.extend(
        [
            "-show_entries",
            (
                "format=duration:stream=index,codec_type,codec_name,width,height,"
                "pix_fmt,sample_aspect_ratio,sample_rate,channels,r_frame_rate,"
                "avg_frame_rate,nb_read_frames,duration,start_time"
            ),
            "-of",
            "json",
            str(path),
        ]
    )
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or f"ffprobe failed for {path}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid ffprobe JSON for {path}: {exc}") from exc


def has_stream(payload: dict, stream_type: str) -> bool:
    return any(
        stream.get("codec_type") == stream_type for stream in payload.get("streams", [])
    )


def parse_rate(value: str | None) -> float | None:
    if not value or value == "0/0":
        return None
    try:
        return float(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return None


def inspect_source(payload: dict, expected: float | None, fps: int) -> tuple[float, int, int, float]:
    """Reject incompatible whole sources instead of making them fit by editing."""
    streams = payload.get("streams", [])
    videos = [item for item in streams if item.get("codec_type") == "video"]
    audios = [item for item in streams if item.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) > 1:
        raise ValueError("each source needs exactly one video and at most one audio stream")
    video = videos[0]
    try:
        source_frames = int(video["nb_read_frames"])
        declared_duration = float(video["duration"])
        video_start = float(video.get("start_time", 0))
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError("source video duration or decoded frame count is unavailable") from exc
    if not math.isfinite(declared_duration) or not 4.0 <= declared_duration <= 5.0:
        raise ValueError(f"complete source must be 4–5s, found {declared_duration:g}s")
    if not math.isfinite(video_start):
        raise ValueError("source video start time is invalid")
    source_fps = parse_rate(video.get("r_frame_rate"))
    average_fps = parse_rate(video.get("avg_frame_rate"))
    if (
        source_fps is None or average_fps is None or not 0 < source_fps <= fps
        or abs(source_fps - average_fps) > 0.001
    ):
        raise ValueError("supported sources are CFR at no more than 30fps; high-fps or VFR sources need a conforming complete source")
    duration = source_frames / source_fps
    if abs(declared_duration - duration) > 0.001:
        raise ValueError("source duration and frame count disagree; no retiming is permitted")
    frames = round(duration * fps)
    if abs(frames / fps - duration) > 1e-6:
        raise ValueError("complete source duration must already align to a 30fps frame boundary")
    duration = frames / fps
    if expected is not None and abs(expected - duration) > 1e-6:
        raise ValueError(f"expected {expected:g}s but whole source is {duration:g}s; it will not be cut")
    if audios:
        try:
            audio_start = float(audios[0].get("start_time", 0))
            audio_duration = float(audios[0]["duration"])
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError("source audio duration is unavailable; cannot verify preservation") from exc
        if not all(math.isfinite(value) for value in (audio_start, audio_duration)):
            raise ValueError("source audio timing is invalid")
        if audio_start < video_start - 0.001 or audio_start + audio_duration > video_start + duration + 0.001:
            raise ValueError("source audio extends beyond its video; preserve the source and resolve timing without cutting audio")
    return duration, frames, source_frames, source_fps


def verify_source_timestamps(ffprobe: str, path: Path, frame_count: int, source_fps: float) -> None:
    """Detect variable timing even when container rate metadata looks constant."""
    command = [
        ffprobe, "-v", "error", "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    try:
        timestamps = [
            float(frame["best_effort_timestamp_time"])
            for frame in json.loads(result.stdout)["frames"]
        ]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("source frame timestamps are unavailable") from exc
    if result.returncode or len(timestamps) != frame_count:
        raise ValueError("source frame timestamps do not match the decoded frame count")
    interval = 1 / source_fps
    if any(
        not math.isfinite(timestamp)
        or abs(timestamp - timestamps[0] - index * interval) > 0.0001
        for index, timestamp in enumerate(timestamps)
    ):
        raise ValueError("variable or irregular frame timing is unsupported; source was not changed")


def normalize_video(width: int, height: int) -> str:
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease:"
        "force_divisible_by=2:reset_sar=1,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
        "setsar=1,format=yuv420p"
    )


def frame_pixels(ffmpeg: str, path: Path, frame: int, width: int, height: int) -> bytes:
    command = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(path),
        "-map", "0:v:0", "-vf",
        f"select=eq(n\\,{frame}),{normalize_video(width, height)},scale=64:36,format=gray",
        "-fps_mode", "passthrough", "-f", "rawvideo", "pipe:1",
    ]
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode or len(result.stdout) != 64 * 36:
        raise RuntimeError(f"cannot decode boundary frame {frame} for {path}")
    return result.stdout


def validate_master(
    payload: dict,
    expected_duration: float,
    expected_frames: int,
    width: int,
    height: int,
    fps: int,
) -> list[str]:
    errors: list[str] = []
    streams = payload.get("streams", [])
    videos = [stream for stream in streams if stream.get("codec_type") == "video"]
    audios = [stream for stream in streams if stream.get("codec_type") == "audio"]
    forbidden = [
        stream
        for stream in streams
        if stream.get("codec_type") in {"subtitle", "data", "attachment"}
    ]
    if len(videos) != 1:
        errors.append(f"expected one video stream, found {len(videos)}")
    if len(audios) != 1:
        errors.append(f"expected one audio stream, found {len(audios)}")
    if forbidden:
        errors.append("output contains a forbidden subtitle/data/attachment stream")
    if videos:
        video = videos[0]
        if (video.get("width"), video.get("height")) != (width, height):
            errors.append("wrong output dimensions")
        if video.get("codec_name") != "h264":
            errors.append("output video is not H.264")
        if video.get("pix_fmt") != "yuv420p":
            errors.append("output pixel format is not yuv420p")
        if video.get("sample_aspect_ratio") != "1:1":
            errors.append("output sample aspect ratio is not 1:1")
        rate = parse_rate(video.get("r_frame_rate"))
        if rate is None or abs(rate - fps) > 0.001:
            errors.append("wrong output frame rate")
        try:
            video_duration = float(video["duration"])
        except (KeyError, TypeError, ValueError):
            errors.append("output video duration is unavailable")
        else:
            if abs(video_duration - expected_duration) > 0.001:
                errors.append("output video duration differs from the sum of complete sources")
        try:
            frames = int(video.get("nb_read_frames"))
        except (TypeError, ValueError):
            errors.append("ffprobe did not return a readable frame count")
        else:
            if frames != expected_frames:
                errors.append(f"expected {expected_frames} frames, found {frames}")
    if audios:
        audio = audios[0]
        if audio.get("codec_name") != "aac":
            errors.append("output audio is not AAC")
        if str(audio.get("sample_rate")) != "48000":
            errors.append("output audio is not 48 kHz")
        if int(audio.get("channels") or 0) != 2:
            errors.append("output audio is not stereo")
    try:
        duration = float(payload.get("format", {}).get("duration"))
    except (TypeError, ValueError):
        errors.append("output duration is unavailable")
    else:
        if abs(duration - expected_duration) > 0.10:
            errors.append(
                f"expected {expected_duration:.3f}s, found {duration:.3f}s"
            )
    return errors


def build_filter(
    probes: list[dict],
    shot_frames: list[int],
    width: int,
    height: int,
    fps: int,
) -> str:
    chains: list[str] = []
    audio_inputs = ["[silence]"]
    offset_samples = 0
    duration = sum(shot_frames) / fps
    chains.append(f"anullsrc=channel_layout=stereo:sample_rate=48000:d={duration:.9f}[silence]")
    for index, (payload, frames) in enumerate(zip(probes, shot_frames)):
        chains.append(
            f"[{index}:v:0]setpts=PTS-STARTPTS,fps={fps}:start_time=0,"
            f"{normalize_video(width, height)}[v{index}]"
        )
        if has_stream(payload, "audio"):
            video = next(item for item in payload["streams"] if item["codec_type"] == "video")
            audio = next(item for item in payload["streams"] if item["codec_type"] == "audio")
            local_offset = float(audio.get("start_time", 0)) - float(video.get("start_time", 0))
            delay = offset_samples + max(0, round(local_offset * 48000))
            chains.append(
                f"[{index}:a:0]asetpts=PTS-STARTPTS,aresample=48000,"
                "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
                f"adelay=delays={delay}S:all=1[a{index}]"
            )
            audio_inputs.append(f"[a{index}]")
        offset_samples += frames * 48000 // fps
    video_inputs = "".join(f"[v{i}]" for i in range(len(probes)))
    chains.append(f"{video_inputs}concat=n={len(probes)}:v=1:a=0[outv]")
    chains.append(
        f"{''.join(audio_inputs)}amix=inputs={len(audio_inputs)}:duration=longest:"
        "normalize=0:dropout_transition=0[outa]"
    )
    return ";".join(chains)


def main() -> int:
    args = build_parser().parse_args()
    if args.width != 1280 or args.height != 720 or args.fps != 30:
        print("This Skill requires 1280x720 at 30 fps.", file=sys.stderr)
        return 2
    if not 0 <= args.crf <= 51:
        print("--crf must be between 0 and 51.", file=sys.stderr)
        return 2

    ffmpeg = args.ffmpeg_bin or shutil.which("ffmpeg")
    ffprobe = args.ffprobe_bin or shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        print("ffmpeg and ffprobe are required.", file=sys.stderr)
        return 127

    clips = [path.expanduser().resolve() for path in args.clip]
    output = args.out.expanduser().resolve()
    raw_durations = args.shot_duration
    if not raw_durations:
        durations = [None] * len(clips)
    elif len(raw_durations) == 1:
        durations = raw_durations * len(clips)
    elif len(raw_durations) == len(clips):
        durations = raw_durations
    else:
        print(
            "Pass no --shot-duration values, one shared value, or exactly one per clip.",
            file=sys.stderr,
        )
        return 2

    shot_frames: list[int] = []
    source_frame_counts: list[int] = []
    source_rates: list[float] = []
    normalized_durations: list[float] = []
    for index, duration in enumerate(durations, start=1):
        if duration is None:
            continue
        if not math.isfinite(duration) or not 4.0 <= duration <= 5.0:
            print(
                f"Shot {index} expectation must be between 4 and 5 seconds: {duration:g}",
                file=sys.stderr,
            )
            return 2
        frames = round(duration * args.fps)
        normalized = frames / args.fps
        if abs(normalized - duration) > 1e-6:
            print(
                f"Shot {index} duration must align to a 30 fps frame boundary: {duration:g}",
                file=sys.stderr,
            )
            return 2
    if len(set(clips)) != len(clips):
        print("Duplicate clip paths are not allowed.", file=sys.stderr)
        return 2
    if output in clips:
        print("Output path must not equal an input path.", file=sys.stderr)
        return 2
    if output.exists() and not args.overwrite:
        print(f"Output already exists: {output}", file=sys.stderr)
        return 2

    probes: list[dict] = []
    for clip, expected in zip(clips, durations):
        if not clip.is_file():
            print(f"Input does not exist: {clip}", file=sys.stderr)
            return 2
        try:
            payload = run_probe(ffprobe, clip, count_frames=True)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        try:
            duration, frames, source_frames, source_fps = inspect_source(payload, expected, args.fps)
            verify_source_timestamps(ffprobe, clip, source_frames, source_fps)
        except ValueError as exc:
            print(f"{clip}: {exc}", file=sys.stderr)
            return 2
        if args.reject_missing_audio and not has_stream(payload, "audio"):
            print(f"Input has no audio stream: {clip}", file=sys.stderr)
            return 2
        probes.append(payload)
        normalized_durations.append(duration)
        shot_frames.append(frames)
        source_frame_counts.append(source_frames)
        source_rates.append(source_fps)

    expected_frames = sum(shot_frames)
    expected_duration = expected_frames / args.fps
    filter_graph = build_filter(
        probes,
        shot_frames,
        args.width,
        args.height,
        args.fps,
    )
    temporary_path: Path | None = None
    if args.dry_run:
        temporary_path = output.with_name(f".{output.stem}.temporary.mp4")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        handle = tempfile.NamedTemporaryFile(
            prefix=f".{output.stem}.", suffix=".mp4", dir=output.parent, delete=False
        )
        handle.close()
        temporary_path = Path(handle.name)

    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y"]
    for clip in clips:
        command.extend(["-i", str(clip)])
    command.extend(
        [
            "-filter_complex",
            filter_graph,
            "-map",
            "[outv]",
            "-map",
            "[outa]",
            "-c:v",
            "libx264",
            "-preset",
            args.preset,
            "-crf",
            str(args.crf),
            "-pix_fmt",
            "yuv420p",
            "-fps_mode",
            "passthrough",
            "-c:a",
            "aac",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(temporary_path),
        ]
    )
    if args.dry_run:
        print(json.dumps(command, ensure_ascii=False, indent=2))
        return 0

    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode:
            raise RuntimeError(completed.stderr.strip() or "ffmpeg failed")
        payload = run_probe(ffprobe, temporary_path, count_frames=True)
        errors = validate_master(
            payload,
            expected_duration,
            expected_frames,
            args.width,
            args.height,
            args.fps,
        )
        if errors:
            raise RuntimeError("; ".join(errors))
        tail_checks = []
        first_checks = []
        cumulative_frames = 0
        for clip, frames, source_frames in zip(clips, shot_frames, source_frame_counts):
            source_first = frame_pixels(ffmpeg, clip, 0, args.width, args.height)
            output_first = frame_pixels(ffmpeg, temporary_path, cumulative_frames, args.width, args.height)
            first_error = sum(abs(a - b) for a, b in zip(source_first, output_first)) / len(source_first)
            if first_error > 12.0:
                raise RuntimeError(f"first-frame preservation check failed for {clip}: mean luma error {first_error:.2f}")
            first_checks.append({"source": str(clip), "master_frame": cumulative_frames, "mean_luma_error": round(first_error, 3)})
            cumulative_frames += frames
            source_tail = frame_pixels(ffmpeg, clip, source_frames - 1, args.width, args.height)
            output_tail = frame_pixels(ffmpeg, temporary_path, cumulative_frames - 1, args.width, args.height)
            mean_error = sum(abs(a - b) for a, b in zip(source_tail, output_tail)) / len(source_tail)
            if mean_error > 12.0:
                raise RuntimeError(f"final-frame preservation check failed for {clip}: mean luma error {mean_error:.2f}")
            tail_checks.append({"source": str(clip), "master_frame": cumulative_frames - 1, "mean_luma_error": round(mean_error, 3)})
        os.replace(temporary_path, output)
    except RuntimeError as exc:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()
        print(f"Assembly failed: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "output": str(output),
                "shots": len(clips),
                "shot_durations": normalized_durations,
                "shot_frames": shot_frames,
                "source_frame_counts": source_frame_counts,
                "source_frame_rates": source_rates,
                "duration": expected_duration,
                "frames": expected_frames,
                "format": "1280x720/30fps/H.264/AAC-48kHz-stereo",
                "music": False,
                "source_coverage": "complete; original speed; no temporal or spatial crop",
                "first_frame_checks": first_checks,
                "tail_frame_checks": tail_checks,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
