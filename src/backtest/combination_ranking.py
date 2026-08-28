"""Cross-sectional ranking for every stock-strategy result pair."""

from __future__ import annotations

import numpy as np
import pandas as pd

COMBINATION_PILLARS = {
    "net_pnl": ("Net PnL", 0.25),
    "sharpe": ("Sharpe", 0.20),
    "pnl_30bps": ("PnL at 30 bps/side", 0.20),
    "max_drawdown": ("Drawdown resilience", 0.15),
    "excess_pnl": ("Excess PnL vs buy-and-hold", 0.20),
}


def _relative_score(values: pd.Series) -> pd.Series:
    """Return a 0-100 percentile score, treating missing values as worst."""
    numeric = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan)
    if numeric.notna().sum() == 0:
        return pd.Series(0.0, index=values.index)
    floor = float(numeric.min())
    penalty = max(abs(floor) * 0.01, 1e-9)
    numeric = numeric.fillna(floor - penalty)
    if len(numeric) <= 1:
        return pd.Series(100.0, index=values.index)
    ranks = numeric.rank(method="average", ascending=True)
    return (ranks - 1.0) / (len(numeric) - 1.0) * 100.0


def rank_stock_strategy_combinations(results: pd.DataFrame) -> pd.DataFrame:
    """Rank all stock-strategy pairs using return, risk, and cost resilience.

    The overall score is relative to all pairs in the same run. The evidence
    tier and sample tier remain absolute so that a high relative score is not
    mistaken for an execution-quality or out-of-sample claim.
    """
    required = {
        "isin",
        "symbol",
        "company_name",
        "strategy",
        "number_of_trades",
        "coverage_ratio",
        "liquidity_flag",
        "confidence_95_low",
        *COMBINATION_PILLARS,
    }
    missing = required - set(results.columns)
    if missing:
        raise ValueError(f"Missing stock-strategy ranking columns: {sorted(missing)}")

    ranked = results.copy()
    for column, (_, weight) in COMBINATION_PILLARS.items():
        ranked[f"score_{column}"] = _relative_score(ranked[column])
    ranked["combination_score"] = sum(
        ranked[f"score_{column}"] * weight
        for column, (_, weight) in COMBINATION_PILLARS.items()
    )

    positive = pd.DataFrame(
        {
            "net_profitable": ranked["net_pnl"].gt(0),
            "positive_sharpe": ranked["sharpe"].gt(0),
            "cost_survives": ranked["pnl_30bps"].gt(0),
            "beats_buy_hold": ranked["excess_pnl"].gt(0),
            "positive_confidence_floor": ranked["confidence_95_low"].gt(0),
        }
    )
    ranked["positive_pillars"] = positive.sum(axis=1).astype(int)
    ranked["evidence_tier"] = ranked["positive_pillars"].map(
        {
            5: "ROBUST POSITIVE",
            4: "BROAD POSITIVE",
            3: "MIXED",
            2: "MIXED",
            1: "WEAK / NEGATIVE",
            0: "WEAK / NEGATIVE",
        }
    )
    comparable = (
        ranked["coverage_ratio"].ge(0.95)
        & ranked["liquidity_flag"].eq("OK")
        & ranked["number_of_trades"].ge(20)
    )
    ranked["sample_tier"] = np.select(
        [comparable, ranked["number_of_trades"].lt(20) | ranked["coverage_ratio"].lt(0.95)],
        ["COMPARABLE", "LIMITED SAMPLE"],
        default="LOW LIQUIDITY",
    )
    ranked["profit_rank"] = ranked["net_pnl"].rank(method="min", ascending=False).astype(int)
    ranked = ranked.sort_values(
        ["combination_score", "positive_pillars", "net_pnl", "symbol", "strategy"],
        ascending=[False, False, False, True, True],
    ).reset_index(drop=True)
    ranked.insert(0, "combination_rank", range(1, len(ranked) + 1))

    ranked["comparable_rank"] = pd.Series(pd.NA, index=ranked.index, dtype="Int64")
    comparable_index = ranked.index[ranked["sample_tier"].eq("COMPARABLE")]
    ranked.loc[comparable_index, "comparable_rank"] = pd.array(
        range(1, len(comparable_index) + 1), dtype="Int64"
    )
    return ranked
