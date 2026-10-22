#!/usr/bin/env python3
"""Classify supplied quote metadata; never fetch quotes, trade, or write files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation


NOTICE = (
    "Checks supplied metadata only; does not independently verify source access, "
    "real-time entitlements, exchange calendars, market status, or latest sessions. "
    "No network access, orders, or file writes."
)
ENUMS = {
    "price_type": {"last_trade", "close", "bid", "ask", "other"},
    "freshness": {"verified_realtime", "delayed", "eod", "unknown"},
    "market_state": {"regular", "auction", "break", "extended", "closed", "halted", "unknown"},
}
REQUIRED = {
    "symbol", "exchange", "currency", "price", "quote_time", "trade_date", "fetched_at",
    "source_realtime_verified", "latest_session_verified", *ENUMS,
}
ACTIVE = {"regular", "auction", "extended"}
REALTIME_PRICE_TYPES = {"last_trade", "bid", "ask"}


class InputError(ValueError):
    pass


def _timestamp(value: object, name: str) -> datetime:
    if not isinstance(value, str):
        raise InputError(f"{name} must be a timezone-aware ISO8601 string")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise InputError(f"{name} must be a timezone-aware ISO8601 string") from None
    if result.tzinfo is None or result.utcoffset() is None:
        raise InputError(f"{name} requires an explicit timezone")
    return result


def check_quote(snapshot: dict, *, now: str, max_age_seconds: int) -> dict:
    """Return an assessment without filling missing quote times from fetch times."""
    if type(max_age_seconds) is not int or max_age_seconds <= 0:
        raise InputError("max_age_seconds must be a positive integer")
    checked_at = _timestamp(now, "now")
    if not isinstance(snapshot, dict):
        raise InputError("input must be a JSON object")
    missing = REQUIRED - snapshot.keys()
    if missing:
        raise InputError("missing fields: " + ", ".join(sorted(missing)))
    for name in ("symbol", "exchange", "currency"):
        if not isinstance(snapshot[name], str) or not snapshot[name].strip():
            raise InputError(f"{name} must be a nonempty string")
    for name, choices in ENUMS.items():
        if not isinstance(snapshot[name], str) or snapshot[name] not in choices:
            raise InputError(f"{name} must be one of: " + ", ".join(sorted(choices)))
    for name in ("source_realtime_verified", "latest_session_verified"):
        if name == "latest_session_verified" and snapshot[name] is None:
            continue
        if type(snapshot[name]) is not bool:
            raise InputError(f"{name} must be a boolean" + (" or null" if name.startswith("latest") else ""))
    source = {key: snapshot[key] for key in ("source_url", "source_tool")
              if isinstance(snapshot.get(key), str) and snapshot[key].strip()}
    if not source:
        raise InputError("a nonempty source_url or source_tool identifier is required")
    try:
        price = Decimal(str(snapshot["price"]))
    except (InvalidOperation, ValueError):
        raise InputError("price must be a finite positive number") from None
    if isinstance(snapshot["price"], bool) or not price.is_finite() or price <= 0:
        raise InputError("price must be a finite positive number")
    quote_time = None if snapshot["quote_time"] is None else _timestamp(snapshot["quote_time"], "quote_time")
    fetched_at = _timestamp(snapshot["fetched_at"], "fetched_at")
    trade_date = snapshot["trade_date"]
    if trade_date is not None:
        try:
            if not isinstance(trade_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", trade_date):
                raise ValueError
            parsed_date = date.fromisoformat(trade_date)
        except ValueError:
            raise InputError("trade_date must be YYYY-MM-DD or null") from None

    age = (checked_at - quote_time).total_seconds() if quote_time is not None else None
    invalid = []
    if trade_date is not None and parsed_date > checked_at.astimezone(timezone(timedelta(hours=14))).date():
        invalid.append("trade_date_is_in_the_future_in_all_market_timezones")
    if fetched_at > checked_at:
        invalid.append("fetched_at_is_in_the_future")
    if age is not None and age < 0:
        invalid.append("quote_time_is_in_the_future")
    if quote_time is not None and fetched_at < quote_time:
        invalid.append("fetched_at_precedes_quote_time")
    reasons = list(invalid)
    if quote_time is None:
        reasons.append("quote_time_missing; fetched_at_is_not_a_quote_timestamp")
    if trade_date is None and quote_time is None:
        reasons.append("no_quote_timestamp_or_trade_date")
    freshness, market = snapshot["freshness"], snapshot["market_state"]
    if freshness != "verified_realtime":
        reasons.append("source_freshness_" + freshness)
    if not snapshot["source_realtime_verified"]:
        reasons.append("source_realtime_status_not_verified")
    if market not in ACTIVE:
        reasons.append("market_state_" + market)
    if market == "closed" and snapshot["price_type"] == "close" and snapshot["latest_session_verified"] is not True:
        reasons.append("latest_session_not_verified")
    stale = age is not None and age > max_age_seconds
    if stale:
        reasons.append("quote_age_exceeds_realtime_threshold")
    if snapshot["price_type"] not in REALTIME_PRICE_TYPES:
        reasons.append("price_type_" + snapshot["price_type"] + "_not_eligible_for_realtime")

    use_class = "historical_or_unverified"
    if invalid:
        use_class = "unusable"
    elif (market == "closed" and snapshot["price_type"] == "close"
          and snapshot["latest_session_verified"] is True
          and (quote_time is not None or trade_date is not None)):
        use_class = "latest_close_reference"
        reasons.append("latest_session_close_verified; not_a_realtime_quote")
    elif stale and market in ACTIVE:
        use_class = "stale"
        reasons.append("stale_during_active_market")
    elif (freshness == "verified_realtime" and snapshot["source_realtime_verified"]
          and snapshot["price_type"] in REALTIME_PRICE_TYPES
          and market in ACTIVE and age is not None and 0 <= age <= max_age_seconds):
        use_class = "verified_realtime"
        reasons.append("supplied_metadata_meets_realtime_gate")

    return {
        **{key: snapshot[key] for key in REQUIRED if key != "price"}, **source,
        "price": str(price), "checked_at": checked_at.isoformat(),
        "max_age_seconds": max_age_seconds, "quote_age_seconds": age,
        "real_time_usable": use_class == "verified_realtime", "use_class": use_class,
        "reasons": reasons, "notice": NOTICE,
    }


class JsonParser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError(message)


def _reject_constant(value: str):
    raise InputError(f"nonfinite JSON constant is not allowed: {value}")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    if "--help" in argv or "-h" in argv:
        print(json.dumps({
            "usage": "quote_check.py --input snapshot.json --now ISO8601 --max-age-seconds INTEGER",
            "required_cli": {"--input": "JSON snapshot file to read",
                             "--now": "timezone-aware ISO8601 timestamp",
                             "--max-age-seconds": "positive integer"},
            "required_snapshot_fields": sorted(REQUIRED),
            "snapshot_schema": {
                "symbol": "nonempty string", "exchange": "nonempty string",
                "currency": "nonempty currency string", "price": "finite positive number or decimal string",
                **{key: sorted(choices) for key, choices in ENUMS.items()},
                "quote_time": "timezone-aware ISO8601 or null", "trade_date": "YYYY-MM-DD or null",
                "fetched_at": "timezone-aware ISO8601", "source_realtime_verified": "boolean",
                "latest_session_verified": "boolean or null",
                "source_url / source_tool": "at least one nonempty source URL or tool identifier",
            },
            "minimal_example": {
                "symbol": "TEST", "exchange": "EXAMPLE", "currency": "USD", "price": "10.25",
                "price_type": "last_trade", "quote_time": "2026-01-02T14:00:00Z",
                "trade_date": None, "fetched_at": "2026-01-02T14:00:05Z",
                "freshness": "verified_realtime", "source_realtime_verified": True,
                "market_state": "regular", "latest_session_verified": None,
                "source_tool": "example.quote_metadata",
            },
            "realtime_price_types": sorted(REALTIME_PRICE_TYPES), "notice": NOTICE,
        }, ensure_ascii=False, sort_keys=True, allow_nan=False))
        return 0
    parser = JsonParser(add_help=False)
    for name in ("input", "now", "max-age-seconds"):
        parser.add_argument("--" + name, required=True)
    try:
        args = parser.parse_args(argv)
        if not re.fullmatch(r"[1-9][0-9]*", args.max_age_seconds):
            raise InputError("max-age-seconds must be a positive integer")
        with open(args.input, encoding="utf-8") as handle:
            snapshot = json.load(handle, parse_float=Decimal, parse_constant=_reject_constant)
        result = check_quote(snapshot, now=args.now, max_age_seconds=int(args.max_age_seconds))
    except (InputError, OSError, UnicodeError, ValueError, OverflowError) as exc:
        print(json.dumps({"quote_age_seconds": None, "real_time_usable": False,
                          "use_class": "unusable", "reasons": ["invalid_input: " + str(exc)],
                          "notice": NOTICE}, ensure_ascii=False, allow_nan=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
