# 用户提供的 RunningHub 图生图节点

证据：2026-10-12 用户上传的两份 RunningHub 导出，原样副本和 SHA-256 位于 `assets/workflows/provenance.json`。这里记录实际文件内容；界面菜单、费用、运行结果需另行在当前网站核验。

## 模板事实与陷阱

| 项目 | GPT Image 2 模板 | Nano Banana 2.1 模板 |
| --- | --- | --- |
| 用户源文件 | `runninghub的GPT2图生图2k.json` | `runninghub的Nanobanana2.1图生图2k.json` |
| 生成节点 class | `RH_RhartImageG2ImageToImage` | `RH_RhartImageNNb21ImageToImage` |
| 生成节点 ID | `20` | `18` |
| 图片接口 | `image1`–`image10` | `image1`–`image14` |
| 输入 / 输出 | `LoadImage` ID `15` / `SaveImage` ID `19` | 同左 |
| 原文件分辨率实际值 | **`1k`** | **`1k`** |
| 原文件比例 | `3:4` | `3:4` |
| 原 prompt | 空字符串 | 空字符串 |
| 源图片值 | `example.png`，占位文件名 | 同左 |
| 默认错误处理 / seed | `false` / `0` + `randomize` | 同左 |
| quality / Medium 字段 | **没有** | **没有** |
| 凭据接口 | `api_config` 未连接 | 同左 |

**不能因为文件名写了 2k 就认为节点已设成 2K。** 本 Skill 默认把真实 widget 值改为小写 `2k`，导入后仍检查下拉框选中项。两份文件都没有 SeaArt 的“中质量”参数，禁止补造 `quality=Medium`。`api_config` 是可选接口，模板未携带任何 API key；不要为了发布而填写账号密钥。

原件包含相同 workflow UUID、旧布局及插件技术元数据，没有发现账号、会话令牌或真实私人图片。生成副本重新分配 workflow UUID、重置 revision、清理未列入技术白名单的 metadata/preview，并把图片值换成明确待上传占位符；保留原件用于审计，绝不直接修改用户 Downloads 文件。

## Widget 顺序：两模型不能通用下标

索引从 0 开始。

| 参数 | GPT Index | Nano Index |
| --- | ---: | ---: |
| prompt | 0 | 0 |
| resolution | 5 | 1 |
| aspectRatio | 1 | 2 |
| skip_error | 2 | 3 |
| seed | 3 | 4 |
| 前端 seed 控制值 `randomize` | 4 | 5 |

GPT export 的 `inputs[].widget.name` 明确记录了 prompt、aspectRatio、skip_error、seed、resolution。Nano export 只列出图片与 `api_config` socket；2026-10-12 已在两者真实节点界面确认 prompt、resolution、aspectRatio、skip_error、seed、control_after_generate，分辨率菜单均有 `1k / 2k / 4k`。正式发布绑定仍以当前选择器为准。`randomize` 是前端 control_after_generate 的值，不是一个已验证的 API 输入字段。不要把 UI JSON 机械改名为 API JSON。

## 生成工作流副本

脚本仅本地处理 JSON，无登录、网络、浏览器或计费操作。默认 GPT Image 2、2k、3:4、单图。使用用户提供的 class 与端口，保留 v0.4 格式，不创建猜测的文本节点。

```bash
python3 scripts/prepare_workflow.py \
  --model gpt-image-2 \
  --title '应用名称' \
  --prompt-file /absolute/run/fixed-prompt.txt \
  --output /absolute/run/workflow.json
```

输出 `workflow.json` 和 `workflow.parameters.json`。后者列出每个图片输入、分辨率、比例的节点 ID/widget 索引和建议中文标签，列出隐藏固定 prompt 及 SaveImage 输出。JSON 可供 UI 导入，但其中 `UPLOAD_IMAGE_01.png` 等不是现成素材；必须在编辑器对应 LoadImage 节点实际上传已授权素材后再运行。

双图示例：

```bash
python3 scripts/prepare_workflow.py \
  --model nano-banana-2.1 \
  --title '人物与宠物合拍' \
  --images 2 \
  --image-label '上传人物照片' \
  --image-label '上传宠物照片' \
  --prompt-file /absolute/run/fixed-prompt.txt \
  --output /absolute/run/workflow.json
```

如已通过当前平台 UI 上传并取得真实文件名，可为每张图片提供一个 `--image-name`。仅接受文件名，拒绝本地路径和 URL；这不会执行上传。额外图片节点只克隆原有 `LoadImage`，连接已存在的 `image2` 等 socket，并同步顶层 links、输入 link、输出 links、节点顺序和 ID 计数。

其他分辨率/比例先检查当前节点下拉框，再传 `--resolution` / `--aspect-ratio` 和 `--allow-unverified-parameters`。该参数只是允许本地写值，不能代表选项已受平台支持。输出已存在时默认拒绝覆盖，需要确实更新派生文件才加 `--overwrite`。

## 固定与可变提示词

- 固定效果：只暴露图片、画面分辨率、画面比例。固定 prompt 在生成节点内部，不给用户空白提示词框。
- 可变概念：固定 prompt 只写身份保持、构图、材质等稳定规则；用户可改的职业、情绪、地点等内容放进单独变量节点，经实际已验证的拼接/替换节点进入生成 prompt。**两份原模板不包含这样的文本节点。** 在网站添加并导出节点确认 class、socket、顺序后才能扩展；该脚本不会凭空造 SeaArt 的“文本附加”节点。
- 多图 prompt 清楚写出 Image 1、Image 2 各自角色，与发布输入标签保持一致。不能把“可选第二图”写进应用说明而实际只绑定一个输入。

## 验证边界

脚本会验证 ID 唯一、端口范围、双向链接引用、数据类型及末尾 ID 计数。2026-10-12 已验证两模型的单图、双图和最大图片数分支（GPT 10 / Nano 14），并用 `comfyui-workflow-builder/scripts/validate_workflow.py` 再次通过静态检查。超出图片端口数被拒绝；用户原件哈希未改变。

上述证据只证明图结构，**不是 RunningHub 导入、执行、发布或“同步 AI 站”成功**。发布与试运行按主 Skill 当前界面流程执行，最终记录真实应用 URL、试运行任务结果、社区帖子 URL。
