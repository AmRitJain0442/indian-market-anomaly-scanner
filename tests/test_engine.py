from dataclasses import replace

import pandas as pd

from config import CONFIG
from src.backtest.engine import BacktestEngine
from src.data.calendar import evaluation_window
from src.data.universe import build_security_master
from src.features.returns import add_return_features
from src.strategies.daily import OpenToClose


def test_engine_ranks_net_pnl_and_writes_complete_outputs(tmp_path):
    dates = pd.bdate_range("2026-01-01", periods=12)
    rows = []
    for symbol, isin, intraday in (
        ("UP", "INE000000001", 0.01),
        ("DOWN", "INE000000002", -0.01),
    ):
        previous_close = 100.0
        for day in dates:
            open_price = previous_close
            close = open_price * (1 + intraday)
            rows.append(
                {
                    "date": day,
                    "symbol": symbol,
                    "isin": isin,
                    "company_name": symbol,
                    "series": "EQ",
                    "open": open_price,
                    "high": max(open_price, close),
                    "low": min(open_price, close),
                    "close": close,
                    "last_price": close,
                    "previous_close": previous_close,
                    "volume": 10000,
                    "traded_value": 1_000_000,
                    "number_of_trades": 100,
                    "delivery_quantity": None,
                    "delivery_percentage": None,
                    "instrument_type": "STK",
                    "raw_close_return": intraday,
                    "corporate_action_flag": False,
                    "circuit_like_flag": False,
                }
            )
            previous_close = close
    market = pd.DataFrame(rows)
    config = replace(CONFIG, project_root=tmp_path, evaluation_sessions=10)
    config.processed_dir.mkdir(parents=True)
    evaluation_dates = evaluation_window(market, 10)
    master = build_security_master(market, evaluation_dates, config)
    engine = BacktestEngine(add_return_features(market), master, evaluation_dates, config)
    result = engine.run(OpenToClose("open_to_close", "LONG_ONLY"))
    assert result.ranking.iloc[0]["symbol"] == "UP"
    assert result.ranking["pnl_rank"].tolist() == [1, 2]
    assert result.curve_path.exists()
    assert result.trade_path.exists()
    curves = pd.read_parquet(result.curve_path)
    assert len(curves) == 20
    assert set(curves["missing_session_flag"]) == {False}

