# ComfyUI workflow formats

Read this reference before authoring or modifying workflow JSON.

## UI workflow JSON

The UI graph stores visual nodes, positions, sizes, widget values, links, groups, and frontend metadata. Current ComfyUI documentation defines Workflow JSON v1.0 and also documents legacy v0.4. Preserve the version of a supplied working export unless there is a concrete reason to migrate it.

Official schemas:

- v1.0: <https://docs.comfy.org/specs/workflow_json>
- v0.4: <https://docs.comfy.org/specs/workflow_json_0.4>

For a new graph, prefer the version demonstrably accepted by the target platform. Do not mechanically add `version: 1` to a v0.4 graph; the structures differ.

Important invariants:

- node IDs are unique;
- link IDs are unique;
- every link source and target node exists;
- node input/output link references agree with the top-level link records;
- node socket types and indexes match the installed node definition;
- `widgets_values` follows the exact widget order for that node version.

Widget order is the main reason arbitrary hand-written UI JSON can look valid but import incorrectly. Use a known-good exported node whenever possible.

## API prompt format

API format is an execution graph keyed by node ID. Each node normally contains `class_type` and `inputs`; a connection is represented as `[source_node_id, output_index]`. It omits UI layout and is not interchangeable with the UI workflow JSON.

Official overview: <https://docs.comfy.org/development/cloud/overview>

Example shape:

```json
{
  "3": {
    "class_type": "KSampler",
    "inputs": {
      "model": ["4", 0],
      "seed": 42,
      "steps": 24
    }
  }
}
```

Do not infer API input names from UI labels. Export API format from a compatible frontend or derive it from confirmed backend node definitions.

## Editing supplied workflows

Preserve unknown top-level and node properties unless the target rejects them. Change the smallest possible surface. When replacing a node, re-check all incoming and outgoing socket indexes and regenerate its widget values from a confirmed target definition.

## Compatibility report shape

Use a compact structure that can be extended without breaking readers:

```json
{
  "generated_at": "ISO-8601 timestamp",
  "logical_workflow": "short name",
  "format": "ui-v0.4 | ui-v1.0 | api",
  "targets": {
    "seaart": {"status": "structural-only", "evidence": []},
    "runninghub": {"status": "variant-required", "evidence": []},
    "liblib": {"status": "structural-only", "evidence": []}
  },
  "nodes": [],
  "resources": [],
  "placeholders": [],
  "runtime_tests": []
}
```

Allowed status meanings:

- `verified`: inventory confirmed and representative runtime succeeded;
- `structural-only`: static graph checks passed, runtime/resources not fully confirmed;
- `variant-required`: a documented adapter file is required;
- `unsupported`: a required capability is unavailable or no safe mapping exists.
