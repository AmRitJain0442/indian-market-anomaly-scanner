import pytest

from publish_pilot_result import summarize


def test_report_counts_known_nofill_as_zero_without_inventing_a_trade():
    summary = {"mode": "minute-proxy", "incomplete": False, "initial_investment": 1000,
               "evaluation_sessions": 1, "ending_equity": 1000}
    ledger = [{"date": "2026-09-04", "status": "NO_FILL", "starting_equity": 1000,
               "ending_equity": 1000, "net_pnl": None, "reason": "ENTRY_ADVERSE_LIMIT"}]
    metrics, sessions, trades = summarize(summary, ledger)
    assert metrics["net_pnl"] == 0
    assert metrics["closed_trades"] == 0
    assert metrics["no_fill_sessions"] == 1
    assert sessions.net_pnl.iloc[0] == 0
    assert trades.empty


def test_report_rejects_incomplete_performance():
    with pytest.raises(ValueError, match="complete minute"):
        summarize({"mode": "minute-proxy", "incomplete": True}, [])


def test_report_drawdown_includes_initial_capital():
    summary = {"mode": "minute-proxy", "incomplete": False, "initial_investment": 1000,
               "evaluation_sessions": 1, "ending_equity": 996}
    ledger = [{"date": "2026-09-04", "status": "CLOSED", "symbol": "TEST", "side": "LONG",
               "starting_equity": 1000, "ending_equity": 996, "net_pnl": -4,
               "quantity": 1, "entry_time": "09:17", "entry_price": 200, "notional": 200,
               "planned_loss": 4, "stop": 198, "target": 204, "exit_bar_time": "09:22",
               "exit_price": 197, "reason": "STOP", "charges": {"total": 1}}]
    metrics, _, _ = summarize(summary, ledger)
    assert metrics["max_realized_drawdown"] == pytest.approx(-0.004)
    assert metrics["estimated_trading_charges"] == 1
