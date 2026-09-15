#!/usr/bin/env python3
"""Safely build or execute one LibTV Seedance 2.0 video-node command.

The prompt is read from UTF-8 and passed as one subprocess argv element. The
default behavior is preview-only; a paid node call requires explicit --run.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys


RATIOS = ("adaptive", "16:9", "4:3", "1:1", "3:4", "9:16", "21:9")
RESOLUTIONS = ("480p", "720p", "1080p", "4k")
MODES = ("singleImage2video", "frames2video", "image2video", "mixed2video")
RESERVED_SETTINGS = {
    "model",
    "modeType",
    "count",
    "ratio",
    "resolution",
    "duration",
    "enableSound",
    "search_enabled",
    "autoCompliance",
    "prompt",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="LibTV canvas UUID")
    parser.add_argument("--group", required=True, help="Existing ordinary group")
    parser.add_argument("--node", required=True, help="Unique video-node name")
    parser.add_argument("--index", required=True, type=int, help="One-based shot index")
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument(
        "--reference",
        action="append",
        default=[],
        help="Upstream node or media resource; repeat in first/end-frame order",
    )
    parser.add_argument("--model", default="Seedance 2.0 VIP")
    parser.add_argument("--mode", choices=MODES, default="singleImage2video")
    parser.add_argument("--ratio", choices=RATIOS, default="16:9")
    parser.add_argument("--resolution", choices=RESOLUTIONS, default="720p")
    parser.add_argument(
        "--duration",
        type=float,
        default=4,
        help="Complete native shot seconds, 4–5; defaults to 4 (no trimming)",
    )
    parser.add_argument(
        "--delivery-duration",
        type=float,
        default=None,
        help="Optional delivery expectation; must equal --duration exactly",
    )
    parser.add_argument(
        "--schema-min-duration",
        type=float,
        default=4,
        help="Minimum from the live schema; change only after re-querying it",
    )
    parser.add_argument(
        "--schema-max-duration",
        type=float,
        default=15,
        help="Maximum from the live schema; change only after re-querying it",
    )
    parser.add_argument(
        "--schema-duration-step",
        type=float,
        default=1,
        help="Duration step from the live schema (currently 1 second)",
    )
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--sound", choices=("on", "off"), default="on")
    parser.add_argument("--search-enabled", choices=(0, 1), type=int, default=0)
    parser.add_argument("--auto-compliance", choices=(0, 1), type=int, default=1)
    parser.add_argument("--omit-search-enabled", action="store_true")
    parser.add_argument("--omit-auto-compliance", action="store_true")
    parser.add_argument("--x", type=int)
    parser.add_argument("--y", type=int)
    parser.add_argument(
        "--extra-setting",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Additional setting verified in the live schema",
    )
    parser.add_argument(
        "--extra-setting-file",
        action="append",
        default=[],
        metavar="KEY=PATH",
        help="Read an additional live-schema value from a UTF-8 file",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Execute the paid node call; without this flag only print argv",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--libtv-bin", help="Explicit libtv executable path")
    return parser


def split_setting(spec: str, option: str) -> tuple[str, str]:
    key, separator, value = spec.partition("=")
    key = key.strip()
    if not separator or not key:
        raise ValueError(f"{option} requires KEY=VALUE")
    if key in RESERVED_SETTINGS:
        raise ValueError(f"{option} cannot override standard setting: {key}")
    return key, value


def validate(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.index < 1:
        parser.error("--index must be at least 1")
    if args.run and args.dry_run:
        parser.error("choose either --run or --dry-run, not both")
    if args.count != 1:
        parser.error("this production workflow requires count=1 per video node")
    schema_values = (
        args.schema_min_duration, args.schema_max_duration, args.schema_duration_step
    )
    if not all(math.isfinite(value) for value in schema_values):
        parser.error("live-schema duration values must be finite")
    if (
        args.schema_min_duration <= 0
        or args.schema_max_duration < args.schema_min_duration
        or args.schema_duration_step <= 0
    ):
        parser.error("invalid live-schema duration bounds")
    if not math.isfinite(args.duration) or not 4.0 <= args.duration <= 5.0:
        parser.error("complete native shot duration must be between 4 and 5 seconds")
    if not args.schema_min_duration <= args.duration <= args.schema_max_duration:
        parser.error(
            f"duration must be {args.schema_min_duration}–{args.schema_max_duration} "
            "seconds for the checked live schema"
        )
    steps = (args.duration - args.schema_min_duration) / args.schema_duration_step
    if abs(steps - round(steps)) > 1e-6:
        parser.error(
            f"duration must follow the checked native step of "
            f"{args.schema_duration_step:g}s; rounding or trimming is not allowed"
        )
    native_frames = round(args.duration * 30)
    if abs(native_frames / 30 - args.duration) > 1e-6:
        parser.error("native duration must align to a 30 fps frame boundary")
    if args.delivery_duration is not None and (
        not math.isfinite(args.delivery_duration)
        or abs(args.delivery_duration - args.duration) > 1e-6
    ):
        parser.error("delivery duration must equal native duration; no trimming or retiming")

    references = len(args.reference)
    if args.mode == "singleImage2video" and references != 1:
        parser.error("singleImage2video requires exactly one confirmed image")
    if args.mode == "frames2video" and not 1 <= references <= 2:
        parser.error("frames2video accepts one or two references in first/end order")
    if args.mode == "image2video" and not 1 <= references <= 9:
        parser.error("image2video requires 1–9 references in the checked schema")
    if args.mode == "mixed2video" and not 1 <= references <= 15:
        parser.error("mixed2video requires 1–15 references in the checked schema")


def add_setting(command: list[str], key: str, value: object) -> None:
    command.extend(["-s", f"{key}={value}"])


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    validate(args, parser)

    prompt_path = args.prompt_file.expanduser().resolve()
    try:
        prompt = prompt_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        print(f"Cannot read prompt file: {exc}", file=sys.stderr)
        return 2
    if not prompt:
        print("Prompt file is empty.", file=sys.stderr)
        return 2

    try:
        extra_settings = [
            split_setting(spec, "--extra-setting") for spec in args.extra_setting
        ]
        for spec in args.extra_setting_file:
            key, raw_path = split_setting(spec, "--extra-setting-file")
            value_path = Path(raw_path).expanduser().resolve()
            value = value_path.read_text(encoding="utf-8").strip()
            if not value:
                raise ValueError(f"Extra-setting file is empty: {value_path}")
            extra_settings.append((key, value))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    libtv_bin = args.libtv_bin or shutil.which("libtv")
    if not libtv_bin:
        print("libtv executable was not found.", file=sys.stderr)
        return 127

    column = (args.index - 1) % 3
    row = (args.index - 1) // 3
    x = args.x if args.x is not None else 120 + 620 * column
    y = args.y if args.y is not None else 720 + 460 * row
    command = [
        libtv_bin,
        "node",
        "--x",
        str(x),
        "--y",
        str(y),
        "create",
        args.node,
        "-p",
        args.project,
        "-g",
        args.group,
        "-t",
        "video",
    ]
    add_setting(command, "model", args.model)
    add_setting(command, "modeType", args.mode)
    add_setting(command, "count", args.count)
    add_setting(command, "ratio", args.ratio)
    add_setting(command, "resolution", args.resolution)
    add_setting(command, "duration", f"{args.duration:g}")
    add_setting(command, "enableSound", args.sound)
    if not args.omit_search_enabled:
        add_setting(command, "search_enabled", args.search_enabled)
    if not args.omit_auto_compliance:
        add_setting(command, "autoCompliance", args.auto_compliance)
    for key, value in extra_settings:
        add_setting(command, key, value)
    for reference in args.reference:
        command.extend(["--left", reference])
    command.extend(["--prompt", prompt])
    if args.run:
        command.append("--run")

    if args.dry_run or not args.run:
        print(json.dumps(command, ensure_ascii=False, indent=2))
        return 0
    completed = subprocess.run(command, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
