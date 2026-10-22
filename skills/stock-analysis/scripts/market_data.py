#!/usr/bin/env python3
"""Read-only Tushare adapter. Standard library only; credentials never go in argv."""
import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

ENDPOINT = "https://api.tushare.pro"
TIMEOUT = 20
MAX_BYTES = 8 * 1024 * 1024
DOCS = {"rt_k": 372, "rt_hk_k": 383, "daily": 27, "hk_daily": 192,
        "us_daily": 254, "income": 33, "balancesheet": 36, "cashflow": 44, "trade_cal": 26}
META = "ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,end_type"
FIELDS = {
    "rt_k": "ts_code,name,pre_close,open,high,low,close,vol,amount,num,trade_time,ask_price1,ask_volume1,bid_price1,bid_volume1",
    "rt_hk_k": "ts_code,pre_close,open,high,low,close,vol,amount",
    "daily": "ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount",
    "hk_daily": "ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount",
    "us_daily": "ts_code,trade_date,open,high,low,close,pre_close,change,pct_change,vol,amount",
    "income": META + ",revenue,total_revenue,oper_cost,operate_profit,n_income,n_income_attr_p,basic_eps,update_flag",
    "balancesheet": META + ",total_share,money_cap,accounts_receiv,inventories,total_assets,st_borr,lt_borr,bond_payable,non_cur_liab_due_1y,total_liab,total_hldr_eqy_exc_min_int,update_flag",
    "cashflow": META + ",net_profit,n_cashflow_act,c_pay_acq_const_fiolta,n_cashflow_inv_act,n_cash_flows_fnc_act,c_cash_equ_end_period,update_flag",
    "trade_cal": "exchange,cal_date,is_open,pretrade_date",
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


# A single injectable call, with redirects disabled so credentials stay on the allowlisted host.
urlopen = urllib.request.build_opener(NoRedirect()).open


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError("Invalid command or arguments; use --help. Never pass tokens in command arguments.")


def parser():
    p = Parser(description=__doc__)
    p.add_argument("--credentials-file", help="Explicit local JSON containing tushare_token; environment takes priority")
    subs = p.add_subparsers(dest="command", required=True)
    for command in ("doctor", "quote", "daily", "financials", "calendar"):
        q = subs.add_parser(command)
        q.add_argument("--credentials-file", default=argparse.SUPPRESS)
        if command in ("quote", "daily", "financials"):
            q.add_argument("--symbol", required=True)
        if command in ("quote", "daily"):
            q.add_argument("--market", choices=("CN", "HK") if command == "quote" else ("CN", "HK", "US"),
                           help="If omitted, infer CN/HK suffix or US symbol")
        if command in ("daily", "calendar"):
            q.add_argument("--start", required=True)
            q.add_argument("--end", required=True)
        if command == "financials":
            q.add_argument("--statement", required=True, choices=("income", "balancesheet", "cashflow"))
            q.add_argument("--period", required=True)
        if command == "calendar":
            q.add_argument("--exchange", choices=("SSE", "SZSE"), default="SSE",
                           help="Requires Tushare trade_cal permission (official documentation: 2000 points)")
    return p


def valid_date(value):
    if not re.fullmatch(r"[0-9]{8}", value):
        raise ValueError("Dates must be YYYYMMDD.")
    try:
        return dt.datetime.strptime(value, "%Y%m%d").date()
    except ValueError:
        raise ValueError("Invalid calendar date.") from None


def market_symbol(symbol, requested=None):
    market = requested or ("HK" if symbol.endswith(".HK") else
                           "CN" if symbol.endswith((".SH", ".SZ", ".BJ")) else "US")
    patterns = {"CN": r"(?:6[0-9]{5}\.SH|[03][0-9]{5}\.SZ|[489][0-9]{5}\.BJ)",
                "HK": r"[0-9]{5}\.HK", "US": r"[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,4})?"}
    if not re.fullmatch(patterns[market], symbol):
        raise ValueError("Symbol format does not match the selected stock market.")
    return market


def plan(args):
    if args.command == "calendar":
        api, params, market = "trade_cal", {"exchange": args.exchange}, None
    else:
        market = market_symbol(args.symbol, "CN" if args.command == "financials" else args.market)
        params = {"ts_code": args.symbol}
        if args.command == "quote":
            if market not in ("CN", "HK"):
                raise ValueError("Realtime quotes support CN and HK only.")
            api = "rt_k" if market == "CN" else "rt_hk_k"
        elif args.command == "daily":
            api = {"CN": "daily", "HK": "hk_daily", "US": "us_daily"}[market]
        else:
            valid_date(args.period)
            if args.period[4:] not in ("0331", "0630", "0930", "1231"):
                raise ValueError("CN report period must be a calendar quarter end.")
            api = args.statement
            params.update(period=args.period, report_type="1")
    if args.command in ("daily", "calendar"):
        if valid_date(args.start) > valid_date(args.end):
            raise ValueError("Start date must not be after end date.")
        params.update(start_date=args.start, end_date=args.end)
    return api, params, market


def load_token(path):
    token = os.environ.get("TUSHARE_TOKEN", "").strip()
    if token or not path:
        return token
    try:
        with open(path, encoding="utf-8") as handle:
            content = handle.read(65537)
        if len(content) > 65536:
            raise ValueError()
        data = json.loads(content)
        token = data.get("tushare_token") if isinstance(data, dict) else None
        if not isinstance(token, str) or not token.strip():
            raise ValueError()
        return token.strip()
    except (OSError, ValueError):
        raise ValueError("Credentials file must be readable JSON with a non-empty tushare_token string.") from None


def redact(value, token):
    if isinstance(value, str):
        return value.replace(token, "[REDACTED]") if token else value
    if isinstance(value, dict):
        return {redact(k, token): redact(v, token) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v, token) for v in value]
    return value


def quote_time(value, timezone):
    if not isinstance(value, str):
        return None
    try:
        if re.fullmatch(r"[0-9]{14}", value):
            parsed = dt.datetime.strptime(value, "%Y%m%d%H%M%S")
        elif re.fullmatch(r"[0-9]{8} [0-9]{2}:[0-9]{2}:[0-9]{2}", value):
            parsed = dt.datetime.strptime(value, "%Y%m%d %H:%M:%S")
        elif re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})?", value):
            parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            return None
        zone = ZoneInfo(timezone)
        return (parsed.replace(tzinfo=zone) if parsed.tzinfo is None else parsed.astimezone(zone)).isoformat()
    except (ValueError, KeyError):
        return None


def normalize_quote(row, market, source_url, fetched_at, source_realtime_verified):
    symbol = row.get("ts_code")
    zone = "Asia/Shanghai" if market == "CN" else "Asia/Hong_Kong"
    raw_time = row.get("trade_time") if market == "CN" else None
    parsed_time = quote_time(raw_time, zone)
    time_basis = ("source_explicit_offset" if re.search(r"(?:Z|[+-][0-9]{2}:[0-9]{2})$", raw_time)
                  else "market_convention_assumed") if parsed_time else "unverified"
    exchange = {"SH": "SSE", "SZ": "SZSE", "BJ": "BSE", "HK": "HKEX"}.get(
        symbol.rsplit(".", 1)[-1]) if isinstance(symbol, str) else None
    return {"symbol": symbol, "exchange": exchange, "currency": "CNY" if market == "CN" else None,
            "price": row.get("close"), "price_type": "last_trade" if market == "CN" else "other",
            "source_price_field": "close", "source_price_label": "最新价" if market == "CN" else "收盘价",
            "quote_time_raw": raw_time, "quote_time": parsed_time, "timezone": zone,
            "quote_time_timezone_basis": time_basis,
            "trade_date": dt.datetime.fromisoformat(parsed_time).date().isoformat() if parsed_time else None,
            "fetched_at": fetched_at, "source_realtime_verified": source_realtime_verified,
            "latest_session_verified": None, "market_state": "unknown", "freshness": "unknown", "source_url": source_url}


def finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Non-finite JSON number.")
    return number


def query(api, params, market, token):
    if api not in DOCS:
        return {"status": "invalid_input", "message": "API is not allowlisted."}
    source_url = "https://tushare.pro/document/2?doc_id=" + str(DOCS[api])
    result = {"status": "unknown", "source_api": api, "source_url": source_url,
              "endpoint": ENDPOINT, "fetched_at": None, "limitations": []}
    if not token:
        return dict(result, status="missing_token", message="Provide TUSHARE_TOKEN or --credentials-file.")
    limits = result["limitations"]
    if api in ("rt_k", "rt_hk_k"):
        limits.append("Requires separate realtime product permission; API success does not establish market state or current freshness. CN rt_k close maps to last_trade because its documented meaning is latest price; source field/label are retained. This does not apply to historical daily close.")
        limits.append("Only a complete source datetime is parsed; never infer today's date from a time-only field.")
        if market == "CN":
            limits.append("A naive complete trade_time is interpreted as Asia/Shanghai by CN market convention; the source schema does not separately declare its timezone. This is an explicit assumption.")
        if market == "HK":
            limits.append("Official rt_hk_k schema has no quote timestamp or currency; both remain unverified, including the trading counter currency.")
    elif api in ("daily", "hk_daily", "us_daily"):
        limits.append("End-of-day historical data; inspect trade_date. No intraday freshness is claimed. HK/US require separate permissions.")
        result["freshness"] = "eod"
        if api == "daily":
            limits.append("Unadjusted; daily volume is lots and amount is CNY thousands, unlike rt_k shares/CNY. Daily data normally enters storage at 15:00-16:00; halted days may be absent.")
    else:
        limits.append("Official documentation requires at least 2000 points. Calendar excludes individual suspensions; financials use report_type=1 and retain publication dates and update flags.")
    body = json.dumps({"api_name": api, "token": token, "params": params, "fields": FIELDS[api]}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            raw = response.read(MAX_BYTES + 1)
        result["fetched_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        if len(raw) > MAX_BYTES:
            raise ValueError("Response exceeded size limit.")
        payload = json.loads(raw, parse_float=finite_float, parse_constant=finite_float)
        if not isinstance(payload, dict) or type(payload.get("code")) is not int:
            raise ValueError("Response API status code must be an integer, not a boolean or other type.")
        if payload["code"] != 0:
            return redact(dict(result, status="api_error", api_code=payload["code"], message=str(payload.get("msg", "API failure"))[:500]), token)
        data = payload.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("fields"), list) or not isinstance(data.get("items"), list):
            raise ValueError("Success response lacks tabular data.")
        fields, items = data["fields"], data["items"]
        if not all(isinstance(f, str) for f in fields) or len(set(fields)) != len(fields):
            raise ValueError("Invalid or duplicate field names.")
        if any(not isinstance(row, list) or len(row) != len(fields) for row in items) or (items and not fields):
            raise ValueError("Response row/field lengths do not match.")
        result.update(status="ok" if items else "no_data", raw={"fields": fields, "items": items})
        if api in ("rt_k", "rt_hk_k"):
            rows = [dict(zip(fields, row)) for row in items]
            if any(not isinstance(row.get("ts_code"), str) or not row["ts_code"] for row in rows):
                raise ValueError("Quote response is missing a usable ts_code.")
            if any(row["ts_code"] != params["ts_code"] for row in rows):
                raise ValueError("Quote response contains an unexpected symbol.")
            if any(isinstance(row.get("close"), bool) or not isinstance(row.get("close"), (int, float)) or
                   row["close"] <= 0 for row in rows):
                raise ValueError("Quote close must be present and a finite positive number, not a boolean.")
            result["source_realtime_verified"] = bool(items) and api == "rt_k"
            result["normalized"] = [normalize_quote(row, market, source_url, result["fetched_at"],
                                                   result["source_realtime_verified"]) for row in rows]
            if any(row["quote_time"] is None for row in result["normalized"]):
                limits.append("Source quote time is absent or not a complete parseable datetime; fetched_at must not replace it.")
        return redact(result, token)
    except urllib.error.HTTPError as exc:
        return dict(result, status="http_error", http_status=exc.code, message="HTTPS request failed; no retry performed.")
    except (urllib.error.URLError, TimeoutError, OSError):
        return dict(result, status="network_error", message="HTTPS transport failed; no retry performed.")
    except (ValueError, TypeError, UnicodeError) as exc:
        return redact(dict(result, status="protocol_error", message=str(exc)), token)


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        request = None if args.command == "doctor" else plan(args)
    except ValueError as exc:
        print(json.dumps({"status": "invalid_input", "message": str(exc)}))
        return 2
    try:
        token = load_token(args.credentials_file)
    except ValueError as exc:
        print(json.dumps({"status": "credentials_error", "message": str(exc)}))
        return 2
    result = ({"status": "ok", "token_present": bool(token), "endpoint": ENDPOINT}
              if args.command == "doctor" else query(*request, token))
    print(json.dumps(redact(result, token), ensure_ascii=False, allow_nan=False))
    return 0 if result["status"] in ("ok", "no_data") else 1


if __name__ == "__main__":
    sys.exit(main())
