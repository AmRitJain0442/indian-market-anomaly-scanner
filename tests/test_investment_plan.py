import pandas as pd

from src.planning.investment_plan import build_investment_plan, position_size


def test_position_size_respects_notional_and_risk_caps():
    sized = position_size(200)
    assert sized == {
        "quantity": 25,
        "notional": 5_000.0,
        "planned_risk": 50.0,
        "cash_remaining": 5_000.0,
    }
    assert position_size(200, "half")["quantity"] == 12
    assert position_size(6_000)["quantity"] == 0


def test_plan_requires_both_directions_and_strict_quality():
    base = {
        "company_name": "Example",
        "strategy": "gap_fade_100",
        "combination_score": 90,
        "net_pnl": 20_000,
        "pnl_30bps": 5_000,
        "sharpe": 2,
        "max_drawdown": -0.1,
        "number_of_trades": 60,
        "win_rate": 0.6,
        "coverage_ratio": 1,
        "liquidity_flag": "OK",
        "median_daily_value": 100_000_000,
        "corporate_action_observations": 0,
        "circuit_like_sessions": 0,
        "confidence_95_low": 0.001,
    }
    ranked = pd.DataFrame(
        [
            {**base, "isin": "GOOD", "symbol": "GOOD", "combination_rank": 1},
            {**base, "isin": "ONELEG", "symbol": "ONELEG", "combination_rank": 2},
            {**base, "isin": "ILLIQ", "symbol": "ILLIQ", "combination_rank": 3, "median_daily_value": 1_000_000},
        ]
    )
    trades = pd.DataFrame(
        [
            *[{"strategy": "gap_fade_100", "isin": "GOOD", "side": "LONG", "net_return": 0.01}] * 10,
            *[{"strategy": "gap_fade_100", "isin": "GOOD", "side": "SHORT", "net_return": 0.01}] * 10,
            *[{"strategy": "gap_fade_100", "isin": "ONELEG", "side": "LONG", "net_return": 0.01}] * 10,
            *[{"strategy": "gap_fade_100", "isin": "ONELEG", "side": "SHORT", "net_return": -0.01}] * 10,
            *[{"strategy": "gap_fade_100", "isin": "ILLIQ", "side": "LONG", "net_return": 0.01}] * 10,
            *[{"strategy": "gap_fade_100", "isin": "ILLIQ", "side": "SHORT", "net_return": 0.01}] * 10,
        ]
    )
    plan = build_investment_plan(ranked, trades, 100_000)
    assert plan["symbol"].tolist() == ["GOOD"]
    assert plan.iloc[0]["historical_pnl_10k"] == 2_000
