"""Liquidity helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd


def liquidity_log(values: pd.Series) -> pd.Series:
    """Natural log of positive daily value, safe for plotting."""
    return np.log(values.where(values > 0))

