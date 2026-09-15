---
name: new-chinese-ink-landscape
description: Create original text-to-image posters in a new Chinese ink-wash landscape style. Use when a user wants an image, poster, cover, key visual, or scenic illustration based on text, combining Chinese landscape ink painting, restrained modern graphic design, springtime Zen atmosphere, misty cinematic light, and refined 8K-detail rendering.
---

# 新中式水墨山水

Turn the user's text into a finished vertical poster image. Preserve every concrete requested element while expressing it through a new Chinese ink-landscape visual language.

## Workflow

1. Extract the requested subject, setting, season/time, action, emotional tone, and any non-negotiable objects from the user's text. Do not add narrative characters, logos, or props unless implied.
2. Infer a concise Chinese theme title of 2–6 characters that closely matches the scene's meaning. If the user supplies title text, use it verbatim. Do not invent a title when the user explicitly asks for no text.
3. Build one production prompt using the template below. Make the scene description specific, but retain the fixed visual system.
4. Generate with the built-in `image_gen` tool. Inspect the result for: requested elements, vertical composition, legible spatial depth, restrained palette, no garbled text/watermarks, and a balanced central breathing space.
5. If the image contains corrupted Chinese characters, regenerate once with `Text: none; reserve a clean top-center vertical calligraphy area with no pseudo-text or symbols.` Tell the user the intended title and offer a separate typesetting pass if they need fully reliable Chinese lettering.

## Fixed visual system

- **Style:** new Chinese ink-wash landscape poster; Eastern minimalism; traditional ink diffusion fused with contemporary editorial design; spring Zen atmosphere; airy, humid, quiet, restrained; cinematic light and shadow; premium art-paper quality; highly refined 8K-level detail.
- **Composition:** portrait orientation; substantial negative space; clear foreground/middle-ground/background depth; a subtly open central axis for visual breathing; balanced but rhythmic placement. Let the requested subject dominate naturally without filling every empty area.
- **Palette:** early spring morning—jade green, mist blue, pale gray, and light ink; low saturation; transparent, soft, cool-forward color with only restrained warm/cool contrast.
- **Rendering:** layered wet-and-dry ink washes, varied density and moisture, soft feathered edges, visible paper/grain nuance, luminous atmospheric perspective, translucent fine details. Avoid heavy black fills, gaudy color, flat vector graphics, photorealistic Western landscape, or cliché scroll borders.
- **Typography:** when text is requested, place the title at the top center in a vertical layout, using organic handwritten semi-cursive/cursive calligraphy with Wang Xizhi-inspired brush energy, varied pressure, dry-brush gaps, and ink bloom; deep blue-black or soft ink-black. Treat the title as hand-painted calligraphy, never a digital font.

## Prompt template

```text
Use case: stylized-concept
Asset type: finished vertical art poster
Primary request: [faithful restatement of the user's request]
Scene/backdrop: [specific scene made only from the user's requested elements]
Subject: [main subject and required details]
Style/medium: New Chinese ink-wash landscape poster; Eastern minimalism; ink painting fused with contemporary editorial design; spring Zen atmosphere; humid, ethereal, tranquil, restrained; cinematic light and premium fine-art texture; refined 8K-level detail.
Composition/framing: Portrait composition. Large intentional negative space, clear layered depth, gently open central axis, harmonious visual rhythm. [Place the subject to best serve the request.]
Lighting/mood: Soft cinematic spring-morning light through mist, quiet moisture in the air, contemplative and spacious.
Color palette: Low-saturation jade green, mist blue, pale gray, and diluted ink; transparent soft tones; restrained cool/warm contrast.
Materials/textures: Rich wet-and-dry ink diffusion, controlled ink bleed, softened edges, tonal gradation, subtle xuan-paper grain, translucent atmospheric detail.
Text (verbatim): "[2–6-character Chinese title]"; top-center vertical hand-painted semi-cursive calligraphy, natural Wang Xizhi-inspired brushwork, varied pressure, flying-white dry-brush texture, blue-black ink.  [Or: none; retain a clean title area.]
Constraints: Keep every requested element recognizable and semantically accurate. No watermark, logo, frame, random symbols, extra captions, garbled text, oversaturation, or generic stock-photo appearance.
```

## Adaptation rules

- Translate modern subjects into the style without deleting them: e.g., architecture becomes a quiet contemporary pavilion or skyline integrated into mist and ink; products remain clearly recognizable but are presented as refined still-life focal points.
- For people or animals, retain the requested identity markers, pose, count, clothing, and action; render them with elegant ink-derived forms rather than adding unrelated figures.
- For night, autumn, winter, or dramatic requests, honor the user's timing and mood while keeping the palette muted, atmospheric, and painterly. Do not force a spring scene when it contradicts the request.
- Use explicit user constraints over stylistic defaults. If the requested content clashes materially with the style, ask one concise clarification rather than silently changing the requested subject.
