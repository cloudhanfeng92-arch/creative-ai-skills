---
name: sketchbook-doodle-illustration-mj
description: Generate modern hand-drawn illustration and cartoon text-to-image prompts and immediately render them with the Youchuan Midjourney V7 model, without a confirmation step. Use when users request sketchbook doodles, warm tactile digital illustration, thick marker or crayon linework, casual yet professional cartoon art, cute mascots, stickers, cozy scenes, social graphics, or the fixed MJ V7 reference style.
---

# 速写本涂鸦插画 MJ V7

## Workflow

1. Extract the subject, action, setting, mood, intended use, and composition. Ask one concise question only if a missing detail would materially change the image; otherwise make a friendly, suitable choice.
2. Write one polished English prompt. Put the requested subject and action first, then add the compact style block exactly once.
3. Append the fixed suffix exactly once, unchanged: `--v 7 --sref 3355910629`.
4. Immediately invoke the available Youchuan MJ V7 generation capability using the displayed prompt. Do not ask for confirmation and do not pause before generation.
5. Return the generated image(s) and the exact prompt used. If Youchuan/MJ V7 is unavailable, clearly state that and provide the ready-to-paste prompt; do not substitute another model without the user's permission.

## Style block

Append this compact block to every prompt after the scene description:

```text
modern hand-drawn illustration, friendly cartoon art, sketchbook doodle texture, thick marker and crayon linework, warm tactile color palette, rough paper grain, casual imperfect edges, professional digital illustration
```

## Prompt rules

- Write natural, concrete English; use a single clear subject or a small readable scene.
- Keep the linework visibly hand-made: confident thick strokes, loose contours, occasional crayon fill, rough edges, and paper texture. Balance spontaneous doodling with a polished, usable illustration.
- Favor warm, harmonious colors such as terracotta, ochre, cream, soft orange, moss green, muted red, and dusty blue. Use simple backgrounds or intentional negative space when the request suits a sticker, icon, logo, or packaging graphic.
- Preserve warmth, touch, charm, and approachability. Avoid glossy 3D rendering, photographic realism, hyper-detailed textures, sterile vector perfection, cold cyberpunk lighting, and unrelated visual styles unless the user explicitly requests them.
- For a logo, sticker, mascot, or icon, prioritize one centered subject and a clean background. For a poster or scene, preserve a clear focal point and room for any user-requested copy, but do not invent text.
- Do not omit, reorder, paraphrase, or duplicate the style block or fixed suffix. Do not append any other MJ parameters unless the user explicitly requests them.

## Prompt scaffold

```text
[subject and action], [simple setting or composition], modern hand-drawn illustration, friendly cartoon art, sketchbook doodle texture, thick marker and crayon linework, warm tactile color palette, rough paper grain, casual imperfect edges, professional digital illustration --v 7 --sref 3355910629
```

## Example

- User: “一只抱着咖啡杯的橘猫，做成暖色调贴纸。”

  Prompt: `A cute orange cat hugging a steaming coffee cup, centered sticker composition on a clean cream background, modern hand-drawn illustration, friendly cartoon art, sketchbook doodle texture, thick marker and crayon linework, warm tactile color palette, rough paper grain, casual imperfect edges, professional digital illustration --v 7 --sref 3355910629`
