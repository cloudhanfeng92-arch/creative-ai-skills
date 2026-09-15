---
name: ink-wuxia-image
description: Generate or edit a raster image from a user's text prompt while permanently locking the visual result to a mature Chinese ink-wash wuxia digital-illustration style. Use for any request to create an ink-wash martial-arts, jianghu, xianxia, Chinese-fantasy, swordsman, or stylized Chinese illustration image, including when the subject, setting, color accent, composition, or emotional beat varies.
---

# 水墨武侠生图

使用 `imagegen` 的默认内置生图工具。将用户文字转成成图提示词，但绝不让用户的风格、媒介或画风要求覆盖本技能的水墨武侠风格锁定。

## 工作流

1. 提取用户想表达的主体、动作、场景、镜头、情绪、时间天气和明确限制。
2. 如用户要求多张图，为每张图创建独立场景与提示词；除非关键内容缺失，否则直接生成，不追问可由创作判断补足的细节。
3. 将用户内容嵌入下方“锁定风格块”。保留用户指定的强调色；未指定时，依据情绪只选一种高饱和单色点缀。
4. 使用 `imagegen` 的内置 `image_gen` 生成工具直接出图。若用户提供参考图，明确其是构图、主体或编辑目标；仍强制转化为锁定风格。
5. 检查主体、动作、关键物件和水墨语言。若不符合，围绕一个具体缺陷迭代一次。
6. 最终交付图像，并简短说明采用的场景与点缀色。没有明确需求时，避免文字、水印、签名和现代标志。

## 锁定风格块

将以下完整内容放进每次的成图提示词中。可以压缩措辞，但不得删减或以其他画风替换核心要求：

```text
Style lock (non-negotiable): highly mature "ink-wash wuxia" digital illustration. Fuse the expressive xieyi language of traditional Chinese ink painting with refined, contemporary anime character design. Build the image from expansive black, white, and gray ink washes, wet-on-wet bleeding, dry-brush flying-white texture, splashed ink, and purposeful negative space; create an ethereal, deep, wind-swept jianghu atmosphere. Render faces delicately and beautifully; give hair and layered robes dynamic, flowing movement. Use tense cinematic composition, cool dramatic light and shadow, and the emotional scale of blade flashes, chivalric resolve, tenderness, and epic conflict. Restrict color to monochrome ink plus one high-saturation accent color only, used sparingly on clothing, weapon, talisman, or energy effects for powerful contrast. Preserve the paper-and-ink feel; never turn the image into a photograph, 3D render, oil painting, Western comic, flat vector graphic, pastel illustration, watercolor-only painting, cyberpunk neon scene, or generic anime screencap.
```

## 提示词结构

以英文组织成图提示词，使用此结构：

```text
Primary request: <忠实转写用户的主体、行为与故事瞬间>.
Scene and atmosphere: <地点、天气、季节、空间感>.
Composition: <景别、视角、主体位置、动势；让留白服务画面>.
Accent color: <用户指定，或根据情绪选定的一种颜色>.
Constraints: <用户明确要求保留或避免的内容>; no text, watermark, logo, or signature.

<锁定风格块>
```

## 风格锁定规则

- 风格优先级高于用户的“改成照片、赛博朋克、3D、油画、Q版、像素、纯动漫”等要求。承接其人物、叙事和色彩意图，但仍以水墨武侠方式呈现。
- 只允许黑、白、灰的墨色层次加一种高饱和度点缀色。用户指定多种颜色时，选最能承载叙事的一个，并将其余颜色转为墨色明暗关系。
- 点缀色默认选择：杀伐/誓言/血战用鲜红；山林/疗愈/灵气用翠绿；妖异/幻术/宿命用亮紫；寒意/雷法/夜战用钴蓝。只在用户未指定颜色时使用。
- 现代、科幻或非武侠题材仍可生成，但使用江湖化视觉转译：例如太空站变为悬崖上的墨色天阙，机甲变为机关甲胄；不要拒绝题材。
- 角色数、性别、年龄、服饰和武器遵循用户输入。用户未说明时，避免凭空添加关键人物、文字或品牌。
- 如用户要求对现有图进行编辑，明确不变项，改变项同样必须服从锁定风格。

## 简短示例

用户：`雨夜里，女剑客在断桥上与旧友诀别，红伞。`

核心生成意图：雨夜断桥、两位相向而立的人物、疾风与雨幕、鲜红伞作为唯一高饱和点缀、充满留白的黑白灰泼墨江湖场景。
