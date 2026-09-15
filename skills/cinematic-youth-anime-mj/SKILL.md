---
name: cinematic-youth-anime-mj
description: Generate and, only after explicit user confirmation, render cinematic youth-animation image concepts with the Youchuan Midjourney V7 model. Use when users request luminous city twilight anime scenes, blue-and-gold coming-of-age imagery, rain-lit youth memories, animated-film visual storytelling, or this fixed MJ V7 prompt aesthetic.
---

# 电影感青春动画 MJ V7

## Workflow

1. Extract the subject, location, time/weather, emotional beat, key motion or prop, palette, composition, and aspect ratio. Ask one concise question only if a missing detail would materially change the result; otherwise make a fitting choice.
2. Summarize the concept briefly in Chinese and provide one polished English MJ prompt in a code block. Do not call an image model yet.
3. Build the prompt in this order: `character or focal subject, city/environment and story beat, cinematic lighting and weather details, palette and depth composition, youth-memory animation aesthetic`.
4. Append the fixed suffix exactly once and keep it unchanged: `--sref 4233758526 --v 7`.
5. Add an aspect-ratio flag only when requested or clearly beneficial. Put it before the fixed suffix, for example `--ar 16:9 --sref 4233758526 --v 7`.
6. Ask for explicit confirmation in Chinese: `提示词已准备好。是否确认使用悠船 MJ V7 出图？确认后将消耗积分。` Do not generate, submit, or spend credits until the user replies affirmatively.
7. After affirmative confirmation, invoke the available Youchuan/MJ V7 generation capability using the displayed prompt. Return the generated image(s) and the exact prompt used. If this capability is unavailable, say so plainly and provide the ready-to-paste prompt; do not switch models without the user's permission.

## Visual language

- Express the requested look through its visible traits rather than naming or imitating a living artist.
- Favor cinematic Japanese youth-animation imagery: luminous twilight cityscapes, rain-bright streets or windows, sunbeams through clouds, intricate skies, reflective water, translucent atmospheric detail, and a sense of vast space.
- Use deep perspective and foreground/middle-ground/background storytelling. Let one character, gesture, or meaningful everyday object carry the emotional focus.
- Default palette: sapphire/cyan shadows against amber/gold light, with warm red accents only when helpful. Use crisp yet gentle lighting, fine water droplets, drifting autumn leaves, soft cloud glow, or sparkling dust when appropriate.
- Aim for youth, discovery, longing, growth, memories, and dreams. Keep the mood emotionally sincere and hopeful, not bleak, horror-driven, or visually noisy unless explicitly requested.
- Use concrete English visual direction. Avoid creator names and vague phrases such as “in this style.”

## Prompt scaffold

```text
[character or focal subject], [city or landscape at twilight and narrative action], [cinematic lighting, weather, and material details], [blue-and-golden palette], [deep spatial composition and atmospheric perspective], [luminous youth-animation film still, emotional theme] --sref 4233758526 --v 7
```

## Example

- User: “放学后的女孩在雨中车站等车，横构图，带一点对未来的期待。”

  Prompt: `A high-school girl holding a transparent umbrella at a quiet train platform after class, her school bag catching tiny beads of rain as a distant train approaches, rain-wet rails reflecting the glowing city skyline, sun breaking through dramatic clouds at twilight, drifting autumn leaves and shimmering water droplets, sapphire blue shadows and warm golden light, deep spatial composition with layered platform perspective, luminous youth-animation film still, tender anticipation for the future, intricate environmental detail --ar 16:9 --sref 4233758526 --v 7`
