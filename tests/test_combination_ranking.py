import pandas as pd

from src.backtest.combination_ranking import rank_stock_strategy_combinations


def _row(symbol, pnl, sharpe, pnl_30bps, drawdown, excess, confidence, trades=50, coverage=1.0, liquidity="OK"):
    return {
        "isin": f"ISIN-{symbol}",
        "symbol": symbol,
        "company_name": symbol,
        "strategy": "test_strategy",
        "net_pnl": pnl,
        "sharpe": sharpe,
        "pnl_30bps": pnl_30bps,
        "max_drawdown": drawdown,
        "excess_pnl": excess,
        "confidence_95_low": confidence,
        "number_of_trades": trades,
        "coverage_ratio": coverage,
        "liquidity_flag": liquidity,
    }


def test_combination_ranking_rewards_profitable_robust_pair():
    results = pd.DataFrame(
        [
            _row("ROBUST", 50_000, 2.0, 25_000, -0.08, 30_000, 0.002),
            _row("MIXED", 10_000, 0.2, -2_000, -0.30, -5_000, -0.001),
            _row("WEAK", -20_000, -1.0, -35_000, -0.60, -15_000, -0.005),
        ]
    )
    ranked = rank_stock_strategy_combinations(results)
    assert ranked["symbol"].tolist() == ["ROBUST", "MIXED", "WEAK"]
    assert ranked.iloc[0]["combination_score"] == 100
    assert ranked.iloc[0]["evidence_tier"] == "ROBUST POSITIVE"
    assert ranked.iloc[0]["positive_pillars"] == 5
    assert ranked.iloc[0]["comparable_rank"] == 1


def test_combination_ranking_labels_sample_quality_without_dropping_rows():
    results = pd.DataFrame(
        [
            _row("FULL", 10_000, 1.0, 5_000, -0.1, 8_000, 0.001),
            _row("SHORT", 20_000, 2.0, 8_000, -0.05, 15_000, 0.002, trades=5),
            _row("ILLIQUID", 15_000, 1.5, 7_000, -0.08, 12_000, 0.001, liquidity="LOW"),
        ]
    )
    ranked = rank_stock_strategy_combinations(results)
    tiers = ranked.set_index("symbol")["sample_tier"].to_dict()
    assert len(ranked) == 3
    assert tiers == {
        "SHORT": "LIMITED SAMPLE",
        "ILLIQUID": "LOW LIQUIDITY",
        "FULL": "COMPARABLE",
    }
    assert ranked["comparable_rank"].notna().sum() == 1
