# Prompt compiler

Compile each requested image independently. Shared style language creates coherence; shot-specific camera, space, action, and light create variety.

## 1. Normalize the request

Capture these fields internally:

- theme and image purpose;
- setting, season, time, and weather;
- exact subject count and demographics, including “no people”;
- relationship between subjects;
- primary action and important object;
- mood and intensity;
- output mode: one native group, several same-theme groups, or a distinct-shot series;
- aspect ratio and any supplied visual reference;
- whether a person, place, outfit, or object must remain continuous.

Do not invent a named-dynasty detail, gender, age, or number of people when it would change the user's idea. Ordinary scenic details may be inferred.

## 2. Plan groups and shots

Distinguish these concepts:

- **One native group:** one prompt and one Style Image V8.2 image node, currently yielding four candidate variations.
- **Several prompt groups:** several prompts and nodes exploring different compositions or moments of the same theme.
- **Distinct-shot series:** each final image has a different narrative job. A useful four-shot arc is environment establishment, principal activity, human relationship or material detail, and quiet resolution.

Never put four unrelated scenes into one long prompt and expect `count=4` to distribute them. Never describe same-prompt variations as a four-shot story.

## 3. Lock continuity

For a series, write a short shared `STYLE_LOCK` containing image character, material truth, palette discipline, and lighting logic. Copy its meaning—not necessarily every word—into every production prompt. Keep season and time stable only when the concept requires continuity; for a four-season or dawn-to-night story, make the transitions explicit and causal.

For recurring people, write a `CAST_LOCK` for each person:

`role + requested age range, or only a broad life stage when needed + face/bone structure + brows/eyes/nose/lips + skin character + hair + garment layers + fixed color slots`

Omit an exact age when the user did not provide one.

Use distinct locks for different people. Repeating the same beauty vocabulary for everyone encourages copied faces. If identity consistency is important, select one character image through the quality gate and attach that concrete file as a reference for later nodes; wait for user approval first only when they explicitly requested a character-approval checkpoint. State that the reference controls identity, hair, and fixed garment colors—not the new camera, composition, pose, or action. Wording alone is not a face lock.

## 4. Bind people, space, and actions

For a closed group whose people are all important:

1. State the exact total once: “exactly N people” or “画面明确只有 N 人.”
2. Place each person in foreground, midground, or background and on a clear side of frame.
3. Give each person a distinct face, hair, and color anchor.
4. Give each person one primary task, state, or relationship role. When tools are present, give each tool a clear owner.
5. For physical actions, describe the contact chain: which hand or body part contacts which object, in what direction, and where the gaze goes.
6. Use complementary actions to reveal relationships; do not make everyone perform the same task or look in the same direction.

For an open market, bridge, street, procession, or other public scene, lock one to three principal people with the method above and describe everyone else collectively as sparse background passersby or market activity. Do not demand an exact total for an intentionally open crowd, but do prevent background faces from replacing or duplicating the principal people.

Examples of useful action syntax:

- “her right hand steadies the bamboo rim while her left folds the wet cloth inward”;
- “the elder holds the clay lid near the steam while the child watches the waterline”;
- “one person passes the basket toward the seated companion, whose hands are already beneath its weight.”

## 5. Compile the production prompt

Use this order because early tokens carry the most important constraints:

`camera → exact subjects → spatial anchors and negative space → per-subject placement and action/contact → clothing and material behavior → motivated light and palette → image character and mood`

Write the production prompt as compact, imageable MJ-style clauses. The prompt must not contain:

- source filenames, source titles, or reference-video timecodes;
- aspect-ratio prose such as `16:9 horizontal`; ratio belongs only in the LibTV `ratio` field;
- model-native flags such as `--ar`, `--s`, or `--v`;
- workflow or comparison commands such as `strictly match`, `according to the reference`, `final override`, scoring instructions, or selection rules;
- a long `Avoid ...` / `不要...` / `禁止...` inventory. Keep rejection criteria in the quality gate, not in the visual prompt.

Translate the analyzed reference into direct visual facts: name the light source, direction, softness, illuminated surfaces, fill source, palette, exposure character, material response, and lens behavior without naming the reference itself.

English production template for people or a closed group:

```text
[camera height, focal length, framing and view], [exact principal-subject count and concise subject definition] in [specific setting], [two to four spatial anchors and negative space], [subject position, appearance anchor, owned prop, contact action and gaze], [restrained Song-inspired clothing and material behavior], [dominant light source, direction, softness and illuminated surfaces], [motivated fill source and lifted shadow surfaces], [restrained palette], photorealistic cinematic still, observational Chinese everyday life, natural skin texture, asymmetric layered composition, credible unperformed emotion, real optical depth, gentle highlight rolloff, subtle film grain.
```

English production template for a scene with no people:

```text
[camera height, focal length, framing and view], an empty well-kept [specific Song-inspired setting or landscape], [primary scenic subject], [two to four spatial anchors and negative space], [material behavior, weather movement, water or foliage response, and one small evidence of lived life], [dominant light source, direction, softness and illuminated surfaces], [motivated fill or reflection], [restrained palette], photorealistic cinematic still, quiet observational Chinese atmosphere, asymmetric layered composition, tactile lived-in surfaces, coherent architecture, real optical depth, gentle highlight rolloff, subtle film grain.
```

Also provide a short Chinese summary in this structure:

`镜头与场景 + 人物与位置 + 动作关系 + 光色材质 + 关键避错`

Use the English prompt for generation by default. If the user explicitly requests a Chinese production prompt, use Chinese throughout while preserving the same order.

## 6. Camera and detail decisions

- Use 50mm eye-level medium-wide for ordinary group or environment scenes.
- Use 40mm low or water-level medium-long for boats, banks, ponds, fields, or ground work.
- Use 85mm three-quarter medium-close for a quiet single-person portrait within a setting.
- Use depth of field to separate roles, but keep all key people and contact actions understandable.
- One image should have one primary visual sentence. Remove decorative details that compete with the task.

## 7. Keep rejection logic outside the prompt

Use subject count, owned props, contact chains, coherent materials, and named spatial anchors as positive constraints. Do not append a generic negative inventory to every MJ prompt. Evaluate extra people, anatomy, hands, props, water, cloth, architecture, modern intrusions, text, logos, and watermarks after generation through the quality gate. If one failure recurs and a rerun is authorized, correct it with one short, imageable positive clause rather than a long prohibition list.

## 8. Preflight

Before rendering, verify that:

- the principal-subject count, closed-group total, or explicit “no people” condition is consistent everywhere;
- each closed-group subject has a unique position, role or action, and gaze; each present prop has a clear owner;
- scene, weather, time, and light do not contradict each other;
- the aspect ratio is supported by the live schema and set only in the node field, not repeated in prompt prose;
- the prompt contains no unsupported CLI parameters;
- the prompt contains no source filename or timecode, comparison command, final-override language, scoring rule, or long negative list;
- series prompts share the locks but have genuinely different shot deltas.
