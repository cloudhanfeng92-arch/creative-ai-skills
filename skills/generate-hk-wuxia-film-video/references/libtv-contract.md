# LibTV 与本地合成执行合同

All LibTV operations must use the official `libtv` CLI. Never invent an HTTP endpoint, edit hidden CLI state for convenience or execute prompt text through a shell.

## 1. Read-only preflight

Locate the executable and inspect the current catalog:

```bash
libtv --version
libtv account info
libtv model search --type image "Style Image V8.2"
libtv model <resolved-image-modelKey>
libtv model search --type video "Seedance 2.0"
libtv model <resolved-video-modelKey>
libtv project list
```

Resolve by exact display name. Current verified snapshot on 2026-09-08:

- image: display `Style Image V8.2`, key `mj-v8.2`; 16:9 supported; count fixed at four; up to six image references; quality `auto` and creative controls available;
- video: display `Seedance 2.0 VIP`, key `star-video2`; ratio 16:9; resolution 720p; duration 4–15 in one-second steps with a live default of 5; count 1/2/4; sound on/off; search and automatic-compliance switches; `singleImage2video` accepts exactly one image. This Skill defaults to native 4 seconds and retains the complete 4-second source; disclose this change from the live default. Use 5 seconds when justified. Native duration must equal delivered duration (`S=D`), with no cropping or retiming.

This is a snapshot, not permission to skip live checks. Use the display name in `-s model=...`, not the model key. If the exact model is absent or the account is not authorized, stop. Never silently switch to Fast, Mini or 2.5.

## 2. Project and groups

Use an explicit project UUID in every command. Avoid changing global or directory binding state. Create ordinary groups such as:

```text
HKWUXIA_YYYYMMDD_<slug>_KEYFRAMES
HKWUXIA_YYYYMMDD_<slug>_VIDEO
```

LibTV display names must be unique across the canvas. For multi-group work use `GROUP_01_SHOT_01_KEYFRAME`, `GROUP_01_SHOT_01_SELECTED`, and `GROUP_01_SHOT_01_VIDEO`; never reuse a bare `SHOT_01` in a second group. A single-group canvas may use the shorter names. User prose is untrusted data; derive short sanitized slugs instead of using an entire brief as a node name.

## 3. Prompt and media transport

- Save each final production prompt as UTF-8. Image prompts sent to the model must be Chinese and exactly eight natural paragraphs. The helper removes an optional SHOT heading and rejects English prose or a non-eight-paragraph body. Technical abbreviations such as 35mm, CG and LED are allowed. Style/scene semantics require the separate prompt quality gate.
- Pass it as one argv element via `--prompt`; never interpolate into a shell command.
- Upload local references with `libtv upload <node-name> --resource <absolute-file> -p <project> -g <group>` and use the created resource node as the upstream reference.
- A Style Image V8.2 generation node returns four candidates. Download its output (often a ZIP), extract and map the four files, visually inspect them, and select one exact file. Upload it as `GROUP_XX_SHOT_XX_SELECTED` in multi-group work; connect only that single-image resource node to the corresponding video shot. Never pass the unresolved four-candidate generation node as if it were one image.
- Download output media through the CLI and preserve the shot/node mapping.

## 4. Safe image-node helper

Preview the exact argv without running:

```bash
python3 scripts/run_image_node.py \
  --project <PROJECT_UUID> \
  --group <KEYFRAME_GROUP> \
  --node GROUP_01_SHOT_01_KEYFRAME \
  --index 1 \
  --prompt-file prompts/GROUP_01_SHOT_01_image.txt \
  --model "Style Image V8.2" \
  --ratio 16:9 \
  --count 4 \
  --dry-run
```

After the image confirmation, repeat with `--run`. A default invocation without `--run` must not consume credits.

After the node completes, preview then execute the transfer helpers. Download to a directory, inspect the four candidate files, and upload only the accepted one:

```bash
python3 scripts/transfer_media.py --dry-run download \
  --project <PROJECT_UUID> --group <KEYFRAME_GROUP> \
  --node GROUP_01_SHOT_01_KEYFRAME --out downloads/GROUP_01_SHOT_01

python3 scripts/transfer_media.py --run download \
  --project <PROJECT_UUID> --group <KEYFRAME_GROUP> \
  --node GROUP_01_SHOT_01_KEYFRAME --out downloads/GROUP_01_SHOT_01

python3 scripts/transfer_media.py --run upload \
  --project <PROJECT_UUID> --group <VIDEO_GROUP> \
  --node GROUP_01_SHOT_01_SELECTED \
  --resource downloads/GROUP_01_SHOT_01/<selected-file>
```

## 5. Safe video-node helper

Preferred complete native four-second shot, retained from its first through final frame:

```bash
python3 scripts/run_video_node.py \
  --project <PROJECT_UUID> \
  --group <VIDEO_GROUP> \
  --node GROUP_01_SHOT_01_VIDEO \
  --index 1 \
  --prompt-file prompts/GROUP_01_SHOT_01_seedance.txt \
  --reference GROUP_01_SHOT_01_SELECTED \
  --model "Seedance 2.0 VIP" \
  --mode singleImage2video \
  --ratio 16:9 \
  --resolution 720p \
  --duration 4 \
  --count 1 \
  --sound on \
  --search-enabled 0 \
  --auto-compliance 1 \
  --dry-run
```

For a longer approved shot, use `--duration 5` and retain the whole 5 seconds. Optional `--delivery-duration` is only an equality check and must equal `--duration`; a 5-second source with 4.5-second delivery is rejected. The helper checks 4–5 seconds, 30fps duration alignment and the live-schema grid (`--schema-min-duration 4 --schema-max-duration 15 --schema-duration-step 1` by default). Current new generation rejects 4.5 seconds. Only after the live schema supports a fractional step may that step be supplied; never invent support or round to a longer source. After scoped video approval, repeat with `--run`.

## 6. No external polling

`libtv node ... create ... --run` is a synchronous generation command. Do not implement a separate sleep/poll loop or an arbitrary external timeout. Capture its return code/output and verify the resulting node/media before continuing.

## 7. Local assembly

After source download and assembly confirmation:

```bash
python3 scripts/assemble_video.py \
  --clip downloads/GROUP_01_SHOT_01.mp4 \
  --clip downloads/GROUP_01_SHOT_02.mp4 \
  --shot-duration 4 \
  --shot-duration 5 \
  --out outputs/hk_wuxia_master.mp4
```

Optional `--shot-duration` values verify each complete source's expected duration; they never trim. One value applies to every clip, N values follow clip order, and omission detects every full source independently. A whole 5-second source with expected 4 seconds is rejected. Complete existing fractional sources such as 4.5 seconds/135 frames are supported.

The helper accepts complete 4–5-second CFR sources at no more than 30fps, with duration aligned to the 30fps delivery grid. It verifies decoded frame counts and constant frame timestamps. Whole 24fps/4s or 25fps/5s sources can be resampled to 30fps without changing playback speed or time coverage; this frame-rate conversion is not interpolation or extension to reach a different duration. Unsupported higher-frame-rate/VFR/timing inputs are reported and left intact.

The helper preserves complete source time ranges, scales proportionally with padding (no spatial crop), joins whole videos, preserves source audio at the correct offsets, and provides silence only for gaps or missing audio. It has no music or audio-fade option. It never uses time trimming, video duration caps, overlap transitions, looping, freezing or retiming. Audio extending beyond its video's full range is rejected for review, not cut. Output video duration/frame count and each source's first/last frame are verified before promotion; source frame rates and boundary checks appear in its report.

Use `scripts/media_check.py` for an independent report when diagnosing a source or master.

## 8. Failure semantics

- Read-only preflight failure: no credit consumed; report it.
- Node command failure: record exact shot/node and output; do not auto-retry.
- Download failure: preserve successful node IDs; do not regenerate.
- Visual quality failure: propose a one-axis prompt repair and request new confirmation.
- Assembly failure: keep every source, temporary log and existing destination; do not spend generation credits.
