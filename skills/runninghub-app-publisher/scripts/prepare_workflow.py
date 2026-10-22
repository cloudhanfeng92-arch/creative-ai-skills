#!/usr/bin/env python3
"""Clone the supplied RunningHub UI templates; no network or account access.

Output is a UI workflow, not an API prompt and not runtime verification.
Only node classes, socket layouts and widget orders present in the source exports
are used. Additional image inputs clone the export's existing LoadImage node.
"""

import argparse
import copy
import hashlib
import json
import re
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = {
    "gpt-image-2": {
        "file": "gpt-image-2.original.json",
        "sha256": "734aead3be85a89dafe6440371b8dd7317c39aa2530e82e111bd8beafc609487",
        "node_type": "RH_RhartImageG2ImageToImage",
        "widgets": {"prompt": 0, "aspectRatio": 1, "skip_error": 2, "seed": 3,
                    "control_after_generate": 4, "resolution": 5},
        "max_images": 10,
    },
    "nano-banana-2.1": {
        "file": "nano-banana-2.1.original.json",
        "sha256": "6b6c10a53896255addca300c07752f7a1e9d9d09947ad67353c5bde4aa80abd4",
        "node_type": "RH_RhartImageNNb21ImageToImage",
        "widgets": {"prompt": 0, "resolution": 1, "aspectRatio": 2, "skip_error": 3,
                    "seed": 4, "control_after_generate": 5},
        "max_images": 14,
    },
}


def dump_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_graph(graph):
    """Check all links in both directions, slot ranges, and socket types."""
    nodes = graph["nodes"]
    by_id = {n["id"]: n for n in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("Duplicate node ID")
    links = {l[0]: l for l in graph["links"]}
    if len(links) != len(graph["links"]):
        raise ValueError("Duplicate link ID")
    for link in graph["links"]:
        if len(link) != 6:
            raise ValueError("Expected v0.4 six-item link")
        lid, source_id, source_slot, target_id, target_slot, dtype = link
        if source_id not in by_id or target_id not in by_id:
            raise ValueError(f"Link {lid}: missing node")
        source, target = by_id[source_id], by_id[target_id]
        if not 0 <= source_slot < len(source.get("outputs", [])):
            raise ValueError(f"Link {lid}: invalid output slot")
        if not 0 <= target_slot < len(target.get("inputs", [])):
            raise ValueError(f"Link {lid}: invalid input slot")
        output, input_ = source["outputs"][source_slot], target["inputs"][target_slot]
        if lid not in (output.get("links") or []) or input_.get("link") != lid:
            raise ValueError(f"Link {lid}: endpoint references disagree")
        if output["type"] != dtype or input_["type"] != dtype:
            raise ValueError(f"Link {lid}: socket types disagree")
    for node in nodes:
        for slot, input_ in enumerate(node.get("inputs", [])):
            lid = input_.get("link")
            if lid is not None and (lid not in links or links[lid][3:5] != [node["id"], slot]):
                raise ValueError(f"Node {node['id']}: dangling input link")
        for slot, output in enumerate(node.get("outputs", [])):
            for lid in output.get("links") or []:
                if lid not in links or links[lid][1:3] != [node["id"], slot]:
                    raise ValueError(f"Node {node['id']}: dangling output link")
    if graph["last_node_id"] < max(by_id) or graph["last_link_id"] < max(links, default=0):
        raise ValueError("last_node_id / last_link_id below used IDs")


def clean_identity(graph):
    # Source exports are pinned by SHA-256. Do not copy their workflow identity.
    graph["id"] = str(uuid.uuid4())
    graph["revision"] = 0
    # Keep only confirmed frontend/extension metadata; no sessions, source asset
    # previews, user/account metadata, execution history or signed URLs.
    safe_extra = {"links_added_by_ue", "ue_links", "VHS_KeepIntermediate", "VHS_MetadataImage",
                  "0246.VERSION", "pixaromaGroups", "VHS_latentpreviewrate", "frontendVersion",
                  "VHS_latentpreview", "KKvideo_latentpreview", "KKvideo_latentpreviewrate"}
    graph["extra"] = {k: v for k, v in graph.get("extra", {}).items() if k in safe_extra}
    graph["config"] = {}
    for node in graph["nodes"]:
        node["properties"] = {k: v for k, v in node.get("properties", {}).items()
                              if k in {"Node name for S&R", "widget_ue_connectable"}}
        for key in ("imgs", "images", "imageIndex", "preview", "execution", "user_id", "session_id"):
            node.pop(key, None)


def prepare(args):
    spec = TEMPLATES[args.model]
    template_path = ROOT / "assets" / "workflows" / spec["file"]
    raw = template_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != spec["sha256"]:
        raise ValueError("Bundled source template changed; inspect and re-verify its interface before use")
    graph = json.loads(raw)
    validate_graph(graph)
    clean_identity(graph)
    generator = next(n for n in graph["nodes"] if n["type"] == spec["node_type"])
    loader = next(n for n in graph["nodes"] if n["type"] == "LoadImage")
    output = next(n for n in graph["nodes"] if n["type"] == "SaveImage")
    if not 1 <= args.images <= spec["max_images"]:
        raise ValueError(f"{args.model} supports 1–{spec['max_images']} image sockets in this export")
    if args.image_name and len(args.image_name) != args.images:
        raise ValueError("Supply exactly one --image-name per --images input, or omit all names")
    if args.image_label and len(args.image_label) != args.images:
        raise ValueError("Supply exactly one --image-label per --images input, or omit all labels")
    prompt = args.prompt_file.read_text(encoding="utf-8") if args.prompt_file else args.prompt
    if not prompt or not prompt.strip():
        raise ValueError("A nonempty fixed prompt is required")
    if args.resolution != "2k" and not args.allow_unverified_parameters:
        raise ValueError("Default is requested 2k; other resolutions require live UI verification and --allow-unverified-parameters")
    if args.aspect_ratio != "3:4" and not args.allow_unverified_parameters:
        raise ValueError("Only 3:4 is shown in supplied exports; verify alternatives live before --allow-unverified-parameters")
    if not re.fullmatch(r"[1-9][0-9]*:[1-9][0-9]*", args.aspect_ratio):
        raise ValueError("aspect ratio must be positive W:H")
    for key, value in (("prompt", prompt.strip()), ("resolution", args.resolution), ("aspectRatio", args.aspect_ratio)):
        generator["widgets_values"][spec["widgets"][key]] = value
    generator["title"] = args.title or "图像生成"
    output["title"] = "生成结果"
    output["widgets_values"][0] = "RunningHubApp"
    original_loader = copy.deepcopy(loader)
    image_parameters = []
    for index in range(args.images):
        image_number = index + 1
        image_name = args.image_name[index] if args.image_name else f"UPLOAD_IMAGE_{image_number:02d}.png"
        if not image_name or image_name != Path(image_name).name or any(c in image_name for c in ("/", "\\", ":")):
            raise ValueError("--image-name accepts a platform-uploaded file name, not a URL or local path")
        if index == 0:
            current = loader
        else:
            current = copy.deepcopy(original_loader)
            graph["last_node_id"] += 1
            graph["last_link_id"] += 1
            current["id"] = graph["last_node_id"]
            current["pos"] = [loader["pos"][0], loader["pos"][1] + 365 * index]
            current["outputs"][0]["links"] = [graph["last_link_id"]]
            for output_ in current["outputs"][1:]:
                output_.pop("links", None)
            target_slot = next(i for i, p in enumerate(generator["inputs"]) if p["name"] == f"image{image_number}")
            generator["inputs"][target_slot]["link"] = graph["last_link_id"]
            graph["links"].append([graph["last_link_id"], current["id"], 0, generator["id"], target_slot, "IMAGE"])
            graph["nodes"].append(current)
        label = args.image_label[index] if args.image_label else ("上传照片" if args.images == 1 else f"上传图片{image_number}")
        current["title"] = label
        current["order"] = index
        current["widgets_values"][0] = image_name
        image_parameters.append({"label": label, "node_id": current["id"], "node_type": "LoadImage",
                                 "widget_name": "image", "widget_index": 0, "generator_socket": f"image{image_number}",
                                 "default_value": image_name, "requires_upload": not bool(args.image_name),
                                 "note": "Upload or select the explicitly authorized original source in this exact node."})
    generator["order"] = args.images
    output["order"] = args.images + 1
    for group in graph.get("groups", []):
        group["title"] = args.title or "RunningHub 图生图应用"
        group["bounding"][3] = max(group["bounding"][3], 440 + 365 * (args.images - 1))
    validate_graph(graph)
    graph_path = args.output.resolve()
    mapping_path = args.mapping.resolve() if args.mapping else graph_path.with_suffix(".parameters.json")
    protected_paths = [template_path.resolve()] + [p.resolve() for p in (ROOT / "assets" / "workflows").glob("*.json")]
    if graph_path == mapping_path or graph_path in protected_paths or mapping_path in protected_paths:
        raise ValueError("Outputs must be distinct and must not overwrite bundled templates/provenance")
    if any(p.name in {"runninghub的Nanobanana2.1图生图2k.json", "runninghub的GPT2图生图2k.json"}
           for p in (graph_path, mapping_path)):
        raise ValueError("Refusing to overwrite a user source filename")
    if (graph_path.exists() or mapping_path.exists()) and not args.overwrite:
        raise ValueError("Output exists; choose a fresh run directory or explicitly use --overwrite")
    exposed = image_parameters + [
        {"label": "画面分辨率", "node_id": generator["id"], "widget_name": "resolution",
         "widget_index": spec["widgets"]["resolution"], "default_value": args.resolution,
         "allowed_values": "Read current node/publish selector; do not invent a list"},
        {"label": "画面比例", "node_id": generator["id"], "widget_name": "aspectRatio",
         "widget_index": spec["widgets"]["aspectRatio"], "default_value": args.aspect_ratio,
         "allowed_values": "Read current node/publish selector; do not invent a list"},
    ]
    mapping = {
        "schema_version": 1, "model": args.model, "workflow_format": "ComfyUI UI v0.4",
        "source_template": spec["file"], "source_sha256": spec["sha256"],
        "verification": {"static_graph": "passed", "live_inventory": "not_checked", "runtime": "not_run"},
        "image_node": {"id": generator["id"], "type": spec["node_type"], "widget_order": spec["widgets"]},
        "expose_as_application_inputs": exposed,
        "fixed_prompt": {"node_id": generator["id"], "widget_name": "prompt", "widget_index": spec["widgets"]["prompt"],
                         "expose": False, "note": "Fixed-effect app: keep hidden. For variable concepts wire a separately verified text composition node; this script does not fabricate one."},
        "output": {"node_id": output["id"], "node_type": "SaveImage", "source": [generator["id"], 0]},
        "publish_configuration": {"publish_mode": "AI application", "sync_ai_site": True,
                                  "trial": "Run published application once, then publish that generated result to community"},
        "warnings": ["Both source filenames say 2k but their original resolution is 1k; generated default is explicitly 2k.",
                     "No quality/Medium widget exists in either supplied node.",
                     "Nano widget names except image sockets are inferred from supplied widget values; confirm labels in live UI before binding.",
                     "Empty api_config remains disconnected. Never insert an account secret into this template.",
                     "Uploading JSON or passing static validation does not prove runtime or publication success."],
    }
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    dump_json(graph_path, graph)
    dump_json(mapping_path, mapping)
    return {"workflow": str(graph_path), "parameter_mapping": str(mapping_path), "nodes": len(graph["nodes"]),
            "links": len(graph["links"]), "model": args.model, "resolution": args.resolution,
            "aspectRatio": args.aspect_ratio, "status": "static-only; import, source upload and runtime still required"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=TEMPLATES, default="gpt-image-2")
    prompt = parser.add_mutually_exclusive_group(required=True)
    prompt.add_argument("--prompt", help="Fixed transformation instructions only")
    prompt.add_argument("--prompt-file", type=Path, help="UTF-8 fixed prompt")
    parser.add_argument("--resolution", default="2k", help="Exact case-sensitive node value (default: 2k)")
    parser.add_argument("--aspect-ratio", default="3:4")
    parser.add_argument("--allow-unverified-parameters", action="store_true",
                        help="Permit parameters beyond the supplied/default values, only after checking the live UI")
    parser.add_argument("--images", type=int, default=1)
    parser.add_argument("--image-name", action="append", help="Already uploaded platform file name; repeat for every image")
    parser.add_argument("--image-label", action="append", help="Chinese input label; repeat for every image")
    parser.add_argument("--title", default="")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mapping", type=Path, help="Default: OUTPUT.parameters.json")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated outputs, never templates")
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, StopIteration, json.JSONDecodeError) as exc:
        print(f"prepare_workflow: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
