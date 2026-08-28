"""Transparent basis-point transaction cost model."""

from __future__ import annotations

import pandas as pd


def apply_round_trip_cost(
    gross_return: pd.Series,
    active: pd.Series,
    one_way_bps: float,
) -> pd.Series:
    return gross_return - active.astype(float) * (2.0 * one_way_bps / 10_000.0)

