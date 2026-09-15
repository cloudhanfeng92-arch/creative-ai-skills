# Creative AI Skills · 中文创作工作流

把一个想法，变成可执行的图像、分镜、视频、音乐与文字创作流程。

这里收录 **42 个个人自建 AI Skill**，面向中文创作者。每个 Skill 都保留完整的 `SKILL.md`、配套参考资料与已有脚本，并提供中文简介和可直接复制的使用示例。

**从这里开始：** [安装指南](docs/INSTALL.md) · [使用说明](docs/USAGE.md) · [工具依赖与来源](docs/DEPENDENCIES.md) · [完整机器可读目录](catalog.json)

## 适合做什么

- **图像设计**：武侠、宋式美学、水墨、插画、书籍封面、城市海报与提示词反推。
- **分镜与角色**：角色四视图、九格故事板、八格预演分镜。
- **视频制作**：故事讲解、东方神话、山海神兽、复古梦境、FPV 与机甲变身。
- **广告与电商**：食品商品图、电影广告分镜、游戏宣传片、科技产品 TVC。
- **音乐与文字**：原创配乐、中文叙事、公众号图文与社媒素材适配。

## 快速体验

把下面这句话发给支持 Skill 安装的 Codex：

```text
请从 https://github.com/cloudhanfeng92-arch/creative-ai-skills
安装 skills/generate-hk-wuxia-film-images 这个 Skill。
```

安装后，在下一轮对话输入：

```text
使用 $generate-hk-wuxia-film-images，
以“雨夜古寺，两位旧友隔着石阶对望”为主题，生成一组16:9港式胶片武侠图片。
```

实际生图前，需要配置该 Skill 使用的模型服务和账号。也可以先安装纯文本用途的 [公众号图文创作](skills/wechat-article-copy-designer/README.md) 或 [中文叙事写作](skills/new-concept-first-prize-writing/README.md)。

## Skill 目录

### 图像设计

| Skill | 简介 |
| --- | --- |
| [AI 专业书籍封面](skills/ai-book-cover-designer/README.md) | 根据书名、简介与参考图，生成带完整标题排版的专业封面。 |
| [电影感青春动画](skills/cinematic-youth-anime-mj/README.md) | 编写蓝金黄昏、雨夜青春动画电影风格提示词，并在确认后生图。 |
| [城市照片编辑艺术海报](skills/city-photo-editorial-poster/README.md) | 把城市或风景照片转成摄影与抽象画面上下分区的文字海报。 |
| [港式胶片武侠生图](skills/generate-hk-wuxia-film-images/README.md) | 用中文长篇提示词制作90年代港式胶片武侠电影感组图。 |
| [宋式美学生图](skills/generate-song-aesthetic-images/README.md) | 把简单主题扩写成写实宋式生活美学组图，涵盖人物与庭院街巷。 |
| [水墨武侠生图](skills/ink-wuxia-image/README.md) | 把文字创意转成成熟中国水墨武侠数字插画。 |
| [胡金铨邵氏武侠](skills/king-hu-shaw-wuxia-mj/README.md) | 以经典武侠电影美学编写提示词并调用悠船Midjourney生成图像。 |
| [童趣蜡笔插画](skills/naive-crayon-illustration-mj/README.md) | 制作稚拙蜡笔与粗纸绘本质感的温暖插画。 |
| [新中式水墨山水](skills/new-chinese-ink-landscape/README.md) | 根据主题制作清雅的新中式水墨山水海报和视觉作品。 |
| [海报封面生成器](skills/poster-cover-generator/README.md) | 依据文字、参考图或两者组合，生成带完整排版的海报与封面。 |
| [逐图提示词反推](skills/prompt-reverse-engineer/README.md) | 逐张分析参考图的主体、画风、质感与构图，输出中文标题和提示词。 |
| [速写本涂鸦插画](skills/sketchbook-doodle-illustration-mj/README.md) | 使用温暖手绘质感、粗线条与现代卡通语言生成插画。 |
| [宋韵旧梦电影感](skills/song-dream-cinematic-images/README.md) | 制作宋韵人物与生活静帧，结合故事构图、自然材质与暖金或灯影光线。 |
| [复古梦境超现实生图](skills/vintage-dream-surreal-mj/README.md) | 编写复古梦境、日常物件与宁静不可能空间的提示词，确认后生图。 |

### 音乐配乐

| Skill | 简介 |
| --- | --- |
| [AI 原创配乐](skills/ai-music-composer/README.md) | 根据文字简报或视频设计原创配乐，匹配情绪、结构与实际时长。 |

### 视频制作

| Skill | 简介 |
| --- | --- |
| [中国古港市井绘卷](skills/ancient-coastal-market-video/README.md) | 制作中国古代沿海、河岸与市井生活的城市风俗绘卷短片。 |
| [东方神话幻想视频](skills/eastern-mythic-video/README.md) | 从概念或参考图制作具有连贯关键帧、运动与配乐的东方神话短片。 |
| [东方仙侠巨景视频](skills/eastern-xianxia-megastructure-video/README.md) | 突出宏大建筑、山河与渺小人物尺度对比，制作仙侠奇观短片。 |
| [FPV 导演运镜](skills/fpv-director-video/README.md) | 根据参考图设计有空间锚点和时间轴的一镜到底路线，确认后生成视频。 |
| [港式胶片武侠视频](skills/generate-hk-wuxia-film-video/README.md) | 从文字或参考图制作16:9港片武侠短片，保持人物、光影与胶片质感。 |
| [山海经神兽视频](skills/generate-shanhai-beast-video/README.md) | 制作荒古巨兽或云海天宫神兽短片，强调尺度、材质与运动重量。 |
| [宋式美学视频](skills/generate-song-aesthetic-video/README.md) | 制作宋韵生活短片，贯通关键帧、图生视频、配乐与剪辑混音。 |
| [成语故事讲解视频](skills/idiom-story-explainer-storyboard-to-video/README.md) | 把成语、寓言或历史小故事制作成分镜、视频、旁白与字幕方案。 |
| [图片转视频](skills/image-to-video-prompt-and-generate/README.md) | 分析图片内容与构图，编写匹配的运动提示词，确认后生成视频。 |
| [故事讲解视频](skills/story-explainer-video/README.md) | 从故事真值分析到角色场景、剧情表演、配音字幕与完整成片。 |
| [UE5 机甲变身](skills/ue5-mecha-transformation-video/README.md) | 从角色参考图制作固定15秒、具有写实3D CGI质感的机甲变身视频。 |
| [复古梦境超现实视频](skills/vintage-dream-surreal-video/README.md) | 将日常物件与复古空间转为连贯的超现实短片，配合缓慢运动与音乐。 |
| [视频拆解与复刻](skills/viral-video-breakdown-replication/README.md) | 分析参考视频的剧情、镜头、台词与节奏，输出可执行复刻流程。 |
| [Y2K DV 第一人称短片](skills/y2k-dv-pov-story-video/README.md) | 锁定复古校园DV画风与角色场景，制作第一人称剧情短片。 |

### 分镜与角色

| Skill | 简介 |
| --- | --- |
| [九格铅笔故事板](skills/character-plot-storyboard/README.md) | 根据角色参考图和简短剧情生成一张黑白九格连续故事板。 |
| [角色四视图设定](skills/character-turnaround-reference/README.md) | 从一张角色图生成正面、侧面、背面全身及面部特写参考。 |
| [八格预演分镜表](skills/storyboard-sheet-generator/README.md) | 根据故事和角色参考图制作16:9八格分镜表，含镜头与动作标注。 |

### 广告与电商

| Skill | 简介 |
| --- | --- |
| [电影广告分镜导演](skills/cinematic-ad-storyboard/README.md) | 把产品资料转化为商业广告分镜、场景图与视频提示词。 |
| [食品电商批量生图](skills/food-ecommerce-image-batch/README.md) | 依据同一食品SKU参考图生成包装白底图、主图及详情页模块。 |
| [游戏演示宣传片](skills/game-demo-trailer-to-video/README.md) | 从游戏设定、角色与美术风格规划分镜并制作游戏演示宣传片。 |
| [百万转场广告](skills/million-transition-video/README.md) | 通过三态关键图制作15秒高速穿梭、一镜到底的品牌广告。 |
| [科技产品 TVC](skills/tech-product-tvc-ad/README.md) | 从产品视觉锚点与分镜延伸到镜头、配乐、剪辑和广告成片。 |

### 工作流工具

| Skill | 简介 |
| --- | --- |
| [ComfyUI 工作流制作](skills/comfyui-workflow-builder/README.md) | 按生成任务设计、适配和验证可迁移的 ComfyUI 工作流 JSON。 |

### 写作与发布

| Skill | 简介 |
| --- | --- |
| [新概念风格叙事写作](skills/new-concept-first-prize-writing/README.md) | 按指定人物、事件、视角和参考文风创作克制、细节驱动的中文叙事。 |
| [海艺应用创作与参赛](skills/seaart-app-publisher/README.md) | 研究视觉玩法和赛事，将创意封装为可测试、可发布的海艺应用。 |
| [中文社媒发布运营](skills/social-media-publisher-operator/README.md) | 把成品视频、图集或文章适配为各中文平台的发布素材与运营方案。 |
| [公众号图文创作](skills/wechat-article-copy-designer/README.md) | 从主题生成公众号标题、摘要、正文和封面及插图提示词。 |

## 仓库结构

```text
creative-ai-skills/
├── README.md              中文总览与分类目录
├── catalog.json           Skill 名称、简介、示例和依赖索引
├── docs/                  安装、使用、依赖说明
└── skills/
    └── skill-name/
        ├── README.md      中文简介与调用示例
        ├── SKILL.md       AI 助手执行的完整规则
        ├── agents/        已有的界面元数据（部分 Skill 提供）
        ├── references/    详细方法、平台约定和参考资料（按需）
        └── scripts/       辅助脚本（按需）
```

## 使用前了解

Skill 是交给 AI 助手的工作说明，不是独立运行的生图或剪辑软件。安装本仓库不会自动获得 LibTV、即梦、悠船、SeaArt 等服务，也不会提供账号或生成额度。

各 Skill 内的模型选择、审批步骤、时长与画幅约定均按原文件保留。平台能力可能变化，执行时应核对实际可用工具。发布包通过结构、文档链接及脚本语法检查；未逐一执行需要付费服务的生成流程。

## 来源与反馈

本仓库发布个人自建工作流。已识别的官方 Skill、第三方项目和重复副本未打包为自建内容，详见[来源清单](docs/DEPENDENCIES.md)。模型、平台、参考作品与所用素材的权利属于各自权利人。

目前未指定仓库统一开源许可证。公开可见不代表附带任意再授权或商业分发许可；如需授权，请通过 [GitHub Issues](https://github.com/cloudhanfeng92-arch/creative-ai-skills/issues) 联系维护者。

遇到问题时，请在 Issue 中注明 Skill 名称、宿主、所用平台、操作步骤与已去除凭据的错误信息。
