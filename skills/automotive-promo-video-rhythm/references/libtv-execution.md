# LibTV 执行规则

2026-09-22 通过本机 `libtv 1.1.3` 的帮助和在线模型目录核验。仅查询过能力，未付费生成验证。本文件是执行参考，不能替代每次运行时的实际 schema。先读环境中已安装的 `libtv-cli` Skill，所有 LibTV 操作均通过其 CLI。

## 查询真实模型

```bash
libtv --version
libtv model search --type image 'Lib Image 2.5 Pro'
libtv model lib-image-2.5-s
libtv model search --type video 'Seedance 2.5'
libtv model star-video2.5
```

| 用途 | 展示名 | 本次 key | 生成节点参数 |
| --- | --- | --- | --- |
| 参考/分镜图 | Lib Image 2.5 Pro | lib-image-2.5-s | `-s 'model=Lib Image 2.5 Pro'` |
| 视频 | Seedance 2.5 | star-video2.5 | `-s 'model=Seedance 2.5'` |

`model <key>` 查询接受 key；`node -s model` 当前只接受展示名。模型详情的顶层 `modelName` 本次可能返回 key，因此应使用 search 的展示名。缺模型、无权限或显示名称变化时核实，不静默改为 Fast、Style Image、Seedance 2.0 等。

“GPTimage2.5”是用户对指定图片模型的称呼；目录不能证明其与某个 OpenAI 底层版本的对应关系。执行承诺是使用 Lib Image 2.5 Pro。

## 本次能力快照

图片：`modeType=image2image`；0–14 张参考；`resolution=1K/2K/4K`；`quality=low/medium/high/xhigh/max`；`count=1/2/4`；支持16:9、9:16等常用比例。汽车参考和分镜可从2K、medium、count=1起，在确认单里明确参数；密集多视角板可建议更高分辨率，不自动加价。

视频：

| 真实 modeType | 输入 | 使用说明 |
| --- | --- | --- |
| singleImage2video | 1张图 | 单图启动，适合以分镜图做首帧工作流 |
| frames2video | 1–2张图 | 文档明确称首尾帧；提交前核对顺序/端点 |
| image2video | 1–30张图 | 多图参考，明确每张图的职责 |
| mixed2video | 总计1–50个媒体 | 图最多30、视频10、音频10；只在创意需要时用 |

`duration=4–30`，步长1秒；`resolution=480p/720p/1080p`；`count=1/2/4`；`enableSound=on/off`；ratio支持16:9、4:3、1:1、3:4、9:16、21:9及adaptive。要统一比例就显式设置。参考视频时长计入模型收费总时长；本次未得到本账户准确单价，不能编造积分报价。

schema的输入张数不能证明严格首帧锁定。单图与一张首帧模式的实际保真差异未付费验证，必须检查真实起始画面。多图上限不是建议张数，选少量相关视角更易明确职责。

## 创建、连线、执行

在专属制作目录操作；优先每条命令显式 `-p`，避免误用其他画布。创建画布的参数先查 `libtv project create --help`；已有指定画布用其真实 UUID。以下为未执行的模板，所有尖括号都需替换；不得复制占位值发起请求。

```bash
libtv project use '<画布UUID>'
libtv upload 'CAR_ORIGINAL_01' -p '<画布UUID>' --resource '<原图绝对路径>'

libtv node create 'CAR_MASTER_v01' -p '<画布UUID>' -t image \
  -s 'model=Lib Image 2.5 Pro' -s modeType=image2image \
  -s resolution=2K -s quality=medium -s ratio=16:9 -s count=1 \
  --left 'CAR_ORIGINAL_01' --prompt '<已确认的完整参考图提示词>'

# 读取参数；本批出图得到用户明确确认后才运行。
libtv node 'CAR_MASTER_v01' -p '<画布UUID>'
libtv node 'CAR_MASTER_v01' -p '<画布UUID>' --run

# 单视角可由已验收参考裁出并重新上传；原图足够清晰也可直接用。
libtv upload 'CAR_FRONT_APPROVED' -p '<画布UUID>' --resource '<合格单视角绝对路径>'
libtv node create 'S01_FRAME_v01' -p '<画布UUID>' -t image \
  -s 'model=Lib Image 2.5 Pro' -s modeType=image2image \
  -s resolution=2K -s quality=medium -s ratio=16:9 -s count=1 \
  --left 'CAR_ORIGINAL_01' --left 'CAR_FRONT_APPROVED' \
  --prompt '<已确认的完整分镜图提示词>'
# 分镜图本批获准后执行 --run，验收通过才进入视频。

libtv node create 'S01_VIDEO_v01' -p '<画布UUID>' -t video \
  -s 'model=Seedance 2.5' -s modeType=singleImage2video \
  -s ratio=16:9 -s resolution=1080p -s duration=5 -s count=1 -s enableSound=off \
  --left 'S01_FRAME_v01' --prompt '<根据实际静帧推导的视频提示词>'

# 多图示例：这些独立视角节点都必须已上传、已验收。
libtv node create 'S02_VIDEO_v01' -p '<画布UUID>' -t video \
  -s 'model=Seedance 2.5' -s modeType=image2video \
  -s ratio=16:9 -s resolution=1080p -s duration=5 -s count=1 -s enableSound=off \
  --left 'S02_FRAME_v01' --left 'CAR_FRONT_APPROVED' --left 'CAR_SIDE_APPROVED' \
  --prompt '<逐图说明构图和身份职责的完整视频提示词>'

# 视频已在授权范围内后执行，单节点只提交一次。
libtv node 'S01_VIDEO_v01' -p '<画布UUID>' --run
libtv download -p '<画布UUID>' -n 'S01_VIDEO_v01' \
  -o '<输出目录绝对路径>' --vip --without-ai-watermark
```

这里16:9、1080p、5秒只是示例，按已批准方案和实际schema设置。提示词可用 `{{Node "节点名"}}` 或 `{{Node <nodeKey>}}` 精确引用连线节点；节点同名时用nodeKey。构造命令优先用Python `subprocess.run([...])` 参数列表，避免长提示词里的引号、换行、反引号或`$()`被shell解释。

## 状态与恢复

- `--run` 同步提交、内部轮询并写回终态。工具返回运行中的session后，读取同一进程输出，不重新调用`--run`。等待期间及时向用户报告阶段进展。
- 保存画布UUID、nodeKey、参数、提示词版本、任务ID（若返回）、终态结果、退出码和实际文件。不硬编码未经验证的终态字段名。
- 异常断开先查询原节点/现有输出，再决定恢复，不把暂时无响应当作可以重抽的依据。
- 下载始终同时使用`--vip --without-ai-watermark`。账号权限不足或无原链时报告阻塞，不能省略参数交付有水印版本或涂抹水印。
- 成功终态、可读资源、下载文件、汽车一致性、最终剪辑是不同检查。最后探测并实际看内容，不能从节点存在推断成片完成。
