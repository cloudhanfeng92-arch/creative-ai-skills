# 工具依赖与来源

## 外部能力

不同 Skill 使用的工具不同；每个 Skill 的 README 列出从执行说明中识别的相关工具，实际要求以 `SKILL.md` 为准。

| 工具或服务 | 常见用途 | 准备事项 |
| --- | --- | --- |
| LibTV / libtv CLI | 图片、视频与画布制作 | 配置官方 CLI、登录，并检查账号模型权限 |
| 即梦 / Dreamina | 图片、视频与画布生成 | 安装对应官方能力，完成登录和额度检查 |
| 悠船 / Midjourney | 风格图像与关键帧 | 配置相应生成服务和可用模型 |
| SeaArt / 海艺 | 图像视频、应用创建 | 配置官方工具与账号；发布前明确目标 |
| FFmpeg / ffprobe | 拼接、混音、媒体验证 | 安装本地二进制并确保命令可访问 |
| Python | 部分辅助脚本 | 根据脚本导入准备依赖 |
| 浏览器与搜索 | 参考研究、平台操作 | 由宿主提供对应能力 |

模型名和平台参数可能更新。仓库保留工作流原有约定，不承诺某个服务在任何账号或地区都可用。

## 未纳入自建发布包的项目

以下项目在本地存在，但有明确的官方或第三方来源，因此本次不作为自建 Skill 上传：

| 项目 | 来源或处理方式 |
| --- | --- |
| `handdraw-style-prompter` / `handraw-style` | [yang0/handraw-style](https://github.com/yang0/handraw-style)，两个安装位置只记作同一上游项目 |
| `photo-abstract-editorial` | [ZzzLc0405/photo-abstract-editorial](https://github.com/ZzzLc0405/photo-abstract-editorial)，保留上游授权边界 |
| `ffmpeg-skill` | [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) |
| `jianying-editor-skill` | [luoluoluo22/jianying-editor-skill](https://github.com/luoluoluo22/jianying-editor-skill) |
| `chatgpt-apps`、`screenshot`、`.system` | Codex / OpenAI 提供的工具与系统 Skill |
| `libtv-cli` | LibTV 官方 CLI 操作 Skill，从官方渠道安装 |
| `dreamina-cli`、`dreamina-canvas-cli` | 即梦 CLI / 画布工具配套 Skill，从其分发渠道安装 |
| `seaartai` | SeaArt 官方 Skill，从官方渠道安装 |
| `hyperframes` 系列、`media-use` | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)，作为第三方依赖另行安装 |
| `ms-hub`、`ms-studio-deploy` | [modelscope/modelscope-skills](https://github.com/modelscope/modelscope-skills)，不作为个人自建内容重新发布 |
| 插件缓存中的 Skill | 属于已安装插件，未随个人工作流重新分发 |

这些依赖未打包不影响浏览和学习本仓库，但执行依赖它们的工作流前需要另行安装。上游项目的内容、许可和运行要求以其自身说明为准。

## 发布包处理

- 收录42个自建 Skill 的执行说明及配套文本、脚本和元数据。
- 新增分类总览、42份中文简介与示例，以及安装、使用和依赖说明。
- 将两处个人电脑绝对路径改为通用 Skill 安装路径。
- 不包含账号凭据、登录状态、个人缓存、Git 内部目录或已识别第三方包。
- 缩短一处超长的 Skill 发现描述；业务执行正文保持不变。
- 未改写各 Skill 的业务流程，也未执行付费生成任务。

## 2026-10-22 补充发布

新增 19 个此前未发布的自建 Skill，总目录现有 61 个条目。每项提供独立仓库、中文说明、安装入口和使用示例，配套文件按本地当前安装版打包。

- 发布副本将一处个人 LibTV 安装路径改为通用路径；SeaArt 两处私人素材目录及历史授权改为当前用户提供或明确授权的素材目录。
- `stock-analysis` 的凭据示例全部为空，MCP 地址为禁用的占位模板；读取环境变量的代码不包含密钥。
- 不包含第三方安装包、账号数据、个人运行记录、缓存或媒体产物；本地已安装 Skill 保持原样。
- 新增流程涉及的 RunningHub、Liblib、Google Chrome、Node.js、Git/GitHub CLI、Blender（按具体路线）以及 AKShare/yfinance 等依赖需要使用者另行准备。
- 本次只做发布包静态检查和 GitHub 内容核验，未重新执行生成、平台发布或金融数据调用。
