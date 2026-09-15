# LibTV Style Image V8.2 生图契约

本技能只通过 LibTV 官方 CLI 运行 Style Image V8.2 生图。视频阶段不得使用 LibTV；必须转入 Dreamina Canvas `seedance_2.5`。

执行前完整读取 `~/.codex/skills/libtv-cli/SKILL.md`，并以当前 CLI 的 `--help`、账号状态、模型搜索和实时 schema 为准。不得自造 HTTP 请求、网页模拟、模型键、价格或参数。

## 1. 只读预检

```bash
libtv auth status
libtv account
libtv model search --type image "Style Image V8.2"
```

实际命令如有变化，以当前 `libtv-cli` 文档为准。

确认：账号已登录、目标画布可访问、Style Image V8.2 可用、16:9 和候选数量受支持、积分报价可查询。无法查询精确积分时如实说明，不猜数字。

## 2. 节点规则

- 每镜一个独立提示词节点，默认生成四个同镜候选。
- 提示词必须包含 `ARVIN_LIGHT_MATCH_BLOCK` 的具体化版本。
- 候选图先经过 `LIGHT_MATCH_SCORECARD`，再检查人物、构图、解剖、时代和可动性。
- 只把通过硬门的单张结果下载/上传为独立首帧资源。
- 四宫格母节点不能直接作为视频参考；不得把第二候选当尾帧。
- 保存画布 id、节点 id、提示词、模型、参数、任务 id、资源 id 和选片评分。

## 3. 生成确认与失败处理

平台要求确认时，展示模型、画幅、节点数、每节点候选数、完整提示词和平台报价；一次确认只覆盖列出的调用。重做、增加节点、改模型或提高规格需按服务要求重新确认。

候选无一通过光影硬门时，重写该镜提示词并重新生成；不得选择“最不差”的暗脸、死白衣料、死黑背景、水印图或崩坏图，也不得计划在 Seedance 或后期阶段补救。

## 4. 安全与可追溯

不得把 token、Cookie、授权头或账号秘密写入技能、脚本、日志或交付文件。所有生成记录应能从镜头编号追溯到提示词节点、候选、选中资源和后续 Dreamina 视频节点。
