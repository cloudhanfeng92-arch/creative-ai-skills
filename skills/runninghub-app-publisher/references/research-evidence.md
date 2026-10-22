# 研究证据与适用范围

日期：2026-10-12（Asia/Taipei）。用户目标是制作发布 Skill；下面不构成线上发布或费用授权。

## 直接 UI 与文件证据

| 来源 | 已确认 | 未确认 |
| --- | --- | --- |
| 用户的两份 RunningHub JSON | 原始节点 class、端口、连线、实际 1k/3:4、无质量字段 | 运行输出与计费 |
| 当前 GPT/Nano 工作流编辑器 | 原生显示名、prompt/resolution/aspectRatio/skip_error/seed/control_after_generate；两者 resolution 菜单 1k/2k/4k | 本次未修改参数、未运行 |
| 当前节点库搜索 `concatenate` | 可见 `Concatenate Text`、`Concatenate String`、`Text Concatenate`（WAS Suite）、`🔤 CR Text Concatenate`（Comfyroll Studio）等候选 | 未插入节点、未导出候选 class/socket、未验证实际拼接 |
| GPT 工作流顶部发布入口 | 弹窗“首次发布前请先运行一次工作流” | 成功运行后的本次发布 |
| 用户截图所示的发布页及实时 UI | AI应用页签、版本提示、必填资料、输入选择器/卡片、输入预览、社区范围、同步AI站、三种运行模式 | 最终提交/审核/同步成功 |
| 公开应用示例及实时 UI | 立即运行、我的生成、历史记录、发布作品；0/8选择器、200字简介、标签和发布范围 | 选中实际结果后的发布成功、跨站同步 |

本次原生显示名：GPT 为 `RH GPT Image 2.0 Edit Channel Low Price`，Nano 为 `RH Nano Banana 2.1 Image to Image Economy`。不要按营销名推断海艺参数。观察到人民币/次价格徽标，但价格是动态数据，不作为 Skill 的固定报价；每次运行重新读。

## 官方站点资料

- [工作流广场](https://www.runninghub.cn/page-workflow)：ComfyUI 工作流检索入口。
- [官方 AI 应用使用教程](https://www.runninghub.cn/blog/comfyui-workflows-cn/runninghub-ai-apps-guide)：选应用、上传/输入、生成的基本流程。
- [公开应用示例](https://www.runninghub.cn/ai-detail/2059602245771157506)：用于只读研究公开应用和作品发布入口，不能当作本 Skill 创建的应用。
- [AI 应用接入示例](https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287339) 与 [高阶接入示例](https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287340)：解释 nodeId、fieldName、IMAGE/STRING/LIST 等字段概念；不是网页表单操作规范，不授予 API/密钥访问权限。
- [工作流接入示例](https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287342)：指出运行 API 所需文件来自“导出工作流 API”，不能混同编辑器 UI JSON。
- [账户设置页](https://www.runninghub.cn/user-setting)：公开页面存在“绑定 AI 站账号”及 runninghub.ai；公开抓取结果不代表当前用户绑定状态。

未查到“同步AI站”实际完成后的统一提示规范；必须在执行任务时记录平台真实反馈。字符串拼接节点的社区案例不能替代当前节点库/导出确认，不能据社区标题硬编码 class_type。
