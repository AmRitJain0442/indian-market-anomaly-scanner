"""Economic and causality checks for the explicitly approximate minute evaluator."""

import pandas as pd
import pytest

from src.backtest.intraday_pilot import evaluate_candidate, estimate_charges, simulate_session, simulate_pilot


def candles(price=200.0, day="2026-08-10"):
    index = pd.date_range(f"{day} 09:15", f"{day} 15:00", freq="min", tz="Asia/Kolkata")
    return pd.DataFrame({"open": price, "high": price + 0.1, "low": price - 0.1,
                         "close": price, "volume": 1000}, index=index)


def stamp(clock, day="2026-08-10"):
    return pd.Timestamp(f"{day} {clock}", tz="Asia/Kolkata")


def candidate(symbol="TEST", gap=-0.02):
    return {"symbol": symbol, "series": "EQ", "reference": 204.0, "gap": gap, "tick_size": 0.01}


def test_fees_are_side_specific_and_whole_share_risk_includes_allowances():
    long_fees = estimate_charges("LONG", 2, 200, 198)
    short_fees = estimate_charges("SHORT", 2, 200, 198)
    assert long_fees["total"] == pytest.approx(sum(value for key, value in long_fees.items() if key != "total"))
    assert short_fees["stt"] >= long_fees["stt"]
    assert long_fees["ipft"] == 0.01
    result = evaluate_candidate(candles(), "LONG", 204, 1000, 0.01)
    assert result["quantity"] == 1  # Two shares exceed risk once charges and allowance are included.
    assert result["planned_loss"] <= 5
    assert result["notional"] <= 500
    assert result["net_pnl"] == pytest.approx(result["gross_pnl"] - result["charges"]["total"])


def test_decision_uses_completed_0915_and_entry_uses_0917_open_only():
    bars = candles()
    bars.loc[stamp("09:16"), ["open", "high", "low", "close"]] = [100, 100, 100, 100]
    result = evaluate_candidate(bars, "LONG", 204, 1000, 0.01)
    assert result["decision_price"] == 200
    assert result["entry_price"] == 200.10
    assert result["entry_time"].startswith("2026-08-10T09:17:")


def test_adverse_entry_limit_consumes_attempt_and_does_not_substitute():
    failed = candles()
    failed.loc[stamp("09:17"), ["open", "high", "low", "close"]] = [201, 201.1, 200.9, 201]
    result = simulate_session("2026-08-10", [candidate("FIRST"), candidate("SECOND")],
                              {"FIRST": failed, "SECOND": candles()})
    assert result["status"] == "NO_FILL"
    assert result["reason"] == "ENTRY_ADVERSE_LIMIT"
    assert result["symbol"] == "FIRST"
    assert result["attempted"] is True
    assert len(result["candidate_checks"]) == 1


def test_decision_disqualification_can_select_next_frozen_name():
    result = simulate_session("2026-08-10", [candidate("FIRST"), candidate("SECOND")],
                              {"FIRST": candles(203.5), "SECOND": candles()})
    assert result["symbol"] == "SECOND"
    assert result["status"] == "CLOSED"
    assert result["candidate_checks"][0]["reason"] == "DECISION_TARGET_DISTANCE"


def test_favorable_entry_does_not_increase_decision_order_quantity():
    bars = candles()
    bars.loc[stamp("09:17"), ["open", "high", "low", "close"]] = [150, 150.1, 149.9, 150]
    result = evaluate_candidate(bars, "LONG", 204, 1000, 0.01)
    assert result["decision_quantity"] == 1
    assert result["quantity"] == 1
    assert result["notional"] == result["entry_price"]
    assert result["adverse_fill_allowance"] == pytest.approx(max(0.002 * result["entry_price"], 0.02))


@pytest.mark.parametrize("side, reference, extreme", [("LONG", 204, 197), ("SHORT", 196, 203)])
def test_long_and_short_stops_apply_adverse_fill(side, reference, extreme):
    bars = candles()
    bars.loc[stamp("09:18"), "low" if side == "LONG" else "high"] = extreme
    result = evaluate_candidate(bars, side, reference, 1000, 0.01)
    assert result["status"] == "CLOSED"
    assert result["reason"] == "STOP"
    assert result["exit_price"] < result["stop"] if side == "LONG" else result["exit_price"] > result["stop"]
    assert result["net_pnl"] < 0


def test_gap_through_stop_fills_at_worse_open():
    bars = candles()
    bars.loc[stamp("09:18"), ["open", "high", "low", "close"]] = [195, 195.1, 194.9, 195]
    result = evaluate_candidate(bars, "LONG", 204, 1000, 0.01)
    assert result["reason"] == "STOP_GAP"
    assert result["exit_price"] < 195 < result["stop"]


def test_target_touch_does_not_fill_but_trade_through_fills_at_limit():
    bars = candles()
    bars.loc[stamp("09:18"), "high"] = 204
    touch = evaluate_candidate(bars, "LONG", 204, 1000, 0.01)
    assert touch["reason"] == "TIMED_EXIT"
    bars.loc[stamp("09:18"), "high"] = 204.01
    through = evaluate_candidate(bars, "LONG", 204, 1000, 0.01)
    assert through["reason"] == "TARGET_TRADE_THROUGH"
    assert through["exit_price"] == 204


def test_same_bar_stop_and_target_takes_stop_and_marks_ambiguity():
    bars = candles()
    bars.loc[stamp("09:17"), ["high", "low"]] = [205, 197]
    result = evaluate_candidate(bars, "LONG", 204, 1000, 0.01)
    assert result["reason"] == "STOP_FIRST"
    assert result["ambiguity_flags"] == ["STOP_AND_TARGET_SAME_BAR_STOP_FIRST"]
    assert result["net_pnl"] < 0


def test_timed_exit_does_not_use_the_rest_of_1500_candle():
    bars = candles()
    bars.loc[stamp("15:00"), ["high", "low"]] = [210, 190]
    result = evaluate_candidate(bars, "LONG", 204, 1000, 0.01)
    assert result["reason"] == "TIMED_EXIT"
    assert not result["ambiguity_flags"]


def test_missing_bar_after_entry_is_unresolved_and_blocks_next_session():
    first = candles().drop(stamp("09:18"))
    sessions = [
        {"date": "2026-08-10", "candidates": [candidate()], "bars_by_symbol": {"TEST": first}},
        {"date": "2026-08-11", "candidates": [candidate()], "bars_by_symbol": {"TEST": candles(day="2026-08-11")}},
    ]
    result = simulate_pilot(sessions)
    assert result["daily"][0]["status"] == "UNRESOLVED"
    assert result["daily"][0]["net_pnl"] is None
    assert result["daily"][1]["status"] == "HALTED"
    assert result["ending_equity"] is None
    assert result["halt_reason"] == "UNRESOLVED_POSITION"


def test_missing_decision_data_does_not_silently_select_lower_rank():
    result = simulate_session("2026-08-10", [candidate("FIRST"), candidate("SECOND")],
                              {"FIRST": candles().drop(stamp("09:15")), "SECOND": candles()})
    assert result["status"] == "INCOMPLETE_DATA"
    assert result["symbol"] == "FIRST"
    assert not result["attempted"]


def test_missing_decision_data_invalidates_portfolio_path_and_blocks_next_day():
    result = simulate_pilot([
        {"date": "2026-08-10", "candidates": [candidate()], "bars_by_symbol": {"TEST": candles().drop(stamp("09:15"))}},
        {"date": "2026-08-11", "candidates": [candidate()], "bars_by_symbol": {"TEST": candles(day="2026-08-11")}},
    ])
    assert result["incomplete"] is True
    assert result["ending_equity"] is None
    assert result["realized_profit"] is None
    assert result["daily"][0]["ending_equity"] is None
    assert result["daily"][1]["status"] == "HALTED"
    assert result["daily"][1]["ending_equity"] is None
    assert result["halt_reason"] == "INCOMPLETE_DATA"


def test_drawdown_starts_at_initial_capital_and_stops_future_entries():
    bars = candles()
    bars.loc[stamp("09:18"), ["open", "high", "low", "close"]] = [140, 141, 139, 140]
    result = simulate_pilot([
        {"date": "2026-08-10", "candidates": [candidate()], "bars_by_symbol": {"TEST": bars}},
        {"date": "2026-08-11", "candidates": [candidate()], "bars_by_symbol": {"TEST": candles(day="2026-08-11")}},
    ])
    assert result["max_realized_drawdown"] < -0.05
    assert result["daily"][1]["status"] == "HALTED"
    assert result["halt_reason"] == "DRAWDOWN_LIMIT"


def test_unknown_or_restricted_series_never_enters():
    restricted = {**candidate(), "series": "BZ"}
    result = simulate_session("2026-08-10", [restricted], {"TEST": candles()})
    assert result["status"] == "NO_TRADE"
    assert not result["attempted"]


def test_incorrect_dates_and_duplicate_bars_are_rejected():
    with pytest.raises(ValueError, match="session_date"):
        simulate_session("2026-08-11", [candidate()], {"TEST": candles()})
    bars = candles()
    with pytest.raises(ValueError, match="unique"):
        evaluate_candidate(pd.concat([bars, bars.iloc[:1]]), "LONG", 204, 1000, 0.01)
