---
name: ue5-mecha-transformation-video
description: Create a fixed 15-second UE5 photorealistic 3D CGI mecha-transformation video from a user-uploaded character image and optional text describing the target mecha and monster. Use for giant-mecha transformations, cyberpunk high-magic armor sequences, inverted free-fall transformations, one-take Seedance 2.0 reference-to-video generation, or requests that must preserve the exact supplied action, camera, and timing sequence while replacing only character and creature visual identities.
---

# UE5 Mecha Transformation Video

Turn one uploaded character reference and a short design brief into a character-specific mecha reference image, a locked-format Chinese image-to-video prompt, and one 15-second Seedance 2.0 video.

## Non-negotiable lock

Read [references/locked-video-prompt.md](references/locked-video-prompt.md) before drafting or generating anything.

Preserve all of these exactly:

- Every time range, action, direction, pose, transformation beat, camera transition, and event order.
- The inverted free-fall state, inward red-orange digital-cube vortex, 1:1 armor outline, explosive enlargement to 60 meters, front flip, one-knee landing, and confrontation with a 120-meter monster.
- The UE5 photorealistic 3D CGI, cyberpunk high-magic mecha, rainy night, cyan-orange IMAX look, handheld breathing, and one-take treatment.
- The 15-second duration, 720p resolution, and 16:9 ratio.

Only substitute visual identity variables:

- The uploaded character's identity, apparent age, face, hair, clothing motifs, accessories, and distinctive details.
- The target mecha's appearance, materials, colors, energy system, symbols, and carried-over character motifs.
- The monster's appearance, materials, colors, anatomy, and energy system.
- Names and concise appearance descriptions in `出场人物` and visual-style descriptions where necessary to keep the chosen design consistent.

Do not add, remove, merge, split, reorder, shorten, or extend shots. Do not invent a 14–15 second action. Do not change motion verbs to stylistic alternatives. Do not change the 60-meter mecha or 120-meter monster scale unless the user explicitly asks to revise the locked choreography.

## Credit gate

Treat image and video generation as credit-consuming actions.

1. Analyze and draft without confirmation.
2. Before the first image generation, show the design summary, exact image prompt, model, ratio, and image count; ask for explicit confirmation.
3. After inspecting the generated image, show the final locked video prompt and video settings; ask for explicit confirmation before video generation.
4. Ask again before every retry, alternate model run, or additional output.

Do not interpret approval for image generation as approval for video generation.

## Workflow

### 1. Inspect input

- Require at least one character image. If no image is attached or accessible, stop and ask the user to upload it.
- Inspect the image directly. Record identity anchors: facial structure, hairstyle, body proportions, outfit silhouette, palette, accessories, visible materials, and any emblem.
- Parse the text brief for target mecha and monster details. If details are sparse, infer them from the character while retaining the locked white/black/gold/cyan and dark-steel/blue/red contrast as the default.
- Ask only when a missing choice would materially change the design. Otherwise proceed with a stated assumption.
- Do not infer sensitive personal attributes. Use visible, non-sensitive appearance descriptions.

### 2. Produce a compact design bible

Write four blocks:

1. `角色身份锁定`: immutable visible traits from the upload.
2. `60米机甲设计`: silhouette, armor, materials, palette, core, lights, carried-over motifs.
3. `120米怪兽设计`: silhouette, anatomy, material, eyes, energy pathways, threat profile.
4. `一致性锚点`: 5–8 short phrases that must recur in both image and video prompts.

Keep design nouns concrete. Do not alter the action timeline.

### 3. Draft the mecha reference image

Create one 16:9 design reference that makes the 60-meter mecha and 120-meter monster visually unambiguous while preserving the uploaded character's motifs. Use the uploaded character image as an upstream reference.

Image prompt structure:

```text
以 @image_1 上传角色为唯一人物身份与服装母题参考，设计其专属60米巨型机甲，并同时明确120米对手机械怪兽的外形。保留角色的[身份锚点]，把[服装/配饰母题]转译为[机甲装甲语言]。机甲：[完整设计]。怪兽：[完整设计]。UE5超写实3D CGI，赛博朋克高魔机甲风，雨夜废墟与暗绿云海，幽冷青绿环境光对比炽烈橙红能量光，重工业磨损钢铁，真实物理材质与流体，Lumen全局光照，高精度粒子，IMAX胶片摄影，青橙低饱和。16:9横构图，完整清晰轮廓，人物母题、机甲和怪兽的设计关系明确，无文字，无水印，无拼贴，无多余角色。
```

Choose the model dynamically in this order:

1. Search for `Lib Image` and `GPT Image 2`. Use either available primary model; prefer `Lib Image` when both are available unless the user's brief benefits materially from GPT Image 2.
2. If neither primary model is available or the primary generation fails, offer `General image Pro` as the fallback.
3. Never silently switch to the fallback or retry; return to the credit gate.

Default image settings: one image, 16:9, high quality, 2K when supported.

### 4. Generate and inspect the image

Use LibTV CLI for all LibTV canvas, model, upload, node, and generation operations. Read the installed `libtv-cli` skill if its detailed command contract is needed. Follow [references/libtv-execution.md](references/libtv-execution.md).

After explicit image approval:

- Upload the character reference to the bound canvas.
- Create a uniquely named image-generation node, connect the character reference, set the chosen model and supported parameters, and run it synchronously.
- Wait for `libtv node ... --run` to exit. Do not add polling or an external timeout.
- Inspect the resulting image. Check identity motifs, full mecha silhouette, monster design, palette, readable energy core, and absence of unwanted text/collage.
- If unusable, explain the concrete defect and request approval for one revised generation.

### 5. Fill the locked video prompt

Copy [references/locked-video-prompt.md](references/locked-video-prompt.md) and replace every bracketed variable. Bind references as:

- `@image_1`: the user's uploaded character, always the protagonist and identity authority.
- `@image_2`: the approved generated mecha/monster design image, the design authority.

Keep the exact headings and sequence. Ensure each design variable uses the same nouns as the design bible and reference image. Do not paraphrase locked choreography.

Present the entire final prompt plus these settings for approval:

- Model: `Seedance 2.0 VIP` (`Seedance 2.0` family)
- Mode: `mixed2video`
- Duration: `15`
- Resolution: `720p`
- Ratio: `16:9`
- Count: `1`
- Sound: `on` by default; change only if the user asks

### 6. Generate the video

After explicit video approval:

- Search the live model catalog and resolve the current Seedance 2.0 model name and schema.
- Upload or connect both approved references.
- Create the video node with the approved full prompt and exact settings.
- Run synchronously and wait for terminal JSON.
- Report the result node or output path and the exact model/settings used.
- Do not claim that the timing is correct without reviewing the produced video when a viewable result is available.

## Quality checklist

Before image generation:

- Character identity anchors are concrete.
- Mecha and monster designs are specific and mutually distinct.
- The image prompt uses the character upload as its reference.

Before video generation:

- The timeline text matches the locked template character-for-character except bracketed visual variables.
- `@image_1` remains the protagonist; `@image_2` is the approved design reference.
- All 0–14 second time ranges remain unchanged and ordered.
- The 1:1 armor stage and 0.5-second explosive enlargement remain explicit.
- Mecha and monster scales remain 60 meters and 120 meters.
- Settings are 15 seconds, 720p, 16:9, one output.
- The user has explicitly approved this video generation.

