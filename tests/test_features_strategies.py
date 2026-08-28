import numpy as np
import pandas as pd

from config import CONFIG
from src.features.returns import add_return_features
from src.strategies.daily import GapStrategy, LaggedMoveStrategy, VolumeShockStrategy


def _market_frame():
    dates = pd.bdate_range("2026-01-01", periods=25)
    rows = []
    for index, day in enumerate(dates):
        previous = 100 + index
        open_price = previous * (1.01 if index == 21 else 1.0)
        close = open_price * (1.02 if index == 21 else 1.001)
        rows.append(
            {
                "date": day,
                "symbol": "TEST",
                "isin": "INE000000001",
                "open": open_price,
                "high": max(open_price, close) * 1.001,
                "low": min(open_price, close) * 0.999,
                "close": close,
                "previous_close": previous,
                "volume": 5000 if index == 21 else 1000,
                "traded_value": close * 1000,
                "corporate_action_flag": False,
                "circuit_like_flag": False,
            }
        )
    return pd.DataFrame(rows)


def test_gap_and_lagged_signals_have_expected_direction():
    features = add_return_features(_market_frame())
    fade = GapStrategy("gap_fade_050", 0.005, -1).generate_returns(features)
    continuation = GapStrategy("gap_continuation_050", 0.005, 1).generate_returns(features)
    active = fade["signal"].ne(0)
    assert active.sum() >= 1
    assert (fade.loc[active, "signal"] == -continuation.loc[active, "signal"]).all()

    reversal = LaggedMoveStrategy(
        "reversal_1d", "previous_cc_signal", 0.01, -1
    ).generate_returns(features)
    momentum = LaggedMoveStrategy(
        "momentum_1d", "previous_cc_signal", 0.01, 1
    ).generate_returns(features)
    assert (reversal["signal"] == -momentum["signal"]).all()


def test_volume_signal_uses_previous_session_information():
    features = add_return_features(_market_frame())
    strategy = VolumeShockStrategy("volume", 2.0, 0.01, 1.0)
    output = strategy.generate_returns(features)
    shock_index = features["volume_ratio"].idxmax()
    assert output.loc[shock_index, "signal"] == 0
    if shock_index + 1 < len(output):
        assert output.loc[shock_index + 1, "signal"] in (-1, 1)


def test_suspension_does_not_create_cross_gap_overnight_return():
    primary = _market_frame().drop(index=10)
    peer = _market_frame().assign(symbol="PEER", isin="INE000000002")
    frame = pd.concat([primary, peer], ignore_index=True)
    features = add_return_features(frame)
    day_after_gap = pd.bdate_range("2026-01-01", periods=25)[11]
    value = features.loc[
        features["date"].eq(day_after_gap) & features["symbol"].eq("TEST"),
        "ret_overnight",
    ].iloc[0]
    assert np.isnan(value)
