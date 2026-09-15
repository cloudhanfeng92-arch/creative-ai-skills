---
name: character-turnaround-reference
description: Generate a professional four-view character turnaround reference sheet from one uploaded character image. Use when a user asks to turn a reference image into full-body front, side, and back views plus a front facial close-up while locking the original character identity, outfit, materials, colors, and art style; use for character sheets, model sheets, animation references, or 3D-modeling references.
---

# Character Turnaround Reference

Create one polished character reference sheet from a single uploaded image. Treat that image as the sole authority for both character design and visual style. Use the `imagegen` skill and its default built-in image-generation path.

## Required input and confirmation

1. Confirm that one usable character image is uploaded. If none is available, ask for it; do not invent a reference subject.
2. Inspect the reference before writing the prompt. Identify the silhouette, face, hairstyle, proportions, clothing layers, accessories, palette, materials, rendering, lighting, and any asymmetry that must remain consistent.
3. If an essential design area is hidden or cropped, state the ambiguity briefly and ask whether the user prefers a faithful inference or supplying another reference. Do not silently add distinctive design details.
4. Before a credit-consuming image-generation call, obtain the user's explicit confirmation. State that the output will be one four-view reference sheet based only on the uploaded image.

## Generation procedure

1. Use the uploaded image as an image input with the role `sole visual reference`.
2. Generate one landscape, single-sheet character turnaround; do not produce four separate files unless the user explicitly requests that variation.
3. Use a clean 2-by-2 grid with these unambiguous panels:
   - upper left: full-body front view, neutral A-pose or relaxed neutral stance;
   - upper right: full-body exact side profile, facing toward the sheet center where composition permits;
   - lower left: full-body back view, keeping hair, garment backs, closures, and accessories visible;
   - lower right: front-facing facial close-up, neutral expression.
4. Keep all three full-body views at identical scale and use an orthographic or near-orthographic character-sheet presentation. Keep the whole body, hands, footwear, and outer silhouette in frame.
5. Lock every visible design invariant across panels: identity, facial structure, hairstyle, body shape and proportions, garment construction, accessories, colors, material finish, textures, and characteristic asymmetry. Reveal plausible reverse-side construction only where the source does not show it; do not redesign the character.
6. Match the reference's medium, linework or painterly treatment, rendering method, lighting character, texture density, contrast, and color handling. Do not turn the image into a generic anime, realistic, 3D, or different-art-style sheet.
7. Use a neutral clean studio background with subtle, consistent lighting and sufficient separation from the character. Do not add a floor scene, props, borders, UI, or decorative elements.

## Prompt template

Use this production prompt, replacing bracketed observations only when the source clearly supports them:

```text
Use case: identity-preserve
Asset type: professional character turnaround reference for modeling and animation
Input images: uploaded image — sole visual reference; do not use any other source
Primary request: Create one precise four-view character turnaround sheet of the exact character in the uploaded reference.
Subject: Preserve the same character identity: [concise observed face, hairstyle, silhouette, outfit, accessories, and notable asymmetries].
Composition/framing: One landscape 2-by-2 sheet. Upper left: full-body front view. Upper right: full-body exact side profile. Lower left: full-body back view. Lower right: front-facing facial close-up. Keep the three full-body views at the same scale, with the entire head, body, hands, and footwear visible. Neutral expression and neutral standing pose. Orthographic or near-orthographic model-sheet presentation.
Style/medium: Match the uploaded image exactly: its art style, linework, rendering technique, lighting, shadows, color grading, materials, and texture quality. The uploaded image is the sole visual and style reference.
Scene/backdrop: Clean neutral studio background with even, subtle illumination; no floor scene, no props, no border.
Constraints: Strictly preserve facial features, hairstyle, body proportions, outfit design and construction, accessories, colors, materials, patterns, texture placement, and all distinctive asymmetries across every panel. Show the same character, not a redesign. Infer only hidden back or side details conservatively from the visible design language. Maintain complete style consistency across all four panels.
Avoid: text, letters, typography, captions, labels, watermark, logo, signature, UI elements, symbols, numbers, character name, design notes, extra characters, cropped feet, incomplete bodies, pose changes, inconsistent clothing, altered accessories, altered colors, generic style drift, duplicate angles.
```

## Quality gate and iteration

Inspect the generated sheet before delivering it. Check all of the following:

- It has exactly the requested front, side, back, and facial-close-up panels.
- Each full-body panel is complete and consistently scaled.
- The character is recognizably identical in all panels.
- Clothing, accessories, colors, materials, and asymmetrical details agree with the source and one another.
- The art style and rendering match the uploaded source.
- No text-like marks, labels, watermark, logo, UI, or unwanted props appear.

If a result fails, explain the specific mismatch and, after obtaining confirmation for another generation, make one targeted corrective pass. Preserve successful aspects rather than broadening the redesign. Save project-bound final images inside the current project's deliverable location, following the `imagegen` skill's save-path policy, and report the final path plus the prompt used.
