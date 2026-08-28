"""PnL-first stock rankings and market breadth summaries."""

from __future__ import annotations

import pandas as pd


def rank_strategy(results: pd.DataFrame) -> pd.DataFrame:
    ranking = results.sort_values(
        ["net_pnl", "sharpe", "symbol"], ascending=[False, False, True]
    ).copy()
    ranking.insert(0, "pnl_rank", range(1, len(ranking) + 1))
    return ranking


def breadth_summary(results: pd.DataFrame, equal_weight_pnl: float) -> dict:
    return {
        "strategy": results["strategy"].iloc[0],
        "stocks_tested": int(len(results)),
        "number_profitable": int(results["net_pnl"].gt(0).sum()),
        "pct_profitable": float(results["net_pnl"].gt(0).mean()),
        "median_net_pnl": float(results["net_pnl"].median()),
        "mean_net_pnl": float(results["net_pnl"].mean()),
        "p10_net_pnl": float(results["net_pnl"].quantile(0.10)),
        "p25_net_pnl": float(results["net_pnl"].quantile(0.25)),
        "p75_net_pnl": float(results["net_pnl"].quantile(0.75)),
        "p90_net_pnl": float(results["net_pnl"].quantile(0.90)),
        "median_sharpe": float(results["sharpe"].median()),
        "median_drawdown": float(results["max_drawdown"].median()),
        "equal_weight_pnl": float(equal_weight_pnl),
    }

