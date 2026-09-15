# Quality gate

Inspect the generated pixels; prompt compliance cannot be inferred from the terminal status alone. A candidate may be delivered only when it passes the checks that apply to its scene.

## Hard checks

- Correct aspect ratio, subject type, principal-person count or closed-group total, and requested activity; an intentionally open background crowd may remain approximate.
- No unexpected duplicate faces, extra people, missing people, or identity swap.
- No obvious missing limbs, fused fingers, broken hands, overlapping bodies, or objects passing through anatomy.
- Key tool, vessel, boat, fabric, furniture, or architectural element has coherent structure and scale.
- No modern object, plastic-film textile, theatrical palace costume, heavy beauty retouching, tutorial-page layout, model-generated caption, logo, or fake watermark. A platform-required AI mark is not a generation defect and must not be evaded.
- Light has a credible source and direction; highlights, fill, reflection, and shadows agree.

## Song-aesthetic checks

- The image feels lived-in rather than staged or fashion-led. A requested ceremony, festival, busy market, storm, or urgent action may be energetic, but it must remain credible rather than theatrical spectacle.
- The palette remains restrained and low in saturation, with no arbitrary neon accents.
- Cotton-linen, bamboo, clay, aged wood, stone, leaves, and water behave like their real materials.
- The setting has useful negative space or layered depth; a group is not arranged in a rigid row.
- Faces retain believable texture and variation rather than copied beauty-template features.
- The requested topic remains primary; decorative “ancient Chinese” motifs do not take over.

## Series checks

- Shared image character, material truth, palette discipline, and overall lighting logic are coherent. Any planned change of season, weather, time, or light source reads as intentional rather than accidental drift.
- Recurring people keep their face, hair, garment layers, and fixed color slots when a reference lock was requested.
- Shot scale and composition vary enough to create rhythm; the series is not a set of near-duplicates.
- Each image performs its assigned narrative job and contains only its intended people and props.

For an explicitly person-free scene, also verify that no decorative person or silhouette was added, architecture remains structurally coherent, water and mist obey the scene's physical conditions, and generic ancient ornament does not displace the requested landscape or still-life subject.

## Candidate selection

For each native four-candidate group, rank candidates in this order:

1. exact request and count compliance;
2. anatomy, contact, tool, and spatial correctness;
3. continuity with the rest of the series;
4. motivated light and material truth;
5. composition, expression, and atmosphere.

Reject a beautiful candidate when it violates a hard constraint. For a single-group request, show all viable candidates and identify the strongest one. For a distinct-shot series, deliver one selected candidate per shot as the main sequence and retain the alternatives on the LibTV canvas.

## Targeted correction

Correct the cause, not the whole prompt:

- wrong count → move the exact count to the opening clause and remove conflicting plural language;
- copied faces → strengthen distinct face, hair, color, position, and task anchors;
- broken action → simplify to one contact chain and one tool per person;
- flat light → name one source, direction, target, and secondary fill;
- plastic fabric → state weight, fiber, folds, wetness, and gravity behavior;
- generic costume-drama look → reduce ornament and reinforce ordinary cotton-linen workwear, natural posture, and documentary framing.
