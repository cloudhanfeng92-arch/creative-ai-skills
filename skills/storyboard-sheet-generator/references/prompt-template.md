# Unified image-generation prompt template

Use this as a structural template, not as text to copy blindly. Replace every bracketed field with concrete content.

```text
STORYBOARD SHEET — SINGLE UNIFIED IMAGE

Create one clean professional 16:9 horizontal previs storyboard sheet optimized as a visual reference for Seedance video generation. Use a strict 4-column by 2-row layout: exactly 8 clearly separated panels, numbered 1–8 from left to right across the top row, then left to right across the bottom row. Use consistent gutters and reserve a narrow note strip below each panel.

REFERENCE PRIORITY AND CHARACTER LOCK
The supplied reference image(s) are the exact identity and design authority for [CHARACTER NAMES]. Preserve, in every relevant panel: [FACE AND IDENTITY MARKERS]; [BODY PROPORTIONS AND SILHOUETTE]; [HAIR/HEADWRAP/HEADGEAR/GOGGLES]; [OUTFIT, MATERIALS, COLORS, ACCESSORIES, GLOVES, BOOTS]; [STYLIZED CARTOON SHAPE LANGUAGE AND LINE STYLE]. Keep the character instantly recognizable and perfectly on-model from all angles. Never redesign, merge identities, change costume details, change color placement, age up/down, make realistic, convert to anime, reinterpret as painterly art, or render as realistic 3D.

STORY AND CONTINUITY
[CONCISE STORY SUMMARY]
Continuity anchors: [LOCATION GEOGRAPHY]; [SCREEN DIRECTION]; [PROP STATES]; [LIGHTING/TIME]; [CHARACTER POSITIONING]. Maintain clear eyelines, entrances/exits, left/right action continuity, and believable perspective across all panels.

EIGHT PANELS
1. [SHOT SIZE/ANGLE] — [COMPOSITION, ACTION, EXPRESSION, ENVIRONMENT]. Camera note: “[VERY SHORT NOTE]”. Action note: “[VERY SHORT NOTE]”.
2. [SHOT SIZE/ANGLE] — [COMPOSITION, ACTION, EXPRESSION, ENVIRONMENT]. Camera note: “[VERY SHORT NOTE]”. Action note: “[VERY SHORT NOTE]”.
3. [SHOT SIZE/ANGLE] — [COMPOSITION, ACTION, EXPRESSION, ENVIRONMENT]. Camera note: “[VERY SHORT NOTE]”. Action note: “[VERY SHORT NOTE]”.
4. [SHOT SIZE/ANGLE] — [COMPOSITION, ACTION, EXPRESSION, ENVIRONMENT]. Camera note: “[VERY SHORT NOTE]”. Action note: “[VERY SHORT NOTE]”.
5. [SHOT SIZE/ANGLE] — [COMPOSITION, ACTION, EXPRESSION, ENVIRONMENT]. Camera note: “[VERY SHORT NOTE]”. Action note: “[VERY SHORT NOTE]”.
6. [SHOT SIZE/ANGLE] — [COMPOSITION, ACTION, EXPRESSION, ENVIRONMENT]. Camera note: “[VERY SHORT NOTE]”. Action note: “[VERY SHORT NOTE]”.
7. [SHOT SIZE/ANGLE] — [COMPOSITION, ACTION, EXPRESSION, ENVIRONMENT]. Camera note: “[VERY SHORT NOTE]”. Action note: “[VERY SHORT NOTE]”.
8. [SHOT SIZE/ANGLE] — [COMPOSITION, ACTION, EXPRESSION, ENVIRONMENT]. Camera note: “[VERY SHORT NOTE]”. Action note: “[VERY SHORT NOTE]”. The final panel clearly resolves or punctuates the scene.

VISUAL LANGUAGE
Professional storyboard/previs presentation only: clean confident black sketch linework, minimal grayscale shading, selective reference-matched color accents only where useful, strong silhouette readability, expressive poses, exaggerated acting when tonally appropriate, and simple recognizable environmental blocking. Use red camera-frame guides sparingly. Use blue motion arrows for movement and action direction. Put one short camera note and one short action note in [NOTE LANGUAGE] beneath each panel. Make the action readable at thumbnail size.

NEGATIVE CONSTRAINTS
No finished comic-book polish, no splash-page composition, no photorealism, no anime redesign, no painterly reinterpretation, no realistic 3D, no costume mutation, no anatomy drift, no style drift, no clutter, no confusing staging, no unnecessary characters, no excessive background detail, no decorative tangents, no duplicated panels, no missing panels, no fused panels, no gore unless explicitly requested.
```

## Prompt compression rule

If the prompt becomes too long, preserve information in this order:

1. Character lock and identity markers.
2. Concrete content of all eight panels.
3. Continuity anchors and 4-by-2 layout.
4. Previs visual language.
5. Negative constraints.

Remove repeated adjectives before removing any panel action or character-identity detail.
