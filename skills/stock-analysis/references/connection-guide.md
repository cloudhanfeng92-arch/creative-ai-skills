# 默认免密数据接入

更新：2026-10-03。推荐版本是 **AKShare + yfinance + 宿主搜索/网页读取**。本包的默认接口无需数据账户、API Key、积分或新增 MCP。保留一个 stock-analysis 入口及八类分析能力。

## 数据分工

| 问题 | 默认来源 | 关键口径 |
|---|---|---|
| A 股单股快照 | AKShare / 东方财富，异常或缺时间时一次腾讯单股后备 | 保留同一来源的价格和完整时间；腾讯也失败时保留可用东财快照并标时效未知，不拼接两源价与时间。 |
| A 股历史日线 | AKShare / 东方财富，失败时有限新浪后备 | 明确 none/qfq/hfq；不同源成交量单位可能是手/股，不能直接拼接。 |
| A 股三大财报 | AKShare / 新浪财经 | 保留报告期和公告字段；利润/现金流按年初累计处理，单季须差分。 |
| 港美股报价与日线 | yfinance / Yahoo Finance，失败时一次 AKShare / 新浪历史后备 | HK通常延迟15分钟；US按实际标的核实。历史后备仅是收盘研究参考，不是盘中报价。 |
| 港美股年度/季度财报 | yfinance / Yahoo Finance | 季度不是TTM；公开日期、币种/单位缺失时明示，并回原始披露核对。 |
| 新闻、政策、正式披露 | 宿主搜索 + 网页读取 | A股巨潮/交易所/公司IR，港股披露易，美股SEC。搜索摘要仅用于定位。 |

这些公开接口适合按需研究，可能限流或因网页改版失效，不能承诺逐笔行情或持续可用性。只承诺已测试的本次能力；具体证券的覆盖和字段仍取决于来源。

## 本机与其他设备初始化

本次已在本机独立环境安装 AKShare 1.19.1、yfinance 1.7.0；具体连通结果见 [验证记录](verification.md)。运行环境位于 `~/.local/share/stock-analysis/venv`，不放进 ZIP。技能脚本会自动选择它，无需激活虚拟环境。

在其他设备保留整个技能目录，用现有 Python 3.11+ 初始化一次：

```sh
python3 <技能目录>/scripts/setup_free_data.py
python3 <技能目录>/scripts/free_market_data.py doctor
```

如果默认 python3 版本较旧，使用宿主已有的 Python 3.11+ 路径：

```sh
python3 <技能目录>/scripts/setup_free_data.py --python <Python3.11以上解释器路径>
```

Codex 桌面环境可先发现宿主自带 Python，再传入路径；不要把某台机器的绝对解释器路径写进可移植技能。安装脚本仅在独立环境安装固定版本的两套库及依赖，不修改系统 Python/MCP。无需注册和配置密钥，也不自动安装证券客户端。正常研究复用已有环境，不重复更新依赖。

默认从官方 PyPI 安装。如 PyPI 网络不可达，可用 AKShare 官方安装说明列出的公开镜像：

```sh
python3 <技能目录>/scripts/setup_free_data.py --index-url https://mirrors.aliyun.com/pypi/simple/
```

安装成功仅代表依赖可导入，doctor只做离线检查，不表示行情、财报一定可用。

## 使用示例

证券名称先核实为代码和市场，避免A/H股混用。以下日期只是参数示例，执行研究时换成当前任务区间。

```sh
python3 <技能目录>/scripts/free_market_data.py quote --market CN --symbol 600519.SH
python3 <技能目录>/scripts/free_market_data.py daily --market CN --symbol 600519.SH --start 20260901 --end 20260930 --adjust qfq
python3 <技能目录>/scripts/free_market_data.py financials --market CN --symbol 600519.SH --statement income --period 20260630
python3 <技能目录>/scripts/free_market_data.py quote --market HK --symbol 00700.HK
python3 <技能目录>/scripts/free_market_data.py daily --market US --symbol AAPL --start 20260901 --end 20260930
python3 <技能目录>/scripts/free_market_data.py financials --market US --symbol AAPL --statement cashflow --frequency quarterly
```

三表参数为 income、balancesheet、cashflow。CN报表quarterly表示季度报告期，利润/现金流的原始值通常为累计，不能直接当作单季。港美股仅提供日线 `--adjust none`，Yahoo调整口径不能冒充A股前/后复权。起止日期均含当天，但仅返回该源有记录的交易日，不填补停牌/休市空白。

港美股股票类别代码采用 Yahoo 格式，例如 `BRK-B`，不使用 `BRK.B`。

每次默认45秒超时，`--timeout`可设5至90秒；默认最多输出1500行，`--max-rows`可设1至5000。超限会标记 partial、truncation 与保留范围，不悄悄称完整历史。A股财报按提供商支持保留近8期；明确历史报告期时按该期检索，缺失需回原始披露。

## 成功、失败与时效

- `ok`：得到了相应数据。仍须检查身份、币种、日期、单位和limitations；不是实时或投资结论的认证。
- `partial`：存在字段、范围或输出限制，只使用已证实部分。
- `no_data`：没有匹配记录；不推断公司没有经营或没有风险。
- `timeout`、`provider_error`、`dependency_missing`：分别表示超时、源失败和运行环境缺依赖；不返回旧缓存伪装成功。
- `normalized`是报价元数据，`metadata_checks`复用quote_check.py。源未给quote_time就保留null；market_state/latest_session_verified必须通过交易日历及证券状态另查。120秒是诊断默认值，实际任务须说明自己的时效要求。

取数失败时：脚本最多使用一次既定后备 → 确认代码和网络 → 使用当前已授权的其他行情工具或对应官方网页 → 降级为有日期的收盘研究/仅财务分析。港美股财报为空时明确缺口并查公司原始披露，不能把空表当作零利润。不要连续重试全市场接口，不自动开户、申请Token或购买数据。数据不足时限制相应结论，仍完成能核实的研究。

对港美股报告，股价币种和财务报表币种分别核对。对历史时点研究，不能把后来披露或修订的财报当作当时已知信息；提供商没给公告时间时须补原文。

## 保留的可选增强

`market_data.py` 仍提供 Tushare 取数，只有用户选择或已有授权时启用；没有 TUSHARE_TOKEN 不会阻断免密方案。Tavily、Tushare MCP 与其他授权行情的配置见 [可选增强连接](optional-connections.md)。默认无需复制任何 MCP 配置。

当前运行通过Python脚本，适用于支持工具执行的Agent Skills宿主；只支持远程MCP、不能运行脚本的宿主仍需要额外包装/部署，不能把下载技能当作已经连通。

依据：[AKShare](https://github.com/akfamily/akshare)、[股票接口文档](https://akshare.akfamily.xyz/data/stock/stock.html)、[安装说明](https://akshare.akfamily.xyz/installation.html)、[yfinance](https://github.com/ranaroussi/yfinance)、[yfinance用法](https://ranaroussi.github.io/yfinance/)、[Yahoo市场延迟](https://help.yahoo.com/kb/SLN2352.html)。
