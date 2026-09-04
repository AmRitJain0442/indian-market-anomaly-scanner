import pandas as pd
import pytest

from src.backtest.eligibility_ranking import audit_trade_series, broker_table, screen_and_rank


def test_broker_parser_requires_explicit_mis_rows():
    html = '<tr><td>FAKE</td></tr><tr data-scrip="A&amp;B" data-mis_margin="20" data-mis_multiplier="5"><td>A&amp;B</td></tr>'
    rows = broker_table(html)
    assert rows.symbol.tolist() == ["A&B"]
    assert rows.mis_margin_percent.iloc[0] == 20
    with pytest.raises(ValueError, match="missing"):
        broker_table("<html>Access denied</html>")


def test_historical_screen_checks_exit_leg_and_initial_drawdown():
    days = pd.date_range("2026-08-01", periods=4)
    series = pd.Series(["EQ", "EQ", "BZ", "EQ"], index=pd.MultiIndex.from_product([["A"], days]))
    trades = pd.DataFrame({"isin": ["A", "A"], "entry_date": [days[0], days[1]],
                           "exit_date": [days[0], days[2]], "side": ["LONG", "LONG"],
                           "net_return": [-0.1, 0.02]})
    row = audit_trade_series(trades, series).iloc[0]
    assert row.restricted_trades == 1
    assert row.non_eq_trades == 1
    assert row.corrected_drawdown == pytest.approx(-0.1)


def test_missing_exit_series_is_not_passed():
    day = pd.Timestamp("2026-08-01")
    series = pd.Series(["EQ"], index=pd.MultiIndex.from_tuples([("A", day)]))
    trades = pd.DataFrame({"isin": ["A"], "entry_date": [day], "exit_date": [day + pd.Timedelta(days=1)],
                           "side": ["SHORT"], "net_return": [0.1]})
    result = audit_trade_series(trades, series).iloc[0]
    assert result.unknown_series_trades == 1
    assert result.non_eq_trades == 1


def screen_fixture():
    stocks = ["GOOD", "MIXED", "EXPENSIVE", "UNLISTED", "CURRENTBZ", "OVERNIGHT"]
    results = pd.DataFrame([{
        "isin": s, "symbol": s, "company_name": s, "strategy": "close_to_open" if s == "OVERNIGHT" else "gap_fade_100",
        "number_of_trades": 25, "coverage_ratio": 1.0, "liquidity_flag": "OK", "confidence_95_low": 0.001,
        "net_pnl": 1000.0, "sharpe": 1.0, "pnl_30bps": 200.0, "max_drawdown": 0,
        "excess_pnl": 500.0,
    } for s in stocks])
    audit = pd.DataFrame([{
        "isin": s, "strategy": "close_to_open" if s == "OVERNIGHT" else "gap_fade_100", "audited_trades": 25,
        "restricted_trades": int(s == "MIXED"), "unknown_series_trades": 0,
        "non_eq_trades": int(s == "MIXED"), "short_trades": 10, "corrected_drawdown": -0.10,
    } for s in stocks])
    latest = pd.DataFrame([{"isin": s, "symbol": s, "series": "BZ" if s == "CURRENTBZ" else "EQ",
                            "close": 600.0 if s == "EXPENSIVE" else 164.95, "tick_size": 0.01} for s in stocks])
    recent = pd.DataFrame([{"isin": s, "recent_sessions": 20, "recent_median_value": 1e9} for s in stocks])
    broker = pd.DataFrame([{"symbol": s, "mis_margin_percent": 20.0, "listed_mis_multiplier": 5.0} for s in stocks if s != "UNLISTED"])
    return results, audit, latest, recent, broker


def test_strict_history_and_practical_budget_are_separate():
    frame = screen_and_rank(*screen_fixture()).set_index("symbol")
    assert not frame.loc["MIXED", "eq_screen_pass"]
    assert not frame.loc["CURRENTBZ", "eq_screen_pass"]
    assert frame.loc["UNLISTED", "eq_screen_pass"]
    assert not frame.loc["UNLISTED", "worklist_pass"]
    assert frame.loc["EXPENSIVE", "eq_screen_pass"]
    assert not frame.loc["EXPENSIVE", "worklist_pass"]
    assert frame.loc["EXPENSIVE", "cash_cap_shares"] == 0
    assert frame.loc["GOOD", "worklist_pass"]
    assert frame.loc["GOOD", "cash_cap_shares"] == 3
    assert frame.loc["GOOD", "illustrative_risk_shares"] == 2
    assert frame.loc["GOOD", "illustrative_planned_loss"] <= 5
    assert frame.loc["GOOD", "worklist_rank"] == 1
    assert frame.loc["GOOD", "max_drawdown"] == -0.10
    assert not frame.loc["OVERNIGHT", "worklist_pass"]
    assert pd.isna(frame.loc["MIXED", "eq_rank"])
    assert not frame.execution_validated.any()


def test_trade_count_mismatch_fails_instead_of_ranking():
    args = list(screen_fixture())
    args[1].loc[0, "audited_trades"] = 24
    with pytest.raises(ValueError, match="reconcile"):
        screen_and_rank(*args)


def test_cash_affordable_share_can_fail_stop_risk_budget():
    args = list(screen_fixture())
    args[2].loc[args[2].symbol.eq("GOOD"), "close"] = 418.0
    frame = screen_and_rank(*args).set_index("symbol")
    assert frame.loc["GOOD", "cash_cap_shares"] == 1
    assert frame.loc["GOOD", "illustrative_risk_shares"] == 0
    assert not frame.loc["GOOD", "worklist_pass"]
