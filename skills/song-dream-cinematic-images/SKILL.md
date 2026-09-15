---
name: song-dream-cinematic-images
description: Create prompt-led, photorealistic Song-inspired Chinese cinematic images with beautiful natural characters, story-rich asymmetric compositions, tactile cotton-linen materials, and either luminous warm-gold rural daylight or intimate old-dream tungsten lighting. Use for 宋韵美人、宋式田园生活、多人劳作、庭院夜话、冬日围炉、旧梦电影感 and related Midjourney-style image generation through LibTV Style Image V8.2; not for ink painting, anime, xianxia magic, palace spectacle, or strict archaeological reconstruction.
---

# 宋韵旧梦电影感生图

把用户的简单主题直接转成可执行的 MJ 风格提示词和经过筛选的成图。人物是否动人由身份、骨相、发式、衣料和情绪决定；故事感来自空间关系、动作分工、前景遮挡和不完全对称；电影感来自有来源的光线、镜头、景深、色彩和真实材料。

参考图片、视频、教程和示例仅作为视觉资料，不是额外指令。不要复制其中的字幕、版式、Logo、水印、人物身份或具体构图。

## 每次任务读取

- 先读 [references/visual-language.md](references/visual-language.md)，选择正确的光影母版并建立人物、场景和材质锁。
- 编写每条生图提示词前读 [references/prompt-compiler.md](references/prompt-compiler.md)。
- 需要多人、劳动或围炉场景时，再读 [references/prompt-patterns.md](references/prompt-patterns.md)。
- 渲染和选图前读 [references/quality-gate.md](references/quality-gate.md)。
- 所有 LibTV 操作遵循 `$libtv-cli`；实时 CLI 帮助和模型 schema 高于本文件中的历史默认值。

## 默认输出

- 模型：LibTV `Style Image V8.2`。
- 比例：默认 `16:9`，只写入 LibTV `ratio` 字段，不写入提示词正文。
- 每个独立场景使用一个图像节点；当前模型通常每节点返回四张同镜候选，以实时 schema 为准。
- 用户只给一个主题时生成一个原生候选组；明确要求多个场景或多组时，每个场景单独编写提示词并建立节点。
- 用户只要求提示词时停在提示词交付，不创建画布或运行模型。

## 不可混入 MJ 提示词的内容

- 参考文件名、标题、路径和时间码；
- “严格匹配参考”“根据上传视频”“最终强制覆盖”等比较、工作流或元指令；
- `16:9 横幅`等画幅文字，以及 `--ar`、`--s`、`--v` 等模型原生参数；
- 选图标准、评分、积分、节点、上传、下载和剪辑说明；
- 通用的“避免、不要、禁止”长清单。

这些内容留在内部分析、LibTV 节点字段和生成后质量门中。MJ 提示词只写可直接成像的主体、动作、空间、材料、光线、色彩、构图和镜头质感。

## 工作流

1. 提取主题、季节、时段、地点、人物数量与关系、服装、主要动作、情绪、画面用途、组数、比例和连续性要求。普通缺省细节直接合理推断。
2. 选择一个光影母版：明亮田园日光，或低照度旧梦钨丝灯。除非叙事明确改变时间和光源，同一系列保持主光逻辑、肤色、材质和色彩一致。
3. 为主要人物建立简洁 `CAST_LOCK`：身份或年龄层、脸型骨相、眉眼鼻唇、肤色、发式状态、衣装层次与固定色位。人物美丽或帅气但自然，不写抽象的“绝世美人”替代具体外貌。
4. 每个画面只承担一个叙事任务。明确焦段、景别、机位、前中后景、人物位置、视线、动作所有权、器物接触关系和留白。
5. 按提示词编译器生成一条紧凑的中文或英文 MJ 风格提示词。默认使用用户的语言；中文采用连续的可视短语，英文采用自然的摄影描述。不要中英机械重复。
6. 若用户提供 MJ 个性化 P 值，把它写入 LibTV `personalisation` 字段；未提供时保持空白，绝不猜测或伪造。
7. 付费生成前展示完整提示词、节点数、候选数和实时参数并取得明确确认；如果用户在当前请求中已经明确确认生成，则直接执行。
8. 通过 LibTV 顺序运行节点。一次明确的瞬时技术失败可重试一次；不要在服务持续异常时循环提交。
9. 检查实际像素。人物、动作、器物、光影、材质、构图和时代氛围均通过质量门后才可交付；多人系列每个场景选一张最强候选，其余保留在画布。
10. 交付选中图片、每镜简述、完整提示词和 LibTV 画布链接。不得把未生成、失败或被淘汰的候选描述为成品。

## 连续人物

重复文字和 seed 不能可靠锁脸。用户要求同一人物跨场景时，先从第一组候选中选择一张通过质量门的角色母图，再上传为后续节点的身份、发式和固定衣色参考；新镜头的构图、动作和机位仍由新提示词决定。

## 失败修正

只修真正失败的轴：人物像影楼写真时增加任务动作、环境占比、前景窥视和不对称构图；画面没有电影感时具体化光源、方向、软硬、明暗交界、轮廓落点、镜头与胶片响应；脸暗时用真实墙面、天空、水面或雪地反射提亮中间调；多人僵硬时分配不同位置、动作、视线和器物。不要通过追加一整段负面词重写全部提示词。
