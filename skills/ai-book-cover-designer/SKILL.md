---
name: ai-book-cover-designer
description: Analyze one block of book information and directly generate exactly one complete professional front-cover image with integrated typography. Use when Codex needs to infer genre, market style, composition, title layout, and mood from a Chinese or multilingual book brief; prioritize user-supplied reference images; render with Lib Image or GPT Image 2; default to a 3:4 cover ratio; or follow another ratio explicitly requested by the user.
---

# AI Book Cover Designer

Create exactly one finished front-cover image from the user's book information. Analyze first, write one complete cover prompt, then immediately make one image-generation call. Do not pause for confirmation unless required input is genuinely missing.

## Non-negotiable single-generation rule

- Make exactly **one credit-consuming image-generation call** per user request.
- Generate the complete cover in that call: artwork, title, optional subtitle, optional author, and final layout.
- Do not generate a background first. Do not generate variants, drafts, typography passes, correction passes, or automatic retries.
- Perform read-only inspection and model-availability checks before rendering; these do not count as image generations.
- If a preflight check proves an engine unavailable before rendering begins, choose the fallback engine. Once a render starts, do not switch engines or retry automatically.
- After generation, inspect the result and report any issue honestly. Generate again only after a new explicit user request.

## Workflow

1. Parse the user's single input into:
   - exact title; preserve spelling, punctuation, capitalization, and language
   - optional subtitle and author name
   - genre, subgenre, audience, market positioning, emotional tone, period/world, setting, characters, and core visual symbols
2. Inspect every user-supplied image before prompting. Label each image's role: subject/identity reference, style reference, composition reference, or content to preserve.
3. Prioritize relevant user images over invented visual details. Preserve recognizable identity, character design, objects, colors, and visual language when requested. Use the written brief to supply story context around the reference, not to contradict it.
4. If the title is genuinely absent, ask only for the title. Infer other non-critical fields. Omit author or subtitle when absent.
5. Read [references/genre-guide.md](references/genre-guide.md), choose one primary market genre, and select a matching composition, palette, and typography direction.
6. Use the user's requested ratio. If none is supplied, use **3:4 portrait**.
7. Form a compact cover analysis and the final prompt using the template below. Share them briefly in commentary, then render immediately without requesting approval.
8. Make one generation call with all relevant reference images included in that same call.
9. Inspect the single result for title accuracy, reference fidelity, hierarchy, margins, and thumbnail readability. Deliver only that image, state the model and ratio, and include the final prompt.

## Model routing

Honor an explicit model choice. Otherwise:

1. Prefer a currently available **Lib Image** model through the installed `libtv-cli` skill.
   - Preflight with `libtv model search --type image`; do not hardcode a stale model key.
   - Prefer the highest-quality supported Lib-branded text-to-image or reference-image model.
   - Inspect its schema with `libtv model <exact-name-or-key>` before setting its ratio or reference inputs.
   - Use only documented `libtv` commands. Never invent HTTP endpoints.
2. Use the built-in `image_gen` tool with GPT Image 2 when LibTV is unavailable, unauthenticated, unbound to a canvas, or unsuitable for the supplied references.
3. Do not use GPT Image 1.5 unless the user explicitly requests or approves it.

When using local reference files with the built-in tool, inspect them first and pass every relevant file in the single generation call. When references exist only in recent conversation images, include the smallest recent-image count that contains all of them.

## Cover analysis

Before rendering, determine:

- exact visible text
- primary genre and target readership
- one dominant focal subject or visual metaphor
- relationship of any reference image to the final cover
- title, subtitle, and author positions
- type style, hierarchy, contrast, and safe margins
- palette, lighting, atmosphere, and background depth
- requested ratio, defaulting to 3:4

Favor one legible visual idea over a collage of plot events. Keep the title readable at thumbnail size.

## Final prompt template

Write the prompt in English for model clarity while keeping all visible book text verbatim in its original language.

```text
Use case: ads-marketing
Asset type: complete professional book front cover, final artwork with integrated typography
Aspect ratio: <user ratio, otherwise vertical 3:4>
Book title (render verbatim): "<exact title>"
Subtitle (render verbatim): "<exact subtitle, omit this line if absent>"
Author (render verbatim): "<exact author, omit this line if absent>"
Genre and market: <primary genre, subgenre, readership, market position>
Core concept: <one-sentence visual interpretation of the book>
Reference images: <for each image, state exactly what identity, subject, style, palette, or layout to preserve; say that supplied references take priority>
Scene/backdrop: <world, setting, depth, and atmosphere>
Focal subject: <one dominant character, object, symbol, or environment>
Style/medium: <genre-matched premium publishing style>
Composition: <clear visual hierarchy, subject placement, negative space, safe margins, thumbnail-readable silhouette>
Typography layout: <title position and scale; subtitle position; author position; alignment; spacing; maximum two type styles>
Typography style: <genre-matched font qualities, exact language glyph support, strong contrast, refined professional typesetting>
Lighting/mood: <lighting and emotion>
Color palette: <3-5 colors and contrast intent>
Materials/textures: <relevant tactile detail>
Required text rule: reproduce only the quoted title, subtitle, and author exactly; correct spelling and punctuation; no extra words or random letters
Constraints: one complete flat front-cover design; no mockup, book object, spine, back cover, barcode, publisher logo, badge, watermark, template marks, or border; premium commercial finish
Avoid: clutter, duplicated objects, malformed anatomy, muddy contrast, illegible typography, pseudo-text, cheap poster effects
```

Omit the `Reference images` line when no images are supplied. Do not paste the whole synopsis into the prompt. Translate the synopsis into a coherent art direction and retain only details that materially affect the cover.

## Reference-image priority

- Use user images as the primary visual anchor whenever they are relevant.
- Preserve the referenced person's or character's identity and distinctive design when the reference depicts a subject.
- Preserve the supplied visual language when the image is a style reference, without copying unrelated content.
- Preserve layout logic when the image is a composition reference, while replacing its text and story elements with the user's book content.
- If image and text conflict, follow the user's explicit instruction; otherwise preserve reference identity/appearance and use text for narrative context.
- Never silently ignore an attachment.

## Ratio and layout

- Default to **3:4 portrait**.
- Follow any other user-requested ratio exactly when the chosen model supports it.
- If a model offers only discrete ratios, select the supported ratio closest to the request and disclose the actual ratio after rendering.
- Keep essential text and faces inside a 10% safe margin.
- Use a strong title hierarchy visible at small thumbnail size.
- Use no more than two complementary type styles and no extra cover copy.

## Delivery

- Deliver exactly one final image and render it inline when supported.
- State the model, actual aspect ratio, and whether references were used.
- Include the exact final prompt.
- Do not claim the image is a print-ready full-wrap KDP file. A spine and back cover require trim size, page count, paper type, and bleed settings.
