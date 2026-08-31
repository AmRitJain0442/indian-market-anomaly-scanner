import numpy as np
import pandas as pd

from src.forecasting.short_horizon import ForecastConfig, build_forecast_frame, fit_forecasts


def _panel(sessions: int = 180, stocks: int = 80) -> pd.DataFrame:
    dates = pd.bdate_range("2025-01-02", periods=sessions)
    rows = []
    for stock in range(stocks):
        price = 80.0 + stock
        for index, day in enumerate(dates):
            lag_signal = np.sin((index + stock) / 7) * 0.002
            close_return = lag_signal + ((stock % 5) - 2) * 0.0001
            open_price = price * (1 + close_return / 3)
            close = price * np.exp(close_return)
            rows.append(
                {
                    "date": day,
                    "symbol": f"S{stock}",
                    "isin": f"INE{stock:09d}",
                    "company_name": f"Stock {stock}",
                    "open": open_price,
                    "high": max(open_price, close) * 1.002,
                    "low": min(open_price, close) * 0.998,
                    "close": close,
                    "volume": 10_000 + stock * 100 + index,
                    "traded_value": close * (10_000 + stock * 100 + index),
                    "corporate_action_flag": False,
                }
            )
            price = close
    return pd.DataFrame(rows)


def test_forward_target_requires_consecutive_clean_sessions():
    market = _panel(sessions=50, stocks=2)
    affected_isin = "INE000000000"
    affected_date = pd.bdate_range("2025-01-02", periods=50)[35]
    market.loc[
        market["isin"].eq(affected_isin) & market["date"].eq(affected_date),
        "corporate_action_flag",
    ] = True
    frame = build_forecast_frame(market)
    prior_date = pd.bdate_range("2025-01-02", periods=50)[34]
    target = frame.loc[
        frame["isin"].eq(affected_isin) & frame["date"].eq(prior_date),
        "target_1",
    ].iloc[0]
    assert np.isnan(target)


def test_walk_forward_cutoffs_precede_every_test_session():
    settings = ForecastConfig(
        horizons=(1, 3),
        evaluation_sessions=20,
        refit_every_sessions=5,
        training_sessions=140,
        minimum_training_sessions=60,
        minimum_training_rows=2_000,
    )
    latest, evaluation, metrics = fit_forecasts(_panel(), settings)
    assert set(latest["horizon"]) == {1, 3}
    assert len(metrics) == 2
    assert (evaluation["training_cutoff_session"] < evaluation["session_number"]).all()
    assert evaluation[["predicted_return", "lower_return", "upper_return"]].notna().all().all()
    assert (evaluation["lower_return"] <= evaluation["upper_return"]).all()
