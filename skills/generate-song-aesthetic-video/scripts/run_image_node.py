#!/usr/bin/env python3
"""Safely create and optionally run one LibTV Style Image V8.2 node."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="LibTV canvas UUID")
    parser.add_argument("--group", required=True, help="Existing ordinary group")
    parser.add_argument("--node", required=True, help="Unique image-node name")
    parser.add_argument("--index", required=True, type=int, help="One-based shot index")
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--reference", action="append", default=[])
    parser.add_argument("--model", default="Style Image V8.2")
    parser.add_argument("--ratio", default="16:9")
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--quality", default="auto")
    parser.add_argument("--stylize", type=int, default=150)
    parser.add_argument("--weird", type=int, default=0)
    parser.add_argument("--chaos", type=int, default=0)
    parser.add_argument("--x", type=int)
    parser.add_argument("--y", type=int)
    parser.add_argument("--omit-ratio", action="store_true")
    parser.add_argument("--omit-count", action="store_true")
    parser.add_argument("--omit-quality", action="store_true")
    parser.add_argument("--omit-stylize", action="store_true")
    parser.add_argument("--omit-weird", action="store_true")
    parser.add_argument("--omit-chaos", action="store_true")
    parser.add_argument("--no-run", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--libtv-bin", help="Explicit libtv executable path")
    return parser


def add_setting(command: list[str], key: str, value: object) -> None:
    command.extend(["-s", f"{key}={value}"])


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.index < 1:
        parser.error("--index must be at least 1")
    if len(args.reference) > 6:
        parser.error("the checked Style Image V8.2 schema allows at most six references")
    if args.count != 4 and not args.omit_count:
        parser.error("the checked Style Image V8.2 schema fixes count at four")

    prompt_path = args.prompt_file.expanduser().resolve()
    try:
        prompt = prompt_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        print(f"Cannot read prompt file: {exc}", file=sys.stderr)
        return 2
    if not prompt:
        print("Prompt file is empty.", file=sys.stderr)
        return 2

    libtv_bin = args.libtv_bin or shutil.which("libtv")
    if not libtv_bin:
        print("libtv executable was not found.", file=sys.stderr)
        return 127

    column = (args.index - 1) % 3
    row = (args.index - 1) // 3
    x = args.x if args.x is not None else 80 + 540 * column
    y = args.y if args.y is not None else 80 + 420 * row
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
        "image",
    ]
    add_setting(command, "model", args.model)
    if args.reference:
        add_setting(command, "modeType", "image2image")
    if not args.omit_ratio:
        add_setting(command, "ratio", args.ratio)
    if not args.omit_count:
        add_setting(command, "count", args.count)
    if not args.omit_quality:
        add_setting(command, "quality", args.quality)
    if not args.omit_stylize:
        add_setting(command, "stylize", args.stylize)
    if not args.omit_weird:
        add_setting(command, "weird", args.weird)
    if not args.omit_chaos:
        add_setting(command, "chaos", args.chaos)
    for reference in args.reference:
        command.extend(["--left", reference])
    command.extend(["--prompt", prompt])
    if not args.no_run:
        command.append("--run")

    if args.dry_run:
        print(json.dumps(command, ensure_ascii=False, indent=2))
        return 0
    completed = subprocess.run(command, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
