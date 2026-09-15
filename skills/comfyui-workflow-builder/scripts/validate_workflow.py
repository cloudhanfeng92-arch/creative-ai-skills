#!/usr/bin/env python3
"""Static validator for ComfyUI UI workflow and API prompt JSON files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SECRET_RE = re.compile(r"(?i)(api[_-]?key|access[_-]?token|secret|authorization)")
ABSOLUTE_PATH_RE = re.compile(r"^(?:/|[A-Za-z]:[\\/]|~[\\/])")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from None


def walk_values(value: Any, trail: str = "$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk_values(child, f"{trail}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_values(child, f"{trail}[{index}]")
    else:
        yield trail, value


def node_inventory(path: Path | None) -> dict[str, set[str]]:
    if path is None:
        return {}
    raw = load_json(path)
    if isinstance(raw, list) and all(isinstance(item, str) for item in raw):
        return {"inventory": set(raw)}
    if isinstance(raw, dict):
        result: dict[str, set[str]] = {}
        for key, value in raw.items():
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise ValueError("inventory object values must be arrays of node type strings")
            result[str(key)] = set(value)
        return result
    raise ValueError("inventory must be an array of node types or an object of named arrays")


def validate_ui(data: dict[str, Any]) -> tuple[list[str], list[str], set[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    nodes = data.get("nodes")
    links = data.get("links", [])
    if not isinstance(nodes, list):
        return ["UI workflow must contain a nodes array"], warnings, set()
    if not isinstance(links, list):
        errors.append("UI workflow links must be an array")
        links = []

    node_ids: set[str] = set()
    node_types: set[str] = set()
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"nodes[{index}] is not an object")
            continue
        node_id = str(node.get("id"))
        if node.get("id") is None:
            errors.append(f"nodes[{index}] has no id")
        elif node_id in node_ids:
            errors.append(f"duplicate node id: {node_id}")
        node_ids.add(node_id)
        node_type = node.get("type")
        if not isinstance(node_type, str) or not node_type:
            errors.append(f"node {node_id} has no valid type")
        else:
            node_types.add(node_type)

    link_ids: set[str] = set()
    for index, link in enumerate(links):
        if isinstance(link, list):
            if len(link) < 5:
                errors.append(f"links[{index}] legacy link has fewer than 5 fields")
                continue
            link_id, origin_id, _origin_slot, target_id, _target_slot = link[:5]
        elif isinstance(link, dict):
            link_id = link.get("id")
            origin_id = link.get("origin_id")
            target_id = link.get("target_id")
        else:
            errors.append(f"links[{index}] is neither an array nor object")
            continue
        sid = str(link_id)
        if link_id is None:
            errors.append(f"links[{index}] has no id")
        elif sid in link_ids:
            errors.append(f"duplicate link id: {sid}")
        link_ids.add(sid)
        if str(origin_id) not in node_ids:
            errors.append(f"link {sid} references missing origin node {origin_id}")
        if str(target_id) not in node_ids:
            errors.append(f"link {sid} references missing target node {target_id}")

    referenced_links: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        for input_item in node.get("inputs", []) or []:
            if isinstance(input_item, dict) and input_item.get("link") is not None:
                referenced_links.add(str(input_item["link"]))
        for output_item in node.get("outputs", []) or []:
            if isinstance(output_item, dict):
                for link_id in output_item.get("links", []) or []:
                    referenced_links.add(str(link_id))
    for missing in sorted(referenced_links - link_ids):
        errors.append(f"node socket references missing link id {missing}")
    for orphan in sorted(link_ids - referenced_links):
        warnings.append(f"top-level link {orphan} is not referenced by a node socket")

    output_types = {"SaveImage", "PreviewImage", "SaveAnimatedWEBP", "VHS_VideoCombine"}
    if not (node_types & output_types):
        warnings.append("no commonly recognized preview/save output node found")
    return errors, warnings, node_types


def validate_api(data: dict[str, Any]) -> tuple[list[str], list[str], set[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    node_ids = {str(key) for key in data}
    node_types: set[str] = set()
    output_candidate = False
    for node_id, node in data.items():
        if not isinstance(node, dict):
            errors.append(f"API node {node_id} is not an object")
            continue
        class_type = node.get("class_type")
        inputs = node.get("inputs")
        if not isinstance(class_type, str) or not class_type:
            errors.append(f"API node {node_id} has no valid class_type")
        else:
            node_types.add(class_type)
            if class_type in {"SaveImage", "PreviewImage", "SaveAnimatedWEBP", "VHS_VideoCombine"}:
                output_candidate = True
        if not isinstance(inputs, dict):
            errors.append(f"API node {node_id} has no inputs object")
            continue
        for input_name, value in inputs.items():
            if (
                isinstance(value, list)
                and len(value) == 2
                and isinstance(value[1], int)
                and isinstance(value[0], (str, int))
            ):
                source = str(value[0])
                if source not in node_ids:
                    errors.append(f"API node {node_id} input {input_name} references missing node {source}")
                if value[1] < 0:
                    errors.append(f"API node {node_id} input {input_name} uses negative output index")
    if not output_candidate:
        warnings.append("no commonly recognized preview/save output node found")
    return errors, warnings, node_types


def detect_format(data: Any) -> str:
    if not isinstance(data, dict):
        return "unknown"
    if isinstance(data.get("nodes"), list):
        return "ui"
    if data and all(isinstance(value, dict) and "class_type" in value for value in data.values()):
        return "api"
    return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path)
    parser.add_argument("--inventory", type=Path, help="JSON node inventory array or named arrays")
    args = parser.parse_args()

    try:
        data = load_json(args.workflow)
        inventories = node_inventory(args.inventory)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    fmt = detect_format(data)
    if fmt == "ui":
        errors, warnings, node_types = validate_ui(data)
    elif fmt == "api":
        errors, warnings, node_types = validate_api(data)
    else:
        print("ERROR: could not identify UI workflow or API prompt format")
        return 2

    for trail, value in walk_values(data):
        if isinstance(value, str) and ABSOLUTE_PATH_RE.match(value):
            warnings.append(f"machine-specific absolute path at {trail}")
        if isinstance(value, str) and len(value) > 80 and SECRET_RE.search(trail):
            warnings.append(f"possible embedded credential at {trail}")

    inventory_results: dict[str, list[str]] = {}
    for name, supported in inventories.items():
        inventory_results[name] = sorted(node_types - supported)

    print(f"format: {fmt}")
    print(f"nodes: {len(data.get('nodes', [])) if fmt == 'ui' else len(data)}")
    print(f"node_types: {len(node_types)}")
    for name, missing in inventory_results.items():
        if missing:
            print(f"inventory {name}: missing {len(missing)} type(s): {', '.join(missing)}")
        else:
            print(f"inventory {name}: all node types present")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"result: FAIL ({len(errors)} error(s), {len(warnings)} warning(s))")
        return 1
    print(f"result: PASS ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
