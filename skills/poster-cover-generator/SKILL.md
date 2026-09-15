---
name: poster-cover-generator
description: Create finished raster poster and cover images from a user's copy, a reference image, or both. Use when Codex needs to turn a title, headline, event details, product copy, book or album information, or an image into a cohesive poster, social cover, book cover, album cover, campaign key visual, or thumbnail with style-matched typography and artwork.
---

# Poster Cover Generator

Create one polished, readable poster or cover image. Use the built-in image-generation workflow; this skill supplies the art-direction, type-selection, and quality-control process.

## Intake and defaults

Extract and preserve all user-supplied copy exactly. Treat a supplied image as one of these roles:

- **Style reference:** match its visual language, palette, texture, and mood without copying protected logos or text.
- **Subject/reference:** create a new cover featuring its subject or visual motifs.
- **Edit target:** retain the image and add, replace, or refine its typography only when the user explicitly asks to edit it.

Ask only if the exact copy is missing or a required output size/platform is genuinely consequential. Otherwise, choose the format that best suits the use: 2:3 vertical for print-like posters or book covers, 4:5 for feed posts, 9:16 for stories, 1:1 for album/podcast covers, or 16:9 for video/banner covers. If no use is stated, default to a 2:3 vertical poster.

## Art direction

1. Identify the dominant genre and emotional register from the words and/or reference image.
2. Create a visual hierarchy: title first, then optional subtitle, then supporting details. Keep the title readable at thumbnail size.
3. Select a typography direction from [Typography playbook](references/typography-playbook.md). Match both the form of the lettering and the image treatment to the same genre.
4. Reserve a clean, high-contrast title zone before deciding the composition. Do not let text collide with important faces, logos, or focal details.
5. Use a limited palette, deliberate negative space, and no visual element that does not support the central message.

Do not default to a generic template. Let the source drive the work: a suspense title can use compressed, high-contrast or distressed lettering; a gentle children's cover can use round, hand-drawn forms; a premium technology cover can use restrained geometric sans-serif lettering and ordered space.

## Build the generation brief

Write a compact, labeled generation prompt. State literal copy in a separate `Text (verbatim)` line and require it exactly once. Describe font attributes rather than relying on a brand font that may not be available. Use this structure when relevant:

```text
Use case: ads-marketing
Asset type: <poster / book cover / album cover / social cover>
Primary request: <what the cover communicates>
Input image: <role and what to preserve/match, if supplied>
Format: <aspect ratio and orientation>
Visual direction: <genre, subject, medium, backdrop, palette, mood>
Typography: <playbook direction; title scale; layout; contrast; text effects>
Text (verbatim): "<exact title>"; "<optional exact secondary copy>"
Composition: <focal point, title zone, hierarchy, margins>
Constraints: render every supplied string exactly once; typography must be crisp and legible; no placeholder or invented copy; no watermark; no unrelated logos or trademarks
Avoid: <genre-specific clutter or conflicts>
```

For a reference-image edit, explicitly repeat the invariants: `change only the typography/layout; preserve the supplied subject, framing, and visual style.`

## Generate and refine

1. Generate the image using the image-generation workflow. For an edit target, first make the image available to the image tool and use edit mode; otherwise use generation with the reference image labeled by role.
2. Inspect the result at full size and at a small preview. Verify spelling, character order, font-style fit, contrast, safe margins, composition, and absence of accidental extra copy.
3. If copy is inaccurate, crowded, or visually weak, iterate with one focused correction. Re-state every literal text string and the target type direction. Prefer a clean re-layout over forcing a noisy result.
4. Save the selected final image in the user's requested destination. If no destination is specified, provide it as an inline preview and report the generated file path.

Never present a poster with misspelled required copy as final. If the generator cannot reproduce a long or dense text block accurately after a focused retry, explain the limitation and offer a short-title version or a composited typography workflow.

## Completion checklist

- Match the source's mood and visual language without imitating trademarks or protected logos.
- Render exact supplied copy once, with clear title-to-detail hierarchy.
- Use a font direction appropriate to the genre and readable against its background.
- Deliver one finished raster poster/cover in the intended aspect ratio, without watermarks.
