# 安装指南

## 方法一：让 Codex 按链接安装

从[目录](../README.md)选一个 Skill，把仓库地址与目录路径一起发给 Codex：

```text
请安装 https://github.com/cloudhanfeng92-arch/creative-ai-skills
中的 skills/wechat-article-copy-designer。
```

安装完整目录，包含 `SKILL.md` 和配套资源。安装后在下一轮对话调用；若宿主尚未刷新列表，再重新打开会话。

## 方法二：下载后手动安装

1. 下载本仓库 ZIP 并解压，或执行：

   ```bash
   git clone https://github.com/cloudhanfeng92-arch/creative-ai-skills.git
   ```

2. 把需要的 `skills/<skill-name>` 整个目录复制到 Codex 的 Skill 目录。默认是 `~/.codex/skills/`；若设置了 `CODEX_HOME`，则使用其下的 `skills/`。
3. 确保最终结构是 `skills/<skill-name>/SKILL.md`，不要多嵌套一层仓库目录。
4. 如有同名 Skill，先备份已有目录，再决定是否替换。

macOS / Linux 单个安装示例（目标存在时会停止）：

```bash
cd creative-ai-skills
skill_dir="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$skill_dir"
if [ -e "$skill_dir/wechat-article-copy-designer" ]; then
  echo "目标已存在，请先备份并核对。"
else
  cp -R skills/wechat-article-copy-designer "$skill_dir/"
fi
```

要安装全部，可逐个复制 `skills/` 下的42个目录；建议先选择实际需要的工作流。

## 其他 AI 助手

可将完整 Skill 目录放入该宿主规定的 Skill 位置。目录发现方式和工具名称因宿主而异，不能假设与 Codex 完全兼容。涉及 Codex 专用工具时，需要适配调用方式。

## 配置工具依赖

参阅[依赖说明](DEPENDENCIES.md)。先完成相关平台登录和必要 CLI 配置，再运行生图、生视频或发布工作流。账号、密钥、Cookie 和付费额度都由使用者自行配置，不随仓库分发。

## 更新

更新仓库后，比较目标 Skill 的变化，备份本地修改再替换完整目录。不要用未经核对的批量覆盖命令覆盖自己的定制内容。
