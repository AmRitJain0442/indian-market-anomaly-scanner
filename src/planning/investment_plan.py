"""Build a conservative small-capital pilot from the anomaly research output."""

from __future__ import annotations

import numpy as np
import pandas as pd

PLAN_CAPITAL = 10_000.0
PRIMARY_STRATEGY = "gap_fade_100"
MAX_POSITION = 5_000.0
RISK_PER_TRADE = 50.0
DAILY_LOSS_LIMIT = 100.0
PILOT_DRAWDOWN_LIMIT = 500.0
STOP_DISTANCE = 0.01
WATCHLIST_SIZE = 5

ELIGIBILITY_RULES = {
    "coverage_ratio": 0.99,
    "minimum_trades": 50,
    "minimum_median_daily_value": 50_000_000.0,
    "maximum_circuit_like_sessions": 2,
}


def position_size(entry_price: float, live_stage: str = "full") -> dict[str, float | int]:
    """Size a trade so a 1% stop risks at most 0.5% of plan capital."""
    if entry_price <= 0:
        raise ValueError("Entry price must be positive")
    multiplier = 0.5 if live_stage == "half" else 1.0
    notional_cap = MAX_POSITION * multiplier
    risk_cap = RISK_PER_TRADE * multiplier
    quantity = int(min(notional_cap / entry_price, risk_cap / (entry_price * STOP_DISTANCE)))
    notional = quantity * entry_price
    return {
        "quantity": quantity,
        "notional": round(notional, 2),
        "planned_risk": round(notional * STOP_DISTANCE, 2),
        "cash_remaining": round(PLAN_CAPITAL - notional, 2),
    }


def _directional_history(trades: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (isin, side), group in trades.groupby(["isin", "side"], observed=True):
        returns = group["net_return"].dropna()
        ending = PLAN_CAPITAL * (1.0 + returns).prod()
        rows.append(
            {
                "isin": isin,
                "side": side,
                "directional_trades": int(len(returns)),
                "directional_pnl_10k": float(ending - PLAN_CAPITAL),
                "directional_win_rate": float(returns.gt(0).mean()) if len(returns) else np.nan,
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=["isin", "side", "directional_trades", "directional_pnl_10k", "directional_win_rate"]
        )
    return pd.DataFrame(rows)


def build_investment_plan(
    ranked: pd.DataFrame,
    trades: pd.DataFrame,
    research_initial_capital: float,
) -> pd.DataFrame:
    """Select a strict, direction-checked watchlist for a ₹10k pilot.

    This is a research-to-paper-trading bridge, not a forecast. Candidates must
    pass coverage, liquidity, sample, data-quality, and statistical filters, and
    both long and short legs must have been positive independently.
    """
    required = {
        "isin",
        "symbol",
        "company_name",
        "strategy",
        "combination_rank",
        "combination_score",
        "net_pnl",
        "pnl_30bps",
        "sharpe",
        "max_drawdown",
        "number_of_trades",
        "win_rate",
        "coverage_ratio",
        "liquidity_flag",
        "median_daily_value",
        "corporate_action_observations",
        "circuit_like_sessions",
        "confidence_95_low",
    }
    missing = required - set(ranked.columns)
    if missing:
        raise ValueError(f"Missing investment-plan columns: {sorted(missing)}")
    if research_initial_capital <= 0:
        raise ValueError("Research initial capital must be positive")

    rules = ELIGIBILITY_RULES
    eligible = ranked[
        ranked["strategy"].eq(PRIMARY_STRATEGY)
        & ranked["coverage_ratio"].ge(rules["coverage_ratio"])
        & ranked["liquidity_flag"].eq("OK")
        & ranked["number_of_trades"].ge(rules["minimum_trades"])
        & ranked["median_daily_value"].ge(rules["minimum_median_daily_value"])
        & ranked["corporate_action_observations"].eq(0)
        & ranked["circuit_like_sessions"].le(rules["maximum_circuit_like_sessions"])
        & ranked["confidence_95_low"].gt(0)
    ].copy()

    directional = _directional_history(trades[trades["strategy"].eq(PRIMARY_STRATEGY)])
    direction_pivot = directional.pivot(index="isin", columns="side")
    valid_isins = []
    for isin in eligible["isin"]:
        if isin not in direction_pivot.index:
            continue
        long_pnl = direction_pivot.loc[isin, ("directional_pnl_10k", "LONG")]
        short_pnl = direction_pivot.loc[isin, ("directional_pnl_10k", "SHORT")]
        long_trades = direction_pivot.loc[isin, ("directional_trades", "LONG")]
        short_trades = direction_pivot.loc[isin, ("directional_trades", "SHORT")]
        if long_pnl > 0 and short_pnl > 0 and long_trades >= 10 and short_trades >= 10:
            valid_isins.append(isin)
    plan = eligible[eligible["isin"].isin(valid_isins)].sort_values("combination_rank").head(WATCHLIST_SIZE).copy()

    for side, prefix in (("LONG", "long"), ("SHORT", "short")):
        subset = directional[directional["side"].eq(side)].drop(columns="side")
        subset = subset.rename(
            columns={
                "directional_trades": f"{prefix}_trades",
                "directional_pnl_10k": f"{prefix}_pnl_10k",
                "directional_win_rate": f"{prefix}_win_rate",
            }
        )
        plan = plan.merge(subset, on="isin", how="left")
    plan["historical_pnl_10k"] = plan["net_pnl"] * PLAN_CAPITAL / research_initial_capital
    plan["historical_ending_10k"] = PLAN_CAPITAL + plan["historical_pnl_10k"]
    plan.insert(0, "watchlist_rank", range(1, len(plan) + 1))
    return plan
