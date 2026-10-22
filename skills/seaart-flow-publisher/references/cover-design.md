# 内置生图制作应用封面

## 默认规格

- 使用 Codex 内置 `image_gen` 图像生成工具；这是 Codex 侧的封面制作，不是在 SeaArt 工作流中加一个消耗积分的封面节点。生成时遵守工具当前参数定义，不虚构尺寸字段或输出路径参数。
- **3:4竖版**，最终文件的实际宽高满足 `width × 4 = height × 3`。在提示词中明确比例，生成后检查实际尺寸；其他竖版比例不能冒充3:4。工具支持实际尺寸选项时选精确3:4，否则要求内置生图重构为3:4并复核；仍不能得到该比例时明确未完成，不能用文字宣称解决。
- 大标题为**英文应用名**，拼写与本次确定的英文名逐字一致；中文应用名可以保留在发布表单中，不影响封面英文名。英文名未提供时根据功能起简短、自然、易记的名称。
- 主体和玩法画面占主要空间，英文大标题在缩略图中仍清晰。标题通常置于上方或视觉留白区，可用1至3行醒目排版，不遮挡人脸、关键道具与转换结果；四周留出裁切安全区。
- 画面生动、美观、有趣，围绕应用实际玩法设计。用同一主体的输入→输出、变身中间瞬间、前后对照或核心效果场景，让用户一眼理解。以应用效果为主，避免无关装饰、伪网站UI和大量说明文字。

## 人物与效果

有需要自选的人物演示时优先欧美面孔，默认使用虚构成年人物并匹配应用风格。用户提供或锁定人物身份、历史角色、题材地域时保持指定主体；该偏好不能改变实际用户上传图中的身份。

照片变钥匙扣：原始肖像和同一人物的可爱钥匙扣产生清楚关联。换装应用：同一人物的原服装与目标造型。子弹时间：定格粒子与清晰主体、空间纵深传达效果。物品或宠物应用无需额外加入人脸。

封面可用概念化画面表达已配置的玩法，但不能呈现应用不支持的能力。没有运行测试时，不把内置工具的概念封面标注为SeaArt真实测试结果。用户已有已验证输出或指定素材时，可用作内置生图的参考，保留其核心特征。

## 可改写的提示词规格

将下列设计项替换为本应用真实内容后再调用工具；占位项是封面写作结构，不是网站参数。

```text
Use case: ads-marketing
Asset type: SeaArt quick-app cover, portrait 3:4 composition
Primary request: Create a polished, lively and playful promotional cover for the app.
App function: Describe the actual supported input-to-output transformation.
Subject: If people are needed and no identity is locked, use a fictional adult with a Western European or North American appearance. Keep the same identity across the input and transformed result.
Gameplay visual: Show one clear transformation or interaction, with a large attractive result and a smaller recognizable input cue. Adapt the layout to the effect rather than repeating a fixed collage.
Style: Match the app's visual genre, with expressive posing, clear focal hierarchy, appealing color, rich but tidy detail and professional lighting.
Text (verbatim): "EXACT ENGLISH APP NAME"
Typography: Large bold high-contrast English headline, legible at thumbnail size, clean letterforms, correct spelling, balanced spacing and generous edge margins.
Constraints: Exactly 3:4 portrait image; keep face, core effect and entire title visible; show only supported gameplay; no extra slogans, unrelated brands, watermarks or garbled text.
```

例如钥匙扣应用可用英文标题 `CHARM ME`，主体是一位欧美面孔人物的小幅输入肖像，视觉中心是一只手展示同一造型的Q版软胶钥匙扣；标题位于上方，不遮挡金属环和钥匙扣主体。这是示例设计，不能将该名称固定应用到所有项目。

## 调用、保存与验收

准备精确英文文案和完整视觉规格后调用内置生图。全新图片不附不存在的参考路径；编辑或参考已有图时先查看图片，再按工具文档传入实际参考。内置工具不可用时保存封面方案并说明限制，不静默切换外部API或站内积分生成。

生成后将可上传的实际图片文件保存或复制到本次工作目录的 `cover/`，不能仅保留临时地址或只有预览而无可上传文件。使用图片查看工具检查成片；用当前文件工具读取实际像素尺寸，只做尺寸检查，不以代码绘图替代内置生图。

核验比例、英文标题准确性、标题可读性、画面美感、人物身份和玩法是否一目了然。若标题错误、被截断或比例不符，通过内置图像编辑修正并重新查看。记录 `cover` 的生成来源、提示词、英文标题、文件路径、宽高与检查结果，再上传发布表单并复核平台裁切后的缩略图。
