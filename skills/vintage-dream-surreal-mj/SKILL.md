---
name: vintage-dream-surreal-mj
description: Generate and, only after explicit user confirmation, render vintage dream-surreal image concepts with the Youchuan Midjourney V7 model. Use when users request dreamy retro surrealism, liminal dreamcore, nostalgic 90s CGI/3D scenes, or a fixed MJ V7 prompt style featuring ordinary objects in impossible peaceful settings.
---

# 复古梦境超现实 MJ V7

## Workflow

1. Extract the requested subject, setting, surreal transformation, mood, palette, composition, and aspect ratio. Ask one concise question only if a missing detail would materially change the image; otherwise make a fitting creative choice.
2. Explain the image concept in Chinese briefly, then provide one polished English MJ prompt in a code block. Do not call an image model yet.
3. Build the prompt in this order: `main subject + impossible setting/action, atmospheric light and particles, color and emotional direction, retro-render texture, 3D quality`.
4. Append the fixed suffix exactly once and keep it unchanged: `--sref 1360520854 1124116562 4710227 --v 7`.
5. Use an aspect-ratio flag only when the user requests it or it clearly benefits the composition. Place it before the fixed suffix, for example `--ar 16:9 --sref 1360520854 1124116562 4710227 --v 7`.
6. Ask for explicit confirmation in Chinese: `提示词已准备好。是否确认使用悠船 MJ V7 出图？确认后将消耗积分。` Do not generate, submit, or spend credits until the user answers affirmatively.
7. After affirmative confirmation, invoke the available Youchuan/MJ V7 generation capability with the displayed prompt. Return the generated image(s) and repeat the exact prompt used. If the capability is unavailable, say so plainly and give the ready-to-paste prompt; do not substitute another model without explicit permission.

## Style rules

- Preserve the reference look: a familiar everyday object or interior fragment placed in a calm, physically impossible landscape or spatial transition.
- Favor one clear visual paradox and a sparse, peaceful composition over crowded spectacle, horror, glitch effects, text, logos, or people unless the user explicitly asks for them.
- Weave in fitting cues from: soft god rays, gentle mist/haze, luminous dust or drifting particles, soft bloom, reflection, warm/cool color contrast, dreamy 90s postcard or cinematic film grain, nostalgic CGI softness, saturated yet gentle color, liminal serenity, and high-fidelity 3D render.
- Use concrete visual English. Avoid meta phrasing such as “in the style of the reference”; express the visual qualities directly.
- Keep the fixed suffix intact even if the body prompt is Chinese; normally write the body in English for MJ compatibility.

## Prompt scaffold

```text
[ordinary subject] [surreal placement or transformation], [environment and focal details], [light, atmosphere, and particles], [palette and emotional direction], [retro 90s CGI/film texture], [calm surreal high-fidelity 3D render] --sref 1360520854 1124116562 4710227 --v 7
```

## Examples

- User: “一盏台灯放在月球表面，治愈，竖图。”

  Prompt: `A small vintage desk lamp standing alone on the moon’s powdery surface, its warm pool of light revealing tiny silver wildflowers, distant Earth hanging in a deep cobalt sky, soft lunar haze and drifting luminous dust, gentle amber-blue contrast, dreamy 90s postcard grain, nostalgic CGI softness, serene surreal high-fidelity 3D render --ar 2:3 --sref 1360520854 1124116562 4710227 --v 7`

- User: “冰箱在夏日海边。”

  Prompt: `A vintage refrigerator standing open on a quiet summer beach, cool blue light spilling onto mirror-like wet sand while the shelves hold tiny glowing seashells, pastel sunset reflected in the tide, soft sea mist and drifting sparkles, warm coral and turquoise palette, dreamy 90s cinematic grain, nostalgic CGI softness, peaceful surreal high-fidelity 3D render --sref 1360520854 1124116562 4710227 --v 7`
