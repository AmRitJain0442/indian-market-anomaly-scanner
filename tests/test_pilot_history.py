import pandas as pd
import pytest

from src.data.pilot_history import decode_chart, watchlist


def make_market():
    dates = pd.bdate_range("2026-07-01", periods=30)
    rows = []
    for day in dates:
        for index in range(7):
            rows.append({
                "date": day, "symbol": f"S{index}", "isin": f"ISIN{index}",
                "series": "EQ", "close": 200.0, "previous_close": 200.0,
                "open": 198.0, "traded_value": (7 - index) * 1_000_000_000.0,
            })
    return pd.DataFrame(rows)


def test_watchlist_uses_only_completed_history_and_freezes_five():
    market = make_market()
    session = market.date.max()
    before = watchlist(market, session, 1000)
    market.loc[market.date.eq(session), "traded_value"] = 1
    market.loc[market.date.eq(session), "close"] = 10000
    market.loc[market.date.eq(session) & market.symbol.eq("S6"), "traded_value"] = 1e15
    after = watchlist(market, session, 1000)
    assert [row["symbol"] for row in before] == [f"S{i}" for i in range(5)]
    assert [row["symbol"] for row in before] == [row["symbol"] for row in after]
    assert before[0]["median_daily_value"] == after[0]["median_daily_value"]
    assert before[0]["history_sessions"] == 20
    assert before[0]["history_end"] < before[0]["date"]


def test_current_restricted_series_does_not_backfill_watchlist():
    market = make_market()
    session = market.date.max()
    market.loc[market.date.eq(session) & market.symbol.eq("S0"), "series"] = "BE"
    result = watchlist(market, session, 1000)
    assert result[0]["symbol"] == "S0"
    assert result[0]["series"] == "BE"
    assert len(result) == 5


def test_watchlist_rejects_missing_trailing_session():
    market = make_market()
    session = market.date.max()
    market = market.loc[~(market.symbol.eq("S0") & market.date.eq(session - pd.offsets.BDay(2)))]
    assert "S0" not in {r["symbol"] for r in watchlist(market, session, 1000)}


def test_decode_chart_filters_appended_out_of_range_quote():
    stamps = pd.to_datetime(["2026-08-10T09:15:00+05:30", "2026-09-04T15:29:00+05:30"])
    payload = {"chart": {"result": [{
        "meta": {"currency": "INR", "dataGranularity": "1m"},
        "timestamp": [int(x.timestamp()) for x in stamps],
        "indicators": {"quote": [{key: [100, 100] for key in ("open", "high", "low", "close", "volume")}]},
    }], "error": None}}
    result = decode_chart(payload, pd.Timestamp("2026-08-10").date(), pd.Timestamp("2026-08-15").date())
    assert len(result) == 1
    assert str(result.index.tz) == "Asia/Kolkata"


def test_decode_chart_rejects_wrong_granularity():
    with pytest.raises(ValueError, match="one-minute"):
        decode_chart({"chart": {"result": [{"meta": {"currency": "INR", "dataGranularity": "5m"}}]}}, None, None)
