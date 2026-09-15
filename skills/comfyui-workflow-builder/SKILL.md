---
name: comfyui-workflow-builder
description: Create, adapt, inspect, and validate portable ComfyUI workflow JSON packages from user requirements, especially workflows intended for SeaArt, RunningHub, LiblibAI, or local ComfyUI. Use for text-to-image, image-to-image, ControlNet, inpainting, upscaling, batch, video, audio, or API-ready ComfyUI graph requests. Do not use for merely writing image prompts when no workflow is requested.
---

# ComfyUI Workflow Builder

Turn the user's goal into an importable, understandable workflow package. Portability means verified shared structure plus explicit resource mappings; it does not mean pretending every cloud platform has the same models, node versions, or file names.

## Choose the compatibility target

Use the narrowest honest target:

1. **One shared JSON** only when all required node types, models, widget layouts, and I/O behavior are confirmed on every target.
2. **Common core plus platform variants** by default when the graph is portable but model names or adapter nodes differ. Keep topology and stable node IDs aligned where practical.
3. **Platform-specific workflow** when the request depends on a hosted API node, proprietary model, hidden upload node, or unsupported custom node. Explain why a universal file is not possible and provide the closest portable fallback.

Read [references/portability.md](references/portability.md) before targeting SeaArt, RunningHub, or LiblibAI. Read [references/workflow-formats.md](references/workflow-formats.md) before creating or editing JSON.

## Resolve the request

Extract these decisions from the prompt or supplied artifacts:

- task and success criteria;
- inputs and outputs, including count, dimensions, format, and alpha or audio requirements;
- base model family and exact models or LoRAs if specified;
- structural controls such as ControlNet, IP-Adapter, masks, identity, pose, or reference images;
- quality, speed, VRAM, batch, and reproducibility constraints;
- target platforms and whether the workflow is for interactive import, publishing, or API execution.

Ask only when a missing answer changes the graph materially and cannot be inferred safely. Otherwise choose conservative defaults and list them in the delivery notes. Never silently substitute a different model family, paid API node, or platform service.

If the user supplies a workflow, screenshot, exported JSON, platform link, node inventory, or error log, inspect it before designing. Treat an exported working workflow from the target platform as the strongest source for node type names, widget order, and platform adapters.

## Build the graph

Design the logical graph first: inputs -> loaders -> conditioning/control -> sampling or processing -> decode/postprocess -> preview/save. Give each stage a clear title or group and expose only controls the user should edit.

For the common core:

- prefer ComfyUI core nodes and ordinary data connections;
- keep platform upload, API, billing, translation, cache-clearing, and hidden helper nodes out of the core;
- avoid absolute local paths, credentials, tokens, account IDs, signed URLs, embedded private data, and machine-specific output folders;
- separate model/resource selection from processing logic;
- use deterministic seeds when reproducibility is requested; otherwise make seed behavior explicit;
- include at least one visible or saved output path through the graph;
- use placeholders only when the exact resource name is unknown, and make every placeholder conspicuous and documented.

Use custom nodes only when they materially improve or enable the requested result. For each one, record node type, package/repository when known, purpose, version or commit when known, required models, and a core-node fallback or the fact that none exists.

Do not invent a node's `class_type`, socket names, widget order, model filename, or platform availability. Obtain them from a supplied export, a live `/object_info` or equivalent inventory, installed source code, or current official documentation. If none is available, deliver a topology/specification rather than falsely labeling fabricated JSON as runnable.

## Create the deliverables

For an importable workflow, produce:

- `workflow.json`: ComfyUI UI graph with readable layout, groups/titles, and editable widgets;
- `workflow_api.json` when API use is requested, using API prompt format rather than renaming the UI export;
- `compatibility.json`: targets, status (`verified`, `structural-only`, `variant-required`, or `unsupported`), node dependencies, resource mappings, placeholders, and reasons;
- `使用说明.md`: inputs, editable nodes, model installation/mapping, recommended settings, expected outputs, and import/run steps;
- platform variants such as `workflow.seaart.json`, `workflow.runninghub.json`, and `workflow.liblib.json` when needed.

Do not claim runtime verification unless the workflow was actually imported and queued successfully in that environment. Distinguish these checks:

- **schema/static verified**: JSON structure, IDs, links, and references pass local validation;
- **inventory verified**: every node type and named resource is present in a captured target inventory;
- **runtime verified**: the target accepted and executed the graph.

## Validate

Run the bundled checker on every JSON graph:

```bash
python3 scripts/validate_workflow.py path/to/workflow.json
python3 scripts/validate_workflow.py path/to/workflow.json --inventory path/to/platform-inventory.json
```

The inventory file may be a JSON array of supported node type names or an object whose values are arrays, for example `{"seaart": [...], "runninghub": [...], "liblib": [...]}`. The checker performs static consistency checks; it cannot prove model availability or execution success.

Also verify manually that:

- UI and API files are not confused;
- all model families match their text encoders, latent formats, VAEs, samplers, and control models;
- dimensions satisfy the model's constraints and practical compute limits;
- masks use the intended polarity and resolution;
- batch/list semantics are consistent;
- all outputs are reachable;
- platform variants differ only where the compatibility report says they do.

When a target UI or API is available and the user authorized execution, import and run the cheapest representative test. Stop after a successful representative run or after a concrete incompatibility is established; do not consume repeated paid runs merely to tune aesthetics without user direction.

## Handoff

Lead with what is ready and the exact compatibility level. List unresolved model or node mappings plainly. Include a compact node map and the few parameters users are expected to change. If only a specification could be produced, say exactly which export, inventory, or resource name is needed to turn it into runnable JSON.
