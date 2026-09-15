# 复古梦境超现实提示词参考库

本库把 `vintage-dream-surreal-mj` 的固定视觉逻辑扩展到视频流程。核心是“一个熟悉物件 + 一个平静的不可能空间 + 怀旧 80/90 年代 CGI 质感”，而不是堆叠奇观。

## 使用规则

- 生图阶段统一使用 **悠船 Midjourney V7**，尾帧也遵循同一 MJ V7 体系并参考已确认首帧。
- 默认图片与视频均为 16:9；视频统一 Seedance 2.0、720P。
- 图片主体提示词按此顺序：日常主体与悖论 → 环境细节 → 光影、氛围与粒子 → 配色与情绪 → 复古 90 年代 CGI/胶片纹理 → 安静高保真 3D。
- 每场只使用一个核心主体和一个视觉悖论，保持稀疏、和平、可信的梦境感。
- 每条 MJ 提示词固定附加且只附加一次：`--sref 1360520854 1124116562 4710227 --v 7`；16:9 参数放在其前面。
- 保留 soft god rays、gentle mist/haze、luminous dust、soft bloom、reflection、warm/cool contrast、dreamy 90s postcard grain、nostalgic CGI softness 等视觉线索，但不得加入恐怖、故障、文字、Logo 或拥挤人群。

## 12 组日常物件与梦境悖论母题

### 01｜月面台灯

A small vintage desk lamp standing alone on the moon’s powdery surface, its warm pool of light revealing tiny silver wildflowers, distant Earth hanging in a deep cobalt sky, soft lunar haze and drifting luminous dust, gentle amber-blue contrast, dreamy 90s postcard grain, nostalgic CGI softness, serene surreal high-fidelity 3D render.

### 02｜海边冰箱

A vintage refrigerator standing open on a quiet summer beach, cool blue light spilling onto mirror-like wet sand while the shelves hold tiny glowing seashells, pastel sunset reflected in the tide, soft sea mist and drifting sparkles, warm coral and turquoise palette, dreamy 90s cinematic grain, nostalgic CGI softness, peaceful surreal high-fidelity 3D render.

### 03｜云海电话亭

A weathered red telephone booth floating alone above a calm sea of clouds, its black telephone connected by a cable to a warm pendant lamp suspended far below, soft sunset haze and luminous dust, faded red, cream, mist blue and amber palette, dreamy 90s travel-postcard grain, nostalgic CGI softness, serene surreal high-fidelity 3D render.

### 04｜沙漠浴缸

A white enamel bathtub standing alone in an endless quiet desert, filled with perfectly still deep-blue seawater that reflects an indoor ceiling, soft sand haze and tiny drifting sparkles, warm sand, ivory, ocean blue and lavender dusk palette, dreamy 90s CGI film grain, peaceful liminal high-fidelity 3D render.

### 05｜森林电视机

An old CRT television placed in a damp forest clearing, its curved glass screen showing the exact same forest with no visible boundary, soft mossy light and faint scanlines, deep green, charcoal, cool blue and warm brown palette, nostalgic home-video grain, gentle bloom, calm surreal high-fidelity 3D render.

### 06｜盐湖床铺

An old iron bed with pale blue sheets floating at the center of a mirror-like salt lake, its reflection revealing a warm bedroom beneath the water, soft dawn haze and luminous dust, salt white, powder blue, cream and blush palette, dreamy 90s home-advertising grain, nostalgic CGI softness, serene high-fidelity 3D render.

### 07｜草地自动售货机

A rounded mint-green vintage vending machine standing in an endless meadow, its glass compartment filled with a slowly rotating star field instead of drinks, gentle grass movement and tiny floating motes, faded mint, meadow green, deep navy and soft orange palette, nostalgic 90s campus-video grain, peaceful surreal high-fidelity 3D render.

### 08｜屋顶潜水伞

A transparent umbrella turned upside down on a quiet concrete rooftop, holding a complete sphere of clear seawater with tiny fish and no spill, soft overcast rays and delicate reflections, gray blue, transparent aqua, wet silver and muted orange palette, dreamy 90s CGI softness, calm surreal high-fidelity 3D render.

### 09｜雪地收音机

A wooden vintage radio sitting alone in a boundless snowfield, its amber tuning window releasing a small pool of warm indoor light that illuminates falling snow, soft polar haze and glowing dust, cold white, dark walnut and amber palette, nostalgic film grain, gentle bloom, serene surreal high-fidelity 3D render.

### 10｜雨中钢琴室

A black upright piano standing in a roofless room during gentle rain, a dry red carpet beneath it and a small fragment of ceiling hovering above, soft rain reflections and warm interior glow, charcoal black, rain gray, muted red and cream palette, dreamy 90s cinematic grain, calm surreal high-fidelity 3D render.

### 11｜海底公交站

An old yellow bus stop and metal bench resting on a clear ocean floor, coral formations glowing like distant street lamps while dry autumn leaves sit on the bench, soft underwater rays and suspended particles, sea blue, faded yellow, coral orange and deep teal palette, nostalgic travel-video grain, peaceful surreal high-fidelity 3D render.

### 12｜白墙时钟房

A huge round wall clock floating in an empty white room, a far doorway opening onto a misty forest whose movement matches the clock hands, soft window haze and tiny dust motes, ivory, pale gray, mist green and gentle gold palette, minimal 90s CGI grain, quiet surreal high-fidelity 3D render.

## Seedance 2.0 视频模板

```text
[wide/ultra-wide][locked/slow push-in/slow pull-back/gentle lateral move] camera, calm continuous motion with no cuts; the familiar object undergoes one gradual surreal change only; mist, dust, waves, grass, curtains, reflections, CRT glow or lamp light move subtly and naturally; preserve the reference object shape, vintage material, spatial paradox, composition, warm/cool palette, soft bloom and nostalgic 80s/90s CGI texture; no shaking, no stutter, no sudden morphing, no random new objects, people, text, logos or horror effects; Seedance 2.0, 16:9, 720p.
```

首尾帧模式只描述有因果的渐进变化，例如冰箱门缓慢开启，门内海滩薄雾逐渐与外部海岸连成一体；禁止主体替换、跳切、强故障闪烁和梦境逻辑重置。
