"""Market-wide multi-criterion ranking for anomaly strategies."""

from __future__ import annotations

import pandas as pd

COLLECTIVE_PILLARS = {
    "median_net_pnl": "Median stock PnL",
    "pct_profitable": "Profitable-stock breadth",
    "equal_weight_pnl": "Equal-weight universe PnL",
    "median_sharpe": "Median stock Sharpe",
    "pct_profitable_30bps": "Breadth at 30 bps/side",
}

COLLECTIVE_WEIGHTS = {column: 0.20 for column in COLLECTIVE_PILLARS}


def _relative_score(values: pd.Series) -> pd.Series:
    """Map the worst observation to 0 and best to 100, preserving ties."""
    if len(values) <= 1:
        return pd.Series(100.0, index=values.index)
    ranks = values.rank(method="average", ascending=True)
    return (ranks - 1.0) / (len(values) - 1.0) * 100.0


def rank_strategies_collectively(summary: pd.DataFrame) -> pd.DataFrame:
    """Rank strategies across five equally weighted market-wide pillars.

    The score is relative to strategies in the same research run. The evidence
    tier is absolute and prevents a high relative rank from implying profitability.
    """
    missing = set(COLLECTIVE_PILLARS) - set(summary.columns)
    if missing:
        raise ValueError(f"Missing collective-ranking columns: {sorted(missing)}")
    ranked = summary.copy()
    component_columns = []
    for column, weight in COLLECTIVE_WEIGHTS.items():
        score_column = f"score_{column}"
        ranked[score_column] = _relative_score(ranked[column])
        component_columns.append(score_column)
    ranked["collective_score"] = sum(
        ranked[f"score_{column}"] * weight
        for column, weight in COLLECTIVE_WEIGHTS.items()
    )
    positive = pd.DataFrame(
        {
            "median_pnl_positive": ranked["median_net_pnl"].gt(0),
            "majority_profitable": ranked["pct_profitable"].gt(0.50),
            "equal_weight_positive": ranked["equal_weight_pnl"].gt(0),
            "median_sharpe_positive": ranked["median_sharpe"].gt(0),
            "cost_survival_majority": ranked["pct_profitable_30bps"].gt(0.50),
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
    ranked = ranked.sort_values(
        ["collective_score", "positive_pillars", "median_net_pnl"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    ranked.insert(0, "collective_rank", range(1, len(ranked) + 1))
    return ranked

