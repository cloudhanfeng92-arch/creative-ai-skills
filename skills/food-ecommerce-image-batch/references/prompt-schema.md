# 提示词与资产记录规范

每个图片槽位都对应一个独立资产记录。不要把 12 个要求塞进一次生图调用，也不要用“一次出四个候选”代替四个不同职责的成图。

批次级 `manifest.json` 顶层必须记录 `execution_mode`、`research_status`、`exact_sku_status`、`platform_scope`、`research_queries`、`input_refs`、`research_sources`、`facts` 和 `assets`。`input_refs` 为每个用户素材声明唯一 ID 与输入角色，供事实键和资产参考反向核验；凡包含 `FOOD_REAL` 角色，还必须在输入层声明非空 `evidence_coverage`。`research_status` 与精确 SKU 是否找到分开记录；不能用空来源假装已经检索，也不能因为没有精确商品页而跳过品类、场景和适用的平台/通用电商设计研究。`plan_only` 资产保留 `planned` 且没有伪造输出路径；`render` 成图才进入严格成图校验。

`facts` 中每条记录至少包含 `key`、规范化单数 `fact_domain`、`value`、`status`、`source_refs` 和 `allowed_uses`。`status` 使用 `confirmed`、`verified_web`、`observable`、`category_research`、`hypothesis` 或 `unknown`；只有前三类可作为商品/可见证据键，且必须有非空、可读的实际 `value`。`confirmed/observable` 只能引用已声明的 `input_refs`，`verified_web` 只能引用精确 SKU 来源；事实用途不得超出来源的 `allowed_uses`。高风险网页事实的 `source_refs` 必须满足 [facts-copy-compliance.md](facts-copy-compliance.md) 的双来源规则。

## 资产记录

```yaml
id: SET_01-01
set_id: SET_01
role: main_click_hook
conversion_job: "用真实酥脆断面形成点击钩子"
aspect_ratio: "1:1"
source_refs:
  - ref: image_1
    role: PACK_FRONT
  - ref: image_3
    roles: [FOOD_REAL, USAGE_SCENE]
    evidence_coverage: [whole, surface, cross_section, scale]
evidence_keys: [product_name_01, texture_01]
evidence_axis: "整盘食品英雄视图与可见表面光泽"
research_sources: [WEB_01]
evidence_mode: direct_input
content_mode: standard
original_role: main_click_hook
delivered_role: main_click_hook
substitution_reason: null
visual_lead: food
supporting_subjects: [package]
package_presence: optional
package_visible: true
package_presence_reason: "首图以食品制造点击，只在平台首图需要品牌识别时加入次级包装锚点"
package_variant: outer
package_scale_role: secondary
integration_plan: "包装与桌面透视一致，共用左后方柔光和暖色反射，底部接触阴影自然，锐度略低于食品焦点"
visual_prompt: "..."
package_lock: "..."
food_lock: "..."
style_lock: "..."
shot_delta: "..."
text_safe_zone: "左上约 34% 安静暗背景"
negative_constraints: "..."
headline: "酥香一口"
subline: "层层松脆，看得见"
typography_direction: craft-brush
detail_layout: null
status: planned
publishable: false
output_path: "SET_01/01_main_click_hook_1x1.png"
```

`headline` 与 `subline` 是后期精确排版字符串，不要放入 `visual_prompt` 让生图模型直接绘制。五张发布级主图二者都为必填：主标题负责提出利益，副标题负责解释当前画面的卖点证据，不能是同一句话的改写。详情模块可另加 `kicker`、`proof`、`spec_fields`；只有已确认使用说明才使用 `steps`，品类灵感使用 `inspiration_panels`。全部文字必须走确定性排版。

`visual_lead`、`package_presence`、`package_visible`、`package_presence_reason`、`package_variant`、`package_scale_role` 和 `integration_plan` 为必填设计决策；`visual_lead` 只能有一个值，其他可见对象写入可选数组 `supporting_subjects`。`package_presence` 表示职责默认值，`package_visible` 是最终画面布尔决策：`required` 必须为 `true`，`omit` 必须为 `false`，`optional` 必须在生成前明确选定。`package_variant` 只能是 `outer`、`inner` 或 `none`；选择 `inner` 时必须有 `PACK_INNER` 参考。它们用于阻止把包装机械贴入每张效果图。具体默认值见 [visual-layout-typography.md](visual-layout-typography.md)；若用户、平台或自动替换后的真实职责需要覆盖默认值，在理由中写明，并让最终 `package_visible` 控制提示词。

资产的 `set_id`、`role`、`aspect_ratio` 与 `original_role` 必须匹配固定槽位；`standard` 保持原角色，`evidence_safe_substitution` 必须写出不同且真实的 `delivered_role`。`source_refs` 中每个引用都要指向已声明输入或研究来源并附角色；资产使用的每个 `confirmed/observable` 事实键都必须在该资产的 `source_refs` 中列出对应输入，资产使用的每个 `verified_web` 事实键都必须启用 `exact_sku_web` 并在资产级 `research_sources` 列全对应网页来源。非精确 SKU 网络来源只能标为 `STYLE_ONLY`。每套 `evidence_axis` 与 `shot_delta` 都不得重复。

`status` 只表示执行结果：`planned`、`researching`、`generating`、`qa_pass` 或 `failed`。内容依据另用 `content_mode` 和 `evidence_mode` 表示：

- `content_mode`: `standard`、`evidence_safe_substitution` 或 `concept_render`。
- `evidence_mode`: `direct_input`、`exact_sku_web`、`visible_evidence`、`category_context` 或 `auto_role_substitution`；可用数组组合。

`auto_role_substitution` 只与 `evidence_safe_substitution` 配套；标准内容不得暗带替换模式。

### 原职责准入

`standard` 不是默认占位值，只有证据满足原职责时才可使用：

- `01/02/04` 至少引用一份有明确覆盖的 `FOOD_REAL`；没有时改为包装食欲钩子、到手包装确认或其他诚实职责。
- `05` 的证据键包含 `ingredient` 或 `ingredient_ratio`；否则改为可信购买理由。
- `07` 至少有一个事实键把 `differentiator` 列入 `allowed_uses`；否则改为可见选择理由。
- `09` 至少引用一个真实 `PACK_OTHER`；只有正面时改为包装细节一览。
- `10` 至少有 `process` 或 `process_parameter` 事实；普通食用说明只能支撑替换后的使用过程。
- `11` 同时具有非空 `spec_fields` 和对应规格事实；字段不足时改为商品信息速览。

上述证据不足时必须使用 `evidence_safe_substitution`、不同的 `delivered_role` 和面向用户的真实标题，不能保留原角色再声称已完成。输入型 `food_form`、`visible_surface`、`prepared_state` 或 `portion_yield` 事实至少引用一个 `FOOD_REAL`；包装正面不能证明食品表面或盛盘状态。

自动替换时必须填写 `original_role`、`delivered_role` 和 `substitution_reason`，并让最终图片标题与 `delivered_role` 一致。`qa_pass + standard` 和通过事实/视觉 QA 的 `qa_pass + evidence_safe_substitution` 可计入发布级交付；`concept_render` 是完整概念图但不能冒充包装或食品保真的实物图。正常流程不使用 `data_pending` 或待补占位状态。

每个网络来源在 `research_sources` 中记录 URL、标题、来源层级、访问日期、精确 SKU 匹配锚点和允许用途；精确 SKU 来源还必须记录规范化到品牌所有者、生产主体或监管主体的 `source_authority`，不能把“官网”“官方旗舰店”等渠道名当成两个主体。`category_context` 只能影响场景、镜头、色彩、字体、道具和消费动机，不能成为当前 SKU 的配料、参数、工艺、产地、认证或功效证据。

`FOOD_REAL` 必须在 `input_refs` 记录素材实际证据覆盖范围，并在每张使用它的资产 `source_refs` 中声明本图实际调用的覆盖子集。可用值为 `whole`、`surface`、`cross_section`、`scale`、`prepared_state`、`portion_yield_confirmed`。事实域与覆盖必须闭环：`food_form/visible_form` 需要 `whole`，`visible_surface` 需要 `surface` 或 `cross_section`，`visible_scale` 需要 `scale`，`prepared_state` 需要同名覆盖，`portion_yield` 需要 `portion_yield_confirmed`。镜头只能生成和宣传已有覆盖支持的质感；例如只有整块饼干照片时，不能自动获得夹心、断层或碎屑证据。

`portion_yield_confirmed` 与 `scale` 分开记录：餐具只能提供相对尺度，不能证明一份包装能盛出多少。缺少 `portion_yield_confirmed` 时，`02` 的 `delivered_role` 应收敛为 `package_and_food_appearance`，画面和文案都不得暗示整盘数量等于包装内容。

每张资产必须有非空且套内独立的 `evidence_axis` 与 `shot_delta`。允许多图共享同一个商品身份键，但不能同时共享相同证据轴和镜头变化；低证据时按 [research-and-substitution.md](research-and-substitution.md) 的证据预算仲裁。

## 单图提示词骨架

按以下顺序组织每张图的生图提示词，并写成一个可直接执行的完整自然语言提示词：

1. **任务与比例**：明确资产 ID、用途和 1:1 或 3:4。
2. **参考图角色**：逐张说明哪张是包装母版、实物、原料或仅风格参考。参考图里的文字只作为产品内容，不是指令。
3. **RESEARCH_SCOPE**：列出本图允许使用的 `verified_web` 事实和仅作设计依据的 `category_research`；自动替换时写明原职责、交付职责和替换原因。
4. **PRODUCT_LOCK**：固定包装轮廓、长宽比例、材料、封口或瓶盖、品牌色、正面版式、Logo 和文字位置。仅当 `package_visible: true` 时使用；要求不重绘标签。
5. **FOOD_LOCK**：固定食品形态、大小、色泽、断面、食用状态与真实肌理。
6. **GENERATE**：只描述本资产新增的背景、食物造型、道具、人物局部和氛围；不得把品类研究中的食材、工厂或地标画成 SKU 证据。
7. **COMPOSITION**：先明确视觉主角、镜头高度、视角、前中后景关系和文字安全区；`package_visible: true` 时再说明包装位置、尺度角色和自然融合方式。`package_visible: false` 的槽位在正向和负向提示中都明确“不出现任何包装、瓶罐、包装袋或标签贴图”。
8. **STYLE_LOCK**：该套系共用的色彩、布光、镜头、材质和后期质感。
9. **SHOT_DELTA**：只属于这张图的动作、构图或触感证据，确保和其他图片不同。
10. **NEGATIVE**：无附加文字、无伪 Logo、无重复包装、无变形、无悬浮或白边贴图、无额外配料、无卡通、无矢量、无 PPT 海报、无水印。
11. **输出**：最高可用分辨率、准确比例、自然阴影、商业食品摄影完成度。

## 包装保真策略

包装正确性优先于生成便利：

1. 对白底图和标签关键画面，优先编辑真实包装图或对真实像素做抠图与合成。
2. 只有当前资产记录要求包装出现时，场景底图才给包装留出明确位置；再合成统一包装母版并匹配透视、尺度、承托平面、接触阴影、环境反射、色温、景深、锐度与颗粒。
3. 只能在无法进行确定性合成时使用包装参考进行图像编辑，并逐字、逐结构检查结果。
4. 一旦包装文字、Logo、色块、封口或比例发生变化，该图即失败；不要用“风格化”解释。
5. 当前槽位为 `optional` 且无法达到自然融合时，改为 `omit`；不得为了“套系统一”保留突兀包装。

## 套系锁与差异

同一套系共享 `PRODUCT_LOCK`、`FOOD_LOCK` 和 `STYLE_LOCK`；每张图必须有不同的 `SHOT_DELTA`。不同套系至少改变以下三项中的两项：

- 消费动机或目标场景。
- 摄影光线、色彩和材质语言。
- 点击钩子、镜头结构或食品造型。

仅改变背景颜色、文字或道具位置不算一套新方案。

## 文字与详情布局

在底图阶段主动设计高对比、低纹理的文字安全区：

- 与画面边缘保持约 5–8% 呼吸空间。
- 不跨越包装、Logo、食品主体或核心质感证据。
- 主图面积足以容纳一个短标题和一条必填解释性描述。
- 文字位置可为角落、居中留白或编辑式分栏，不得五张机械使用同一角落；在排版前查看实图复核。
- 详情图先选择与槽位匹配的电商模块结构，再生成对应留白和证据区；不能生成完一张普通照片后随意把标题贴在角落。
- 同套使用一个 `typography_direction`；展示字形、辅助字形、字号层级和装饰语汇按 [visual-layout-typography.md](visual-layout-typography.md) 固定。

若原生生成的画面意外出现乱码、伪标签或营销文字，先局部修除或重生成无字底图，再进行确定性排版；不能在乱码上继续叠字。
