---
name: storyboard-sheet-generator
description: Generate one clean 16:9 horizontal eight-panel previs storyboard sheet from a story and one or more character reference images, with strong on-model character consistency, cinematic shot progression, camera notes, action notes, camera-frame guides, and motion arrows. Use when the user asks for 故事版、分镜拆分图、八格分镜、预演分镜、角色一致性分镜、Seedance 分镜参考图、storyboard sheet, previs sheet, shot breakdown, or a single storyboard image that automatically converts a plot, action sequence, scene, commercial beat, or short narrative into eight readable shots. Also use when adapting an uploaded character sheet into a coherent 4-by-2 cinematic storyboard grid.
---

# Storyboard Sheet Generator

Generate exactly one production-readable 16:9 storyboard sheet containing eight numbered panels in a 4-column by 2-row grid. Treat character-reference fidelity as the highest priority and story clarity as the second.

## Required inputs

Collect or infer:

- `character_reference`: one or more uploaded images that define each recurring character.
- `story_input`: plot, action flow, setting changes, emotional rhythm, conflict, key shots, and ending.
- Optional: dialogue, genre, tone, target language for notes, visual accents, continuity constraints, or a required ending frame.

If the request depends on matching a specific character but the reference image is missing, stop and ask the user to attach it. If the user explicitly permits an original character, define the character once and lock that design across all panels. Ask only when missing information materially prevents generation; otherwise infer sensible cinematic details.

## Workflow

### 1. Inspect references

View every local reference image before generating. Identify, without redesigning:

- face shape, key facial features, skin/fur/material treatment;
- body proportions and silhouette;
- hairstyle, headwrap, goggles, eyewear, or headgear;
- outfit layers, palette, accessories, gloves, footwear, and prop ownership;
- line style, shape language, stylization level, and rendering simplicity.

When several characters appear, create an internal mapping such as `Character A -> reference 1`; do not merge traits. When a reference sheet contains multiple views of the same character, treat all views as one identity specification.

### 2. Build the eight-beat sequence

Silently translate the story into exactly eight major visual beats before image generation. Assign one dominant action or emotional beat per panel. Use this default arc when the story does not prescribe another:

1. Establish place, goal, and screen direction.
2. Introduce the initiating action or discovery.
3. Advance the action and clarify spatial relations.
4. Add an obstacle, reaction, or complication.
5. Escalate with the strongest movement or decision.
6. Show consequence, counteraction, or emotional pivot.
7. Deliver the climax or decisive beat.
8. Resolve or punctuate the scene with a clear ending image.

Vary coverage intentionally: establishing, medium, close-up, action, insert, over-the-shoulder, low/high angle, or reaction shot only when motivated. Maintain eyelines, entrances/exits, prop state, character handedness, geography, lighting direction, and left/right action continuity.

### 3. Create concise panel instructions

For each panel define:

- shot size and camera angle;
- subject placement and screen direction;
- one visible action beat;
- expression and body-language change;
- environment/prop continuity;
- one short camera note;
- one short action note;
- blue motion arrows only where motion needs clarification;
- red frame or camera guides only where useful.

Keep notes extremely short so the image model can render them more reliably. Use the user's language; otherwise use Chinese for Chinese requests and English for English requests. Avoid dialogue balloons unless requested.

### 4. Compose the generation prompt

Read [references/prompt-template.md](references/prompt-template.md) and instantiate it with the reference-derived character lock, story summary, eight panel beats, note language, and continuity rules. Include concrete visual content for every panel; never pass a raw placeholder such as `在这里输入故事` to the image model.

### 5. Generate once as a unified sheet

Use the image-generation tool to create one new raster image. Include all target reference images through local `referenced_image_paths` when available; otherwise include the smallest number of recent conversation images that contains every required reference. Never provide both mechanisms.

Generate directly without a confirmation round unless the user explicitly asks to approve the prompt first. Do not generate eight unrelated images and assemble them: render the whole 4-by-2 sheet as one coherent artifact so layout, identity, palette, and spatial continuity share one context.

### 6. Inspect and retry only for material failures

Check the returned sheet for:

- exactly eight separated panels, numbered 1 through 8 in reading order;
- correct 16:9 horizontal sheet and 4-by-2 grid;
- recognizable, on-model character identity in all relevant panels;
- one distinct beat per panel and a readable ending;
- consistent costume, props, screen direction, and environment geography;
- professional previs linework rather than polished comic rendering;
- no duplicated, missing, fused, or extra panels/limbs/characters;
- notes, red guides, and blue arrows that do not obscure the action.

If a material failure is visible, make one focused regeneration that names the defect and preserves everything else. Do not loop indefinitely. Return the strongest result and briefly note any remaining limitation.

## Non-negotiable art direction

- Preserve the exact referenced identity, proportions, silhouette, costume construction, color placement, accessories, and stylized cartoon/illustrated aesthetic.
- Do not age the character up or down, simplify, mutate, make realistic, convert to anime, reinterpret as painterly art, or render as realistic 3D.
- Use clean black sketch linework, minimal grayscale shading, and selective reference-matched color accents.
- Use simple, believable, spatially coherent environment blocking with strong silhouettes and uncluttered backgrounds.
- Prioritize animation readability, pose clarity, action choreography, facial acting, and continuity over decorative detail.
- Present professional previs/storyboard work, not a finished comic page, poster, splash art, contact sheet of polished illustrations, or production render.
- Avoid gore unless explicitly requested.

## Output

Return exactly one generated storyboard image by default. Briefly state that it is an eight-panel 16:9 previs sheet and mention the inferred scene arc only if useful. Do not expose the full internal prompt unless the user asks for it.
