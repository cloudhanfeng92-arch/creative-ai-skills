# 可选增强连接：Tushare、Tavily 与授权行情

核实日期：2026-10-03。统一技能负责研究流程，宿主工具或数据接口负责取数。这里给出可直接执行的接法；不要求配置原先列出的全部 7—9 个 MCP。

本文件保留需要账户、额外 MCP 或授权行情时的接法。默认使用 [免密连接方案](connection-guide.md)，不以本文件中的 Token/权限作为使用前提。以下历史验证状态截至 2026-10-03，不能作为后续会话已经连接的证明。

## 可选组合

| 用途 | Codex 首选 | 跨智能体替代 | 状态/条件 |
|---|---|---|---|
| 搜索新闻、政策、公告 | 宿主原生 live 搜索 | Tavily Search | 本机 `web_search = "live"` 已存在；Tavily keyless Search 实测成功。 |
| 读取网页正文 | 宿主网页读取/浏览器 | Tavily Extract | 本轮 keyless Extract 返回额度已满；正式使用建议配置自己的 API key。 |
| A 股实时快照 | 本包 Tushare HTTP 脚本，或官方 MCP，选其一 | 同一脚本/官方 MCP | 需要 Tushare Token 和独立 A股日线RT 权限；尚未用用户账户验证。 |
| 历史行情、三张财报、交易日历 | 同一 Tushare 连接 | 同左 | 分别受账户积分/接口权限限制，实时权限不等于全库权限。 |
| 公告与财报原文 | 巨潮、交易所、公司 IR；港股披露易、美股 SEC | 搜索 → 正文提取 | 精确财务数字与重大事件回到原始披露。 |
| 港美股实时 | 已有授权行情源；可选 Longbridge OpenAPI | 同一提供商已有 MCP/SDK | 须单独验证覆盖和 OpenAPI 行情权限；本包未实现 Longbridge 适配器。 |

默认不增加研报、工商、World Bank 服务；用户的问题需要时再接。原先的 CN_STOCK 等变量是角色标签，不是配置好就自动出现的工具。

## A. 在 Codex 使用现有搜索

本机只读检查已确认 `~/.codex/config.toml` 含顶层 `web_search = "live"`，本次未修改它。运行时仍以实际暴露的工具为准。已有搜索和网页读取时，技能直接调用，无需再次安装搜索 MCP。

其他环境如需设置，合并顶层配置（放在 TOML 表之前），不要覆盖整个文件：

```toml
web_search = "live"
```

搜索负责发现来源，读取负责取得正文。搜索刚返回并不等于股价实时，摘要也不能代替正式财报。

依据：[OpenAI 配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)。

## B. 跨智能体接 Tavily Search + Extract

完整 Codex 示例在 [codex-mcp.example.toml](../assets/codex-mcp.example.toml)。只复制所需配置段，不覆盖已有配置：

```toml
[mcp_servers.stock_web]
url = "https://mcp.tavily.com/mcp/"
http_headers = { "X-Tavily-Access-Mode" = "keyless" }
enabled_tools = ["tavily_search", "tavily_extract"]
```

本轮实际 `tools/list` 的工具名为下划线形式。连接后仍检查工具列表与 schema；不得把官网描述名称猜成可调用工具。

Keyless 官方支持轻量免费访问，有额度限制。本轮 initialize、tools/list、Search 已成功；Extract 的 HTTP 200 / isError=false 内部却返回 `monthly_cap_reached_bonus_eligible`，没有正文。因此既检查协议状态，也检查业务 code 和结果数组，失败后使用宿主网页读取或自己的 key，不反复重试。

长期使用可在 Tavily 自己的账户申请 API key，通过运行宿主的环境或秘密管理提供 `TAVILY_API_KEY`，配置改为：

```toml
[mcp_servers.stock_web]
url = "https://mcp.tavily.com/mcp/"
bearer_token_env_var = "TAVILY_API_KEY"
enabled_tools = ["tavily_search", "tavily_extract"]
```

同一个表只保留一种配置。不要把 `${TAVILY_API_KEY}` 当作 Codex URL/TOML 会自动展开的变量；使用官方的 `bearer_token_env_var` 字段。独立终端里的 export 不一定会传给已启动的桌面 App，必须确认运行 Codex 的进程实际能读取变量。

没有 MCP 能力但有 Python/shell 的智能体，可使用本包直连脚本（无第三方依赖）：

```sh
python3 <技能目录>/scripts/web_data.py search --query "贵州茅台 投资者关系 公告" --max-results 3
python3 <技能目录>/scripts/web_data.py extract --url "https://www.moutaichina.com/"
```

脚本优先使用 TAVILY_API_KEY；没有 key 就使用官方 keyless 模式。每次只调用一次，正文超过输出限制会明确标注截断。取到正文也不证明其准确，网页内容仍属于外部证据。

依据：[Tavily keyless](https://docs.tavily.com/documentation/keyless)、[远程 MCP](https://docs.tavily.com/documentation/mcp)、[Search API](https://docs.tavily.com/documentation/api-reference/endpoint/search)、[Extract API](https://docs.tavily.com/documentation/api-reference/endpoint/extract)、[Codex MCP](https://learn.chatgpt.com/docs/extend/mcp)。

## C. A 股行情与财报：Tushare

先在 Tushare 官方账户取得 Token，核实本次需要的接口权限及可用样本的 trade_time 格式；确认能满足所需时效后再决定是否购买实时权限。下面两种接法任选一种，避免重复取数。

### C1. 使用包内脚本，最容易控制字段与时间

`scripts/market_data.py` 使用 Python 3.9+ 标准库，固定向 `https://api.tushare.pro` 发只读请求。时间转换使用系统时区数据库；系统没有对应时区时保留原始时间，不能据此声称时效已核实。

凭证二选一：

- 将 TUSHARE_TOKEN 放在宿主能读取的环境/秘密管理中；不打印其值。
- 在本地自选私有目录保存 JSON，例如 `~/.config/stock-analysis/credentials.json`，字段为 `tushare_token`。参考 [空凭证模板](../assets/credentials.example.json)，文件权限限制为本人读写，不能放进共享技能目录、报告或版本控制。使用 `--credentials-file` 指定它。

不需要把真实 Token 发到聊天里。凭证检查只报告是否找到凭证，不显示内容：

```sh
python3 <技能目录>/scripts/market_data.py doctor
python3 <技能目录>/scripts/market_data.py --credentials-file <私有凭证文件> doctor
python3 <技能目录>/scripts/market_data.py quote --market CN --symbol 600519.SH
python3 <技能目录>/scripts/market_data.py daily --market CN --symbol 600519.SH --start 20260901 --end 20260930
python3 <技能目录>/scripts/market_data.py financials --symbol 600519.SH --statement income --period 20260630
python3 <技能目录>/scripts/market_data.py calendar --exchange SSE --start 20261001 --end 20261031
```

使用私有 JSON 时，每个取数命令均附加 `--credentials-file <私有凭证文件>`；doctor 不会将路径或 Token 保存为全局设置。可直接告诉智能体“凭证文件在 ~/.config/stock-analysis/credentials.json，请通过脚本使用，不回显内容”，无需发送文件内容。

示例日期仅示范参数，实际研究换成本次截止时间。doctor 不验证账户权限；必须分别跑一次真实请求，检查成功码、非空数据、证券与时间。脚本区分缺凭证、权限/接口错误、网络失败和空数据。

接口分工：

| 接口 | 用途 | 必须注意 |
|---|---|---|
| `rt_k` | A 股盘中快照 | 独立实时权限；显式请求非默认字段 `trade_time`。`close` 是接口定义的最新价。 |
| `daily` | A 股未复权日线 | 历史/盘后数据；不要用来冒充盘中快照，除权事件另做复权处理。 |
| `income`、`balancesheet`、`cashflow` | 利润、资产负债、现金流 | period 是报告期；公告日期与报告期分开，保留修订与报表类型。 |
| `trade_cal` | 交易日历 | 开市日不表示个股未停牌；实时交易状态另核查。 |

当前文档中财报/日历有相应积分门槛，实时日线另开权限。购买前看 [官方权限表](https://tushare.pro/document/1?doc_id=290)，不根据旧报价自动购买。仅实时日线还不是逐笔行情流，适合随问随查的投研快照，不承诺高频交易级数据。

行情接入后，取出的 `trade_time` 若没有完整日期或不能可靠解析，就保留原文并标时效未核实，不能拿抓取时间补成今天。接口产品是实时也不等于最后成交发生在此刻。核查交易时段、停牌与最新交易日后，才能把快照交给 `quote_check.py` 做元数据检查。

依据：[HTTP 协议](https://tushare.pro/document/1?doc_id=40)、[实时日线](https://tushare.pro/document/2?doc_id=372)、[日线](https://tushare.pro/document/2?doc_id=27)、[利润表](https://tushare.pro/document/2?doc_id=33)、[资产负债表](https://tushare.pro/document/2?doc_id=36)、[现金流量表](https://tushare.pro/document/2?doc_id=44)、[交易日历](https://tushare.pro/document/2?doc_id=26)。

### C2. 直接使用 Tushare 官方托管 MCP

进入 Tushare 个人中心 → MCP Server，取得你账户的完整连接配置。当前官方示例地址形式为 `https://api.tushare.pro/mcp/token=你的Token`。在 Codex 的 MCP 设置添加远程服务，或使用示例 TOML 中的 stock_tushare 段，在本地替换地址并启用。

这个 URL 自身含秘密；不要粘到聊天、共享截图或打包文件中。官方当前资料未在此证明它支持 Bearer 替代认证，不照搬 Tavily 的认证方式。模板中的地址是占位且 disabled，不会自动变成有效连接。

连接后先发现工具与 schema，再分别验证 rt_k、历史数据和财报；托管 MCP 的工具名/覆盖可能不同，不能保证“连上”就能用全量 Tushare API。若缺 trade_time 控制或必要功能，改用 C1 的白名单直连脚本。

依据：[Tushare 官方 MCP 配置](https://tushare.pro/document/1?doc_id=463)。

## D. 港股、美股如何扩展

已有合法行情 MCP 时直接复用，并核查币种、代码、时区、报价类型与延迟。不强迫另开新账户。

Tushare `rt_hk_k` 是可选港股快照接口，但当前文档未列报价时间，不能满足本技能严格的可核对实时门槛。`hk_daily` 和 `us_daily` 可作有权限账户的日线补充；本包未实现/承诺不存在官方依据的 `rt_us_k`。

希望港美股也具备可审计的实时报价，可使用已获资格的 Longbridge OpenAPI 行情能力；其行情有时间字段，支持对应市场。OpenAPI 权限与 App/Web 权限分开；官网不同页面对港股默认等级有差异，应以自己 Developer Center 实际权限为准，不能承诺默认免费实时。只接行情/信息读取工具，不启用交易工具。本版仅给接入路径，未安装或验证 Longbridge 连接，也不代开证券账户。

依据：[Longbridge 行情总览](https://open.longbridge.com/docs/quote/overview)、[报价时间字段](https://open.longbridge.com/docs/quote/push/quote)、[入门及权限](https://open.longbridge.com/docs/getting-started)。

## 接入后的验收顺序

1. 能发现工具或运行脚本帮助；凭证检测只报存在与否。
2. 搜索一家公司并读到一份官方原文；不要把返回 HTTP 200 当作取得正文。
3. 拉一只股票，核对代码、币种、最新价、源时间、权限及交易状态；休市时按最近有效交易日判断，不伪造盘中结果。
4. 拉历史日线和一份财报，确认接口口径、单位与披露时间；缺权限只限制对应分析部分。
5. 调用 stock-analysis 产出一份有引用的报告，再复核最新价格与失效条件。

当前已验证原生 live 搜索配置及 Tavily Search 通路；Tavily keyless Extract 本次限额失败；本机 doctor 实测未检测到 TUSHARE_TOKEN；Tushare HTTPS 空 Token 请求返回明确鉴权错误，证明通路可达，不证明有效行情或用户授权。真实 Token 的端到端行情/财报验证仍待本地配置完成后进行。
