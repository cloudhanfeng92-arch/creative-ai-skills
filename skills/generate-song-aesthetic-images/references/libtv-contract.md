# LibTV rendering contract

LibTV CLI help and the live model schema are authoritative. The verified snapshot used to design this skill was CLI 1.1.3 with the image-model listing `Style Image V8.2` (`modelKey: mj-v8.2`). At that snapshot the schema supported `ratio=16:9`, fixed `count=4`, `stylize` in steps of 50, and up to six image references. Re-resolve these values at runtime because they may change.

## 1. Resolve the model and schema

Run:

```bash
libtv --version
libtv account info
libtv model search --type image "Style Image V8.2"
```

`account info` is the generation-login check; model catalog queries may succeed without a usable signed-in account. On a zero or ambiguous exact-name result, broaden discovery in this order, then strictly select the V8.2 image entry:

```bash
libtv model search --type image mj-v8.2
libtv model search --type image "Style Image"
```

Require exactly one matching V8.2 image model. From the search result:

- keep `matches[0].modelName` as the display label passed to `-s model=...`;
- keep `matches[0].modelKey` only for schema inspection;
- do not pass the `modelKey` to `-s model`.

Then inspect the full schema:

```bash
libtv model "<unique modelKey>"
```

Confirm `properties.ratio`, `properties.count`, `properties.stylize`, any reference-image limit, and any negative-prompt field. If the requested ratio is unsupported, tell the user instead of silently switching models. If authentication fails, ask the user to complete `libtv login web --open`; do not initiate a phone-login flow without their input.

Do not paste legacy prompt suffixes such as `--ar 16:9 --s 150 --v 8.2` into the prompt. Express version through the selected model and express supported controls through `-s` fields.

## 2. Choose or create a canvas without polluting the working tree

Use the current directory's bound canvas when it exists and is accessible, but parse its UUID and pass it explicitly to every mutating command. If none is bound, create a clearly named canvas and parse its returned `uuid`:

```bash
libtv project create "宋式美学-<safe run id>"
```

Do not run `libtv project use` merely for this skill: it writes `.libtv/project.json` into the current directory and may dirty an unrelated repository. Keep the parsed value as `<projectUuid>` and pass `-p "<projectUuid>"` to group, node, upload, and download commands. Use a generated alphanumeric run id in canvas, group, and node names rather than interpolating raw user text into shell commands.

Creating a canvas is part of an explicit image-generation request. Do not create canvases when the user asked only for prompt analysis.

Return the browser link after generation:

```text
https://www.liblib.tv/canvas?projectId=<projectUuid>
```

## 3. Organize the request

Use one ordinary LibTV group for a simple request or coherent series. Use separate LibTV groups only for genuinely separate sets, seasons, stories, or user-named collections. With CLI 1.1.3, create a new group explicitly:

```bash
libtv group create "<safe unique series name>" -p "<projectUuid>"
```

The default `libtv group "<name>"` command operates on an existing group; it does not create one. Choose unique group and node names so an old result is never mistaken for the current run.

## 4. Create and run image nodes

Create a new node with the current CLI syntax; do not use the obsolete `libtv node "name" -t image` form. Put each production prompt in a task-specific UTF-8 text file using a safe file-editing mechanism, then call the bundled helper. The helper invokes `libtv` with a subprocess argument vector and never evaluates prompt text as shell syntax.

```bash
python3 "<skill directory>/scripts/run_image_node.py" \
  --project "<projectUuid>" \
  --group "<safe unique series name>" \
  --node "<safe unique shot name>" \
  --index 1 \
  --prompt-file "<absolute prompt file>" \
  --model "Style Image V8.2" \
  --ratio 16:9 --count 4 --quality auto \
  --stylize 150 --weird 0 --chaos 0
```

Resolve `scripts/run_image_node.py` from this skill's actual filesystem directory. Replace the values above with the live search label, user-requested supported ratio, and schema-valid values. The helper has `--omit-*` switches for fields absent from the live schema. Never place a production prompt directly inside an interpolated shell command.

For several nodes, create and run them sequentially. `--run` submits, waits, writes the canvas result, and exits with terminal JSON. Do not background it, add a timeout wrapper, stop at a task id, or build another polling loop.

Pass the one-based shot number through `--index`; the helper automatically lays nodes out on a three-column grid, 540 pixels between columns and 420 pixels between rows. Explicit `--x` or `--y` overrides remain available when a custom layout is needed.

## 5. Reference images and continuity

Upload a user-supplied or selected local image through the CLI and connect its returned image node as an upstream reference:

```bash
python3 "<skill directory>/scripts/transfer_media.py" upload \
  --project "<projectUuid>" \
  --group "<safe unique series name>" \
  --node "<safe unique reference name>" \
  --resource "<absolute local image path>"

python3 "<skill directory>/scripts/run_image_node.py" \
  --project "<projectUuid>" \
  --group "<safe unique series name>" \
  --node "<safe unique shot name>" \
  --index 1 \
  --prompt-file "<absolute prompt file>" \
  --reference "<safe unique reference name>" \
  --model "Style Image V8.2" \
  --ratio 16:9 --count 4 --quality auto \
  --stylize 150 --weird 0 --chaos 0
```

Use no more references than the live schema permits. State whether each reference controls identity, clothing, object, composition, or visual style. Do not connect tutorial screenshots as style references when their typography and page layout would contaminate the scene; prefer the distilled style language or a clean selected scene image.

For a generated recurring character, download the first node's ZIP, unpack it in a task-specific temporary directory, inspect every candidate, select one concrete image file, and upload that file into the same series group as a dedicated reference node. By default, select it through the quality gate and continue; pause for user approval only when they explicitly asked to approve the character before the series proceeds. Do not treat a four-candidate generator node as one unambiguous identity reference, and do not add a paid character-master generation unless its extra native group was disclosed.

In later prompts, say that the selected reference controls only identity, hair, and fixed garment colors; camera, composition, pose, and action must follow the new shot. If a full-scene reference keeps copying composition, use a clean crop or a user-supplied character reference within the live six-image limit.

## 6. Download and inspect results

After generation, download a node's resources for visual inspection:

```bash
python3 "<skill directory>/scripts/transfer_media.py" download \
  --project "<projectUuid>" \
  --group "<safe unique series name>" \
  --node "<safe unique shot name>" \
  --out "<safe output directory>"
```

A multi-file image node or ordinary group may download as a ZIP; unpack it in a task-specific temporary directory. The transfer helper uses a subprocess argument vector so local paths never become shell syntax. Do not request `--without-ai-watermark` or assert VIP status unless the user explicitly asks and the account is entitled.

## 7. Handle failures

- Read the terminal JSON only after `--run` exits.
- Query the node with explicit scope when needed: `libtv node "<safe unique shot name>" -p "<projectUuid>" -g "<safe unique series name>"`.
- On a transient CLI or network error, first query whether the node exists. If it exists, retry generation once with `libtv node "<safe unique shot name>" -p "<projectUuid>" -g "<safe unique series name>" --run`; rerun `node create` only when creation never succeeded. On a schema or model-name error, re-run discovery and correct the command rather than switching models.
- If the terminal tool yields a live session id before completion, continue waiting on that same process; do not issue the generation command again.
- Never delete or overwrite unrelated nodes, groups, canvases, or user assets.
- Keep already successful nodes when a later shot fails.
