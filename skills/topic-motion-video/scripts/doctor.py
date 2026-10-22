#!/usr/bin/env python3
"""Read-only local inspection; does not install packages or call paid services.

Python 3.9+. Standard library only. Missing optional tools are reported, not
silently installed. Successful inspection is not a successful render test.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from typing import Any, Optional


def inspect_tool(name: str, version_arg: str) -> dict[str, Any]:
    executable = shutil.which(name)
    if not executable:
        return {"found": False, "path": None, "version": None}
    result: dict[str, Any] = {"found": True, "path": executable}
    try:
        proc = subprocess.run(
            [executable, version_arg], capture_output=True, text=True,
            timeout=12, check=False,
        )
        lines = (proc.stdout or proc.stderr).strip().splitlines()
        result.update({"version": lines[0][:250] if lines else None,
                       "version_command_exit_code": proc.returncode})
    except (OSError, subprocess.TimeoutExpired) as exc:
        result.update({"version": None, "inspection_error": str(exc)})
    return result


def emit(report: dict[str, Any], output: Optional[Path]) -> None:
    content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    print(content, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, help="Optional JSON report path")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        emit({"inspection_completed": False,
              "error": f"Project directory does not exist: {project}"}, args.out)
        return 2

    declared: dict[str, Any] = {}
    package_error: Optional[str] = None
    package = project / "package.json"
    if package.is_file():
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("package.json must contain an object")
            dependencies: dict[str, Any] = {}
            for key in ("dependencies", "devDependencies"):
                if isinstance(data.get(key), dict):
                    dependencies.update(data[key])
            names = ("remotion", "@remotion/cli", "@remotion/renderer",
                     "react", "typescript", "three", "gsap", "playwright",
                     "@playwright/test", "puppeteer")
            declared = {name: dependencies[name] for name in names if name in dependencies}
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            package_error = str(exc)

    report = {
        "inspection_completed": True,
        "project": str(project),
        "platform": {"system": platform.system(), "machine": platform.machine()},
        "python": {"version": platform.python_version(), "executable": sys.executable},
        "tools": {name: inspect_tool(name, flag) for name, flag in (
            ("node", "--version"), ("npm", "--version"),
            ("ffmpeg", "-version"), ("ffprobe", "-version"),
            ("codex", "--version"),
        )},
        "package_json_present": package.is_file(),
        "package_json_error": package_error,
        "declared_dependencies_not_install_verification": declared,
        "lockfiles": [name for name in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock",
                                        "bun.lock", "bun.lockb") if (project / name).is_file()],
        "node_modules_present": (project / "node_modules").is_dir(),
        "openai_api_key_present_not_validated": bool(os.environ.get("OPENAI_API_KEY")),
        "not_checked": [
            "Codex in-app browser capabilities (not inspected by CLI)", "Chinese font glyph coverage",
            "Actual dependency imports", "Credentials, service permissions and quota",
            "Image / voice / music generation availability", "Video output quality",
        ],
        "notes": [
            "No package installations, login attempts, purchases or service calls were made.",
            "Missing Codex CLI does not establish that a desktop host is unavailable.",
            "Browser operations are allowed only through official Codex in-app browser tools; external browsers are prohibited.",
            "Dependency findings do not authorize Playwright, Puppeteer, or Remotion to launch a browser.",
            "Web preview is optional. Use a short render only through a verified permitted backend when diagnosis is needed.",
        ],
    }
    emit(report, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
