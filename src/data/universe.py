"""Historical universe and stock-level diagnostics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import ResearchConfig


def build_security_master(
    market: pd.DataFrame,
    evaluation_dates: pd.DatetimeIndex,
    config: ResearchConfig,
) -> pd.DataFrame:
    evaluation = market[market["date"].isin(evaluation_dates)].copy()
    total_sessions = len(evaluation_dates)
    evaluation["near_zero_volume"] = evaluation["volume"].le(config.near_zero_volume)
    latest = (
        evaluation.sort_values("date")
        .groupby("isin", as_index=False)
        .tail(1)[["isin", "symbol", "company_name", "series"]]
    )
    stats = evaluation.groupby("isin", as_index=False).agg(
        first_traded_date=("date", "min"),
        last_traded_date=("date", "max"),
        sessions_available=("date", "nunique"),
        median_daily_value=("traded_value", "median"),
        median_volume=("volume", "median"),
        pct_near_zero_volume=("near_zero_volume", "mean"),
        average_daily_range=("high", lambda x: np.nan),
        circuit_like_sessions=("circuit_like_flag", "sum"),
        corporate_action_observations=("corporate_action_flag", "sum"),
    )
    ranges = (
        evaluation.assign(range_pct=(evaluation["high"] - evaluation["low"]) / evaluation["open"])
        .groupby("isin")["range_pct"]
        .mean()
    )
    stats["average_daily_range"] = stats["isin"].map(ranges)
    stats["coverage_ratio"] = stats["sessions_available"] / total_sessions
    stats["liquidity_flag"] = np.where(
        stats["median_daily_value"].fillna(0) < config.low_liquidity_value_inr,
        "LOW",
        "OK",
    )
    stats["coverage_flag"] = np.where(
        stats["coverage_ratio"] >= config.comparable_coverage_ratio,
        "FULL",
        "PARTIAL",
    )
    stats["new_listing_flag"] = stats["first_traded_date"].gt(evaluation_dates.min())
    stats["suspension_flag"] = stats["sessions_available"].lt(total_sessions)
    master = latest.merge(stats, on="isin", how="inner").sort_values("symbol")
    master.to_parquet(config.processed_dir / "security_master.parquet", index=False)
    return master.reset_index(drop=True)

