---
name: naive-crayon-illustration-mj
description: Generate naive-art, childlike crayon illustration prompts and immediately render them with the Youchuan Midjourney V7 model, without a confirmation step. Use when users request warm vintage picture-book art, dry-media crayon/oil-pastel/colored-pencil texture, rough paper grain, childlike doodles, friendly education or packaging illustrations, whimsical mascots, or this fixed MJ V7 SREF aesthetic.
---

# 童趣蜡笔手绘 MJ V7

## Workflow

1. Extract the subject, action, setting, mood, intended use, and composition. Ask one concise question only if a missing detail would materially change the image; otherwise make a warm, playful choice.
2. Write one polished English prompt. Place the requested subject and action first, followed by the fixed style block exactly once.
3. Append the fixed suffix exactly once, unchanged: `--v 7 --sref 1470170`.
4. Immediately invoke the available Youchuan MJ V7 generation capability with the prompt. Do not ask for confirmation and do not pause before generation.
5. Return the generated image(s) and the exact prompt used. If Youchuan/MJ V7 is unavailable, state that clearly and provide the ready-to-paste prompt; do not substitute another model without the user's permission.

## Style block

Append this block to every prompt after the scene description:

```text
naive art, childlike picture-book illustration, dry crayon and oil pastel texture, rough colored pencil strokes, toothy paper grain, gently trembling imperfect edges, simple geometric shapes, warm muted vintage palette, generous white paper background, handmade emotional warmth
```

## Prompt rules

- Use concrete, friendly English. Favor a single character or a small readable scene, with easy-to-read silhouettes and joyful, offbeat actions.
- Preserve dry-media marks: broken color coverage, visible paper tooth, grainy crayon or oil-pastel strokes, loose hand-drawn contours, and slightly irregular proportions. Do not smooth, polish, or over-render these marks.
- Use restrained vintage colors—dusty pink, ink green, mustard yellow, terracotta, soft blue, warm cream, and muted orange. Keep saturation moderate and layer colors naturally.
- Prefer uncluttered white or warm paper backgrounds. When a setting is needed, build it from simple, flattened shapes rather than strict perspective, photographic depth, or technical anatomy.
- Aim for innocence, humor, warmth, nostalgia, and tactile human imperfection. Suitable outputs include picture books, educational cards, stickers, washi tape, stationery, warm handmade brands, social avatars, and expressive characters.
- Avoid glossy 3D, photorealism, sterile vector precision, smooth airbrushing, hyper-detailed rendering, dramatic cinematic lighting, neon/cyberpunk, and unrelated art styles unless the user explicitly requests them.
- Do not name or imitate a particular artist. Express this visual language through the material, color, line, and composition traits above.
- Do not omit, reorder, paraphrase, or duplicate the style block or fixed suffix. Do not append any other MJ parameters unless the user explicitly requests them.

## Prompt scaffold

```text
[whimsical subject and action], [simple setting or white-paper composition], naive art, childlike picture-book illustration, dry crayon and oil pastel texture, rough colored pencil strokes, toothy paper grain, gently trembling imperfect edges, simple geometric shapes, warm muted vintage palette, generous white paper background, handmade emotional warmth --v 7 --sref 1470170
```

## Example

- User: “围红围巾的鳄鱼骑自行车。”

  Prompt: `A happy crocodile wearing a red scarf, riding a tiny bicycle, simple white paper composition with two loose flowers, naive art, childlike picture-book illustration, dry crayon and oil pastel texture, rough colored pencil strokes, toothy paper grain, gently trembling imperfect edges, simple geometric shapes, warm muted vintage palette, generous white paper background, handmade emotional warmth --v 7 --sref 1470170`
