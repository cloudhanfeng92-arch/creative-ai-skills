#!/usr/bin/env python3
"""Safely upload a LibTV media resource or download a generated node result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--libtv-bin", help="Explicit libtv executable path")
    parser.add_argument("--dry-run", action="store_true")
    subparsers = parser.add_subparsers(dest="operation", required=True)

    upload = subparsers.add_parser("upload")
    upload.add_argument("--project", required=True)
    upload.add_argument("--group", required=True)
    upload.add_argument("--node", required=True)
    upload.add_argument("--type", dest="media_type", choices=("image", "video", "audio"), required=True)
    upload.add_argument("--resource", required=True, type=Path)
    upload.add_argument("--x", type=int, default=80)
    upload.add_argument("--y", type=int, default=-360)

    download = subparsers.add_parser("download")
    download.add_argument("--project", required=True)
    download.add_argument("--group")
    download.add_argument("--node", required=True)
    download.add_argument("--out", required=True, type=Path)
    watermark = download.add_mutually_exclusive_group()
    watermark.add_argument(
        "--without-ai-watermark",
        dest="without_ai_watermark",
        action="store_true",
        default=True,
        help="Request the official no-AI-watermark download (default)",
    )
    watermark.add_argument(
        "--keep-ai-watermark",
        dest="without_ai_watermark",
        action="store_false",
        help="Keep the platform AI watermark only after the user accepts that limitation",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    libtv_bin = args.libtv_bin or shutil.which("libtv")
    if not libtv_bin:
        print("libtv executable was not found.", file=sys.stderr)
        return 127

    if args.operation == "upload":
        resource = args.resource.expanduser().resolve()
        if not resource.is_file():
            print(f"Resource file does not exist: {resource}", file=sys.stderr)
            return 2
        command = [
            libtv_bin,
            "upload",
            args.node,
            "-p",
            args.project,
            "-g",
            args.group,
            "-t",
            args.media_type,
            "--resource",
            str(resource),
            "--x",
            str(args.x),
            "--y",
            str(args.y),
        ]
    else:
        output_dir = args.out.expanduser().resolve()
        command = [libtv_bin, "download", "-n", args.node, "-p", args.project]
        if args.group:
            command.extend(["-g", args.group])
        command.extend(["-o", str(output_dir)])
        if args.without_ai_watermark:
            command.append("--without-ai-watermark")
        if not args.dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print(json.dumps(command, ensure_ascii=False, indent=2))
        return 0
    completed = subprocess.run(command, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
