# Cross-platform portability

Read this reference when targeting SeaArt, RunningHub, LiblibAI, or more than one ComfyUI host.

## Compatibility model

Assess four layers separately:

| Layer | What must match | Safe response to uncertainty |
|---|---|---|
| Graph format | UI workflow schema or API prompt format | Export both formats when API use is required |
| Node interface | exact node type, inputs, outputs, and widget order | verify from a target export or node inventory |
| Resources | exact checkpoint, LoRA, VAE, ControlNet, encoder, and upscaler names | create per-platform resource mappings or placeholders |
| Runtime | versions, GPU limits, timeouts, content rules, proprietary adapters | label as unverified until a representative run succeeds |

A matching display label is not evidence that two nodes share the same internal type or widget layout. A model family name is not an exact resource mapping.

## Portable baseline

Prefer small graphs built from ordinary ComfyUI primitives such as image loading, checkpoint/model loading, text encoding, latent creation or VAE encoding, sampling, VAE decoding, preview, and save. Even core nodes must be checked against the target version when their inputs or widgets have changed.

Avoid in the common file unless verified everywhere:

- host-prefixed upload/download nodes;
- proprietary hosted-model or paid API nodes;
- hidden nodes inserted by a publishing platform;
- browser-only widgets or extensions that do not affect backend execution;
- custom loop, switch, bus, pipe, cache, translation, or metadata nodes when simple connections can replace them;
- file paths or resource names copied from one account.

## Platform notes

These notes are routing guidance, not permanent claims about current inventories. Platform catalogs change, so refresh official information or inspect a current export for real delivery work.

### SeaArt

SeaArt exposes a ComfyUI editor with workflow import/save/publish behavior and a node library. Confirm the exact node and model inventory in the user's current workspace. Do not assume a community workflow proves that every account or region has the same resources.

Current official starting point: <https://www.seaart.ai/articleDetail/d26v0sde878c73f4ep1g>

### RunningHub

RunningHub workflows may include host-specific nodes, including upload/API helpers. Keep `RH...` or other host-provided nodes in a RunningHub adapter unless their presence on other targets is independently verified. A workflow page's node information is useful evidence for that workflow, not a global availability list.

Current official site: <https://www.runninghub.ai/>

### LiblibAI

LiblibAI supports running ComfyUI workflows and exposes workflow-based API applications, but published workflows can depend on community custom nodes and account-bound resources. Keep application/API bindings separate from the portable processing graph.

Current official references:

- <https://www.liblib.art/apis/workflow>
- <https://insight.liblib.art/teaching/54eb95c2d65645c8ab712feba9b0d96d>

## Inventory capture

Prefer evidence in this order:

1. a workflow successfully exported from the exact target workspace;
2. the target's current node inventory or backend object-info response;
3. installed custom-node source and version;
4. current official platform documentation;
5. a recent official/community workflow page showing the exact node;
6. user recollection or name similarity.

Record the capture date and source in `compatibility.json`. If only lower-confidence evidence is available, use `structural-only` or `variant-required`, not `verified`.

## Variant discipline

Keep one logical node map and document substitutions, for example:

```json
{
  "logical_id": "load_base_model",
  "common_type": "CheckpointLoaderSimple",
  "seaart": {"resource": "platform-visible-name"},
  "runninghub": {"resource": "different-visible-name"},
  "liblib": {"resource": "another-visible-name"}
}
```

If a platform adapter changes semantics rather than only resource names or I/O, describe it as a separate branch, not an equivalent substitution.
