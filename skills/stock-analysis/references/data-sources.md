# 数据源、权限与时效

核实日期：2026-10-03。接口权限、额度和交易安排可能变更；实际运行以当前官方文档、账户权限和返回数据为准。

## 运行时选择

1. 先发现当前会话实际可调用的 MCP、行情或财务工具；优先使用已连接且覆盖目标市场的来源。
2. 核对工具的市场、证券类型、代码规则、返回字段、数据截至时间、延迟声明及权限。存在官方 MCP 不代表用户已安装或获实时授权。
3. 有行情工具也须核查响应：成功调用不等于实时；返回空值、无时间戳或权限错误时不能补造数据。
4. 没有合适工具时，先运行内置 free_market_data.py（A股 AKShare，港美股 yfinance），并用网页搜索/读取访问下列官方披露入口、交易所规则和数据商文档。动态网页读不到正文时使用已授权浏览器或其他官方入口；不绕过登录、付费或访问限制。
5. 搜索摘要仅用于定位，重要数字回到公告原文、财报或可核验行情页面。新闻转载作为辅助来源，不能替代正式披露。
6. 不预设特定 MCP 工具名。用户已要求本技能取数且缺公共依赖时，可按连接指南初始化独立运行环境；不修改现有 MCP 配置，不购买行情或订阅服务。常规分析复用环境，不自动升级。

## 官方披露入口

| 市场 | 入口 | 用途 |
|---|---|---|
| A 股 | [巨潮资讯](https://www.cninfo.com.cn/)、[上交所公司公告](https://www.sse.com.cn/disclosure/listedinfo/announcement/)、[北交所公司公告](https://www.bse.cn/disclosure/announcement.html) | 年报、季报、临时公告、公司行动；核对证券代码、公告日期、报告期与更正版本。 |
| 港股 | [披露易标题检索](https://www.hkexnews.hk/homelcititlesearch.html) | 上市公司公告、年报、通函等；保留文件发布时间及原始 PDF 链接。 |
| 美股 | [SEC 文件检索](https://www.sec.gov/search-filings)、[EDGAR 数据 API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | Submissions 与 Company Facts/XBRL；先确认公司 CIK，再匹配报表、币种、期间与修订文件。 |

SEC 披露数据 API 无需 API key，数据随披露更新；批量 ZIP 夜间更新。它是披露源，不是行情源。自动访问须遵守 [SEC 访问规则](https://www.sec.gov/about/webmaster-frequently-asked-questions)，包括总计不超过每秒 10 次请求。

## 可选行情源与限制

默认免密源已提供适配器；其余是增强候选，不代表用户已获权限。完整安装和故障处理见 [连接指南](connection-guide.md)。

| 来源 | 核实能力 | 使用边界 |
|---|---|---|
| AKShare（默认 A股） | 单股快照、历史日线、三大报表 | 所选接口免数据 Key；快照可能缺源时间，财报利润/现金流通常为年初累计。按返回的单位、报告期、公告日期核对。不能把期末日当披露日。 |
| yfinance（默认港美） | 报价元数据、历史日线、年度/季度报表 | Yahoo 非官方客户端；HK 通常15分钟延迟，US不统一保证实时。常规时段价不等于盘前盘后价；quarterly不是TTM。缺财务币种时先核验，不能用股价币种代替报表币种。 |
| 已有行情工具 | 按实际工具说明与响应判定 | 未说明延迟、时间戳或来源时标记“时效未核实”，不能称为实时。 |
| Tushare A 股 `daily` | [官方文档](https://tushare.pro/document/2?doc_id=27)：未复权日线，交易日 15–16 点入库，停牌期间不提供数据 | 盘后历史数据；检查最新 `trade_date`，不能把刚收盘视为当日日线已完成入库。 |
| Tushare A 股实时 | [`rt_k`](https://tushare.pro/document/2?doc_id=372) 为实时日线、[`rt_min`](https://tushare.pro/document/2?doc_id=374) 为实时分钟 | 须核查正式权限；`rt_k` 单独开通。接口名称不能代替返回数据的时间核验。 |
| Tushare 港股 | [`hk_daily`](https://tushare.pro/document/2?doc_id=192) 约 18 点更新当日数据；[`rt_hk_k`](https://tushare.pro/document/2?doc_id=383) 为实时日线 | 两者均须单独权限；当前 `rt_hk_k` 文档未列行情时间戳，不能把抓取时间当作报价时间。 |
| Tushare 美股 | [`us_daily`](https://tushare.pro/document/2?doc_id=254) 提供未复权日线 | 120 积分为试用，正式权限另开；不作为实时源。 |
| Alpha Vantage | [API 文档](https://www.alphavantage.co/documentation/)：`GLOBAL_QUOTE` 默认日终更新 | 须 API key；美股实时及 15 分钟延迟行情需 premium 和 data entitlement，商业用途另询供应商。 |
| HKEX 数据供应商 | [官方 15 分钟延迟供应商列表](https://www.hkex.com.hk/-/media/HKEX-Market/Services/Market-Data-Services/Real-Time-Data-Services/Data-Licensing_/HKEX_IS-Lists/2026/20260131-Delayed-IV-List_E.pdf) | 用于核查供应商身份；名单本身不是免费行情 API，也不能证明用户拥有授权。 |

Tushare 需要 [账户 Token](https://tushare.pro/document/1?doc_id=39)，积分与单独权限按接口分别检查；[交易日历 `trade_cal`](https://tushare.pro/document/2?doc_id=26) 当前要求 2000 积分，不应写成无条件免费。
Alpha Vantage [普通免费额度](https://www.alphavantage.co/support/)当前为每日 25 次；实时/延迟数据授权见 [premium 说明](https://www.alphavantage.co/premium/)。密钥仅通过安全配置读取，不写入报告、脚本或日志。

## 时间证据与交易状态

每次取价保留以下记录；不提供的字段填 `null` 并说明原因，不能用当前时间推填：

```json
{
  "symbol": "证券代码", "exchange": "交易所", "currency": "币种",
  "price": null, "price_type": "last_trade|close|bid|ask|other",
  "quote_time": null, "timezone": "IANA 时区", "trade_date": null,
  "fetched_at": "ISO 8601 含时区时间", "declared_delay_minutes": null,
  "freshness": "verified_realtime|delayed|eod|unknown",
  "source_realtime_verified": false,
  "quote_age_seconds": null, "latest_session_verified": null,
  "acceptable_for_task": null,
  "market_state": "auction|regular|break|extended|closed|halted|unknown",
  "adjustment": "none|forward|backward|unknown", "source_url": "原始来源"
}
```

- `quote_time` 是行情事件/源更新时间，`fetched_at` 是取数时间；二者分别记录。只有交易日期的日线不得虚构分钟级时间。`quote_age_seconds` 用实际分析时间减报价时间计算；未来时间戳先排查时区或源错误。`latest_session_verified` 和 `acceptable_for_task` 为布尔值或未核实时的 null，不能用“延迟15分钟”的标签替代实际年龄与适用性判断。
- 公告另记 `published_at`、`report_period`、文档版本/更正关系及文件 URL；财务报告期不能当作市场已经知悉该信息的日期。
- 使用 `Asia/Shanghai`、`Asia/Hong_Kong`、`America/New_York` 等 IANA 时区；美股由纽约时区处理夏令时，不写死北京时间开盘时间。
- 状态判断结合目标交易所当年节假日日历、半日市/提前收市、具体证券时段、临时停市与个股停牌。周末调休不自动成为 A 股交易日；无成交不自动等于停牌。
- A 股竞价时段参考[上交所 2026 交易规则](https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml)：09:15–09:25 开盘竞价；09:30–11:30、13:00–14:57 连续竞价；14:57–15:00 收盘竞价。其他交易所、板块及盘后机制另核查。
- 港股普通全日连续交易为 09:30–12:00、13:00–16:00；适用收市竞价的证券随机收于 16:08–16:10，半日市另判。见 [HKEX 时段](https://www.hkex.com.hk/Services/Trading-hours-and-Severe-Weather-Arrangements/Trading-Hours/Securities-Market)。
- 美股核心时段为 09:30–16:00 ET；盘前盘后按交易场所/产品区分，假日及提前收市查 [NYSE 日历](https://www.nyse.com/trade/hours-calendars)。
- 已休市时，最近完整交易日收盘可以是最新有效收盘；不得仅因经过数小时判定数据异常，也不得称为当前可成交价。

## 数值一致性

- 先锁定交易所、证券类别和币种；A/H 股、ADR 与本地普通股不可仅按公司名称合并。涉及 ADR 须核实换股比例。
- 技术指标使用同一复权方式、周期与完整历史窗口，记录复权基准；现价展示与交易价位采用可解释的价格口径，不混用复权价格和原始价格。
- 公司行动、拆合股、分红、更正报表会改变可比口径；跨源差异先核查时间、复权、币种、单位及交易时段，再比较数字。
- 财务比较统一报告期、会计口径和币种；估值使用匹配的股数/每股数据，换汇记录汇率来源与日期。
- 成交量与成交额单位按接口核实。例如 Tushare A 股 `daily` 为手/千元，港股 `hk_daily` 为股/元，不能直接拼接。

## 无实时源时降级

1. 先比较数据实际年龄及最近有效交易日，再在有效且适合任务的候选中选择：已验证实时源 → 明确延迟快照 → 最近完整交易日收盘 → 仅公告/财务分析。旧延迟快照不能优先于较新的已核实收盘价。
2. 输出开头说明“截至何时、何种价格、是否延迟”；不以“最新”“刚刚”掩盖旧数据。
3. 继续完成业务、财务、竞争与风险分析。依赖现价的估值/技术指标使用同一价格日期计算并标明基准日；没有可核对价格则留空。
4. 实时需求未满足时明确缺口，不模拟盘中走势、不生成未经数据支持的即时触发结论；如有必要，仅说明可接入的来源与所需权限，等待用户决定。

## 可选本地时效检查

`scripts/quote_check.py` 位于 stock-analysis 技能根目录下。将已有工具回包归一化成上面的 JSON，再执行：

```sh
python3 <stock-analysis目录>/scripts/quote_check.py --help
python3 <stock-analysis目录>/scripts/quote_check.py --input quote.json --now <含时区的ISO时间> --max-age-seconds <本任务可接受秒数>
```

`source_realtime_verified` 仅在来源权限/说明确实验证后填 true，不能根据工具名称自动设置。`latest_session_verified` 仅在交易日历及数据日期核对后填 true。价格必须为正；source_url 或 source_tool 至少一项非空，不能为通过校验伪造字段。

该脚本只校验输入元数据，不能认证行情真伪、自动读取日历或替代来源授权。返回 real_time_usable、quote_age_seconds、use_class 和 reasons；将结果作为时效门槛之一，不作为买卖信号。缺报价时间时保留 null，不能把 fetched_at 复制给它。闭市的已确认最新收盘价可作收盘研究基准，不是实时可成交价格。
