---
name: city-photo-editorial-poster
description: Transform a user-supplied real city, architecture, street, skyline, coastal, mountain, or landscape photograph into one finished vertical editorial art poster with a preserved photographic upper panel, an abstracted soft-gouache lower panel, and automatically written English title and subtitle typography. Use when Codex needs to create an upper-and-lower split city poster, poetic travel art print, contemporary art-book cover, museum-shop poster, Scandinavian or Japanese editorial design, quiet-luxury photo-and-illustration composition, or a refined image-to-image poster rendered with Lib Image or GPT Image 2.
---

# City Photo Editorial Poster

Create one finished poster from the user's real photograph. Keep the top recognizably photographic and turn the same scene into a restrained editorial illustration below. Integrate the title and subtitle into the final image.

## Non-negotiable result

- Produce one flat front-facing poster, not a framed mockup or a poster photographed in a room.
- Preserve the source photo's identity and visual truth in the upper panel. Do not restage, repaint, replace, or substantially alter the skyline, buildings, terrain, weather, clouds, water, roads, lights, or viewpoint.
- Make the lower panel an unmistakable artistic distillation of the same scene, not an unrelated illustration and not a pixel-for-pixel copy.
- Keep the mood premium, quiet, poetic, spacious, low-saturation, and print-oriented.
- Render only one final image unless the user explicitly requests variants. Do not silently retry or spend credits on correction passes.

## Workflow

1. Inspect every supplied image before writing the prompt. If the image is not locally accessible, include the smallest number of recent conversation images needed to cover all references.
2. Identify the photograph's viewpoint, horizon, landmark silhouettes, dominant geometry, lighting, sky, season, palette, and emotional tone.
3. Select three to six distinctive scene elements that the lower illustration must abstract. Prefer recognizable silhouettes, spatial rhythm, and color relationships over tiny detail.
4. Write an English main title of 2-5 words and an English subtitle of 4-10 words.
   - Use a known location only when it is supplied by the user or visually certain.
   - Otherwise use an atmospheric editorial title; do not invent a factual place name.
   - Avoid clichés, promotional slogans, exclamation marks, dates, logos, and extra copy.
5. Use the user's requested aspect ratio. Otherwise use a vertical **3:4** poster.
6. Build one complete image-editing prompt with the template below and include the source photograph as the primary reference.
7. Render immediately without asking for confirmation unless the required source image is missing.
8. Inspect the result for photo fidelity, upper/lower relationship, text accuracy, whitespace, and absence of unwanted decorations. Report any issue honestly; do not automatically regenerate.

## Model routing

Honor an explicit model choice. Otherwise use this order:

1. Prefer a currently available **Lib Image** reference-image model through the installed `libtv-cli` skill.
   - Run `libtv model search --type image`; do not hardcode a possibly stale model key.
   - Choose the highest-quality available Lib-branded model that supports image-to-image/reference input and integrated typography.
   - Inspect the exact schema with `libtv model <exact-name-or-key>` before setting ratio, quality, or reference inputs.
   - Upload the source with `libtv upload`, connect it as the image node's left input, and use only documented `libtv` commands. Never invent HTTP endpoints.
   - Treat `libtv node ... --run` as synchronous and wait for it to exit.
2. Use the built-in `image_gen` tool with **GPT Image 2** when LibTV is unavailable, unauthenticated, not bound to a canvas, lacks a suitable image-to-image model, or cannot preserve the supplied reference reliably.
3. Do not use another model unless the user explicitly requests or approves it.

For a local source image, inspect it first and pass its path as a reference. For conversation-only images, include the minimum recent-image count that contains the source. Make one generation call containing artwork, layout, and typography together.

## Locked art direction

### Overall language

Use: minimal editorial poster, poetic city illustration, contemporary art-book aesthetic, Scandinavian minimalism, Japanese editorial design, quiet luxury, refined print design, soft gouache illustration, abstract cityscape, and restrained museum-shop art print.

### Upper photographic panel

- Allocate approximately 52-58% of the poster height to the photograph.
- Preserve the original composition and camera position as closely as the poster ratio permits. Avoid destructive cropping of the principal landmark or horizon.
- Apply only a subtle cinematic grade: slightly reduced saturation, soft highlight roll-off, natural shadows, restrained contrast, and gentle blue-grey/warm-yellow/ivory harmony.
- Retain authentic photographic texture, optical detail, natural atmosphere, and believable lighting.
- Avoid HDR, aggressive sharpening, plastic denoising, fantasy relighting, object invention, or an AI-repainted appearance.

### Lower illustrated panel

- Allocate approximately 42-48% of the poster height, including generous warm-ivory negative space for typography.
- Abstract the upper photograph's defining forms into simplified geometric color masses, compressed distant silhouettes, small rectangular shapes, and a few deliberate painted gestures.
- Preserve the scene's left-to-right rhythm, skyline profile, dominant landmark, and palette relationship so the visual connection is immediate.
- Use soft gouache, dry-brush texture, watercolor-like opacity, subtle paper grain, hand-painted editorial illustration, matte pigment, and refined printed texture.
- Use no obvious outline. Avoid cartoon styling, literal tracing, 3D rendering, vector-icon geometry, glossy gradients, or busy detail.
- Keep the composition sparse, balanced, calm, and contemporary.

### Palette

Center the design on warm ivory, muted navy, blue grey, smoky grey, warm ochre, mustard yellow, and soft beige. Keep saturation low and use the source image's natural accent color only when it supports the restrained palette.

### Typography

- Place the automatically generated English title and subtitle in the lower panel, left-aligned, with ample breathing room and a strong baseline grid.
- Set the title in an elegant classic serif, deep navy-grey, medium size, refined rather than dominant.
- Set the subtitle in a delicate editorial italic serif, smaller and lighter.
- Use no more than these two text styles. Render only the exact supplied title and subtitle: no pseudo-text, credits, labels, location tags, logos, watermarks, or decorative letters.
- Keep all type inside a 10% safe margin and separate it clearly from the illustration.

## Final prompt template

Write the generation prompt in English. Replace every bracketed field with image-specific observations.

```text
Use case: image-to-image editorial poster
Asset: one complete flat vertical 3:4 art poster with integrated typography
Primary reference: use the supplied real photograph as the authoritative source for the upper panel and as the visual source for the lower illustration

Visible title, render exactly: "[2-5 word English title]"
Visible subtitle, render exactly: "[4-10 word English subtitle]"

Create a sophisticated two-part composition divided horizontally.

UPPER PANEL - approximately 55% of the poster height:
Preserve the supplied photograph's actual viewpoint, framing logic, horizon, skyline, architecture, terrain, sky, clouds, water, road, lights, and recognizable landmark placement. The same real photograph should remain immediately recognizable, with authentic photographic detail and natural optics. Apply only a restrained cinematic editorial grade: slightly reduced saturation, gentle contrast, soft highlight roll-off, natural shadow detail, and a calm blue-grey, warm-yellow, and ivory balance. Do not restage, repaint, replace, add, or remove scene elements. No HDR, no aggressive sharpening, no fantasy lighting, no synthetic AI-redraw appearance.

LOWER PANEL - approximately 45% of the poster height:
Create an original minimal editorial illustration distilled from these exact source elements: [list 3-6 distinctive elements]. Preserve their silhouette hierarchy, left-to-right spatial rhythm, dominant landmark, and color relationships, while simplifying architecture into geometric painted masses and distant details into small compressed rectangular silhouettes. The lower scene must clearly read as a poetic abstraction of the upper photograph, never an unrelated scene and never a literal tracing. Use soft gouache, dry-brush texture, watercolor-like opacity, subtle paper grain, hand-painted editorial illustration, matte pigment, and refined printed texture. No obvious outlines, no cartoon look, no vector-icon look, no 3D, no glossy gradients. Preserve generous warm-ivory negative space.

TYPOGRAPHY:
Place only the exact title and subtitle in the lower panel, left-aligned with a calm editorial grid and generous breathing room. Title: elegant classic serif, deep navy-grey, refined medium scale. Subtitle: delicate smaller editorial italic serif. Accurate spelling, clean kerning, 10% safe margins. No other text, random letters, logo, badge, signature, watermark, border, or ornament.

Art direction: minimal editorial poster, poetic city illustration, contemporary art-book aesthetic, Scandinavian minimalism, Japanese editorial design, quiet luxury, museum-shop art print, refined print design.
Palette: warm ivory, muted navy, blue grey, smoky grey, warm ochre, mustard yellow, soft beige, low saturation.
Mood: quiet, balanced, spacious, poetic, tactile, modern, restrained, premium.
Avoid: commercial advertising language, cheap AI aesthetics, clutter, collage, excessive decoration, oversaturation, cyberpunk, anime, comic styling, photobashing, poster mockup, frame, room scene, folded paper, torn edges, drop shadows, thick divider line.
```

If the user requests another ratio, replace `3:4` and rebalance panel heights without changing the top-photo/bottom-illustration logic. Add scene-specific preservation notes whenever a distinctive landmark or lighting condition could otherwise drift.

## Quality gate

Before delivery, verify:

- The upper panel still looks like the supplied real photograph rather than a painted reconstruction.
- The source viewpoint, major landmark positions, skyline, horizon, and lighting remain faithful.
- The lower panel visibly derives from the same scene through abstraction.
- Warm-ivory whitespace remains substantial; the poster is not crowded.
- The palette stays muted and the texture feels matte, tactile, and printed.
- The title and subtitle are exact, legible, left-aligned, and the only visible text.
- The output contains no mockup, frame, logo, watermark, border, pseudo-text, or commercial-ad decoration.

Deliver the image inline when supported. State the model, actual ratio, generated title, generated subtitle, and whether the user's source image was used as the primary reference.
