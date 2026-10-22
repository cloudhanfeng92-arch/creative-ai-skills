#!/usr/bin/env python3
"""Read-only sizing for adding ordinary shares to an unleveraged long position.

All CLI inputs are required. All money and prices use the one stated currency;
existing_value is the current market value of this same stock. Monetary JSON
values are decimal strings, never binary floats. This module performs no network,
order, or file operations. Run with --help for its explicit-input interface.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import (
    Context, Decimal, DecimalException, DivisionByZero, Inexact,
    InvalidOperation, Overflow, ROUND_HALF_EVEN, localcontext,
)


class InputError(ValueError):
    """Invalid or unsupported calculation input."""


def _decimal(name: str, value: str | Decimal | int, *, positive: bool = False) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, Decimal, int)):
        raise InputError(f"{name} must be an explicit decimal string, Decimal, or integer")
    try:
        result = Decimal(value)
    except (DecimalException, ValueError):
        raise InputError(f"{name} must be a finite decimal number") from None
    if not result.is_finite():
        raise InputError(f"{name} must be finite")
    if result < 0 or (positive and result == 0):
        raise InputError(f"{name} must be {'positive' if positive else 'nonnegative'}")
    # Bound resource use for hostile exponents while retaining ample precision.
    if len(result.as_tuple().digits) > 1000 or abs(result.as_tuple().exponent) > 1000:
        raise InputError(f"{name} exceeds supported precision (1000 digits/exponent magnitude)")
    return result


def _whole_shares(numerator: Decimal, denominator: Decimal) -> int:
    """Exact floor of a decimal ratio, without first rounding its quotient."""
    n_num, n_den = numerator.as_integer_ratio()
    d_num, d_den = denominator.as_integer_ratio()
    return (n_num * d_den) // (n_den * d_num)


def _text(value: Decimal) -> str:
    return "0" if value == 0 else str(value)


def calculate_risk_plan(
    *,
    capital: str | Decimal | int,
    available_cash: str | Decimal | int,
    existing_value: str | Decimal | int,
    max_position_pct: str | Decimal | int,
    risk_pct: str | Decimal | int,
    entry: str | Decimal | int,
    stop: str | Decimal | int,
    target: str | Decimal | int,
    lot_size: int | str,
    cost_bps: str | Decimal | int,
    currency: str,
) -> dict:
    """Return a deterministic report; no input has an implicit default.

    Fees are estimated separately on each buy/sell notional. Minimum commissions,
    taxes, slippage, and unlisted charges are excluded. Stop losses are scenarios,
    not execution guarantees. Risk calculations cover only the added shares.
    """
    raw = {
        "capital": capital, "available_cash": available_cash,
        "existing_value": existing_value, "max_position_pct": max_position_pct,
        "risk_pct": risk_pct, "entry": entry, "stop": stop, "target": target,
        "cost_bps": cost_bps,
    }
    positive = {"capital", "max_position_pct", "risk_pct", "entry", "stop", "target"}
    values = {name: _decimal(name, val, positive=name in positive) for name, val in raw.items()}
    for name in ("max_position_pct", "risk_pct"):
        if values[name] > 100:
            raise InputError(f"{name} must be greater than 0 and at most 100")
    if not values["stop"] < values["entry"] < values["target"]:
        raise InputError("prices must satisfy 0 < stop < entry < target")
    if isinstance(lot_size, bool) or not isinstance(lot_size, (str, int)):
        raise InputError("lot_size must be a positive integer")
    if not re.fullmatch(r"\+?[0-9]{1,1000}", str(lot_size)):
        raise InputError("lot_size must be a positive integer (at most 1000 digits)")
    lot = int(lot_size)
    if lot <= 0:
        raise InputError("lot_size must be a positive integer")
    if not isinstance(currency, str) or not re.fullmatch(r"[A-Za-z]{3}", currency.strip()):
        raise InputError("currency must be an explicit three-letter currency code")
    currency = currency.strip().upper()

    # These finite calculations only multiply/add decimals and powers of ten.
    # Precision accommodates input exponent spans and later quantity products.
    precision = 64 + 4 * sum(
        len(value.as_tuple().digits) + abs(value.as_tuple().exponent)
        for value in values.values()
    )
    exact_context = Context(
        prec=precision, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999,
        traps=[Inexact, DivisionByZero, InvalidOperation, Overflow],
    )
    with localcontext(exact_context):
        capital, cash, existing = values["capital"], values["available_cash"], values["existing_value"]
        entry, stop, target = values["entry"], values["stop"], values["target"]
        fee_rate = values["cost_bps"] * Decimal("0.0001")
        risk_budget = capital * values["risk_pct"] * Decimal("0.01")
        position_cap = capital * values["max_position_pct"] * Decimal("0.01")
        remaining_cap = max(Decimal(0), position_cap - existing)
        buy_fee = entry * fee_rate
        stop_fee, target_fee = stop * fee_rate, target * fee_rate
        cash_per_share = entry + buy_fee
        loss_per_share = entry - stop + buy_fee + stop_fee
        profit_per_share = target - entry - buy_fee - target_fee
        share_limits = {
            "risk_budget": _whole_shares(risk_budget, loss_per_share),
            "position_value": _whole_shares(remaining_cap, entry),
            "available_cash": _whole_shares(cash, cash_per_share),
        }
        min_shares = min(share_limits.values())
        quantity = (min_shares // lot) * lot
        purchase_value = entry * quantity
        purchase_fee = buy_fee * quantity
        cash_required = cash_per_share * quantity
        projected_value = existing + purchase_value
        scenario_loss = loss_per_share * quantity
        scenario_profit = profit_per_share * quantity
        reasons = []
        if existing > position_cap:
            reasons.append("existing_position_already_exceeds_position_limit")
        elif existing == position_cap:
            reasons.append("no_remaining_position_allowance")
        if quantity == 0:
            for name, bound in share_limits.items():
                if bound < lot:
                    reasons.append(f"{name}_cannot_fund_one_lot")

        ratio = None
        if quantity:
            with localcontext() as ratio_ctx:
                ratio_ctx.traps[Inexact] = False
                ratio = _text((profit_per_share / loss_per_share).quantize(
                    Decimal("0.000000000001"), rounding=ROUND_HALF_EVEN
                ))

        def scenario(exit_price: Decimal, exit_fee: Decimal, net_pnl: Decimal) -> dict:
            return {
                "assumed_exit_price": _text(exit_price),
                "gross_pnl": _text((exit_price - entry) * quantity),
                "estimated_buy_cost": _text(purchase_fee),
                "estimated_sell_cost": _text(exit_fee * quantity),
                "estimated_total_cost": _text(purchase_fee + exit_fee * quantity),
                "net_pnl": _text(net_pnl),
            }

        def check(actual: Decimal, limit: Decimal) -> dict:
            return {"actual": _text(actual), "limit": _text(limit), "passed": actual <= limit}

        return {
            "schema_version": 1,
            "status": "quantity_calculated" if quantity else "zero_quantity",
            "scope": {
                "instrument": "ordinary_stock", "side": "long", "leverage": False,
                "transaction": "add_shares", "risk_scope": "new_shares_only",
            },
            "units": {
                "currency": currency, "money": currency, "price": f"{currency}/share",
                "quantity": "shares", "lot_size": "shares/lot", "percentages": "percent",
                "cost_bps": "basis_points_per_side", "decimal_encoding": "decimal_strings",
            },
            "inputs": {**{name: _text(val) for name, val in values.items()},
                       "lot_size": lot, "currency": currency},
            "per_share": {
                "estimated_buy_cost": _text(buy_fee),
                "cash_required": _text(cash_per_share),
                "estimated_stop_sell_cost": _text(stop_fee),
                "estimated_target_sell_cost": _text(target_fee),
                "stop_scenario_loss_including_costs": _text(loss_per_share),
                "target_scenario_net_profit": _text(profit_per_share),
            },
            "limits": {
                "risk_budget": _text(risk_budget),
                "maximum_position_market_value": _text(position_cap),
                "remaining_position_market_value": _text(remaining_cap),
                "maximum_whole_shares_before_lot_rounding": share_limits,
                "tightest_whole_share_limits": [name for name, bound in share_limits.items()
                                                if bound == min_shares],
            },
            "position": {
                "quantity_shares": quantity, "quantity_lots": quantity // lot,
                "entry_market_value": _text(purchase_value),
                "estimated_buy_cost": _text(purchase_fee),
                "estimated_cash_required": _text(cash_required),
                "projected_position_market_value": _text(projected_value),
            },
            "scenarios": {
                "stop": {**scenario(stop, stop_fee, -scenario_loss), "loss": _text(scenario_loss)},
                "target": {**scenario(target, target_fee, scenario_profit),
                           "net_profit": _text(scenario_profit)},
            },
            "net_reward_to_risk_ratio": ratio,
            "ratio_rounding": "12 decimal places, ROUND_HALF_EVEN; null when quantity is zero",
            "limit_checks": {
                "new_shares_stop_scenario_loss": check(scenario_loss, risk_budget),
                "total_position_market_value": check(projected_value, position_cap),
                "new_shares_cash_required": check(cash_required, cash),
                "whole_lots": quantity % lot == 0,
                "nonnegative_quantity": quantity >= 0,
            },
            "zero_quantity_reasons": reasons,
            "assumptions_and_limits": [
                "All monetary inputs, current position value, and prices must use the stated currency; no FX conversion is performed.",
                "Existing value is the current market value of this same stock; scenario P&L and the risk budget cover added shares only.",
                "Position allowance uses entry market value; the cash and risk limits include estimated costs.",
                "Costs equal cost_bps applied to each side's traded notional; minimum commissions, taxes, slippage, and other charges are excluded.",
                "Stop and target outcomes are hypothetical full-execution scenarios; stop execution and loss limits are not guaranteed.",
                "This is a deterministic sizing calculation, not an order or investment recommendation.",
            ],
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    descriptions = {
        "capital": "total account capital, positive, in the stated currency",
        "available-cash": "unborrowed available cash, nonnegative, same currency",
        "existing-value": "current market value of the same stock, nonnegative, same currency",
        "max-position-pct": "maximum total weight of this stock, 0 < percent <= 100",
        "risk-pct": "stop-scenario risk budget for NEW shares, 0 < percent <= 100",
        "entry": "positive entry price per share, same currency",
        "stop": "positive assumed stop sale price per share, below entry",
        "target": "assumed target sale price per share, above entry",
        "lot-size": "positive integer shares per trading lot",
        "cost-bps": "nonnegative estimated costs in basis points PER SIDE; no minimum fees or taxes",
        "currency": "shared three-letter currency code; no conversion is performed",
    }
    for name, help_text in descriptions.items():
        parser.add_argument(f"--{name}", required=True, help=help_text)
    args = parser.parse_args(argv)
    try:
        report = calculate_risk_plan(**vars(args))
    except (InputError, DecimalException, OverflowError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
