# 代码动态视频项目

复制整个模板到工作区独立目录后编辑。默认 15 秒、1920×1080、30 fps，内容与画面按本次需求修改。模板是工程骨架：复用播放器、时间轴与渲染接口，按主题重写示例场景的构图和动作，移除占位文案及演示角标；不能只换标题、颜色便作为最终作品。

- 规格：`video.config.json` 的宽高、帧率、时长和本地最终混音路径；`audio: null` 表示静音。
- 内容与美术：`src/main.js` 的 `CONTENT`、`STYLE`、`drawScene()`。
- 文字：旁白文案默认用代码绘制为字幕或动态文字，不生成朗读；字体、配色、位置和动效按主题修改，模板只是基础结构。
- 时间线：可沿用 `SCENES` 或改用文字 cue 起止，按可读停留与画面节奏安排。已有歌曲可同步歌词；只有明确要求配音时才生成 TTS 并按音频实测时长回填。
- 素材：按需创建 `public/`，资源就绪后设置 `window.__VIDEO_READY__ = true`。

将 `/path/to/skill` 与 `/absolute/project` 替换为 Skill 和项目的实际绝对路径：

```sh
node /path/to/skill/scripts/validate-video.mjs --project . --video output/final.mp4
node /path/to/skill/scripts/export-html.mjs --project . --out /absolute/project/output/作品名.html
```

网页预览按需，不是 MP4 必需步骤；需要浏览器时优先且只使用 Codex 内置浏览器的官方工具，先确认它实际支持的访问、预览与导出能力。禁止外部 Google Chrome、Chrome for Testing、独立 Chromium、个人 profile/CDP、间接浏览器启动或桌面录屏。旧 `render-preview.mjs` / `render-video.mjs` 已在 `openRenderer` 拒绝执行；上列命令仅校验已有 MP4 和打包 HTML，不会生成视频。

内置能力不能完成视频导出时，才复用项目已有、确认不启动浏览器的原生 Canvas/Skia/SVG 等后台入口，并用 FFmpeg 编码；模板未附带通用原生导出器，也不保证 DOM/WebGL 可直接迁移。没有兼容入口时交付源码和已有产物，说明 MP4 未完成。

静帧用于排版排错；有正式输出后，从中后台查看核心动作和关键交界的短时连续变化。交付目标仍为 `output/final.mp4`、`output/作品名.html`、`output/cover.png` 和源码。HTML 仅按内置浏览器实际能力验证，不自动在系统浏览器打开；无法运行或断网验证时注明未验证。封面保留绘制入口，用允许且可用的单帧导出路径。内置浏览器也使用本机资源；默认单任务、保守编码线程，不承诺更省 CPU/GPU。

开发入口依赖 `src/main.js` 和配置文件，单文件交付使用 `export-html.mjs` 打包，不直接把开发入口当成独立 HTML。基础模板提供播放/暂停、重播、进度与按需启用声音，渲染模式隐藏控件并关闭自主播放。导出器只处理本模板的结构；若引入图片、字体、其他脚本等依赖，按 `references/html-delivery.md` 的说明将资源一并打包。

排错时可用校验器的 `--full-decode`；时间轴问题通过允许入口按实际能力定位，不调用旧渲染器。页面兼容接口优先使用 `window.__VIDEO_RENDER_CONFIG__`，否则读取配置；`window.seek(t)` 单位为秒，但不代表内置工具可以直接调用它。
