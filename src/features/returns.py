"""Look-ahead-safe daily return features."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.calendar import add_calendar_positions


def add_return_features(market: pd.DataFrame) -> pd.DataFrame:
    work = market.sort_values(["isin", "date"]).copy()
    calendar = pd.DatetimeIndex(sorted(work["date"].unique()))
    session_number = pd.Series(range(len(calendar)), index=calendar)
    work["session_number"] = work["date"].map(session_number)
    grouped = work.groupby("isin", sort=False)

    work["previous_observed_close"] = grouped["close"].shift(1)
    work["previous_session_number"] = grouped["session_number"].shift(1)
    work["next_open"] = grouped["open"].shift(-1)
    work["next_date"] = grouped["date"].shift(-1)
    work["next_session_number"] = grouped["session_number"].shift(-1)
    previous_consecutive = work["session_number"].sub(work["previous_session_number"]).eq(1)
    next_consecutive = work["next_session_number"].sub(work["session_number"]).eq(1)

    work["prev_close"] = work["previous_observed_close"].where(previous_consecutive)
    work["ret_overnight"] = (work["open"] / work["prev_close"] - 1.0).where(previous_consecutive)
    work["ret_intraday"] = work["close"] / work["open"] - 1.0
    work["ret_cc"] = (work["close"] / work["prev_close"] - 1.0).where(previous_consecutive)
    work["ret_close_to_next_open"] = (work["next_open"] / work["close"] - 1.0).where(next_consecutive)
    work["range_pct"] = (work["high"] - work["low"]) / work["open"]

    close_lag5 = grouped["close"].shift(5)
    session_lag5 = grouped["session_number"].shift(5)
    work["ret_5d"] = (work["close"] / close_lag5 - 1.0).where(
        work["session_number"].sub(session_lag5).eq(5)
    )
    work["volume_ma20"] = grouped["volume"].transform(
        lambda values: values.shift(1).rolling(20, min_periods=20).mean()
    )
    work["volume_ratio"] = work["volume"] / work["volume_ma20"].replace(0, np.nan)
    work["previous_cc_signal"] = grouped["ret_cc"].shift(1).where(previous_consecutive)
    work["previous_5d_signal"] = grouped["ret_5d"].shift(1).where(previous_consecutive)
    work["previous_volume_ratio"] = grouped["volume_ratio"].shift(1).where(previous_consecutive)

    # Today's extreme discontinuity invalidates close-derived signals and returns.
    bad_today = work["corporate_action_flag"]
    bad_next = grouped["corporate_action_flag"].shift(-1, fill_value=False)
    for column in ("ret_overnight", "ret_cc", "ret_intraday"):
        work.loc[bad_today, column] = np.nan
    work.loc[bad_today | bad_next, "ret_close_to_next_open"] = np.nan
    work.loc[bad_today, "ret_5d"] = np.nan
    return add_calendar_positions(work, calendar)
