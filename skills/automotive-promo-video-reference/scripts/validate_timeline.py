#!/usr/bin/env python3
"""Validate a no-keyframe automotive timeline; never calls generation services."""
import argparse
import json
import math
import sys
from pathlib import Path


def validate(data, base_dir, require_local_assets=False):
    errors = []
    eps = 1e-7

    def fail(message):
        errors.append(message)

    def number(value, label, positive=False):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            fail(f"{label}: expected finite number")
            return None
        if value < 0 or (positive and value <= 0):
            fail(f"{label}: invalid negative or zero value")
            return None
        return float(value)

    if not isinstance(data, dict):
        return ["root: expected object"]
    if data.get("schema_version") != 1:
        fail("schema_version: expected 1")
    total = number(data.get("project_duration"), "project_duration", True)
    limit = number(data.get("segment_limit"), "segment_limit", True)
    grid = number(data.get("time_grid"), "time_grid", True)
    fps = number(data.get("fps"), "fps", True)
    if limit is not None and limit > 30:
        fail("segment_limit: must be <= 30 seconds")
    if grid is not None and abs(grid - 0.5) > eps:
        fail("time_grid: this plan format uses 0.5 seconds")

    def on_grid(value, label):
        if value is not None and grid:
            units = value / grid
            if abs(units - round(units)) > eps:
                fail(f"{label}: not on 0.5-second grid")

    on_grid(total, "project_duration")
    assets = data.get("assets", [])
    if not isinstance(assets, list):
        fail("assets: expected list")
        assets = []
    asset_map = {}
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            fail(f"assets[{index}]: expected object")
            continue
        asset_id = asset.get("id")
        if not isinstance(asset_id, str) or not asset_id:
            fail(f"assets[{index}].id: nonempty string required")
            continue
        if asset_id in asset_map:
            fail(f"assets: duplicate id {asset_id}")
        asset_map[asset_id] = asset

    clips = data.get("clips")
    if not isinstance(clips, list) or not clips:
        return errors + ["clips: nonempty list required"]
    clip_ids, shot_ids, referenced = set(), set(), set()
    global_cursor = 0.0
    count = 0
    for index, clip in enumerate(clips):
        label = f"clips[{index}]"
        if not isinstance(clip, dict):
            fail(f"{label}: expected object")
            continue
        clip_id = clip.get("id")
        if not isinstance(clip_id, str) or not clip_id or clip_id in clip_ids:
            fail(f"{label}.id: missing or duplicate")
        else:
            clip_ids.add(clip_id)
            label = clip_id
        start = number(clip.get("start"), label + ".start")
        duration = number(clip.get("duration"), label + ".duration", True)
        on_grid(start, label + ".start")
        on_grid(duration, label + ".duration")
        if duration is not None and (duration > 30 + eps or (limit and duration > limit + eps)):
            fail(f"{label}: clip exceeds segment cap")
        if start is not None and abs(start - global_cursor) > eps:
            fail(f"{label}: global gap/overlap; expected start {global_cursor:g}")
        refs = clip.get("reference_ids")
        if not isinstance(refs, list) or not refs:
            fail(f"{label}: reference_ids must be a nonempty list")
            refs = []
        for ref in refs:
            if not isinstance(ref, str) or ref not in asset_map:
                fail(f"{label}: undefined reference {ref!r}")
            else:
                referenced.add(ref)
        local_cursor = 0.0
        shots = clip.get("shots")
        if not isinstance(shots, list) or not shots:
            fail(f"{label}.shots: nonempty list required")
            shots = []
        for si, shot in enumerate(shots):
            sl = f"{label}.shots[{si}]"
            if not isinstance(shot, dict):
                fail(f"{sl}: expected object")
                continue
            sid = shot.get("id")
            if not isinstance(sid, str) or not sid or sid in shot_ids:
                fail(f"{sl}.id: missing or duplicate global shot id")
            else:
                shot_ids.add(sid)
                sl = sid
            a = number(shot.get("start"), sl + ".start")
            b = number(shot.get("end"), sl + ".end")
            on_grid(a, sl + ".start")
            on_grid(b, sl + ".end")
            if a is not None and abs(a - local_cursor) > eps:
                fail(f"{sl}: local gap/overlap; expected start {local_cursor:g}")
            if a is not None and b is not None:
                if b <= a:
                    fail(f"{sl}: end must be greater than start")
                if duration is not None and b > duration + eps:
                    fail(f"{sl}: shot exceeds local clip duration")
                local_cursor = b
            for field in ("description", "camera", "transition"):
                if not isinstance(shot.get(field), str) or not shot[field].strip():
                    fail(f"{sl}.{field}: text required")
            count += 1
        if duration is not None and abs(local_cursor - duration) > eps:
            fail(f"{label}: shot coverage ends at {local_cursor:g}, expected {duration:g}")
        if start is not None and duration is not None:
            global_cursor = start + duration
    if total is not None and abs(global_cursor - total) > eps:
        fail(f"project coverage ends at {global_cursor:g}, expected {total:g}")
    if total is not None and fps is not None and abs(total * fps - round(total * fps)) > eps:
        fail("project duration does not align to whole output frames")
    if require_local_assets:
        for ref in sorted(referenced):
            asset = asset_map[ref]
            if asset.get("status") not in ("approved", "accepted"):
                fail(f"{ref}: referenced asset not accepted")
            raw_path = asset.get("path")
            if not isinstance(raw_path, str) or not raw_path:
                fail(f"{ref}: missing local path")
                continue
            path = Path(raw_path).expanduser()
            if not path.is_absolute():
                path = base_dir / path
            if not path.is_file() or path.stat().st_size == 0:
                fail(f"{ref}: local file missing or empty")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("timeline", type=Path)
    parser.add_argument("--require-local-assets", action="store_true",
                        help="Also require referenced local files and accepted status; not a model/upload/approval check")
    args = parser.parse_args()
    try:
        data = json.loads(args.timeline.read_text(encoding="utf-8"))
        errors = validate(data, args.timeline.resolve().parent, args.require_local_assets)
    except (OSError, ValueError, TypeError) as exc:
        errors = [str(exc)]
    print(json.dumps({"ok": not errors, "errors": errors,
                      "scope": "timeline and optional local references only; no generation"},
                     ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
