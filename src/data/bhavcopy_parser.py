"""Normalize legacy and UDiFF NSE cash-market bhavcopies."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from config import ResearchConfig
from src.data.nse_downloader import DownloadedSession

NORMALIZED_COLUMNS = [
    "date",
    "symbol",
    "isin",
    "company_name",
    "series",
    "open",
    "high",
    "low",
    "close",
    "last_price",
    "previous_close",
    "volume",
    "traded_value",
    "number_of_trades",
    "delivery_quantity",
    "delivery_percentage",
    "instrument_type",
]

UDIFF_MAP = {
    "TradDt": "date",
    "TckrSymb": "symbol",
    "ISIN": "isin",
    "FinInstrmNm": "company_name",
    "SctySrs": "series",
    "OpnPric": "open",
    "HghPric": "high",
    "LwPric": "low",
    "ClsPric": "close",
    "LastPric": "last_price",
    "PrvsClsgPric": "previous_close",
    "TtlTradgVol": "volume",
    "TtlTrfVal": "traded_value",
    "TtlNbOfTxsExctd": "number_of_trades",
    "FinInstrmTp": "instrument_type",
}

LEGACY_MAP = {
    "TIMESTAMP": "date",
    "SYMBOL": "symbol",
    "ISIN": "isin",
    "SERIES": "series",
    "OPEN": "open",
    "HIGH": "high",
    "LOW": "low",
    "CLOSE": "close",
    "LAST": "last_price",
    "PREVCLOSE": "previous_close",
    "TOTTRDQTY": "volume",
    "TOTTRDVAL": "traded_value",
    "TOTALTRADES": "number_of_trades",
}


def _read_zip(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise ValueError(f"Expected one CSV in {path}, found {csv_names}")
        with archive.open(csv_names[0]) as handle:
            return pd.read_csv(handle, low_memory=False)


def parse_bhavcopy(path: Path, config: ResearchConfig) -> pd.DataFrame:
    raw = _read_zip(path)
    mapping = UDIFF_MAP if "TradDt" in raw.columns else LEGACY_MAP
    missing = {"date", "symbol", "isin", "series", "open", "high", "low", "close", "volume"} - set(mapping.values())
    if missing:
        raise ValueError(f"Parser mapping is incomplete: {sorted(missing)}")
    frame = raw.rename(columns=mapping)
    for column in NORMALIZED_COLUMNS:
        if column not in frame:
            frame[column] = np.nan
    frame = frame[NORMALIZED_COLUMNS].copy()
    frame["company_name"] = frame["company_name"].fillna(frame["symbol"])
    frame["instrument_type"] = frame["instrument_type"].fillna("STK")
    date_format = "%Y-%m-%d" if mapping is UDIFF_MAP else "%d-%b-%Y"
    frame["date"] = pd.to_datetime(frame["date"], format=date_format, errors="coerce")
    for column in (
        "open",
        "high",
        "low",
        "close",
        "last_price",
        "previous_close",
        "volume",
        "traded_value",
        "number_of_trades",
        "delivery_quantity",
        "delivery_percentage",
    ):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["symbol"] = frame["symbol"].astype("string").str.strip()
    frame["isin"] = frame["isin"].astype("string").str.strip()
    frame["series"] = frame["series"].astype("string").str.strip().str.upper()

    ordinary = frame["isin"].str.startswith("INE", na=False)
    allowed_series = frame["series"].isin(config.ordinary_equity_series)
    return frame.loc[ordinary & allowed_series].reset_index(drop=True)


def validate_market_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Validate prices, remove unusable rows, and flag discontinuities."""
    work = frame.copy()
    invalid = (
        work[["date", "symbol", "isin"]].isna().any(axis=1)
        | (work[["open", "high", "low", "close"]] <= 0).any(axis=1)
        | (work["volume"] < 0)
        | (work["high"] < work[["open", "close"]].max(axis=1))
        | (work["low"] > work[["open", "close"]].min(axis=1))
        | (work["high"] < work["low"])
    )
    duplicates = work.duplicated(["date", "isin"], keep="last")
    report = {
        "input_rows": int(len(work)),
        "invalid_ohlcv_rows": int(invalid.sum()),
        "duplicate_date_isin_rows": int(duplicates.sum()),
    }
    work = work.loc[~invalid & ~duplicates].sort_values(["isin", "date"]).copy()
    computed_cc = work.groupby("isin", sort=False)["close"].pct_change(fill_method=None)
    exchange_cc = work["close"] / work["previous_close"] - 1.0
    work["raw_close_return"] = exchange_cc.where(work["previous_close"].gt(0), computed_cc)
    work["corporate_action_flag"] = work["raw_close_return"].abs().gt(0.30)
    work["circuit_like_flag"] = (
        work["open"].eq(work["high"])
        & work["high"].eq(work["low"])
        & work["low"].eq(work["close"])
    )
    report["extreme_discontinuity_rows"] = int(work["corporate_action_flag"].sum())
    report["circuit_like_rows"] = int(work["circuit_like_flag"].sum())
    report["output_rows"] = int(len(work))
    return work.reset_index(drop=True), report


def build_market_dataset(
    sessions: list[DownloadedSession],
    config: ResearchConfig,
) -> tuple[pd.DataFrame, dict]:
    frames = [parse_bhavcopy(item.path, config) for item in sessions]
    combined = pd.concat(frames, ignore_index=True)
    market, report = validate_market_data(combined)
    config.processed_dir.mkdir(parents=True, exist_ok=True)
    market.to_parquet(config.processed_dir / "equity_daily.parquet", index=False)
    calendar = pd.DataFrame({"date": sorted(market["date"].drop_duplicates())})
    calendar.to_parquet(config.processed_dir / "trading_calendar.parquet", index=False)
    (config.processed_dir / "validation_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return market, report
