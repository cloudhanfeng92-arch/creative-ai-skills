# 港式胶片武侠视频语言

This file defines the moving-image grammar. It never replaces the eight-paragraph keyframe language in `image-visual-language.md`; it preserves that frame and makes its world move plausibly.

## 1. Separate the layers

### Visual and atmosphere layer

- 保留关键帧的90年代香港古装武侠电影气质、金庸江湖情绪及按场景建立的低饱和冷暖关系。
- 35mm真实物理显影感：细腻而明显的胶片颗粒、轻微拍立得式朦胧柔光、雾面空气感与柔和边缘漫射光晕。高光柔和温润、不过曝，暗部保留胶片纹理，面孔、手与兵器细节清楚；不把首帧强制改成暖褐粗粒、暗角或过曝的褪色老照片。
- Skin, cotton, linen, old wood, damp stone, dust, water, horse tack and metal must remain tactile and imperfect.
- Warm sunlight is the compatible daylight default. It must come through a real opening and land on named surfaces. Night, rain, snow, dense forest and enclosed rooms use their own plausible sources instead of fabricated sun.
- The comfortable, relaxed feeling belongs mainly to light, color, breathing room, natural performance and environmental rhythm. It can coexist with one brief high-energy action.

### Performance layer

- Expressions follow an event: gaze registers first; breath, shoulders, jaw and mouth follow.
- Happiness is open and genuine but never posed, broad caricature or beauty-advertising laughter.
- Encounters, travel, shared food, music and reunion can end in relaxed warmth or a small true smile.
- Danger, injury and combat require plausible focus, effort, fear, pain, relief or mutual recognition; do not force a smile.
- Dialogue is short and directed to someone visible or spatially established. No voice-over exposition.

### Physics layer

- Name the support point, applied force, center-of-mass transfer, path, contact, reaction, inertia/recoil, deceleration and landing.
- Speed is conveyed by fast commitment, readable body mechanics, foreground crossings, short camera response, material lag and a clean landing—not slow motion or random shake.
- Weight is comparative: thin leaves and hair react sooner; sleeves follow; heavy hems, scabbards, thick branches and bodies lag and move less.
- A weapon has an owner, grip, blade/shaft direction, mass and contact point. It cannot pass through hands, bodies or scenery.
- Shoes grip, slide or land on a named surface. Dust, water, gravel, leaves and timber respond only where contact happens.

## 2. Three motion modes

### `RELAXED_JIANGHU`

Use for walking, riding at an easy pace, flute playing, tea, fishing, tending a wound, reunion, listening, watching weather or quiet travel. The person completes one purposeful action promptly; secondary motion comes from breath, gaze, cloth and the environment. Camera remains observational or makes one short, gentle move.

### `HYBRID_WUXIA`

Use when a relaxed scene contains one crisp interruption: catching a falling cup, turning at a sound, mounting, drawing a blade, avoiding a branch, exchanging an object or a brief playful feint. The normal world remains calm; one force chain is fast and direct, followed by an immediate return to balance.

### `GROUNDED_WUXIA_ACTION`

Use for pursuit, parry, strike, leap down, roll, dodge, archery, horse action or close-quarters conflict. Start within the first 0.12 seconds and finish the main event by `E=(F−B_f)/30`, where `F=round(30D)` and the recovery buffer is `B_f=min(15,max(11,round(0.12F)))` frames. Default `D` to 4 seconds; extend up to 5 only when the same continuous force chain needs more readable phases. Native duration equals delivered duration; current Seedance supports only whole-second 4/5 choices in this range. Keep the whole source and its internal recovery buffer; never shorten, retime or pad it. Default to gravity-bound movement and practical stunt energy; no floating qinggong, teleportation, energy waves or game-skill effects unless the user explicitly overrides realism.

## 3. Camera grammar

One complete 4–5-second shot has one principal camera behavior:

- locked medium or medium-long observation for performance and geography;
- short slow push for recognition, listening or emotional arrival;
- short pullback for reveal or departure;
- lateral follow for walking, riding or crossing;
- action-led pan for a fast entrance, weapon path or evasive move;
- low tracking for footwork, landing, horse or pursuit;
- restrained handheld follow for close danger, with weight and recovery rather than digital jitter.

The camera starts and stops for a reason. It may be partially occluded by branches, cloth, pillars, riders or dust when that clarifies depth and creates readable chaos. Avoid unmotivated orbit, simultaneous pan/tilt/dolly/roll, drone motion, snap zoom, whip movement without a target and random reframing.

Auto-cutting belongs to the edit plan between complete clips. Design the first and last states for gaze, prop state, landing or reveal continuity before generation. Never trim into a clip to find an impact or movement match. Maintain the 180-degree axis and screen direction unless a neutral establishing shot deliberately resets them.

## 4. Wind and environmental comfort

Choose one wind direction per shot and preserve it across a continuous location unless the story changes it.

- Outdoors: light vegetation can sway continuously but asynchronously; avoid every leaf moving in lockstep.
- Hair: loose strands react quickly and with small irregularity; pinned hair remains mostly stable.
- Thin sleeve edges: follow wind and arm speed with a short delay.
- Heavy robe hems and cloaks: lower amplitude, larger inertia and delayed settling.
- Rain, mist, smoke, hanging cloth, water and dust obey the same direction and nearby occlusion.
- Indoors or under a deep eave: reduce wind to a plausible draft near an opening. Heavy furniture, walls and solid objects do not sway.

Comfort comes from coherent natural motion: a steady breeze, soft leaf shadow, subtle breathing, clean spatial sound and enough time to see the body settle. It does not mean slow motion, lethargy or lack of purpose.

## 5. Light and film continuity during motion

- Lock the keyframe's light source direction, color role, face exposure and shadow density.
- Permit only local changes caused by moving leaf shadow, water reflection, cloud cover or a person passing through the source.
- Keep skin tone, costume color and background density stable over time.
- Motion blur must look optical and proportional to speed; do not smear stationary faces or sharpen moving edges digitally.
- Grain may vary frame to frame like film but must not crawl into boiling surfaces, identity changes or geometry shimmer.
- 无全局曝光脉冲、自动白平衡漂移、霓虹高饱和、塑料肤质或过度洁净的数码边缘。保持首帧柔和的胶片光晕，高光不过曝，面孔与关键动作细节完整。

## 6. Dialogue and sound

Default audio is diegetic only: wind, leaves, cloth, footfall, breath, horse, water, wood, stone, weapon and a short spoken line when the story requires it.

- Ordinary shot: at most one roughly 10–12-character Chinese line; prefer 4 seconds, and extend to a supported duration up to 5 only when natural delivery plus the ending buffer cannot fit.
- High-energy shot: preferably no line; if essential, about 4–8 characters outside the peak contact moment.
- Name speaker, addressee, delivery, volume and time window. Require lip sync and end speech by E, before the complete source's internal recovery buffer. Keep that buffer and all audio through the source end.
- Never request music, humming, chanting, singing, voice-over, subtitles, captions, titles, logos, model-painted fake watermarks or any visible writing. A platform-required AI mark is separate delivery metadata, not generated scene content.

## 7. Useful fast-chaos recipe

For grounded wuxia chaos, combine no more than four readable cues:

1. the principal crosses a strong foreground or depth plane;
2. one opponent or companion reacts a fraction later;
3. cloth, loose leaves, dust, rain or water responds at the real contact point;
4. the camera makes one short motivated follow and settles with the body.

Do not manufacture chaos with axis flips, teleportation, crowd multiplication, non-causal explosions, persistent camera vibration or speed ramping.
