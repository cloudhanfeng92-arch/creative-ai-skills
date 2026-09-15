# 科技产品 TVC 制作流程

## 1. 项目规格与时间结构

默认成片：40 秒、1920×1080、16:9、24 fps、H.264 MP4、AAC 立体声。慢动作源素材可用 60 fps，但最终时间线仍按交付帧率输出。

40 秒版本采用六幕结构：

| 幕次 | 时间 | 任务 | 视觉方向 |
|---|---:|---|---|
| 1 沉静开场 | 0–5s | 建立产品质感与悬念 | 微距、慢推进、环境元素 |
| 2 挑战者觉醒 | 5–11s | 目标用户出场、节奏加速 | 人物特写、动态蒙太奇 |
| 3 核心功能 | 11–15s | 产品交互与卖点提示 | 产品特写、UI/字幕 |
| 4 技术拆解 | 15–22s | 建立技术可信度 | CG 结构、剖面、科技光效 |
| 5 极限验证 | 22–29s | 场景化证明核心卖点 | 多场景快切、慢动作爆发 |
| 6 品牌收尾 | 29–40s | 情绪升华、品牌落版 | 超广角、产品英雄镜头、Logo |

其他时长不要机械裁切。优先保留“建立 → 证明 → 升华”的因果链，再按广告时长压缩或扩展镜头数量。15 秒版本可合并第 2、3 幕及第 4、5 幕；60 秒版本可增加使用场景与技术证明，但不要重复同一卖点。

## 2. 产品视觉锚点

### 2.1 抠图

从真实产品图获得透明背景 PNG：边缘干净、透明区域无残留、细小按键与接口完整。检查反光边缘、半透明材质、屏幕和 Logo。

### 2.2 工作室英雄图

默认视觉锚点：深黑背景 `#0a0a0a`，左上 45°主光，右侧柔和补光，低调侧光，冷色高端科技感。尊重真实材质，不要把真实亮面产品强行改成哑光。

```text
Professional studio product photography of {产品名称}, exact design and proportions from the reference product, three-quarter hero angle, low-key Rembrandt-style lighting, left 45-degree key light, subtle right fill, deep black background #0a0a0a, controlled highlights, premium technology aesthetic, cold color palette, crisp material detail, commercial photography, 16:9
```

负面约束应包含：错误 Logo、额外按键、接口变化、比例改变、文字乱码、重复部件、过曝高光、塑料化材质。

### 2.3 三视图

生成正面、侧面、3/4 俯视图。保持同一产品、尺度、焦段感、背景与光线；若生成模型难以在合图中稳定复现，优先分别生成后再排版。

```text
Three-view product reference sheet of {产品名称}: front view, side profile, and three-quarter top-down view; exact same product identity, geometry, materials, colors and branding in every view; consistent studio lighting, deep black background, matched scale, orthographic reference presentation
```

### 2.4 九宫格构图锚点

建立 KF1–KF9：

| 编号 | 构图 |
|---|---|
| KF1 | 环境全景，建立世界观 |
| KF2 | 产品正面中景，突出主要功能区 |
| KF3 | 核心功能特写 |
| KF4 | 侧面中景，展示轮廓与厚度 |
| KF5 | 低角度英雄镜头 |
| KF6 | 材质、接口或 Logo 极致特写 |
| KF7 | 正俯视 |
| KF8 | 倾斜或旋转的动态构图 |
| KF9 | 产品进入真实使用场景 |

每格清楚标注 KF 编号。若一次生成九宫格导致产品身份漂移，改为单格生成并后期拼版。

完成检查：透明 PNG、英雄图、三视图、KF1–KF9 均已生成，并由用户确认产品身份与视觉方向。

## 3. 六幕脚本与分镜

### 3.1 脚本表

每幕至少包含：时间段、幕名、沟通任务、旁白/屏幕文案、视觉描述、主体动作、景别、运镜、声音提示、卖点证据。旁白应简洁有力，避免没有证据的绝对化表述。

```text
为 {产品名称}（{产品类别}）创作一支 {广告时长} 秒科技产品 TVC。
目标受众：{目标受众}
品牌调性：{品牌调性}
已确认卖点：{核心卖点}

使用“建立产品质感—人物需求—功能回应—技术证明—场景验证—品牌升华”的六幕结构。逐幕输出精确时间段、沟通任务、旁白或屏幕文案、可拍摄的视觉动作、景别、运镜和声音提示。镜头时长总和必须等于 {广告时长} 秒。所有产品规格只使用已确认信息。
```

### 3.2 镜头设计

40 秒版本可从以下镜头组起步：产品纯展示 3–4 镜约 10 秒；人物/场景 2–3 镜约 6 秒；技术展示 2–3 镜约 7 秒；极限场景 4–5 镜约 7 秒；收尾 2–3 镜约 10 秒。镜头数量和时长应服务创意，不是硬性配额。

每个镜头按统一字段记录：

```text
镜头编号：S{幕次}-{镜号}
时间码：{起始}-{结束}
时长：{秒}
画面目的：{本镜头证明什么}
景别与焦段感：{极致特写/特写/中景/全景/超广角等}
运镜：{推/拉/摇/移/跟/环绕/固定/航拍等}
主体与动作：{具体、可观察的动作}
环境与光线：{场景、时段、色调、光源}
产品锚点：{英雄图/三视图/KF编号}
声音：{旁白/BGM节拍/音效}
转场：{硬切/匹配剪辑/淡化等}
```

```text
Cinematic storyboard frame for {产品名称} technology commercial, shot {镜头编号}, {景别与构图}, {主体与动作}, {场景与光线}, camera movement implied by composition: {运镜}, exact product identity from the supplied anchor image, premium commercial cinematography, coherent color script, realistic materials, 16:9
```

### 3.3 关键镜头四格推演

对复杂产品运动、转场、技术拆解和高潮镜头生成四格连续画面：起始帧、运动中段 A、运动中段 B、结束帧。四格必须锁定主体身份、运动轴线、空间关系、光线方向与时间连续性。

```text
Four-panel sequential storyboard for shot {镜头编号}, continuous motion from {起始状态} to {结束状态}; panels 1–4 show one uninterrupted camera and subject movement; identical product geometry, lighting direction, environment and screen direction across panels; cinematic commercial quality, 16:9 frames
```

阶段交付：六幕脚本、完整镜头表、全部分镜图、必要的四格推演图。确认后才进入视频生成。

## 4. 分镜视频

每个镜头使用对应分镜图和文字说明生成，文件名使用 `shot-{镜头编号}`。提示词必须描述主体身份、起始状态、结束状态、主体动作、镜头运动、运动速度、环境运动、必须保持不变的元素、时长与画幅。

```text
Cinematic technology-product commercial clip for {产品名称}, shot {镜头编号}, starting from the supplied storyboard frame. {主体动作}. Camera: {运镜、方向、速度}. Environment motion: {环境运动}. Preserve exact product geometry, materials, colors, buttons, ports, screen and logo throughout. Smooth physically plausible motion, stable details, premium commercial lighting, {时长} seconds, 16:9.
```

各幕默认节奏：

- 开场：极慢推进、微距质感、冷色氛围
- 觉醒：人物动态、剪辑加速、对比增强
- 功能：产品交互清楚，字幕安全区预留
- 技术：结构逻辑清晰，避免无依据的内部构造
- 极限：动作爆发但产品仍可辨认
- 收尾：英雄镜头稳定，Logo 与法定文案可读

逐镜检查：时长、运镜方向、产品身份、人物一致性、结构逻辑、画面抖动、边缘融化、Logo/文字漂移、色彩连续性、首尾帧可剪性。记录“通过 / 局部修正 / 重做”及原因。

## 5. BGM 与声音

先依据品牌调性选择方向，不局限于固定曲风：

| 方向 | 适合 | 典型弧线 |
|---|---|---|
| 未来科技电影感 | 旗舰产品、技术突破 | 神秘 → 张力 → 史诗 |
| 赛博重低音 | 年轻受众、街头与运动 | 酷感 → 爆发 → 余韵 |
| 电影化 Phonk | 极限运动、强冲击 | 压迫 → 释放 → 震撼 |

40 秒默认音乐结构：0–5 秒氛围引子、5–15 秒渐进、15–22 秒主节拍爆发、22–29 秒桥段、29–40 秒品牌收尾。节拍爆发应与关键技术或视觉高潮同步，不要只按幕名机械对齐。

```text
Original 40-second cinematic electronic score for a premium technology commercial, cold futuristic atmosphere, sparse ambient intro, controlled rhythmic build, powerful but clean beat drop near 16 seconds, tension-preserving bridge, memorable epic outro, space for concise voice-over, no vocals, BPM 120–140
```

同时规划转场呼啸、机械细节、触控反馈、环境声和品牌收尾音。确保音乐、音效和素材具备所需使用权；不得把受版权保护作品的近似复刻当作默认方案。

## 6. 合成、导出与验收

剪辑以硬切和匹配剪辑为主；只有情绪转换确有需要时使用短淡化。第三幕或对应功能段预留卖点字幕，最后约 3 秒完成产品英雄镜头、Logo 和必要法定信息。

默认混音起点：BGM 约 -6 dB，旁白出现时自动压低至约 -12 dB；实际以响度、清晰度和平台规范为准。首尾分别使用约 0.5 秒淡入和 1 秒淡出，强收尾设计除外。

导出前逐项检查：

- 镜头无遗漏，时间码连续，总时长符合目标
- 卖点出现顺序与脚本一致，文字无错别字
- 产品、人物、场景、色彩与运动轴线连续
- Beat、转场、关键动作和声音命中点同步
- Logo、字幕和法定信息清楚且位于安全区
- 无生成水印、错误品牌、错误规格或未授权素材
- 画面无明显闪烁、形变、重复帧或黑帧
- 音频无削波、突跳、底噪和旁白遮蔽

默认交付：高码率母版、平台发布版、无字幕清洁版（如需要）、音频分轨/字幕文件（如需要）、镜头与素材索引。

## 7. 多场景扩展

山地车、滑雪、跳伞、潜水等独立场景组，应先建立环境锚点和安全合理的使用逻辑，再设计镜头。每组可采用约 5 镜、15 秒作为起点，并可作为独立短片或替换极限验证段；具体长度服从主片结构。

```text
Environment reference for {场景名称} in a {产品名称} commercial, {场景描述}, physically plausible product use, dramatic motivated lighting, cinematic atmosphere, premium action-sports photography, clear spatial layout, 16:9
```
