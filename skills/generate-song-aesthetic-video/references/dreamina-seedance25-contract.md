# Dreamina Canvas Seedance 2.5 执行契约

视频阶段一律使用 `dreamina-canvas` CLI。不得自造网络请求，不得改用 LibTV 视频节点。所有命令和字段以安装版本的 `SKILL.md`、`--help` 与实时模型 schema 为准。

## 1. 运行时预检

执行前检查：

```bash
dreamina-canvas auth status
dreamina-canvas account
dreamina-canvas model find seedance_2.5 --type video
```

若命令名或 schema 与当前文档不同，先读取 `~/.agents/skills/dreamina-canvas-cli/SKILL.md` 并按实时文档调整。不得猜参数、价格、时长或模型键。

## 2. 单首帧模式

Dreamina Canvas CLI 当前可能把首帧/首尾帧统一暴露为 `first_last_frame`。本技能必须只传一个 image reference；一张图等价于单首帧模式。禁止第二张图、尾帧图、多图参考和参考视频。

概念参数：

```text
model: seedance_2.5
mode: first_last_frame
references: exactly one selected first-frame image
ratio: 16:9
resolution: 720p or runtime-approved higher landscape resolution
duration: native 3–5 seconds supported by current schema
count: 1
```

不得在提示词里把参考图称为“首尾帧”。结束状态只写文字。

## 3. 节点生成流程

1. 在即梦画布创建或选择项目。
2. 把 LibTV 选中的单张首帧下载并上传为独立图像资源。
3. 为每镜创建一个视频节点，只引用对应的一张首帧。
4. 先请求平台报价或生成确认信息；获得服务要求的确认后提交。
5. 保存 project id、node id、operation id 和镜头映射，等待任务完成。
6. 下载每个视频资源并通过 `ffprobe` 验证。

命令形态示例仅用于定位字段，执行前必须以实时帮助为准：

```bash
dreamina-canvas node create video \
  --project-id PROJECT_ID \
  --title S01 \
  --mode first_last_frame \
  --prompt VIDEO_PROMPT \
  --model seedance_2.5 \
  --ratio 16:9 \
  --resolution 720p \
  --duration 5 \
  --count 1 \
  --ref node:FIRST_FRAME_NODE
```

## 4. 禁止行为

- 不通过 LibTV 运行 Seedance 或任何替代视频模型。
- 不把四宫格候选节点直接接入视频；必须使用选中的单张独立资源。
- 不把同一镜头的第二张图当尾帧上传。
- 不静默改用 Seedance 2.0、其他版本、文生视频或多图模式。
- 不自动重试、增加数量、升级分辨率或改变时长；新增消耗须重新走服务确认。
- 不在本地文件中记录访问令牌、Cookie 或账号秘密。

## 5. 下载后验证

逐镜记录：首帧资源、模型、模式、真实时长、尺寸、帧率、帧数、音轨、生成任务 id 和文件校验信息。起、中、末都要查看；若光影、人物、动作、口型或声音失败，只重做该镜，不裁剪掩盖。
