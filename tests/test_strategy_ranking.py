import pandas as pd

from src.backtest.strategy_ranking import rank_strategies_collectively


def test_collective_ranking_rewards_broad_cost_surviving_performance():
    summary = pd.DataFrame(
        [
            {
                "strategy": "broad",
                "median_net_pnl": 10_000,
                "pct_profitable": 0.70,
                "equal_weight_pnl": 20_000,
                "median_sharpe": 1.1,
                "pct_profitable_30bps": 0.55,
            },
            {
                "strategy": "mixed",
                "median_net_pnl": 1_000,
                "pct_profitable": 0.51,
                "equal_weight_pnl": 2_000,
                "median_sharpe": 0.1,
                "pct_profitable_30bps": 0.30,
            },
            {
                "strategy": "weak",
                "median_net_pnl": -5_000,
                "pct_profitable": 0.30,
                "equal_weight_pnl": -8_000,
                "median_sharpe": -0.5,
                "pct_profitable_30bps": 0.10,
            },
        ]
    )
    ranked = rank_strategies_collectively(summary)
    assert ranked["strategy"].tolist() == ["broad", "mixed", "weak"]
    assert ranked.iloc[0]["collective_score"] == 100
    assert ranked.iloc[0]["positive_pillars"] == 5
    assert ranked.iloc[0]["evidence_tier"] == "ROBUST POSITIVE"
    assert ranked.iloc[-1]["evidence_tier"] == "WEAK / NEGATIVE"

