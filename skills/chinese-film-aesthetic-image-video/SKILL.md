---
name: chinese-film-aesthetic-image-video
description: >
  将人物、古装、武侠、东方文艺或中式场景需求转换为统一的35mm中式胶片电影画面，并在用户确认后完成生图与图生视频。
  生图默认使用 LibTV Style Image V8.2，视频默认使用 LibTV Seedance 2.5。Skill 会先编写专业电影摄影式生图 Prompt，
  输出4张候选图供用户选择，再基于选定图片编写微动效视频 Prompt。任何会消耗积分的生图、重绘、重新生成、视频生成或批量生成操作，
  执行前都必须获得用户明确确认。
---

# 中式胶片美学｜生图与视频

## 1. Skill 目标

将用户提供的人物、服装、动作、情绪、场景、时间、天气、道具等内容，转换为具有稳定中式电影摄影语言的图像和视频。

视觉方向参考传统中国武侠电影、东方文艺电影与胶片摄影语言，重点不是“普通古风 AI 图”，而是：

- 真实东方人物
- 明确的场景空间关系
- 电影摄影式构图
- 前景遮挡与镜头层次
- 冷青绿环境色 + 克制暖色点光
- 35mm 胶片质感
- 柔和低反差
- 高光晕染与 halation
- 黑位轻抬
- 浅景深
- 空气感、湿度、薄雾、雨雪等真实空间介质
- 克制、自然、可被真实摄影机拍摄的画面

---

# 2. 最高优先级：积分消耗确认机制

任何会实际消耗用户积分、额度或付费算力的操作，都必须先向用户确认。

## 必须确认的操作

包括但不限于：

- 生图
- 重绘
- 局部重绘
- 重新生成
- 批量生图
- 图生视频
- 视频重新生成
- 视频延长
- 批量视频
- 任何付费模型节点执行

## 不需要确认的操作

以下操作可以直接完成：

- 需求分析
- 角色分析
- 场景分析
- 生图 Prompt 编写
- 视频 Prompt 编写
- 构图设计
- 镜头设计
- 运镜设计
- 参数建议
- 已生成图片分析
- 候选图筛选建议

## 生图确认

正式创建或执行生图节点前，必须展示：

- 生图模型：LibTV `Style Image V8.2`
- 默认比例：`16:9`
- `quality=auto`
- `stylize=400`
- `weird=0`
- `chaos=30`
- 当前节点输出：`4 张候选图`

并询问：

> 是否确认开始生成这 4 张候选图？

只有用户明确回复“确认 / 生成 / 开始 / 执行 / 可以 / 直接出图”等明确授权后，才能执行。

## 视频确认

用户选定图片后，先完成视频 Prompt，再展示：

- 视频模型：LibTV `Seedance 2.5`
- 输入：1 张已确认图片
- 规则：1 张已确认图片对应 1 个视频节点、1 条视频
- 本次预计视频节点数量

并询问：

> 是否确认使用当前选定图片生成视频？

未获得明确确认，不得执行。

## 重新生成同样需要再次确认

用户说“重做、换一版、再来四张、重新生成视频”等，如果会再次消耗积分，应先完成 Prompt 或参数调整，再次确认。

只有用户在当前指令中明确表示“这一次不用再问，直接重新生成”，才可仅对当前这一次跳过再次确认。

---

# 3. 默认模型与参数

## 生图模型与参数分层

默认模型：LibTV `Style Image V8.2`。纯文字生图使用平台的 `text2image` 模式；有参考图时按实际 schema 选择参考图模式，不把模式名写入画面正文。

沿用用户提供样本的默认规格：

```text
ratio = 16:9
quality = auto
stylize = 400
weird = 0
chaos = 30
count = 4
```

面向用户展示、可复制到支持这些参数的 MJ 输入框的完整提示词，统一以下尾缀：

```text
--chaos 30 --raw --stylize 400
```

统一尾缀不包含 `--ar`；默认 16:9 通过 LibTV 独立 `ratio` 字段设置。用户指定其他比例时修改该字段，并核对当前 schema，不静默改成别的比例。原生 MJ 输入框使用其独立比例设置；此尾缀本身不指定比例。

**区分 MJ 文本格式和 LibTV 的调用字段：**

- LibTV 的 `quality=auto`、`count=4`、`modeType=text2image` 属于平台配置；不能拼成 `--quality auto`、`--count 4`、`--text2image` 等 MJ 参数。
- `Style Image V8.2` 是平台模型名称，不能据此自行添加 `--v 8.2`。模型选择通过 LibTV 当前模型 schema 完成。
- 执行前用 `libtv model search` 和 `libtv model` 核对模型名、字段与取值，LibTV 操作遵循 `libtv-cli`。不要使用未确认的字段、参考图参数、风格代码或模型版本参数。
- 节点提供独立 `ratio / stylize / chaos / weird / quality / count` 字段时，写入对应字段；提交正文去掉已由字段承载的同义尾缀，防止重复或冲突。不能把用于展示的完整 MJ 提示词和节点参数直接重复叠加。
- Raw 优先使用已确认的独立开关；若没有开关但平台明确支持在 prompt 中透传 `--raw`，在正文末尾保留它。两者均未确认时，注明 Raw 未启用，不捏造 `raw=true` 字段，也不承诺已生效。
- `weird=0` 保留在支持的节点配置中；标准展示尾缀不额外追加它。文本尾缀只使用目标模型已支持的参数。

## 视频模型

默认：LibTV `Seedance 2.5`。

```text
1 张已确认图片 → 1 个 Seedance 2.5 节点 → 1 条视频
```

不得把 4 张候选图自动全部送入视频模型。

---

# 4. 生图提示词总原则

沿用参考样本的电影摄影描述法，每张图是一个可被摄影机捕捉的瞬间。固定两段，参数紧接第二段末尾：

```text
第一段：人物或主体、服饰、单一姿态、场景、前中后景关系、构图、景别和机位。

第二段：场景光源与冷暖关系、固定胶片风格。 --chaos 30 --raw --stylize 400
```

默认英文；用户要求中文时，两段均可中文，MJ 参数保留英文 ASCII 语法。英文并非审核通过或生成成功的保证。

- 第一段建议约 70–120 个英文单词，第二段约 35–65 个；这是编辑目标，不是 MJ 硬性长度限制。道具特写、空场景应更短，不机械补人物或皮肤描述。
- 写可见画面，不写剧情解释、人物内心独白、历史评价、剪辑时间码、音效或多镜头事件链。角色专名不是一致性保证；保留稳定的脸型、发型、服装和道具锚点，有可用参考图时按平台能力引用。
- 每镜一个主要姿态，必要时一项辅助动作；定格动作可以有动势，但不要求在同一张图内完成转身、递物、受伤、作画等连续事件。
- 只选一个主景别、一个主机位；前景虚化不遮住叙事重点。建立远景时使用适当的分层景深，不机械套用极浅景深；同一主体不得同时要求正面和背面。
- 风格核心固定，光源、湿度和气氛随场景变化。不要将所有风格模板串联；粒子、萤火、金饰、透明衣料等不是每镜必需元素。
- 正文不用 JSON、Markdown 标题、项目符号、`/imagine prompt:`、Stable Diffusion 权重括号、未验证的 `::` 权重语法或重复的 `No ...` 清单。
- 衣料、年龄、伤害等内容先做第 24 节的语义审查，再组织英文。禁止把高风险剧情翻译后原样堆入正文，或用隐语包装同一不允许的画面。

---

# 5. 第一段：内容与摄影调度

第一段必须是一段完整、具体、可视化的镜头描述。

必须尽量包含以下信息：

1. 地点 / 环境
2. 时间 / 天气
3. 人物身份
4. 服装与发型
5. 人物动作
6. 眼神 / 情绪
7. 道具与人物的具体关系
8. 人物在画面中的位置
9. 前景遮挡
10. 中景主体
11. 背景空间
12. 景别
13. 机位
14. 构图方式

不要写成：

> ancient Chinese woman, Hanfu, sword, bamboo forest, cinematic

应写成：

> Deep inside a rain-darkened bamboo grove at night, an adult East Asian swordswoman stands slightly right of center in a deep crimson cross-collar robe. Her black hair is half pinned, with damp loose strands resting across her cheek. Her right hand grips a black sword hilt close to the lens while the silver blade cuts diagonally across the frame without covering her eyes. Blurred bamboo leaves obscure the lower-left foreground, and layers of cyan-green bamboo fade into mist behind her. Eye-level facial close-up, hidden-observer composition.

核心要求：

**必须描述空间关系，而不是只描述物体清单。**

---

# 6. 第一段写作顺序

推荐顺序：

```text
场景 + 时间
→ 人物身份
→ 服装 / 发型
→ 动作与道具
→ 神态 / 视线
→ 人物画面位置
→ 前景元素
→ 背景元素
→ 景别
→ 机位
→ 构图
```

例如：

```text
Inside a wet wooden corridor of an ancient mountain temple after midnight rain,
an adult East Asian woman stands beside a vermilion pillar...
```

而不是先写一长串风格词再写人物。

---

# 7. 人物描述规则

人物默认使用：

- adult East Asian man or woman / mature East Asian man or woman
- 成人角色明确用 adult，不能把年龄不明的角色自动写成成人；未成年角色仅按适龄、非性化的实际设定描写
- Chinese / East Asian facial features
- photorealistic human appearance
- natural skin texture

古装人物服装必须具体到：

- 款式
- 主色
- 材质
- 层次
- 必要纹样

例如：

```text
a moon-white wide-sleeved Hanfu embroidered with restrained silver botanical patterns
```

优于：

```text
beautiful white Hanfu
```

发型也应具体：

```text
black hair half tied with loose damp strands beside her cheeks
```

优于：

```text
long black hair
```

---

# 8. 动作描述规则

动作必须：

- 可被单帧摄影捕捉
- 姿态清晰
- 重心合理
- 道具关系明确
- 避免同时发生过多动作

推荐：

- turns her head toward...
- lowers her eyes toward...
- grips the sword hilt...
- raises a round silk fan beside her face...
- protects a candle with both hands...
- places a hairpin into...
- looks back while passing...

避免：

- fights dramatically
- performs many martial arts moves
- moves quickly everywhere

除非用户明确要求动作爆发镜头。

---

# 9. 构图规则

参考样本的共同特征，优先使用以下构图：

- 中近景 / 半身 / 胸像
- facial close-up
- medium close-up
- half-body shot
- medium shot
- medium-long shot
- extreme frontal close-up
- eye-level
- slightly low angle
- slightly side-facing view
- three-quarter rear view
- centered / center-right / center-left
- 对称构图只在亭台、棋局、仪式性场景中使用

不要所有镜头都把人物正中居中。

---

# 10. 前景遮挡规则

前景遮挡是本 Skill 的核心摄影特征之一。

优先使用：

- 竹叶
- 树枝
- 芦苇
- 门框
- 窗框
- 柱体
- 帘幕
- 刀剑
- 马头
- 乐器局部
- 雨丝
- 雪花
- 灯笼虚化
- 焦外人物肩部

写法必须描述“遮挡在哪里”。

例如：

```text
blurred bamboo leaves obscure the lower and right edges
```

```text
a blurred pipa head and musician's shoulder frame the left foreground
```

```text
the sword blade stretches horizontally across the frame, softly blurred close to the lens
```

不要只写：

```text
foreground blur
```

---

# 11. 景深与空间层次

画面必须建立：

```text
前景
→ 主体
→ 背景
```

至少包含两个以上空间层次。

常用：

- foreground occlusion
- subject in sharpest emphasis
- background fading into mist
- lanterns receding into depth
- distant pavilions disappearing into haze
- reeds extending into open space

目的：

避免 AI 平铺、棚拍、背景贴图感。

---

# 12. 第二段：光线与胶片风格

第二段不是完全死板复制同一句，而是在固定核心风格下根据场景自适应。

固定核心必须保留：

```text
35mm cinematic film
low-contrast soft focus
subtle highlight bloom
slight halation
slightly lifted blacks
soft shallow depth of field
fine film grain
photorealistic
```

远景可将 `soft shallow depth of field` 换成 `layered depth with softly resolved distant detail`，保留空间可读性；固定美学不等于所有景别使用同一景深。

并根据场景选择：

- humid cyan-green haze
- clear cyan-green daylight
- soft cyan and cool moonlight tones
- cyan-green shadows
- restrained warm golden light
- restrained red lantern glow
- restrained warm brown interiors
- sparse scattered light particles

---

# 13. 色调体系

核心色彩关系：

```text
冷青绿环境底色
+
克制暖色局部光源
```

冷色：

- cyan
- cyan-green
- cool moonlight
- pale cyan
- blue-green shadows

暖色：

- restrained warm gold
- muted amber
- lantern red
- candle red
- warm brown
- subtle sunset gold

严禁默认：

- 大面积艳红
- 高饱和橙黄
- 霓虹色
- 现代商业 HDR
- 过度 teal-orange
- 黑位压死

---

# 14. 胶片质感

固定优先词：

```text
35mm cinematic film
fine film grain
subtle highlight bloom
gentle halation
slightly lifted blacks
low-contrast soft focus
gently softened in-focus subjects and environmental edges
```

这组词共同形成：

- 柔而不糊
- 有细节但不数码锐
- 高光有胶片扩散
- 黑位不死黑
- 人物和环境边缘略柔
- 真实胶片颗粒

禁止：

- ultra sharp digital
- hyper HDR
- glossy CGI
- plastic skin
- oversharpened
- crushed blacks

---

# 15. 光线模板选择

## 白天自然光

```text
Soft natural daylight, clear cyan-green tones with restrained warm accents
```

## 窗边

```text
Soft natural window light, clear cyan-green garden tones with restrained warm brown interiors
```

## 黄昏

```text
Soft twilight rim backlighting, cyan-green shadows with muted warm golden light
```

## 月夜

```text
Soft moonlight rim backlighting, soft cyan and cool moonlight tones with restrained warm accents
```

## 灯笼 / 烛火

```text
Soft cool ambient light with restrained red lantern glow / candle glow
```

## 雨夜

优先增加：

```text
humid cyan-green haze
wet reflective surfaces
soft diffused moonlight
```

## 雪夜

优先增加：

```text
cool moonlight
soft snow haze
restrained warm lantern glow
```

---

# 16. 环境气氛词使用规则

可以按场景选用：

- humid haze
- thin mist
- drifting snow
- rain haze
- fine scattered light particles
- floating reed seeds
- soft firefly glow
- wet reflections

不要每张图机械加入：

- 萤火虫
- 魔法粒子
- 梦幻光点

真实写实场景中只保留少量 `sparse scattered light particles`。

如果用户要求纯写实，避免 `surrealism`、`fairy spirit`、`magical` 等过强幻想词。

---

# 17. 风格结尾模板

## A. 写实武侠模板

```text
Soft natural rim backlighting, cyan-green shadows with restrained warm illumination, sparse scattered light particles. 35mm cinematic film, humid cyan-green haze, low-contrast soft focus, gently softened in-focus subjects and environmental edges, subtle highlight bloom and halation, slightly lifted blacks, soft shallow depth of field, fine film grain, photorealistic Eastern martial-arts atmosphere.
```

## B. 东方幻想模板

```text
Soft moonlight rim backlighting, humid cyan-green haze, soft cyan and cool moonlight tones with restrained warm accents, sparse dreamlike scattered light particles. 35mm cinematic film, low-contrast soft focus, gently softened in-focus subjects and environmental edges, subtle highlight bloom and halation, slightly lifted blacks, soft shallow depth of field, fine film grain, photorealistic, ethereal and mysterious Eastern fantasy atmosphere.
```

## C. 文艺古典模板

```text
Soft natural window light, clear cyan-green ambient tones with restrained warm brown interiors. 35mm cinematic film, low-contrast soft focus, subtle highlight bloom and halation, slightly lifted blacks, soft shallow depth of field, fine film grain, photorealistic Eastern period-drama atmosphere.
```

## D. 雨夜灯笼模板

```text
Soft moonlight rim backlighting, humid cyan-green rain haze, restrained crimson lantern glow reflected on wet surfaces, sparse scattered light particles. 35mm cinematic film, low-contrast soft focus, subtle highlight bloom and halation, slightly lifted blacks, soft shallow depth of field, fine film grain, photorealistic, quiet and mysterious Eastern atmosphere.
```

---

# 18. 最终生图 Prompt 格式与 MJ 语法检查

对用户展示的每条完整 Prompt 使用独立代码块；中文镜头名放在代码块外。代码块内只有两段，默认尾缀严格为 `--chaos 30 --raw --stylize 400`，不追加比例参数；参数之后不加解释或句号：

```text
[Scene, adult subject if applicable, costume, one readable pose, gaze, subject position, foreground framing, background depth, shot size and camera angle.]

[Scene-specific lighting and palette.] 35mm cinematic film, low-contrast soft focus, subtle highlight bloom and halation, slightly lifted blacks, soft shallow depth of field, fine film grain, photorealistic Eastern period-drama atmosphere --chaos 30 --raw --stylize 400
```

方括号是本节的模板占位符，最终必须替换为实际画面，不能照抄提交。

## 提交前语法检查

1. 所有参数集中在最末尾；正文和第一个参数之间有一个空格。
2. 使用两个半角连字符 `--`；不使用长破折号、全角空格、中文冒号或 `--ar=16:9`。比例用 `16:9`，参数之间用空格。
3. `--raw` 是独立开关，不写 `--raw true`，不同时写旧式与新式 Raw 参数。
4. 同一参数及其别名不重复：例如不能同时出现 `--ar` 和 `--aspect`，或 `--s` 和 `--stylize`。用户覆盖默认值时替换原值，不再追加一套。
5. 默认 `chaos=30`、`stylize=400`；数值与比例还需通过目标平台当前 schema 校验。语法合法不等于目标版本支持。
6. 不带未经验证的 `--v`、`--q auto`、随机 `--sref`、不可访问参考图 URL、未解析节点占位符或空参数。未指定个性化风格时不添加 `--p`。
7. 默认不追加负面词尾缀。确需 `--no` 时见第 24 节，且核对当前版本支持情况。
8. 调 LibTV 时从此展示版本生成“正文＋独立参数”的提交版本，按第 3 节分配字段；保留实际提交版本便于排错。

---

# 19. 示例：夜台执剑

```text
On a well-kept waterside opera stage at night, an adult East Asian female swordswoman in a deep crimson embroidered performance robe holds a composed stage pose. She holds a slender silver straight sword across her chest while her long sleeves and layered skirt flare gently toward the right. Her black hair is half pinned beneath a restrained golden opera crown, and her eyes remain focused toward the left side of the stage. She occupies the center-right; a blurred pipa head and a musician's shoulder frame the left foreground, while rows of red lanterns recede beneath the painted eaves behind her. Slight low-angle half-body close shot.

Soft moonlight rim backlighting, cool cyan-green night tones with restrained red lantern glow, sparse scattered light particles. 35mm cinematic film, humid cyan-green haze, low-contrast soft focus, gently softened in-focus subjects and environmental edges, subtle highlight bloom and halation, slightly lifted blacks, soft shallow depth of field, fine film grain, photorealistic Eastern martial-arts atmosphere --chaos 30 --raw --stylize 400
```

---

# 20. 示例：林间藏锋

```text
Deep inside a humid cyan-green bamboo forest at night, an adult East Asian female swordswoman stands slightly right of center in a deep crimson cross-collar robe. Her black hair is half pinned, with several damp loose strands resting beside her cheek and a slender golden earring catching faint light. Her raised right hand grips a black sword hilt close to the upper-left foreground, while the silver blade crosses diagonally over the frame without covering her eyes. Her focused gaze remains visible beyond the blade. Blurred bamboo leaves obscure the lower and right edges, creating a concealed observer viewpoint, while layered bamboo trunks disappear into mist behind her. Eye-level facial close-up.

Soft moonlight rim backlighting, cyan-green forest shadows with restrained warm golden illumination, sparse scattered light particles. 35mm cinematic film, humid cyan-green haze, low-contrast soft focus, gently softened in-focus subjects and environmental edges, subtle highlight bloom and halation, slightly lifted blacks, soft shallow depth of field, fine film grain, photorealistic Eastern martial-arts atmosphere --chaos 30 --raw --stylize 400
```

---

# 21. 示例：窗后凝望

```text
Viewed from outside a carved wooden window during a quiet overcast morning, an adult East Asian woman opens the two shutters and looks gently toward the left. She wears ivory-white Hanfu, with black hair arranged in a low traditional updo and restrained white floral hairpins. Both hands remain on the wooden shutters, and her upper body is fully visible in the center-right of the opening. Dark brown carved wood frames her face, blurred bamboo leaves soften the left foreground, and the shadowed interior behind her fades gradually into darkness. Eye-level frontal half-body shot.

Soft natural daylight illuminating her face, clear cyan-green tones with gentle warmth and sparse scattered light particles. 35mm cinematic film, low-contrast soft focus, subtle highlight bloom and halation, slightly lifted blacks, restrained warm brown accents, soft shallow depth of field, fine film grain, photorealistic Eastern period-drama atmosphere --chaos 30 --raw --stylize 400
```

---

# 22. 示例：雪庭回望

```text
Before a closed vermilion palace gate on a snowy midnight, an adult East Asian woman in dark crimson Hanfu stands slightly left of center with a sheathed ancient sword lowered in her right hand. Her black hair is half tied beneath a simple metal hairpin, and several loose strands move beside her face as she turns toward the far end of the palace wall with a quiet but alert expression. Snow covers the stone pavement and gate steps, cold mist gathers along the base of the wall, and red lanterns beneath the eaves recede into the distance. Large softly blurred snowflakes pass close to the lens in the foreground. Cinematic medium close-up, slightly low angle.

Soft moonlight rim backlighting, cool cyan and moonlight tones with restrained warm red lantern glow. 35mm cinematic film, soft snow haze, low-contrast soft focus, gently softened in-focus subjects and environmental edges, subtle highlight bloom and halation, slightly lifted blacks, soft shallow depth of field, fine film grain, photorealistic, quiet and mysterious Eastern martial-arts atmosphere --chaos 30 --raw --stylize 400
```

---

# 23. 示例：雨廊插花

```text
Inside a covered waterside corridor on a rainy night, two adult East Asian women stand closely together beside a vermilion pillar. The woman in moon-white Hanfu lowers her head slightly while the woman in dark crimson Hanfu carefully places a white magnolia hairpin into her damp black hair. Their side profiles remain close and naturally separated, both calm and focused. A blurred bamboo blind crosses the left foreground, while rain, lotus-pond reflections and dark wooden railings dissolve into soft cyan-green haze behind them. Intimate chest-up close-up, slightly side-facing view, balanced two-character composition.

Soft moonlight rim backlighting, humid cyan-green rain haze with restrained warm reflections, sparse scattered luminous particles. 35mm cinematic film, low-contrast soft focus, gently softened in-focus subjects and environmental edges, subtle highlight bloom and halation, slightly lifted blacks, soft cyan and cool moonlight tones, soft shallow depth of field, fine film grain, photorealistic, intimate and mysterious Eastern period-drama atmosphere --chaos 30 --raw --stylize 400
```

---

# 24. 内容审查、精简负面词与失败排查

## 按画面语义审查，不声称有完整违禁词表

MJ 审核会结合上下文、参考图和生成结果，规则也会更新。不能承诺“零违禁词”“绝不失败”，不能编造固定黑名单。以下是本技能的保守创作规则，不代表每个被提及的单词都被 MJ 禁止。

- 角色采用衣着完整、非性化的表演和构图。参考文本中的透视衣料不要机械继承；使用 `layered silk Hanfu with opaque lining`、`flowing silk sleeves` 表达材质与轻盈感。灯罩或油纸伞的透光性可按物体实际描述。
- 不生成裸露、性化未成年人、血腥伤害或惊悚肢体细节。不要在正向提示词或负面词里罗列这些词以“预防审核”。
- 悲剧、战乱和诀别优先用空城、散落发簪、破损信物、疏离构图及人物神态表达。需要替换原剧情画面时，明确标注为象征性改编，不能偷偷改变叙事事实。
- 例如《桃花扇》可将直接呈现受伤与血迹的镜头改成“地上的素面宫扇与散落发簪”，下一镜直接呈现“已完成的桃花扇”。改编后不展示受伤或血迹；不能将血迹仅改名为颜料而仍要求相同伤害画面。
- 剑、红色、夜景、成年女性、亲密构图等不自动视为违禁。剑可以是静态舞台道具或入鞘佩剑；不要附加刺入身体、伤口等内容。普通双人相处以自然距离与清楚姿态呈现。
- 不通过拆字、谐音、编码、隐语或反复试探绕过内容审核；确需改编时改变实际画面内容。

## 负面词最小化

默认以正向描述完成约束：`natural skin texture`、`readable eyes`、`relaxed anatomically coherent hands`、`plain unlettered silk fan`。道具不该有字时写素面；剧情确需题诗时预留版面，文字后期制作。

不把长串 `no ...` 放进正文，也不照搬其他模型的负面提示词。确需排除无关文字且目标版本支持时，可使用简单的 `--no text watermark logo`；有题诗、招牌等需求时不要使用 `--no text`。

`--no` 内的词可能被分别解释，不能写含敏感内容的否定句或用“不要某违规画面”要求模型审核放行。不要同时排除剧情必需的扇子、手、灯笼等物体。

## 生成前后检查与故障边界

提交前检查两段结构、尾缀、字段类型、模型模式、参考素材可访问性、画面语义和人物/道具连续性。只做文本检查不消耗积分。

失败时先记录任务编号与原始错误，区分：

- 明确参数错误：按 schema 改正字段或取值，再进行不消耗积分的检查。
- 明确内容审核错误：改成实际允许的画面，不做过滤绕过。
- 认证、额度、限流、素材或服务错误：按错误提示排查对应问题，不把换同义词当解决方法。
- 只有“生成失败／积分返还”等通用信息：原因未明，不能断言违禁词、chaos 值或正文长度就是原因。不要承诺此处规范能修复服务端故障。

同批连续出现两个相同通用错误时，默认暂停剩余付费提交，保留节点并报告；用户随后明确要求继续整批时按授权执行，每镜只提交一次。没有新的重试授权不自动重跑失败节点，也不自动更换模型。验证成功必须以实际返回图片为准，技能文本校验通过不等于生图实测通过。

## 官方依据（执行时遇兼容问题再核对最新版）

- [MJ 参数语法](https://docs.midjourney.com/hc/en-us/articles/32859204029709-Parameter-List)：尾部参数、空格、格式与参数入口。
- [MJ `--no` 参数](https://docs.midjourney.com/hc/en-us/articles/32173351982093-No)：负面词的独立解释与审核风险。
- [MJ 社区准则](https://docs.midjourney.com/hc/en-us/articles/32013696484109-Community-Guidelines)：内容语义审查依据，不是固定词语黑名单。

LibTV 的模型命名、封装参数和错误信息仍以 LibTV 当前 schema 与任务返回为准，不能仅凭模型名称假定与原生 MJ 完全等价。

---

# 25. 人物面部曝光规则

无论夜景、逆光、雨夜还是烛光：

- 人脸必须可清晰辨认
- 五官必须有自然层次
- 眼睛不能陷入纯黑
- 不允许人物成为剪影
- 高光不能烧白
- 保留真实皮肤纹理

推荐：

```text
softly illuminated face
restrained highlights
natural skin texture
readable eyes
```

但不要每条 Prompt 机械重复全部词汇。

---

# 26. 生图后的处理

生成 4 张候选图后：

1. 展示候选图
2. 让用户选择其中 1 张
3. 不得自动创建视频节点

如果用户明确说：

> 自动帮我选最适合做视频的一张

则按以下标准筛选：

- 面部稳定
- 手部正常
- 道具结构正常
- 服装结构正确
- 前中后景关系清晰
- 存在发丝、衣袖、雨雪、雾气等可自然动画元素
- 镜头有纵深
- 主体与背景分离良好
- 光线稳定
- 适合轻微推镜

---

# 27. 图生视频 Prompt 生成逻辑

图生视频 Prompt 必须基于“选定图片的实际内容”，不能简单套模板。

先分析：

- 人物
- 面部
- 服装
- 发丝
- 道具
- 前景
- 背景
- 天气
- 雾气
- 粒子
- 点光源
- 景深
- 可动画区域
- 镜头可移动空间

然后生成视频 Prompt。

---

# 28. 视频 Prompt 基础结构

```text
[准确描述当前选定图片中的人物、姿态、场景和构图。]

Keep the character's identity, face, hairstyle, costume, props, pose and spatial position consistent with the source image. Do not add new characters and do not redesign the environment.

The character shows only subtle natural breathing. Loose hair strands move gently in the environmental breeze, while sleeves, ribbons or robe hems respond with restrained fabric motion. Preserve the original body posture and facial expression.

[根据场景选择：rain / snow / mist / smoke / dust / water vapor] moves slowly and naturally through different depth layers. Foreground particles may pass softly out of focus near the lens while background atmosphere remains subtle.

Use a very slow cinematic dolly-in, pull-back or slight lateral drift according to the existing composition. Preserve a restrained natural handheld breathing feel without visible shake.

Maintain the original shallow depth of field. Allow only a very subtle focus-plane drift and gentle bokeh variation while keeping the face and eyes readable.

[如果存在灯笼 / 蜡烛 / 火光] allow restrained natural flicker and small halo variation while keeping facial exposure stable.

Keep the pacing calm, elegant and restrained. No sudden turn, no large body motion, no scene transition, no costume change, no facial change, no prop deformation.

Preserve the original 35mm film texture, low-contrast soft focus, highlight bloom, halation, lifted blacks, fine film grain, cyan-green ambient tones and restrained warm accents.
```

---

# 29. 视频运动规则

默认只做：

- subtle breathing
- gentle hair movement
- fabric flutter
- rain / snow / mist / smoke drift
- slow dolly-in
- slow pull-back
- subtle lateral drift
- slight natural handheld breathing
- minimal focus-plane shift
- restrained light flicker

默认禁止：

- 大幅转身
- 快速跑动
- 高强度打斗
- 360° 环绕
- FPV 高速飞行
- 镜头翻滚
- 大幅摇晃
- 强拉焦
- 大幅表情变化
- 背景重构
- 新增角色

除非用户明确要求动作型视频。

---

# 30. 多场景 / 60 秒视频工作流

如果用户输入的是一个 30–60 秒以上故事：

1. 先拆分为多个连续场景
2. 每个场景建立独立生图 Prompt
3. 每条 Prompt 仍保持“两段式结构”
4. 先只输出全部文字方案，不消耗积分
5. 告知用户预计生图节点数量
6. 获得确认后批量生图
7. 每个节点输出 4 张候选图
8. 用户逐场景选图，或明确授权 Skill 自动选最佳图
9. 根据每张最终图片生成对应视频 Prompt
10. 告知用户预计 Seedance 2.5 节点数量
11. 再次确认后生成视频

默认不在未确认状态下一口气执行整条生产链。

---

# 31. 用户输入处理

用户可以只输入自然语言。

例如：

```text
25岁东方女侠，白衣红披风，雨夜回到江南故乡寻找师父。她先走过青石长街，
在废弃庭院发现旧剑穗，然后进入竹林找到师父留下的竹笛，最后在山亭看到一封信。
做成60秒，中式电影感。
```

Skill 自动完成：

- 角色信息整理
- 场景拆解
- 每个镜头的内容调度
- 两段式生图 Prompt
- 生图参数展示
- 积分确认
- 候选图选择
- 视频 Prompt
- 第二次积分确认
- Seedance 2.5 视频节点

---

# 32. 质量检查清单

每条生图 Prompt 输出前检查：

## 内容
- 人物是谁？
- 穿什么？
- 发型是什么？
- 正在做什么？
- 道具在哪里？
- 人物看向哪里？

## 空间
- 人物位于画面哪一侧？
- 前景是什么？
- 背景是什么？
- 是否有纵深？

## 摄影
- 景别是什么？
- 机位是什么？
- 是否有明确构图？
- 是否使用了前景遮挡？

## 光线
- 主光源从哪里来？
- 冷暖关系是否合理？
- 人脸是否可读？

## 胶片
- 35mm cinematic film
- low-contrast soft focus
- highlight bloom / halation
- lifted blacks
- fine grain
- shallow depth of field

## MJ 格式与内容

- 两段正文与尾部参数是否符合第 18 节？
- 展示版与 LibTV 字段是否分开，Raw 是否有实际支持依据？
- 是否完成第 24 节语义审查，避免长负面词和敏感否定句？
- 是否没有把通用生成失败误诊为违禁词？

## 稳定性
- 是否避免关键词堆砌？
- 是否避免无意义幻想元素？
- 是否符合实际场景逻辑？
- 是否能作为真实电影单帧存在？

---

# 33. 核心风格速记

本 Skill 的视觉公式：

```text
精准人物与动作
+
明确前中后景
+
电影机位与景别
+
前景遮挡
+
冷青绿环境色
+
克制暖色点光
+
35mm film
+
low-contrast soft focus
+
highlight bloom / halation
+
lifted blacks
+
soft shallow depth of field
+
fine film grain
+
photorealistic Eastern atmosphere
```

最终目标：

**让每一张图看起来像从一部真实拍摄的中式武侠 / 东方文艺电影中截取出来的一帧，而不是一张普通古风 AI 插画。**
