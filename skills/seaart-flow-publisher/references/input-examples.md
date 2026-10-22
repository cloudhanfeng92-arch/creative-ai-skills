# 中间提示词参数的5组输入示例

## 适用条件

仅当应用玩法确实需要用户填写中间提示词、场景描述、改图要求或创意文本时，为该公开参数提供**5组完整、可直接使用的示例**。固定某一个效果的应用不开放用户提示词入口、不增加文本附加节点来收集主题，也不配置主题示例；固定效果的具体要求留在内置提示词中。图片上传、分辨率、比例、时长等字段无需套用文本示例。必要的标题等内容字段按实际功能设计，不为了配置主题示例而改造成创意提示词。

示例属于输入参数高级设置中的可选示例，不是5个工作流、不等于下拉框，也不是运行5次的要求。添加和查看示例本身不应触发生成。

配置入口在发布向导第二步“选择输入输出参数”：先选择实际输入节点字段，再打开该公开输入卡片的齿轮。画布“文本附加”节点里的默认文本与这里的5组示例是两项配置，都要检查。

用户截图中：输入卡片 `[3]String - value` 旁的齿轮打开“高级设置”，已有多行示例文本框，按钮写着“添加(最多添加5个)”。节点号、字段和入口以当前界面为准；截图只能证实该界面支持此配置，不能证明所有SeaArt编辑器都相同。

## 设计要求

- 每组是一条可填入该参数的完整文本，描述明确的玩法、效果或动作，不只给标题、“示例一”或未替换的占位符。
- 5组应有可见区别，覆盖该应用的典型用途；模型、效果和约束保持一致，不加入它不支持的功能。
- 附加示例只填写允许用户修改的具体内容，例如主题、服装、场景、配色、灯光，不重复图像节点的固定任务与限制。每组都要与同一固定提示词合并检查；固定提示词不得写死这些可变维度的另一套具体值或默认方案。已开放的分辨率、比例通过真实控件选择，不在示例内另行固定。
- 内容适合替换用户上传的主体，不把封面人物的欧美身份写进通用输入示例并强迫改变用户身份。要求适用时保持参考主体、姿态、服装、布局等关键特征。
- 默认使用自然英文，固定提示词为中文也不改变这一默认。用户明确指定其他语言时按要求填写；应用简介、控件名称仍可用用户语言。
- 公开输入框的初始默认值、附加文本、占位示例也使用英文。默认值通常来自上游文本节点的 `userInput`、`value` 或实际公开字段，不只检查高级设置；必须在发布前修正其真实来源，再核对公开页。默认值是一条可用场景，不能塞入全部5条。
- 多个互相依赖的提示词字段可按同一序号设计5组相容组合，在记录中保存对应关系；不能宣称界面能自动联动，除非已验证。
- 每个字段总数为5条；已有相关示例计入总数，替换不相关或重复内容。无需生成5份示例输出，运行测试仍服从授权预算。

## 填写与验证

1. 将文本字段绑定为公开输入，并读回来源节点和字段。
2. 点击该输入卡片自己的齿轮，进入“高级设置”。不要误点应用整体设置、节点生成设置或删除图标。
3. 将准备好的5条逐项粘贴到示例框，通过“添加”增加到5条；若已有示例先检查再编辑。按钮计数和最大容量以现场为准。
4. 逐条读回全文，确认无丢字、截断、重复和跨字段粘贴；“参数描述”有独立用途，不能把全部5条粘进描述字段当作完成。
5. 使用实际保存方式，关闭并重新打开高级设置检查5条持久化。发布后从同一应用的编辑入口再次读回；在公开页用“随机”或当前提供的示例入口验证至少一条进入正确输入框，检查英文默认值也已生效。静态用户预览可能无法交互，不能因此点击“创作”另跑一次。没有公开交互能力则记录只完成配置读回，不能声称交互已验证。
6. 在 `inputs` 中为该字段记录 `examples`（长度5）、`examples_configured`、`examples_readback_verified` 和 `examples_preview_verified`。不支持设置或无法保存时记录阻塞，保留5条文本并报告未落到界面。

## 示例：子弹时间场景输入

以下5条匹配截图所示的定格环境主题，可作为同类应用的示例；其他应用必须改写。它们描述场景，实际镜头运动和时长仍由下游视频节点与固定提示词控制。

1. `Freeze colorful paper confetti around the reference subject in soft celebratory light, retaining its natural posture or placement and recognizable features.`
2. `Suspend flower petals at several depths around the reference subject in a softly lit garden, preserving its identity, posture and a suitable environment.`
3. `Freeze raindrops in midair around the reference subject under dramatic cinematic lighting, keeping its appearance and natural placement unchanged.`
4. `Suspend golden autumn leaves at different distances around the reference subject in warm late-afternoon light, retaining its identity and original pose or placement.`
5. `Hold sparkling water droplets in a curved splash around the reference subject, with clear foreground and background layers, preserving its recognizable features and keeping it unobstructed.`

这5条不是封面文案，不应全部塞进同一默认输入值，也不能自动依次执行。将它们分别作为5个可选输入示例保存。
