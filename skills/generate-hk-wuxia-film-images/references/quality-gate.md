# 港式胶片武侠图片质量门槛

Inspect the generated pixels. A successful terminal status proves only that a task completed; it does not prove prompt compliance or visual quality.

## Hard checks

- Correct aspect ratio, principal-subject count, identities, left/right and depth placement, action, gaze, prop ownership, setting, and story beat.
- No extra or missing principal figures, duplicated faces, identity swap, missing limbs, fused fingers, broken anatomy, weapon through body, or impossible hand/prop contact.
- Swords, bows and strings, instruments, horse tack and legs, bridge ropes and planks, stairs, eaves, furniture, garments, and architecture have coherent structure, perspective, and scale.
- No unrequested modern object, plastic-looking textile, immaculate costume-shop styling, palace spectacle, beauty-ad skin, tutorial layout, generated caption, logo, signature, or fake watermark.
- Light has a credible source and direction. Rim, fill, reflection, rain highlights, wet surfaces, and shadows agree; highlights are not clipped and shadows are not crushed.

## Style checks

- The result reads as a 1990s Hong Kong live-action costume-wuxia film still, not an illustration, generic fantasy poster, modern cosplay photograph, anime frame, or glossy 3D render.
- 35mm grain, photochemical tonal roll-off, matte softness, mild haze, and edge halation feel integrated. Eyes and expressions remain readable; the image is not obscured by fake noise or indiscriminate blur.
- Color is aged and low in saturation with a scene-specific warm/cool logic. No neon blue-purple, candy color, modern HDR, extreme teal-orange grade, pure crushed black, or sharp digital outline.
- Mid-telephoto compression, shallow-depth layering, natural foreground obstruction, off-center balance, and useful negative space support the story. A deliberately wider action or environment shot may adapt the lens while retaining older-film restraint.
- Costumes and scenery show weighted natural fibers, wear, dampness, dust, and believable material behavior; nothing looks like glossy plastic or luxury stage costume unless explicitly requested.
- Performance is controlled and psychologically legible. Wind, cloth, hair, rain, smoke, dust, horse motion, or a practical prop creates life without modern action-spectacle excess.
- Requested supernatural imagery feels partly concealed and tactile, like optical or practical effects, not contemporary high-saturation game VFX.

## Series checks

- Shared photochemical image character, palette discipline, material truth, and emotional register remain coherent. Planned changes of time, weather, or light source read as intentional.
- Recurring figures keep face, hair, garment layers and fixed colors, wear state, and signature props when continuity was requested.
- Shot scale, camera position, foreground device, action, and story job vary meaningfully; the series is not a collection of near-duplicate portraits.
- Every prompt's requested people and props appear only in the intended shot, and results map unambiguously to `GROUP`/`SHOT` labels and LibTV nodes.

## Candidate selection

Rank candidates in this order:

1. exact request, count, layout, action, and prop compliance;
2. anatomy, contact, object, horse, and architectural correctness;
3. recurring-character and series continuity;
4. 1990s photochemical style fidelity, motivated light, and material truth;
5. composition, expression, atmosphere, and narrative hook.

Reject an attractive candidate when it violates a hard constraint. For one native group, deliver all viable candidates and identify the strongest. For a distinct-shot series, deliver one strongest candidate per node as the main sequence and note that alternatives remain on the canvas.

## Targeted correction

Correct only the demonstrated failure axis:

- wrong count or layout → move the exact count and left/right/depth anchors into the opening character paragraph and remove conflicting plurals;
- copied or drifting face → strengthen the cast lock and use one selected concrete identity reference;
- broken weapon or instrument action → simplify to one owner, one hand/contact chain, and one frozen phase;
- flat or contradictory light → name one source, direction, target, atmospheric medium, and one motivated fill;
- modern digital look → reinforce photochemical roll-off, integrated grain, aged low saturation, matte softness, and anti-HDR/anti-sharpness constraints;
- plastic or theatrical clothing → state fiber, weight, worn edges, gravity, dampness or dust, and remove decorative costume language;
- glossy fantasy effect → conceal part of it in mist, cloud, shadow, or silhouette and specify optical/practical-effects character.
