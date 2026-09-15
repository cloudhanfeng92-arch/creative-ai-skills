---
name: image-to-video-prompt-and-generate
description: Analyze a user-supplied image, write an image-to-video prompt that matches its subjects, composition, style, and plausible motion, obtain explicit user approval, then generate a video in first-frame-reference mode with Seedance 2.0 by default. Use when the user asks to animate an image, turn a photo or illustration into video, create a matching image-to-video prompt, use an image as the first frame, or generate a Seedance image-to-video clip. Never generate before the user confirms the proposed prompt.
---

# Image-to-video prompt and generation

Follow the sequence below without skipping the approval gate.

## 1. Collect the source and intent

- Require at least one user-supplied image. If it is missing or inaccessible, ask the user to attach it and stop.
- Treat the designated image as the exact first frame. Do not redraw, restyle, enhance, crop, or replace it unless the user explicitly asks.
- Follow any stated story, action, camera, duration, aspect ratio, platform, or model requirements. Otherwise infer a restrained motion concept from the image.
- If several images are attached and the first frame is ambiguous, ask which one to use. Do not silently combine them.

## 2. Inspect the image

Visually inspect the actual image before drafting. Identify:

- primary subjects, appearance, pose, gaze, and spatial relationships;
- setting, depth layers, composition, lighting, weather, and color palette;
- medium and visual style, such as live action, CGI, anime, ink, or product photography;
- elements that can move naturally, including hair, clothing, foliage, water, smoke, light, reflections, particles, vehicles, or background figures;
- identity anchors that must remain stable, especially faces, bodies, hands, products, logos, text, architecture, and costume details;
- likely failure risks such as occlusion, tiny hands, embedded text, reflections, crowd motion, or extreme camera movement.

Describe only visible evidence. Mark uncertain interpretations as inferences and avoid inventing hidden objects, identities, brands, or story facts.

## 3. Design motion that belongs to the frame

- Default to one coherent continuous shot with no cut, teleportation, unexplained transformation, or new major subject.
- Begin from the supplied image exactly, then introduce motion progressively.
- Give the main subject one clear, physically plausible action. Add only subtle supporting environmental motion.
- Choose camera motion that suits the composition: locked camera, gentle push-in, slow pull-back, small pan, orbit, tilt, handheld drift, or subject tracking. Keep it restrained when identity or geometry is fragile.
- Preserve the original art direction, palette, lighting logic, proportions, and scene geography throughout.
- Protect faces, anatomy, text, logos, product geometry, and distinctive costume or architectural details from drift.
- Use stronger action, transformations, cuts, or large camera moves only when the user requests them and the image can support them.

## 4. Draft the generation proposal

Write the prompt in the user's language unless the selected generator requires another language. Make it directly usable, not an explanation. Include, in natural prose:

1. exact continuity from the first frame;
2. primary subject action and its pace;
3. secondary environmental motion;
4. camera movement and framing behavior;
5. lighting, texture, and style continuity;
6. ending state or final beat;
7. concise stability constraints when needed.

Avoid keyword piles, conflicting camera directions, vague praise, and motion unsupported by the image.

Present exactly this approval packet before generating:

```text
画面识别：<brief factual analysis>

图生视频提示词：
<complete generation-ready prompt>

生成设置：
- 模式：首帧参考
- 模型：Seedance 2.0（默认）
- 时长：<user value or chosen tool default>
- 画幅：<user value or preserve source aspect ratio>

请确认是否按以上提示词和设置生成。回复“确认生成”即表示批准此提示词，并授权生成 1 次视频；如需修改，请直接告诉我修改内容。
```

Do not call any video-generation tool in the same turn as the initial proposal.

## 5. Enforce the confirmation gate

- Accept an unambiguous approval such as “确认生成”, “按这个生成”, or “开始生成” only when it clearly refers to the latest proposal.
- Treat requested edits, questions, tentative language, or silence as non-approval. Revise the packet and ask again after any material change to the prompt or settings.
- The approval authorizes exactly one generation attempt using the displayed prompt and settings. Do not add material creative changes after approval.
- If another applicable generator workflow has its own confirmation requirement, this explicit approval may satisfy it only when it approves the same prompt, settings, and single credit-consuming attempt. Obey stricter tool or platform requirements.

## 6. Generate from the confirmed first frame

- Prefer the platform explicitly named by the user. Otherwise select an available generator that supports first-frame image-to-video and Seedance 2.0.
- Use first-frame-reference/image-to-video mode, not text-to-video, end-frame, or all-around-reference mode.
- Pass the original designated image as the first frame and the approved prompt verbatim except for strictly necessary API formatting.
- Default to Seedance 2.0. Change models only when the user explicitly requests another model or Seedance 2.0 is unavailable; disclose and obtain approval for any substitution before generating.
- Preserve the source aspect ratio when supported. If the platform forces a different ratio or consequential crop, disclose it and obtain approval first.
- Use the user's duration. If none was supplied, use the selected tool's default and show that choice in the approval packet.
- Do not auto-retry, upscale, extend, regenerate, or create variants after a failure or unsatisfactory result. Show what happened and request fresh approval for another credit-consuming attempt.

## 7. Deliver the result

Return the generated video or a direct artifact link. State the mode, model, duration, and the exact prompt used. Briefly mention any non-creative formatting imposed by the generator. If generation is unavailable, do not claim success; provide the approved prompt and explain the concrete limitation.
