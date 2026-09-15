---
name: social-media-publisher-operator
description: >-
  Prepare, adapt, publish, track, and improve finished videos, images, articles,
  and mixed-media content for Chinese social platforms including WeChat Official
  Accounts, Bilibili, Douyin, Xiaohongshu, and WeChat Channels. Use for platform
  copy, covers, metadata, authorized publishing, and post-publication operations.
  Follow user-selected accounts, destinations, and draft-only or approval limits.
---

# Social Media Publisher & Operator

## Purpose

将用户已经完成的：

- 视频
- 图片
- 多图
- 海报
- 图文
- Markdown
- HTML
- 长文章
- 短文案
- AI 生成内容
- 视频 + 封面 + 文案组合

自动整理并适配到：

1. 微信公众号
2. 哔哩哔哩 Bilibili
3. 抖音
4. 小红书
5. 微信视频号

最终实现：

**一次输入内容 → 自动识别 → 自动适配 → 自动生成发布文案 → 自动上传 → 自动发布/进入官方发布流程 → 保存发布结果 → 后续运营分析。**

---

# 一、核心原则

## 1. 一个内容源，多平台适配

禁止简单地把完全相同的：

- 标题
- 正文
- 标签
- 封面
- 简介

复制到所有平台。

必须根据平台分别生成最适合该平台的发布版本。

例如：

原始内容：

> AI 还原北宋汴京的一天

自动转化：

### 小红书

标题偏：

> 如果真的穿越到北宋汴京，会看到什么？

正文采用：

- 强开头
- 视觉描述
- 少量分段
- 自然关键词
- 相关话题

### 抖音

标题/描述偏：

> AI还原北宋汴京最繁华的一天，千年前的东京城原来是这样

侧重：

- 前3秒兴趣点
- 搜索关键词
- 话题标签
- 简洁文案

### B站

标题偏：

> 用AI还原《东京梦华录》里的北宋汴京｜千年前世界第一大都市的一天

同时生成：

- 视频简介
- 分区建议
- 标签
- 封面标题建议
- 系列/合集建议

### 微信公众号

自动转成长图文：

- 主标题
- 副标题
- 导语
- 视频介绍
- 正文
- 图片
- 小标题
- 总结
- 封面
- 摘要

### 微信视频号

采用：

- 短标题
- 简短正文
- 关键词
- 话题
- 视频封面

---

# 二、支持的输入

用户可以只提供一个最终文件。

例如：

```text
final.mp4
```

也可以提供：

```text
final.mp4
cover.jpg
article.md
```

或者一个完整项目目录：

```text
/project/
    final.mp4
    cover.png
    article.md
    images/
        01.jpg
        02.jpg
        03.jpg
```

Skill 必须首先扫描输入内容，然后判断：

```text
content_type
```

允许：

```text
video
article
single_image
image_gallery
video_article
mixed_media
```

---

# 三、调用方式

用户可以直接说：

```text
把最终视频一键发布到所有平台
```

或者：

```text
调用 social-media-publisher-operator，
把这个项目发布到抖音、小红书、B站、微信公众号和视频号。
```

也可以：

```text
这个视频做好了，帮我全平台发布。
```

如果当前上下文已经存在明确的最终视频、图片或文章：

**禁止再次要求用户重新提供文件。**

自动寻找当前任务中的最终产物。

---

# 四、默认平台

默认：

```json
{
  "platforms": [
    "wechat_official_account",
    "bilibili",
    "douyin",
    "xiaohongshu",
    "wechat_channels"
  ]
}
```

用户也可以指定：

```text
只发小红书和抖音
```

或者：

```text
除了公众号，其他平台全部发布
```

---

# 五、总体工作流程

必须按照以下顺序执行。

## STEP 1 — 扫描最终内容

读取：

- 视频
- 图片
- 标题
- 文件名
- 项目说明
- 剧本
- 字幕
- 已有文案
- 封面

如果是视频，分析：

- 内容主题
- 视频时长
- 横竖比例
- 分辨率
- 是否有字幕
- 是否有旁白
- 主体人物
- 场景
- 内容类型
- 前3秒
- 高潮
- 结尾
- 是否适合横屏或竖屏平台

不要重新制作视频，除非平台规格确实需要。

---

# 六、识别内容主题

自动生成：

```json
{
  "content_summary": "",
  "content_category": "",
  "main_subject": "",
  "audience": [],
  "keywords": [],
  "search_keywords": [],
  "visual_keywords": [],
  "content_highlights": [],
  "hook": "",
  "tone": "",
  "copyright_notes": "",
  "ai_generated_content": true
}
```

---

# 七、发布前内容安全检查

检查：

- 文件是否损坏
- 视频是否可以正常播放
- 图片是否正常
- 音频是否存在
- 是否明显包含第三方水印
- 是否包含其他平台 Logo
- 是否存在明显版权风险素材
- 是否可能触发平台限制
- 是否包含不适合公开发布的信息
- 是否符合目标平台文件格式

发现问题时：

不要直接终止整个任务。

采用：

```text
可修复 → 自动修复
不能自动修复 → 标记该平台并继续其他平台
```

例如：

```text
抖音：可发布
B站：可发布
小红书：需要人工确认
视频号：进入辅助发布模式
公众号：可创建草稿
```

---

# 八、自动判断内容类型

## 视频型内容

适配：

- B站
- 抖音
- 小红书
- 视频号

同时判断是否值得生成公众号文章。

如果适合：

自动生成：

```text
视频 → 公众号文章
```

文章围绕视频主题扩展，而不是简单复制视频字幕。

---

# 九、微信公众号 Adapter

标识：

```text
wechat_official_account
```

主要内容：

```text
article
image_article
video_article
```

工作流程：

```text
读取原始内容
↓
生成公众号标题
↓
生成摘要
↓
生成正文
↓
生成公众号排版
↓
上传正文图片
↓
上传封面
↓
生成草稿
↓
发布或保留草稿
↓
查询发布结果
```

文章结构默认：

```text
标题

导语

01
正文

02
正文

03
正文

结语
```

正文应适合微信公众号阅读。

禁止：

- 把小红书文案直接复制进公众号
- 大量无意义 emoji
- 大量标签
- 碎片化短句堆积

输出：

```json
{
  "title": "",
  "digest": "",
  "author": "",
  "cover": "",
  "html": "",
  "status": "",
  "article_id": "",
  "url": ""
}
```

---

# 十、Bilibili Adapter

标识：

```text
bilibili
```

主要用于：

```text
video
article
```

视频发布前自动判断：

- 横屏/竖屏
- 内容分区
- 是否原创
- 标签
- 标题
- 简介
- 封面
- 合集

生成：

```json
{
  "title": "",
  "description": "",
  "category": "",
  "tags": [],
  "cover": "",
  "copyright": "original",
  "collection": "",
  "topic": ""
}
```

标题优先：

```text
内容价值 + 核心主题 + 差异化关键词
```

禁止纯标题党。

如果存在对应合集：

优先加入合集。

---

# 十一、抖音 Adapter

标识：

```text
douyin
```

优先使用官方 OpenAPI。

视频流程：

```text
OAuth
↓
验证 video.create
↓
上传视频
↓
获得 video_id
↓
创建视频
↓
返回 item_id
↓
查询审核/发布状态
```

图片流程：

```text
上传图片
↓
获得 image_id
↓
创建图文内容
↓
返回 item_id
```

自动生成：

```json
{
  "title": "",
  "description": "",
  "hashtags": [],
  "cover": "",
  "poi": null,
  "visibility": "public"
}
```

文案原则：

短。

第一句话直接提供兴趣点。

优先识别搜索关键词。

禁止无意义堆积话题。

---

# 十二、小红书 Adapter

标识：

```text
xiaohongshu
```

支持：

```text
image_note
video_note
```

自动生成：

```json
{
  "title": "",
  "body": "",
  "topics": [],
  "cover": "",
  "images": [],
  "video": ""
}
```

正文推荐结构：

```text
一句吸引人的开头

内容描述

值得注意的细节

简短结尾

#话题
```

避免机械营销腔。

如果官方能力只能打开小红书发布器：

执行：

```text
准备内容
↓
传递图片/视频
↓
传递标题
↓
传递正文
↓
传递话题
↓
打开官方发布器
↓
等待用户完成平台要求的确认
```

禁止伪造“已自动发布成功”。

---

# 十三、微信视频号 Adapter

标识：

```text
wechat_channels
```

主要处理：

```text
video
image
short_text
```

生成：

```json
{
  "description": "",
  "hashtags": [],
  "cover": "",
  "video": "",
  "location": null
}
```

优先检测当前账号是否存在官方可用发布接口。

如果存在：

```text
official_api
```

如果不存在：

```text
assisted_publish
```

自动准备完整发布内容并进入官方创作者发布流程。

不要假设所有视频号账号均开放同一种 API。

---

# 十四、统一 Publisher Adapter 架构

每个平台必须实现统一接口：

```text
authenticate()
validate()
prepare()
upload()
publish()
get_status()
get_metrics()
```

统一平台 Adapter：

```text
platforms/
    wechat_official_account
    bilibili
    douyin
    xiaohongshu
    wechat_channels
```

---

# 十五、发布能力等级

每个平台动态检测：

```text
LEVEL 1
official_api
```

表示：

可以通过官方 API 发布。

---

```text
LEVEL 2
assisted_publish
```

表示：

官方允许发布，但必须：

- 调起发布器
- 打开创作中心
- 或要求用户执行最终确认

Skill 自动填写其余内容。

---

```text
LEVEL 3
package_only
```

表示：

没有可靠或授权的自动发布方式。

此时创建：

```text
平台发布包
```

包括：

- 视频
- 封面
- 标题
- 简介
- 标签
- 分类
- 发布说明

禁止为了实现所谓“全自动”而偷偷使用：

- 未授权 Cookie
- 盗取登录态
- 绕过验证码
- 绕过平台安全控制
- 非授权私有接口

---

# 十六、发布模式

支持三种模式。

## safe

```json
{
  "publish_mode": "safe"
}
```

执行：

```text
生成全部平台发布内容
↓
展示发布计划
↓
用户确认
↓
发布
```

---

## confirm_once

推荐默认值：

```json
{
  "publish_mode": "confirm_once"
}
```

用户说：

> 全平台发布

即视为此次任务已确认。

Skill 不再逐个平台重复询问。

---

## draft

```json
{
  "publish_mode": "draft"
}
```

只：

- 生成公众号草稿
- 生成平台发布包
- 上传但不正式公开

---

# 十七、禁止重复确认

如果用户明确说：

```text
发布
一键发布
直接发布
全平台发布
现在发布
```

视为已经完成本次发布授权。

不要再询问：

```text
确定发布吗？
```

但如果平台自身强制要求用户确认：

遵守平台要求。

---

# 十八、封面处理

如果用户已经提供封面：

优先使用。

如果没有：

从：

- 视频关键帧
- 项目已有图片

中寻找最佳封面。

必要时生成封面建议。

不同平台允许使用不同封面。

例如：

```text
B站：
16:9信息密度较高

抖音：
竖屏强主体

小红书：
视觉优先

公众号：
文章型主视觉

视频号：
简洁明确
```

禁止强行把同一封面用于所有平台。

---

# 十九、文案生成

创建：

```text
platform_copy/
```

例如：

```text
douyin.txt
xiaohongshu.txt
bilibili.txt
wechat_channels.txt
wechat_article.html
```

同时生成：

```text
master_content.json
```

---

# 二十、统一 Publish Manifest

每次发布创建：

```json
{
  "content_id": "",
  "source": {
    "type": "",
    "video": "",
    "images": [],
    "article": "",
    "cover": ""
  },

  "platforms": {
    "douyin": {
      "enabled": true,
      "mode": "official_api"
    },

    "xiaohongshu": {
      "enabled": true,
      "mode": "assisted_publish"
    },

    "bilibili": {
      "enabled": true,
      "mode": "auto"
    },

    "wechat_official_account": {
      "enabled": true,
      "mode": "auto"
    },

    "wechat_channels": {
      "enabled": true,
      "mode": "auto"
    }
  },

  "publish_mode": "confirm_once"
}
```

---

# 二十一、账号系统

允许一个平台存在多个账号。

例如：

```text
douyin:
    ai_art
    chinese_aesthetic

xiaohongshu:
    ai_art
    guanlan

bilibili:
    main

wechat:
    guanlan
```

用户可以：

```text
发布到“观澜”账号。
```

然后自动寻找：

```text
account_profile = guanlan
```

---

# 二十二、账号定位

给每个账号保存：

```json
{
  "account_name": "",
  "platform": "",
  "positioning": "",
  "target_audience": [],
  "content_categories": [],
  "preferred_style": "",
  "preferred_keywords": [],
  "avoid_topics": [],
  "posting_preferences": {}
}
```

生成标题和文案时必须考虑账号定位。

---

# 二十三、Credential 管理

任何：

- access_token
- refresh_token
- app_secret
- client_secret
- cookies
- API key

禁止直接写进：

```text
SKILL.md
```

使用：

```text
.env
```

或系统安全凭证库。

例如：

```text
DOUYIN_CLIENT_KEY
DOUYIN_CLIENT_SECRET

WECHAT_APP_ID
WECHAT_APP_SECRET
```

Token 必须支持：

```text
refresh
expiry check
reauthorization
```

---

# 二十四、授权检测

每次发布之前：

```text
check_auth()
```

检测：

```text
authorized
expired
missing_permission
reauthorization_required
```

如果只是 Token 过期且 Refresh Token 有效：

自动刷新。

不要要求用户重新授权。

只有真正需要重新登录/授权时才提示。

---

# 二十五、发布记录

创建：

```text
publish_history.json
```

每个内容保存：

```json
{
  "content_id": "",
  "publish_time": "",
  "platform": "",
  "account": "",
  "platform_post_id": "",
  "url": "",
  "status": "",
  "title": "",
  "tags": [],
  "cover": "",
  "source_file": ""
}
```

---

# 二十六、防重复发布

发布之前计算：

```text
content_hash
```

同时检查：

- 文件哈希
- 标题
- 已有平台 item_id
- publish_history

如果检测到相同内容已经发布：

禁止无提示重复发布。

返回：

```text
该内容已经发布到抖音。
```

如果用户明确要求：

```text
重新发布
```

才允许再次执行。

---

# 二十七、失败恢复

如果五个平台发布：

```text
公众号 ✅
B站 ✅
抖音 ❌
小红书 ✅
视频号 ❌
```

禁止重新从头执行五个平台。

记录 checkpoint：

```text
wechat: success
bilibili: success
douyin: failed
xiaohongshu: success
wechat_channels: failed
```

重试：

```text
douyin
wechat_channels
```

即可。

---

# 二十八、发布状态

统一：

```text
prepared
uploading
uploaded
submitted
reviewing
published
failed
manual_confirmation_required
```

---

# 二十九、发布完成后的结果

最终必须给出清晰结果：

```text
发布完成

微信公众号
✅ 已提交
文章：xxx

B站
✅ 投稿成功
BV：xxx

抖音
✅ 发布成功
作品ID：xxx

小红书
⚠️ 已进入官方发布器
等待最终确认

视频号
✅ 发布成功
作品ID：xxx
```

不能只说：

```text
操作完成
```

---

# 三十、运营模块

Skill 不只负责发布。

还负责：

```text
Operate
```

支持：

- 获取作品数据
- 对比平台表现
- 分析标题
- 分析封面
- 分析内容主题
- 找出高表现作品
- 找出低表现作品
- 推荐下一期内容
- 建立账号内容方向
- 形成周报/月报

---

# 三十一、数据指标

当平台官方接口允许时，获取：

```text
views
likes
comments
favorites
shares
followers_gain
watch_time
completion_rate
click_rate
publish_time
```

不存在的数据：

```text
null
```

禁止自行估算为真实平台数据。

---

# 三十二、跨平台数据表

统一转换：

```json
{
  "content_id": "",
  "platform": "",
  "views": null,
  "likes": null,
  "comments": null,
  "favorites": null,
  "shares": null,
  "followers_gain": null,
  "completion_rate": null
}
```

---

# 三十三、运营分析

对每条作品计算：

```text
内容类型
发布时间
标题结构
主题
视觉风格
视频长度
首屏内容
互动率
传播率
收藏率
涨粉效率
```

然后寻找：

```text
哪些主题表现最好
哪些标题表现最好
哪些视频长度最好
哪些发布时段最好
哪些封面最好
```

---

# 三十四、自动生成运营建议

例如：

```text
过去10条作品中：

宋式人物类：
平均播放最高

古代市井类：
收藏率最高

纯风景类：
点赞不错，但涨粉较低

建议下一周期：

50% 宋式人物
30% 古代城市
20% 实验性内容
```

---

# 三十五、内容再利用

如果某个平台表现明显优秀：

推荐进行二次分发。

例如：

```text
B站长视频
↓
提取3个高信息密度片段
↓
抖音
小红书
视频号
```

或者：

```text
公众号长文
↓
提炼8张图
↓
小红书图文
```

或者：

```text
小红书爆款图文
↓
扩展脚本
↓
生成B站视频
```

---

# 三十六、内容矩阵

允许建立：

```text
1个母内容
        ↓
──────────────────
↓        ↓       ↓
B站     抖音    小红书
↓        ↓       ↓
长视频   短视频   图文
        ↓
      视频号
        ↓
     公众号文章
```

这是 Skill 的核心运营理念。

---

# 三十七、自动排期

如果用户指定：

```text
明天晚上8点发布
```

将平台任务写入：

```text
publish_queue
```

如果平台官方支持定时发布：

使用官方能力。

否则：

使用外部 scheduler 在指定时间调用 Publisher。

不要伪造平台不具备的定时发布接口。

---

# 三十八、运营任务不是永久后台进程

Skill 本身不应假装可以无限后台运行。

需要持续运营时使用：

```text
cron
scheduler
launchd
GitHub Actions
服务器任务
工作流调度器
```

定期调用：

```text
social-media-publisher-operator operate
```

例如：

```text
每天：
同步作品数据

每周：
生成运营报告

每月：
更新内容策略
```

---

# 三十九、目录结构建议

```text
social-media-publisher-operator/

SKILL.md

config/
    accounts.json
    platform_rules.json

platforms/
    douyin/
    xiaohongshu/
    bilibili/
    wechat_official/
    wechat_channels/

publish/
    publisher.py

analytics/
    metrics.py
    report.py

history/
    publish_history.json

queue/
    publish_queue.json

output/
    manifests/
    platform_copy/
    reports/
```

---

# 四十、建议的统一 CLI

提供：

```bash
social-publisher publish
```

例如：

```bash
social-publisher publish ./final.mp4
```

默认：

```text
识别文件
→ 准备内容
→ 选择全部已连接平台
→ 发布
```

---

也支持：

```bash
social-publisher publish ./final.mp4 \
  --platform douyin,xiaohongshu,bilibili
```

---

查看状态：

```bash
social-publisher status
```

---

运营分析：

```bash
social-publisher analytics
```

---

生成周报：

```bash
social-publisher report --period weekly
```

---

# 四十一、Codex 调用逻辑

当其他 Skill 生成最终内容之后：

例如：

```text
generate-song-aesthetic-video
```

完成：

```text
final.mp4
```

用户只需要说：

```text
发布
```

Codex 自动理解为：

```text
调用 social-media-publisher-operator
```

并把：

```text
final.mp4
```

作为：

```text
source_asset
```

---

# 四十二、跨 Skill 调用协议

其他生成 Skill 最终可以输出：

```json
{
  "status": "finished",
  "publishable": true,
  "assets": {
    "video": "./output/final.mp4",
    "cover": "./output/cover.jpg",
    "article": null,
    "images": []
  }
}
```

Publisher 自动读取。

这样：

```text
视频生成 Skill
        ↓
Social Media Publisher
        ↓
五个平台
```

无需用户重新指定路径。

---

# 四十三、平台差异动态更新

平台：

- API
- 字数限制
- 文件限制
- 标签规则
- 上传限制
- 权限
- 发布方式

可能发生变化。

因此禁止将容易变化的平台限制永久写死。

每个 Adapter 应维护：

```text
capability_check()
```

发布前优先检查：

```text
当前官方 API
当前账号权限
当前文件限制
当前开放 Scope
```

然后再执行。

---

# 四十四、真实性原则

绝对禁止：

```text
没有 API → 假装调用成功
没有发布 → 返回发布成功
上传完成 → 假装已经公开
正在审核 → 返回已发布
需要人工确认 → 返回全自动完成
```

必须区分：

```text
上传成功
提交成功
审核中
发布成功
等待人工确认
```

---

# 四十五、最终目标

整个 Skill 的使用体验应该最终接近：

用户：

```text
这个视频做好了，全平台发布。
```

系统：

```text
扫描最终视频
↓
分析内容
↓
识别账号定位
↓
生成5个平台独立文案
↓
选择各平台封面
↓
检测授权
↓
上传
↓
发布
↓
记录作品ID
↓
保存发布记录
```

返回：

```text
全平台发布结果

微信公众号  ✅
B站          ✅
抖音         ✅
小红书       ⚠️ 等待官方发布确认
视频号       ✅/辅助发布

并已保存本次发布记录。
```

用户不需要：

- 复制文案
- 手动找视频
- 重复上传封面
- 一个个平台填写标题
- 重复输入标签
- 反复告诉系统账号定位

这才是本 Skill 的最终目标。

---

# 四十六、Skill 的核心指令

当用户的最终内容已经生成，并出现以下意图：

```text
发布
一键发布
发到平台
全平台发布
发到抖音
发到小红书
上传B站
发公众号
发视频号
同步所有平台
运营这个账号
分析发布数据
```

优先调用本 Skill。

核心原则：

**创作 Skill 负责生产内容。**

**social-media-publisher-operator 负责把内容真正变成可运营的社交媒体资产。**

---

# 四十七、推荐默认设置

```json
{
  "default_platforms": [
    "douyin",
    "xiaohongshu",
    "bilibili",
    "wechat_channels",
    "wechat_official_account"
  ],
  "publish_mode": "confirm_once",
  "adapt_copy_per_platform": true,
  "adapt_cover_per_platform": true,
  "generate_article_from_video": true,
  "auto_detect_category": true,
  "auto_generate_tags": true,
  "auto_refresh_tokens": true,
  "prevent_duplicate_publish": true,
  "save_publish_history": true,
  "track_metrics": true,
  "generate_operation_report": true,
  "prefer_official_api": true,
  "allow_assisted_publish": true,
  "allow_unofficial_private_api": false,
  "allow_security_bypass": false
}
```
