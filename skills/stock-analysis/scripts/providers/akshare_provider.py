"""Read-only, no-data-key A-share adapter. AKShare is imported only on a query.

Upstream definitions checked 2026-10-03: akfamily/akshare (stock_ask_bid_em.py,
stock_hist_em.py, stock_zh_a_sina.py, stock_finance_sina.py). The caller owns
process timeouts/output limits; one AKShare invocation may perform several HTTP calls.
"""
from __future__ import annotations

import importlib
import json
import math
import re
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

DOCS = "https://akshare.akfamily.xyz/data/stock/stock.html"
STATEMENTS = {"income": "利润表", "balancesheet": "资产负债表", "cashflow": "现金流量表"}
EXCHANGES = {"SH": "SSE", "SZ": "SZSE", "BJ": "BSE"}


def _result(api, url, limitations):
    return {"status": "provider_error", "provider": "akshare", "source_api": api,
            "source_url": url, "documentation_url": DOCS, "fetched_at": None,
            "limitations": list(limitations), "raw": {}, "data": []}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _error(result, exc):
    result.update(status="provider_error", data=[], fetched_at=_now(),
                  error=_failure(exc))
    if "normalized" in result:
        result["normalized"] = []
    return result


def _failure(exc):
    # Never echo exceptions: proxy/HTTP errors can contain authenticated URLs.
    return {"type": type(exc).__name__, "message": "request_or_data_validation_failed"}


def _symbol(symbol):
    if not isinstance(symbol, str) or not re.fullmatch(r"[0-9]{6}\.(SH|SZ|BJ)", symbol):
        raise ValueError("symbol must be an A-share code such as 600519.SH")
    code, suffix = symbol.split(".")
    if code[0] not in {"SH": "6", "SZ": "03", "BJ": "489"}[suffix]:
        raise ValueError("symbol prefix and exchange are inconsistent for this A-share adapter")
    return code, suffix, suffix.lower() + code


def _date(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{8}", value):
        raise ValueError("date must be YYYYMMDD")
    return datetime.strptime(value, "%Y%m%d").date()


def _source_date(value):
    text = str(value)
    if re.fullmatch(r"[0-9]{8}", text):
        return _date(text)
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}(?:T.*)?", text):
        return _date(text[:10].replace("-", ""))
    raise ValueError("missing or invalid source report/trade date")


def _frame(frame):
    # pandas handles numpy scalars, NaN/NaT and datetime without leaking invalid JSON.
    records = json.loads(frame.to_json(orient="records", date_format="iso"))
    if not isinstance(records, list) or any(not isinstance(row, dict) for row in records):
        raise ValueError("unexpected AKShare table structure")
    return {"columns": [str(c) for c in frame.columns], "records": records}


def _number(value, *, positive=False):
    if isinstance(value, bool) or value is None:
        raise ValueError("missing or invalid numeric price")
    try:
        result = float(value)
    except (ValueError, TypeError):
        raise ValueError("missing or invalid numeric price") from None
    if not math.isfinite(result) or (positive and result <= 0):
        raise ValueError("price must be finite" + (" and positive" if positive else ""))
    return result


def _snapshot(result, symbol, suffix, price, field, stamp=None):
    return {"symbol": symbol, "exchange": EXCHANGES[suffix], "currency": "CNY",
            "timezone": "Asia/Shanghai", "price": price, "price_type": "last_trade",
            "source_price_field": field, "quote_time": stamp.isoformat() if stamp else None,
            "trade_date": stamp.date().isoformat() if stamp else None,
            "fetched_at": result["fetched_at"], "source_url": result["source_url"],
            "source_tool": result["source_api"], "freshness": "unknown",
            "market_state": "unknown", "source_realtime_verified": False,
            "latest_session_verified": None}


def _ak_quote(symbol):
    result = _result("stock_bid_ask_em", DOCS, [
        "单股东方财富网页行情；接口不返回报价日期或时间，抓取时间不是报价时间。",
        "未验证实时权限、延迟、最新交易日、交易时段或停牌状态。",
        "币种 CNY 和时区 Asia/Shanghai 按 A 股市场惯例标注，非源字段声明。",
        "原始总手单位为手，盘口 *_vol 为股；保留原始字段，不混合成交量口径。"])
    result["normalized"] = []
    try:
        code, suffix, local = _symbol(symbol)
        result["source_url"] = f"https://quote.eastmoney.com/{local}.html"
        raw = _frame(importlib.import_module("akshare").stock_bid_ask_em(symbol=code))
        result.update(raw=raw, fetched_at=_now())
        if not raw["records"]:
            result["status"] = "no_data"
            return result
        if not {"item", "value"}.issubset(raw["columns"]):
            raise ValueError("quote table requires item and value columns")
        values = {row["item"]: row["value"] for row in raw["records"]}
        price = _number(values.get("最新"), positive=True)
        normalized = _snapshot(result, symbol, suffix, price, "最新")
        result.update(status="ok", normalized=[normalized], data=[normalized])
    except Exception as exc:
        return _error(result, exc)
    return result


def _tencent_quote(symbol):
    code, suffix, local = _symbol(symbol)
    url = f"https://qt.gtimg.cn/q={local}"
    result = _result("tencent_quote", url, [
        "腾讯公开单股网页行情，价格与完整源时间来自同一响应；未确认授权或延迟。",
        "币种 CNY 由 A 股代码推定；源时间无时区，按 Asia/Shanghai 解释，非源字段声明。",
        "未核实交易时段、最新交易日或停牌，完整时间不等于已验证实时。"])
    with urllib.request.urlopen(url, timeout=10) as response:
        body = response.read(65537)
    result["fetched_at"] = _now()
    if len(body) > 65536:
        raise ValueError("oversized single-symbol response")
    match = re.fullmatch(r'\s*v_' + re.escape(local) + r'="([^"]*)";?\s*', body.decode("gb18030"))
    fields = match.group(1).split("~") if match else []
    # Confirmed with a public source response on 2026-10-03: code[2], price[3], time[30].
    if len(fields) <= 30 or fields[2] != code or not re.fullmatch(r"[0-9]{14}", fields[30]):
        raise ValueError("missing or mismatched quote identity, price or full source time")
    price = _number(fields[3], positive=True)
    stamp = datetime.strptime(fields[30], "%Y%m%d%H%M%S").replace(tzinfo=ZoneInfo("Asia/Shanghai"))
    item = _snapshot(result, symbol, suffix, price, "fields[3]", stamp)
    item.update(source_quote_time=fields[30], source_quote_time_field="fields[30]")
    result.update(status="ok", raw={"symbol": local, "fields": fields}, normalized=[item], data=[item])
    return result


def quote(symbol):
    try:
        _symbol(symbol)
    except Exception as exc:
        return _error({**_result("stock_bid_ask_em", DOCS, []), "normalized": []}, exc)
    primary = _ak_quote(symbol)
    if primary["status"] == "ok" and primary["normalized"][0]["quote_time"] is not None:
        return primary
    try:
        fallback = _tencent_quote(symbol)
        fallback["fallback_reason"] = ("primary_quote_time_missing" if primary["status"] == "ok"
                                       else "primary_failed_or_empty")
        if "error" in primary:
            fallback["fallback_errors"] = [{"api": "stock_bid_ask_em", **primary["error"]}]
        return fallback
    except Exception as exc:
        primary["fallback_errors"] = [{"api": "tencent_quote", **_failure(exc)}]
        if primary["status"] == "ok":
            primary["limitations"].append("腾讯补查失败，保留无报价时间的东方财富价格作为未验证参考。")
            return primary
        if "error" in primary:
            primary["fallback_errors"].insert(0, {"api": "stock_bid_ask_em", **primary["error"]})
        return _error(primary, exc)


def _daily_rows(raw, symbol, start, end, adjust, sina):
    mapping = {key: key for key in ("date", "open", "high", "low", "close", "volume", "amount")}
    if not sina:
        mapping.update(zip(mapping, ("日期", "开盘", "最高", "最低", "收盘", "成交量", "成交额")))
    if raw["records"] and not set(mapping.values()).issubset(raw["columns"]):
        raise ValueError("daily table is missing date/OHLC/volume/amount columns")
    rows = []
    for record in raw["records"]:
        day = _source_date(record[mapping["date"]])
        if not start <= day <= end:
            continue
        row = {key: record[source] for key, source in mapping.items()}
        for key in ("open", "high", "low", "close"):
            row[key] = _number(row[key], positive=adjust == "none")
        row.update(symbol=symbol, date=day.isoformat(), currency="CNY", adjust=adjust,
                   volume_unit="share" if sina else "lot_100_shares", amount_unit="CNY")
        rows.append(row)
    return sorted(rows, key=lambda row: row["date"])


def daily(symbol, start, end, adjust="none"):
    result = _result("stock_zh_a_hist", DOCS, [
        "日线仅作历史参考；请求日期包含 end，仍需核查交易日及当日是否已收盘。",
        "复权直接使用源站 none/qfq/hfq；前复权历史可变化或为负，跨源复权值未校准。",
        "不自动补停牌日、节假日或缺失数据；CNY 按 A 股市场惯例标注。"])
    try:
        code, _, local = _symbol(symbol)
        begin, finish = _date(start), _date(end)
        if begin > finish or adjust not in {"none", "qfq", "hfq"}:
            raise ValueError("start must not exceed end; adjust must be none/qfq/hfq")
        ak = importlib.import_module("akshare")
        result["source_url"] = f"https://quote.eastmoney.com/{local}.html"
        errors = []
        for sina in (False, True):
            try:
                if sina:
                    result.update(source_api="stock_zh_a_daily",
                                  source_url=f"https://finance.sina.com.cn/realstock/company/{local}/nc.shtml")
                    frame = ak.stock_zh_a_daily(symbol=local, start_date=start, end_date=end,
                                               adjust="" if adjust == "none" else adjust)
                else:
                    frame = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start,
                                              end_date=end, adjust="" if adjust == "none" else adjust,
                                              timeout=15)
                raw = _frame(frame)
                result["raw"] = raw
                rows = _daily_rows(raw, symbol, begin, finish, adjust, sina)
                result.update(status="ok" if rows else "no_data", data=rows, fetched_at=_now(),
                              adjust=adjust, volume_unit="share" if sina else "lot_100_shares",
                              amount_unit="CNY")
                if errors:
                    result["fallback_errors"] = errors
                    result["limitations"].append("主源失败后仅调用一次新浪后备；原始成交量单位为股。")
                    if not rows:
                        raise ValueError("primary source failed and fallback yielded no usable rows")
                return result
            except Exception as exc:
                errors.append({"api": result["source_api"], **_failure(exc)})
                if sina:
                    result["fallback_errors"] = errors
                    raise
    except Exception as exc:
        return _error(result, exc)


def financials(symbol, statement, period=None, frequency="quarterly"):
    result = _result("stock_financial_report_sina", DOCS, [
        "新浪财报为转录数据，应与公司正式披露核对；原字段和可用公告信息保留。",
        "quarterly 表示各季度报告期，利润表/现金流为年初至报告期累计；不等于单季值。",
        "annual 只保留 12 月 31 日；资产负债表为期末余额，不累加或自动计算 TTM。",
        "公告日期缺失保持 null；更新日期不是公告日期，AKShare 的更新日期可能无时区。",
        "未核实原始金额单位，不自动缩放；保留源币种与类型，不填默认财报币种。"])
    try:
        code, _, local = _symbol(symbol)
        if statement not in STATEMENTS or frequency not in {"annual", "quarterly"}:
            raise ValueError("invalid statement or frequency")
        target = _date(period) if period is not None else None
        if target and (target.strftime("%m%d") not in {"0331", "0630", "0930", "1231"}
                       or (frequency == "annual" and target.strftime("%m%d") != "1231")):
            raise ValueError("period must match the requested reporting frequency")
        result["source_url"] = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/{code}.phtml"
        raw = _frame(importlib.import_module("akshare").stock_financial_report_sina(
            stock=local, symbol=STATEMENTS[statement]))
        result.update(raw=raw, fetched_at=_now())
        if raw["records"] and "报告日" not in raw["columns"]:
            raise ValueError("financial table is missing 报告日")
        selected = []
        for row in raw["records"]:
            day = _source_date(row["报告日"])
            if target is not None and day != target:
                continue
            if day.strftime("%m%d") not in ({"1231"} if frequency == "annual" else {"0331", "0630", "0930", "1231"}):
                continue
            selected.append((day, row))
        selected.sort(key=lambda pair: pair[0], reverse=True)
        if target is None:
            selected = selected[:8]
        result["raw"]["records"] = [row for _, row in selected]
        result.update(statement=statement, frequency=frequency,
                      basis="point_in_time" if statement == "balancesheet" else "year_to_date")
        result["data"] = [{"symbol": symbol, "report_period": day.strftime("%Y%m%d"),
                           "announcement_date": row.get("公告日期"), "currency": row.get("币种"),
                           "statement": statement, "frequency": frequency, "basis": result["basis"],
                           "fields": row} for day, row in selected]
        result["status"] = "ok" if selected else "no_data"
    except Exception as exc:
        return _error(result, exc)
    return result
