# English Prompt Specification

Compose directly from the brief in natural visual English. This is an independent specification, not a sentence-by-sentence translation of the Chinese rules. Share the visual identity and user facts; phrasing and sentence order may differ. Produce text only.

## Visual identity and English writing

Create refined East Asian fantasy illustrations with two-dimensional rendering, mineral-pigment color layers, delicate brushwork, flowing organic contours, soft directional cinematic light, clear focal hierarchy, and elegant negative space. Fantasy details feel embedded in the environment.

The default palette combines deep blue-green or blue-black foundations, moon-white or ivory highlights, coral-red and jade-green or turquoise accents, and restrained warm gold. Rebalance it for daylight, snow, or requested colors; do not force every color into every image.

Gender, age, number of figures, hairstyle, exposed shoulders, night settings, lotuses, halos, and multiple arms are content choices, not permanent style features. Preserve requested identity and costume.

Lead with subject, action, and spatial arrangement. Follow with materials, setting, palette, lighting, selected movement and fantasy details, then rendering and mood. Use concrete visual phrases and complete sentences as useful. Avoid empty quality strings such as “masterpiece, best quality, ultra amazing.” About 140–240 words is often sufficient, but completeness matters more than length.

Prefer precise relationships: “seated left of center,” “light from the front right,” “mist behind the figure.” Coordinate wind direction. Match costume to identity rather than defaulting to a feminine dress. For landscapes, make the environment the focal subject and omit portrait language.

Distinguish terms:

- “Moon white” is a color, not a requirement for moonlight.
- “Mural-like texture” does not require a physical wall.
- “Cinematic lighting” does not imply photorealism.
- “Translucent glass flowers” and “jeweled ornaments” are different materials.
- A mandorla and a mandala are different motifs. If a specific form is not requested, describe its appearance, for example “a faded golden halo.”

## Replaceable fields

| Field | Supply |
| --- | --- |
| [SUBJECT] | Identity, number, age group, gender, or species |
| [APPEARANCE AND ACTION] | Features, expression, pose, and interaction with props |
| [COSTUME AND MATERIALS] | Appropriate clothing, layers, ornaments, or nonhuman surface materials |
| [SETTING AND TIME] | Place, season, time of day, and compatible weather |
| [FRAMING AND COMPOSITION] | Aspect intention, shot scale, placement, gaze, and negative space |
| [PALETTE] | Dominant colors and subordinate accents |
| [LIGHTING] | Plausible source, direction, focal illumination, and edge light |
| [NATURAL MOVEMENT] | Relevant fabric, hair, foliage, water, or mist movement |
| [FANTASY DETAILS] | Restrained context-specific motifs; omit if unnecessary |
| [MOOD] | The requested emotional tone |

## Reusable English template

Replace fields and remove unused sentences. Final prompts must not retain brackets, menus of alternatives, or editorial instructions.

```text
A refined East Asian fantasy illustration of [SUBJECT] in [SETTING AND TIME], [APPEARANCE AND ACTION]. [COSTUME AND MATERIALS] establish the subject's identity through clear layers and carefully observed details. [FRAMING AND COMPOSITION], with a distinct visual focus, readable spatial relationships, layered foreground and background, and generous negative space. A mineral-pigment palette of [PALETTE], with luminous soft highlights and richly articulated shadows. [LIGHTING], gently illuminating the focal subject and defining its contours with subtle edge light. [NATURAL MOVEMENT] creates restrained flowing curves across the composition. [FANTASY DETAILS] feels organically embedded in the setting, supporting the subject and surrounding space. Delicate two-dimensional brushwork, fine mineral-pigment grain, translucent layers of color, soft cinematic illumination, elegant composition, and a dreamlike East Asian atmosphere. [MOOD].
```

Adapt subject–verb agreement after replacing fields. For an empty scene, begin “A refined East Asian fantasy illustration of [SETTING AND TIME]” and remove character, costume, and anatomy instructions. For groups, describe relative positions and interactions instead of repeating one pose.

## Optional branches

**Poetic garden fantasy:** Establish depth through plants, water, paths, and architecture. A few translucent petals or ornaments catch environmental light. Mist, foliage, and fabric echo a coherent flow. Wonder comes from subtle natural changes; the focal subject stays readable. Daylight works as well as night.

**Sacred mural fantasy:** Use weathered mineral-color layers, scattered gold leaf, and contrasts between still mural surfaces and flowing foreground fabric or clouds. Select a halo, lotus motif, or mural afterimage only when supported by the brief. A mural does not automatically imply a temple or Buddhist figure. If requested, multiple-hand silhouettes belong to a background mural or backlight while the actual subject retains its specified anatomy.

Choose one leading branch; a blend borrows a small amount of texture or atmosphere instead of stacking every motif.

## Negative constraints and parameters

When needed, keep negative constraints in a separate English block and derive them from the current scene. If the user asks for no negative prompt, omit that block but retain explicit exclusions as natural scene descriptions in the main prompt, such as “an unoccupied garden” or “without a halo.” Optional baseline:

```text
Avoid plastic-looking 3D rendering, harsh neon, blown highlights, a cluttered background, large effects obscuring the focal subject, and unrelated text, logos, or watermarks.
```

Human subjects may need anatomy and hand–prop constraints; empty scenes do not. Do not ban armor, temples, halos, combat, or intended lettering when requested. Distinguish intentional background silhouettes from unwanted extra limbs on the subject.

Do not append model-specific commands by default. Aspect-ratio prose expresses composition intent, not guaranteed output dimensions. If parameters are requested, provide a separate block using the platform's currently supported syntax. Flags in the reference images are not universal style rules.

## Complete English example

Brief: one adult female guardian in jade-green armor, standing before an ancient mountain-pass mural at dusk, holding a sheathed sword; portrait 3:4; no halo or multiple-hand silhouettes.

English positive prompt:

```text
A refined East Asian fantasy illustration of an adult female guardian standing before a weathered mural at an ancient mountain pass at dusk. She holds a sheathed sword naturally at her side, her expression composed and resolute. Jade-green lamellar armor rests over layered ivory silk, with restrained coral-red ties and small warm-gold fittings. Portrait 3:4 composition, the figure slightly right of center, with open space toward her gaze and clear depth between the foreground stone, the guardian, and the mural. Faded mineral colors and scattered traces of gold leaf remain on the ancient wall. Soft dusk light from the front left illuminates her face, armor, and sword grip; a subtle warm reflection outlines the silk folds. Her cloak and low drifting mist flow in the same direction. A few tiny golden fragments appear to lift gently from the painted surface, introducing a quiet sense of wonder. Delicate two-dimensional brushwork, fine mineral-pigment grain, translucent color layers, richly articulated shadows, elegant negative space, and a solemn, dreamlike atmosphere.
```

English negative constraints:

```text
No halo, multiple-hand silhouettes, or extra figures. Avoid distorted anatomy, hands merging with the sword, plastic-looking armor, harsh neon, effects obscuring the face, text, logos, and watermarks.
```
