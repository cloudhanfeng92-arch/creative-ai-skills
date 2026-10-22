# 验证范围说明

> **当前限制（2026-10-05）：下方记录均为历史验证，不验证当前内置浏览器能力，也不授权旧外部浏览器流程。当前网页预览按需，浏览器动作仅允许 Codex 内置官方工具；旧 `render-preview.mjs` / `render-video.mjs` 已禁用。内置无法导出时仅复用已有无浏览器入口。本次文档调整未进行实际视频渲染或 HTML 端到端验证，不能沿用历史通过结果宣称当前成片完成。**

本次调整（2026-10-02）同步简化工作流、默认无TTS和MP4＋离线HTML＋源码交付规则。已检查当前元数据、文档内引用、共享工具路径和各入口的默认规则一致性；辅助脚本通过 Python 3.9 语法解析，doctor 的帮助命令可正常执行。probe 实现未改动，仍默认只读元数据。本次未制作新主题视频，也未重新执行完整渲染、音频或HTML端到端测试。

以下保留原版本记录。日期、19/19结果、Linux与Python环境，以及“尚未在用户电脑安装或运行”等状态均指原验证当时，不代表当前修订版或当前用户环境。历史记录末尾的短渲染建议不是当前每次制作的强制步骤。

---

# 历史版本验证记录（2026-10-01）

验证日期：2026-10-01。范围：当前生成环境中的Skill文件结构与辅助脚本。

自动检查结果：19/19 通过。

| 检查 | 结果 |
| --- | --- |
| Metadata and decode: valid H.264/AAC file | 通过 |
| Fraction frame-rate input | 通过 |
| Width mismatch is rejected | 通过 |
| Required missing audio is rejected | 通过 |
| Silent video allowed without audio requirement | 通过 |
| Incorrect duration is rejected | 通过 |
| Incorrect codec is rejected | 通过 |
| Missing file reports unavailable | 通过 |
| Corrupt stream is rejected | 通过 |
| Invalid requested fps is rejected | 通过 |
| Doctor existing directory | 通过 |
| Doctor missing directory | 通过 |
| Skill YAML frontmatter and name | 通过 |
| UI metadata valid | 通过 |
| Python 3.9 grammar: doctor.py | 通过 |
| Python 3.9 grammar: probe_video.py | 通过 |
| All Skill reference paths exist | 通过 |
| Examples have no named uploaded-film reference | 通过 |
| No bundled font files | 通过 |

## 测试方式

使用本地FFmpeg生成一个1秒的320×180、30fps、H.264/AAC测试流，以及无音轨版本；验证probe脚本的成功、参数不匹配、缺少音轨、损坏文件和文件缺失分支。测试流不是用户主题成片，不随Skill包提供。doctor脚本在存在与不存在的项目目录上执行。

脚本实际执行环境为Linux与Python 3.13.5；另外使用Python 3.9语法解析模式检查了兼容语法，这不等同于已经在Python 3.9运行。

检查SKILL.md的YAML元数据、UI元数据、Skill内相对资源路径与代码语法。示例未使用先前上传视频的名称作为默认参考；包内不含字体文件、素材视频、账号或密钥。

## 未验证范围

尚未在用户电脑安装或运行。没有启动真实Codex会话进行端到端主题视频制作，没有验证用户的浏览器、中文字体、TTS/图像服务、账号与额度，也没有执行付费调用。脚本的技术检查不证明科普内容、画面美术、字幕或声音听感通过。

本Skill是工作流、参考与辅助检查脚本，不是预装的渲染引擎。首次实际制作仍需检测目标环境并完成短渲染测试。
