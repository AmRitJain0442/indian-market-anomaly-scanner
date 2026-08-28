"""Strategy interface and generated-return schema."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class Strategy(ABC):
    name: str
    execution_class: str
    parameters: dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def generate_returns(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Return one row per observed session with signal and gross return."""

    @property
    def parameter_text(self) -> str:
        import json

        return json.dumps(self.parameters, sort_keys=True, separators=(",", ":"))


OUTPUT_COLUMNS = [
    "date",
    "isin",
    "symbol",
    "signal",
    "gross_return",
    "entry_date",
    "entry_price",
    "exit_date",
    "exit_price",
]


def output_frame(
    frame: pd.DataFrame,
    signal: pd.Series,
    gross_return: pd.Series,
    *,
    entry_date: pd.Series | None = None,
    entry_price: pd.Series | None = None,
    exit_date: pd.Series | None = None,
    exit_price: pd.Series | None = None,
) -> pd.DataFrame:
    result = frame[["date", "isin", "symbol"]].copy()
    result["signal"] = signal.fillna(0.0)
    result["gross_return"] = gross_return
    result["entry_date"] = frame["date"] if entry_date is None else entry_date
    result["entry_price"] = frame["open"] if entry_price is None else entry_price
    result["exit_date"] = frame["date"] if exit_date is None else exit_date
    result["exit_price"] = frame["close"] if exit_price is None else exit_price
    invalid = result["gross_return"].isna() | result["entry_price"].isna() | result["exit_price"].isna()
    result.loc[invalid, "signal"] = 0.0
    result.loc[result["signal"].eq(0), "gross_return"] = 0.0
    return result[OUTPUT_COLUMNS]

