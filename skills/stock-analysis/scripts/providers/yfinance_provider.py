"""Keyless Yahoo adapter. Optional yfinance is imported only when fetching.

API contracts checked 2026-10-03 against ranaroussi.github.io/yfinance and
github.com/ranaroussi/yfinance/blob/main/yfinance/{base,scrapers/history}.py.
The calling CLI owns the overall process timeout and output handling.
"""
from datetime import date, datetime, timedelta, timezone
import math
import re
from zoneinfo import ZoneInfo

TIMEOUT = 15
META_FIELDS = ("symbol", "currency", "exchangeName", "fullExchangeName",
               "exchangeTimezoneName", "regularMarketPrice", "regularMarketTime",
               "instrumentType", "dataGranularity")
BASE_LIMITS = ["Yahoo/yfinance 为第三方数据；免 API key 不代表实时、完整或无限调用。"]


class _InvalidInput(ValueError):
    pass


def _clean(value):
    if value is None or type(value).__name__ in ("NAType", "NaTType"):
        return None
    if isinstance(value, dict):
        return {str(_clean(k)): _clean(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_clean(v) for v in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (str, int, bool)):
        return value
    if hasattr(value, "item"):
        return _clean(value.item())
    return str(value)


def _number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        n = float(value)
        return n if math.isfinite(n) else None
    except (TypeError, ValueError):
        return None


def _symbol(symbol):
    if not isinstance(symbol, str):
        raise _InvalidInput("symbol 必须为港股或美股代码。")
    text = symbol.strip().upper()
    if re.fullmatch(r"\d{1,5}\.HK", text):
        code = int(text[:-3])
        if code == 0:
            raise _InvalidInput("港股代码不能为零。")
        return f"{code:05d}.HK", f"{code:04d}.HK", "HK"
    if re.fullmatch(r"[A-Z][A-Z0-9-]{0,14}", text):
        return text, text, "US"
    raise _InvalidInput("仅接受港股代码（如 00700.HK）或美股 Yahoo 代码（如 AAPL）。")


def _day(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{8}", value):
        raise _InvalidInput("日期必须为 YYYYMMDD。")
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except ValueError as exc:
        raise _InvalidInput("日期不存在。") from exc


def _base(symbol):
    return {"status": "unknown", "provider": "yfinance", "symbol": _clean(symbol),
            "source_url": None, "fetched_at": None, "limitations": list(BASE_LIMITS),
            "raw": {}, "data": []}


def _prepare(out, symbol, section):
    canonical, yahoo, market = _symbol(symbol)
    out.update(symbol=canonical, yahoo_symbol=yahoo, market=market,
               source_url=f"https://finance.yahoo.com/quote/{yahoo}/{section}")
    import yfinance  # Optional dependency; no installation or key discovery.
    return yfinance.Ticker(yahoo)


def _done(out, status):
    out.update(status=status, fetched_at=datetime.now(timezone.utc).isoformat())
    return _clean(out)


def _failed(out, exc):
    status = ("invalid_input" if isinstance(exc, _InvalidInput) else
              "dependency_missing" if isinstance(exc, ImportError) else "provider_error")
    out["error_type"] = type(exc).__name__
    out["message"] = (str(exc) if isinstance(exc, _InvalidInput) else
                      "yfinance 请求或依赖失败；未自动重试，未回显可能含会话信息的异常。")
    return _done(out, status)


def _rows(frame):
    if frame is None:
        return []
    return [{"index": _clean(label), "values": _clean(dict(row.items()))}
            for label, row in frame.iterrows()]


def _metadata(ticker):
    meta = ticker.get_history_metadata()
    # New yfinance metadata is lazy: enumerating all keys can cause another fetch.
    return {key: _clean(meta.get(key)) for key in META_FIELDS}


def _bars(rows, first=None, last=None):
    bars, skipped = [], 0
    for row in rows:
        values = {str(k).lower(): v for k, v in row["values"].items()}
        try:
            day = date.fromisoformat(str(values.get("date", row["index"]))[:10])
        except (ValueError, TypeError):
            skipped += 1
            continue
        if (first and day < first) or (last and day > last):
            continue
        bar = {k: _number(values.get(k)) for k in ("open", "high", "low", "close", "volume")}
        bad_price = any(bar[k] is None or bar[k] <= 0 for k in ("open", "high", "low", "close"))
        bad_volume = values.get("volume") is not None and (bar["volume"] is None or bar["volume"] < 0)
        if bad_price or bad_volume:
            skipped += 1
            continue
        bar.update(date=day.isoformat(), adj_close=_number(values.get("adj close")), bar_complete=None)
        bars.append(bar)
    return sorted(bars, key=lambda row: row["date"]), skipped


def _sina_fallback(out, cause, first=None, last=None):
    """One independent historical-source attempt; never retry Yahoo or infer realtime."""
    if isinstance(cause, _InvalidInput) or "market" not in out:
        return _failed(out, cause)
    out.update(requested_provider="yfinance", source_changed=True,
               fallback_errors=[{"provider": "yfinance", "error_type": type(cause).__name__}])
    try:
        import akshare
        hk = out["market"] == "HK"
        symbol = out["symbol"][:-3] if hk else out["yahoo_symbol"]
        # Sina share-class spelling has not been verified; do not guess mappings.
        if not hk and not re.fullmatch(r"[A-Z0-9]+", symbol):
            raise ValueError("新浪后备不支持未核实的美股特殊代码映射。")
        method = "stock_hk_daily" if hk else "stock_us_daily"
        frame = getattr(akshare, method)(symbol=symbol, adjust="")
        rows = _rows(frame)
        bars, skipped = _bars(rows, first, last)
        out.update(provider="akshare", upstream="sina", currency=None, timezone=None,
                   source_url=(f"https://finance.sina.com.cn/stock/hkstock/{symbol}/klc2_kl.js" if hk
                               else f"https://finance.sina.com.cn/staticdata/us/{symbol}"))
        # Sina may return decades even for a single quote. Retain only the raw
        # rows needed to audit this request, not an unrelated full-market history.
        retained_days = {bar["date"] for bar in (bars if first is not None else bars[-5:])}
        retained_rows = [row for row in rows if str(
            {str(k).lower(): v for k, v in row["values"].items()}.get("date", row["index"])
        )[:10] in retained_days]
        out["raw"] = {"primary": out["raw"], "rows": retained_rows,
                      "scope": "requested_date_range" if first is not None else "latest_five_available_bars"}
        out["limitations"].extend([
            "Yahoo 读取失败；仅尝试一次 AKShare 新浪历史后备，未重试或绕过 Yahoo 限制。",
            "新浪 adjust='' 为该源未复权日线；币种、时区、成交量单位及精确成交时间未提供。",
            "最新有效交易日与末根完整性未经独立核验；收盘值仅供历史研究，不是实时成交报价。",
        ])
        if skipped:
            out["limitations"].append(f"后备源 {skipped} 行日期、OHLC 或成交量无效，已跳过。")
        if first is not None:
            out.update(data=bars, start=first.strftime("%Y%m%d"), end=last.strftime("%Y%m%d"),
                       end_inclusive=True, adjustment="none", interval="1d")
        elif bars:
            latest = bars[-1]
            out["normalized"] = [{"symbol": out["symbol"], "exchange": None, "currency": None,
                "price": latest["close"], "price_type": "close", "quote_time": None,
                "timezone": None, "trade_date": latest["date"], "fetched_at": None,
                "source_url": out["source_url"], "source_tool": "akshare." + method,
                "declared_delay_minutes": None, "freshness": "eod", "source_realtime_verified": False,
                "latest_session_verified": None, "market_state": "unknown", "adjustment": "none",
                "acceptable_for_task": None, "source_changed": True}]
            out["data"] = out["normalized"]
        out = _done(out, "partial" if bars or skipped else "no_data")
        for row in out.get("normalized", []):
            row["fetched_at"] = out["fetched_at"]
        if "normalized" in out:
            out["data"] = out["normalized"]
        return out
    except Exception as exc:
        out["fallback_errors"].append({"provider": "akshare", "upstream": "sina",
                                       "error_type": type(exc).__name__})
        out["limitations"].append("Yahoo 与一次新浪历史后备均未得到可用结果；没有行情或实时性保证。")
        return _failed(out, exc)


def quote(symbol):
    """Normalize a source-timed regular-session quote, never an inferred close."""
    out = _base(symbol)
    out["normalized"] = []
    try:
        ticker = _prepare(out, symbol, "")
        frame = ticker.history(period="5d", auto_adjust=False, timeout=TIMEOUT)
        out["raw"]["history"] = _rows(frame)
        meta = _metadata(ticker)
        out["raw"]["metadata"] = meta
        price, epoch = _number(meta.get("regularMarketPrice")), _number(meta.get("regularMarketTime"))
        currency, exchange, tz = (meta.get(k) for k in
                                  ("currency", "exchangeName", "exchangeTimezoneName"))
        try:
            stamp = datetime.fromtimestamp(epoch, timezone.utc).astimezone(ZoneInfo(tz)) if epoch and epoch > 0 else None
        except (ValueError, TypeError, OverflowError, OSError, KeyError):
            stamp = None
        identity_ok = meta.get("symbol") in (None, out["yahoo_symbol"])
        labels_ok = all(isinstance(v, str) and v.strip() for v in (currency, exchange))
        if not (price and price > 0 and stamp and labels_ok and identity_ok):
            out["limitations"].append("来源价格、时间、时区、币种、交易所或标的证据不完整；未生成可用报价。")
            return _done(out, "partial" if price or out["raw"]["history"] else "no_data")
        hk = out["market"] == "HK"
        out["limitations"].extend([
            "regularMarketPrice 是常规时段最近成交价，不保证为官方收盘价。",
            "报价年龄、最新有效交易日和停牌状态须另行校验；抓取成功不证明实时。",
            "港股源说明为延迟 15 分钟，实际报价仍可能更旧。" if hk else "美股具体延迟未核实，不保证实时。",
        ])
        out = _done(out, "ok")
        out["normalized"] = [{"symbol": out["symbol"], "exchange": exchange,
            "currency": currency, "price": price, "price_type": "last_trade",
            "quote_time": stamp.isoformat(), "timezone": tz, "trade_date": stamp.date().isoformat(),
            "fetched_at": out["fetched_at"], "source_url": out["source_url"],
            "source_tool": "yfinance.Ticker.history/get_history_metadata",
            "declared_delay_minutes": 15 if hk else None, "freshness": "unknown",
            "source_realtime_verified": False, "latest_session_verified": None,
            "market_state": "unknown", "adjustment": "none", "acceptable_for_task": None}]
        out["data"] = out["normalized"]
        return out
    except Exception as exc:
        return _sina_fallback(out, exc)


def daily(symbol, start, end, adjust="none"):
    """Daily Yahoo OHLCV; requested end date is inclusive."""
    out = _base(symbol)
    try:
        first, last = _day(start), _day(end)
        if first > last:
            raise _InvalidInput("start 不能晚于 end。")
        if adjust != "none":
            raise _InvalidInput("此适配器仅支持 adjust=none；Yahoo adjusted 口径不等于 A 股 qfq/hfq。")
        ticker = _prepare(out, symbol, "history/")
        frame = ticker.history(start=first.isoformat(), end=(last + timedelta(days=1)).isoformat(),
                               interval="1d", auto_adjust=False, actions=False, timeout=TIMEOUT)
        rows = _rows(frame)
        out["raw"]["rows"] = rows
        try:
            out["raw"]["metadata"] = _metadata(ticker)
        except Exception:
            out["raw"]["metadata"] = {}
            out["limitations"].append("源日线元数据读取失败；有效历史记录仍保留。")
        meta = out["raw"]["metadata"]
        for target, source in (("currency", "currency"), ("timezone", "exchangeTimezoneName")):
            value = meta.get(source)
            out[target] = value if isinstance(value, str) and value.strip() else None
        if out["currency"] is None or out["timezone"] is None:
            out["limitations"].append("源币种或时区未知，未按代码、市场或报告币种推定。")
        out["data"], skipped = _bars(rows, first, last)
        out.update(start=start, end=end, end_inclusive=True, adjustment="none", interval="1d")
        out["limitations"].extend([
            "auto_adjust=False 保留 Yahoo OHLC；Adj Close 单列，未映射为 A 股前/后复权。",
            "日线日期不是精确报价时间；最新一根是否完整、币种及交易日历须另核实。",
        ])
        if skipped:
            out["limitations"].append(f"{skipped} 行 OHLC 非正或无效、或成交量无效，未纳入数据。")
        return _done(out, "partial" if skipped else "ok" if out["data"] else "no_data")
    except Exception as exc:
        return _sina_fallback(out, exc, locals().get("first"), locals().get("last"))


def financials(symbol, statement, period=None, frequency="annual"):
    """Return statement records by report end date, without inventing publication dates."""
    out = _base(symbol)
    try:
        methods = {"income": ("get_income_stmt", "financials/"),
                   "balancesheet": ("get_balance_sheet", "balance-sheet/"),
                   "cashflow": ("get_cash_flow", "cash-flow/")}
        if statement not in methods or frequency not in ("annual", "quarterly"):
            raise _InvalidInput("statement 必须为 income/balancesheet/cashflow；frequency 必须为 annual/quarterly。")
        wanted = _day(period) if period is not None else None
        method, section = methods[statement]
        ticker = _prepare(out, symbol, section)
        frame = getattr(ticker, method)(as_dict=False, pretty=False,
                                      freq="yearly" if frequency == "annual" else "quarterly")
        out["raw"]["rows"] = _rows(frame)
        for row in _rows(frame.T if frame is not None else None):
            report_day = date.fromisoformat(str(row["index"])[:10])
            if wanted is not None and wanted != report_day:
                continue
            if not any(value is not None for value in row["values"].values()):
                continue
            out["data"].append({"report_period": report_day.isoformat(),
                "period": report_day.strftime("%Y%m%d"), "published_at": None,
                "statement": statement, "frequency": frequency, "currency": None,
                "unit": None, "period_basis": "yahoo_" + frequency,
                "items": row["values"]})
        out["data"].sort(key=lambda row: row["report_period"], reverse=True)
        out.update(statement=statement, period=period, frequency=frequency)
        out["limitations"].extend([
            "列日期是报告期末，公告/披露日期未提供；不能用于判断历史时点何时已公开。",
            "财报币种与单位证据不足；金额、股数、每股值可能混合，不采用交易币种补填。",
            "annual/quarterly 保留 Yahoo 返回口径；季度不视作 TTM 或累计，不推算缺失期间。",
            "Yahoo 财务摘要应回到公司/交易所报表核验完整性、会计口径及更正。",
        ])
        return _done(out, "ok" if out["data"] else "no_data")
    except Exception as exc:
        return _failed(out, exc)
