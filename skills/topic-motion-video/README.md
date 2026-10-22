# 主题科普代码动画

围绕单个主题进行事实核查、脚本与原创图解动画制作，用动态文字和图形解释知识，交付视频、可播放网页、封面及源码。

## 安装

把下面的请求发给支持 Skill 安装的 AI 助手，安装对应 Skill 的完整目录：

```text
请从 https://github.com/cloudhanfeng92-arch/creative-ai-skills
安装 skills/topic-motion-video 目录中的 Skill。
```

可在 [总仓库](https://github.com/cloudhanfeng92-arch/creative-ai-skills/tree/main/skills/topic-motion-video) 安装 `skills/topic-motion-video`。保留 `SKILL.md` 及所有配套文件；同名本地版本应先备份再替换。详见[安装指南](https://github.com/cloudhanfeng92-arch/creative-ai-skills/blob/main/docs/INSTALL.md)。

## 使用示例

```text
使用 $topic-motion-video，制作一支约90秒的“潮汐如何形成”科普动画，用动态图解解释，不要口播，配原创音乐。
```

主题、规格与素材可以替换；具体输入、默认值、流程与交付要求见 [SKILL.md](SKILL.md)。

## 工具与环境

- JavaScript/Node.js 运行环境与事实核查能力
- 实际可用的内置浏览器导出能力，或项目已有兼容原生绘制入口与 FFmpeg
- 可复用 code-motion-video 工具；按画面需要使用 Canvas、WebGL、SVG 或 Three.js

安装 Skill 不会自动配置外部工具、账号、模型权限或额度。依赖项及可选功能以执行说明和实际宿主能力为准；生成或发布按用户的明确要求和授权范围进行。

## 发布说明

此仓库发布工作流说明与辅助文件。本次发布做了结构、文件完整性和脚本语法检查，未重新执行外部平台生成、发布或行情请求；原文件中的历史验证记录保留其原日期和限制。

配套软件、模型、平台及参考素材的权利归各自权利人。仓库未新增统一开源许可证。

- [完整执行说明](SKILL.md)
- [通用使用说明](https://github.com/cloudhanfeng92-arch/creative-ai-skills/blob/main/docs/USAGE.md)
- [依赖与来源](https://github.com/cloudhanfeng92-arch/creative-ai-skills/blob/main/docs/DEPENDENCIES.md)

---

## 原始详细说明

# 主题科普动画 · 简化使用说明

用一个主题制作一条原创知识动画，默认连续完成内容、画面、轻量检查与导出。最终提供 **MP4、可双击离线播放的单文件 HTML、代码绘制的 PNG 封面、可编辑源码**。

## 默认做法

- 中文、普通成年观众、约 90 秒、16:9、1080p、30 fps；用户指定的参数和风格优先。
- 根据主题直接选择合适的视觉方向并简述理由，不默认要求选择三个方案或逐阶段确认。
- 自动根据具体画面选择 JavaScript + Canvas 2D / WebGL、SVG / DOM 或 Three.js，可混合文字层与主视觉；兼顾表现力、已有环境和导出耗时，无需用户先选技术栈。
- 先核对关键事实与原意，写清观众要理解的变化，再让同一对象、尺度或关系在画面里完成解释；来源与不确定之处简洁记录。
- 先设计起始张力、关键变化和阅读落点的构图，再编排主动作、次级响应、镜头与声音；让母题随观点发展，转场承接上一段留下的对象或问题。具体判断见 [创意与分镜](references/creative-direction.md)。
- “旁白／解说文案”默认作为屏幕字幕或动态文字，不生成 TTS、不朗读。字体、颜色、位置和动效随主题；歌词效果按需要制作，不添加无关标签。
- 默认用 JavaScript 合成原创 BGM 和适配音效，按主题、叙事情绪、时代文化与画面选声音；音乐随知识推进发展，音效对应具体事件，推理阅读保留留白，不按题材套固定曲风。离线输出同一最终混音用于 MP4 与 HTML；用户要求静音或指定歌曲时遵循其选择，只有明确要求配音或朗读时才额外生成口播。声音细则见 [制作与交付](references/production.md)，未实际试听时如实注明。
- 将代表构图、核心解释动作及关键交界的短时连续变化纳入一次轻量检查，可复用正式导出结果后台观察，再确认规格与HTML控件；静帧和元数据不能单独证明动画设计达标。具体问题局部修复，不新增逐镜审批或默认样片。

## 直接使用

```text
$topic-motion-video

制作一条“雨后为什么会出现彩虹？”的原创知识动画，约90秒，16:9、1080p、30fps，面向普通成年人。
按主题选择视觉风格，用光线、雨滴和观察位置的变化解释机制，核对关键事实。
解说文案做成可读的动态文字，默认不配音。连续完成，交付MP4、可双击离线播放的HTML、代码绘制的PNG封面和可编辑源码。
```

更多完整输入见 [示例](examples/prompts.md)。用户主动要求先看风格、脚本或样片时，按指定节点停下；其余常规工作连续推进。

## 工程与续作

复用已有内容、时间轴和 `code-motion-video` 的非浏览器工具。网页预览按需；需要浏览器时，优先且只用 Codex 内置浏览器的官方工具，先核对实际能力，不假定任意 JavaScript、seek、批量采帧、下载或离线验收。禁止外部 Google Chrome、Chrome for Testing、独立 Chromium、个人 profile/CDP、改浏览器路径或桌面录屏；旧 `render-preview.mjs` / `render-video.mjs` 已禁用，不调用或绕过。

内置能力不能完成导出时，才复用项目已有且确认不启动浏览器的原生 Canvas/Skia/SVG 等后台帧输出入口，再用 FFmpeg 编码；不通过 Remotion/Puppeteer 等间接启动浏览器，也不把 FFmpeg 当作 HTML 渲染器。没有兼容入口就保留源码和已有产物，说明 MP4 未完成。基础模板仍可用 `export-html.mjs` 打包 HTML；不自动在系统浏览器打开，未完成的运行或离线验证如实注明。默认单任务、保守编码线程；内置也使用本机资源，不保证更省 CPU/GPU。

续作时直接说明需要修改的主题内容或片段。读取当前项目的必要文件，从现有成果继续，只修改受影响部分。交付中的事实、时间线和文字应保持一致；未完成项如实说明，不默认上传发布。

## 按需检查工具

- `scripts/doctor.py`：环境未知或发生依赖问题时使用，读取版本和依赖声明，不安装软件。
- `scripts/probe_video.py`：默认只读视频元数据；`--decode` 才执行完整解码，`--require-audio` 仅在本片确实需要音轨时使用。已用渲染工具完成等效检查时无需重复运行。
- [验证记录](VALIDATION.md) 保留历史版本的检查范围，不代表每次成片或当前环境都已经通过端到端验证。
