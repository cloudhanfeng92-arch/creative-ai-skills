# 汽车宣传片导演

从汽车照片与可选参考视频制作宣传短片，先锁定车辆多视角参考，再生成分镜图与视频并剪辑交付。

## 安装

把下面的请求发给支持 Skill 安装的 AI 助手，安装仓库完整内容：

```text
请安装 https://github.com/cloudhanfeng92-arch/automotive-promo-video 中的 Skill。
```

也可从 [总仓库](https://github.com/cloudhanfeng92-arch/creative-ai-skills/tree/main/skills/automotive-promo-video) 安装 `skills/automotive-promo-video`。保留 `SKILL.md` 及所有配套文件；同名本地版本应先备份再替换。详见[安装指南](https://github.com/cloudhanfeng92-arch/creative-ai-skills/blob/main/docs/INSTALL.md)。

## 使用示例

```text
使用 $automotive-promo-video，根据这辆汽车的照片，制作一支20秒的豪华汽车宣传片，先给我分镜和参考图方案。
```

主题、规格与素材可以替换；具体输入、默认值、流程与交付要求见 [SKILL.md](SKILL.md)。

## 工具与环境

- libtv-cli 与可用的 LibTV 账号
- Lib Image 2.5 Pro、Seedance 2.5 的可用权限
- ffmpeg-skill；剪映工程按需使用 jianying-editor

安装 Skill 不会自动配置外部工具、账号、模型权限或额度。依赖项及可选功能以执行说明和实际宿主能力为准；生成或发布按用户的明确要求和授权范围进行。

## 发布说明

此仓库发布工作流说明与辅助文件。本次发布做了结构、文件完整性和脚本语法检查，未重新执行外部平台生成、发布或行情请求；原文件中的历史验证记录保留其原日期和限制。

配套软件、模型、平台及参考素材的权利归各自权利人。仓库未新增统一开源许可证。

- [完整执行说明](SKILL.md)
- [通用使用说明](https://github.com/cloudhanfeng92-arch/creative-ai-skills/blob/main/docs/USAGE.md)
- [依赖与来源](https://github.com/cloudhanfeng92-arch/creative-ai-skills/blob/main/docs/DEPENDENCIES.md)
