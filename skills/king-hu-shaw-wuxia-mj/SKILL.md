---
name: king-hu-shaw-wuxia-mj
description: Generate wuxia text-to-image prompts and immediately render them with the Youchuan Midjourney V7 model, without a confirmation step. Use when users request Hu Jinquan wuxia aesthetics, Shaw Brothers classic-film imagery, jianghu martial-arts scenes, vintage Chinese wuxia cinema, or prompts that must include the fixed seven Chinese style phrases.
---

# 胡金铨邵氏武侠 MJ V7

## Workflow

1. Extract the requested character, action, location, time of day, and story beat. Make a suitable wuxia choice when details are absent; do not pad the scene with unrelated elements.
2. Write one compact Chinese prompt, normally 45–90 Chinese characters before the required style phrase block. Use only: subject, action, setting, one controlled light-and-shadow treatment, and one spatial relationship. Append the required style phrase block exactly once. Do not add any MJ parameters, `--` flags, reference-image numbers, or other parameter suffixes.
3. Immediately invoke the available Youchuan MJ V7 generation capability with that prompt. Do not ask for confirmation and do not pause before generation.
4. Return the generated image(s) and the exact Chinese prompt used. If Youchuan/MJ V7 is unavailable, clearly state that and return the prompt ready to paste; do not substitute another model without the user's permission.

## Required style phrase block

Append this block unchanged to every prompt, retaining every phrase and the punctuation:

```text
胡金铨武侠美学，邵氏老电影风格，电影级柔光布光，宽景长镜头，复古胶片肌理，色彩浓郁深沉，江湖氛围感
```

## Prompt rules

- Use concise Chinese throughout unless the user explicitly requests another language. Write a single sentence and no explanatory adjectives stacked in lists.
- Compose the scene as theatrical cinematic space: a quiet wide view, a clear figure or movement, foreground obstruction or framing, and restrained depth. Do not add more than one major action.
- Keep light and color strictly within classic wuxia cinema: use diffused overcast daylight, low warm lantern or candle light, pale moonlight, or slanting sunset light; pair it with soft shadow, mist, rain, smoke, or bamboo-shadow layering. Use deep vermilion, ink black, dark cyan/blue-green, muted gold, and warm amber as the dominant palette.
- Avoid hard modern rim light, neon glow, electric blue/purple gradients, lens flare, glitter particles, volumetric laser-like beams, high-key commercial lighting, candy pastels, glossy 3D rendering, or photoreal fashion-editorial lighting.
- Exclude all non-wuxia content unless the user explicitly requires it: modern cities, vehicles, screens, firearms, sci-fi, cyberpunk, anime effects, fantasy magic circles, excessive supernatural energy, Western medieval armor, text, logos, posters, and watermarks.
- Favor bamboo groves, temple corridors, inns, courtyards, mountain paths, desert passes, rain, mist, lanterns, martial robes, swords, veils, and tiled eaves only when they fit the user's scene. Do not force them in.
- Do not add modern graphic design, aspect-ratio flags, model flags, style-reference flags, negative prompts, or any parameter suffix.
- Do not omit, translate, paraphrase, reorder, or duplicate the required style phrase block.

## Prompt scaffold

```text
[人物/主体]在[古典场景]中[单一动作]，[一种符合年代感的光源与阴影]，[前中后景关系]，胡金铨武侠美学，邵氏老电影风格，电影级柔光布光，宽景长镜头，复古胶片肌理，色彩浓郁深沉，江湖氛围感
```

## Example

- User: “一位女剑客在暴雨里穿过竹林。”

  Prompt: `黑衣女剑客穿过雨夜竹林，长剑半出鞘，山寺灯笼投下温暖暗金光，前景湿竹遮映，中景人物疾行，远山隐于墨蓝雾色，胡金铨武侠美学，邵氏老电影风格，电影级柔光布光，宽景长镜头，复古胶片肌理，色彩浓郁深沉，江湖氛围感`
