"""Evaluation-window and trading-calendar utilities."""

from __future__ import annotations

import pandas as pd


def evaluation_window(market: pd.DataFrame, sessions: int) -> pd.DatetimeIndex:
    dates = pd.DatetimeIndex(sorted(market["date"].dropna().unique()))
    if len(dates) < sessions:
        raise ValueError(f"Need {sessions} sessions, only {len(dates)} are available")
    return dates[-sessions:]


def add_calendar_positions(frame: pd.DataFrame, calendar: pd.DatetimeIndex) -> pd.DataFrame:
    work = frame.copy()
    cal = pd.DataFrame({"date": calendar})
    cal["month"] = cal["date"].dt.to_period("M")
    cal["month_from_start"] = cal.groupby("month").cumcount() + 1
    cal["month_from_end"] = cal.groupby("month")["date"].transform("size") - cal.groupby("month").cumcount()
    cal["weekday"] = cal["date"].dt.dayofweek
    return work.merge(
        cal[["date", "month_from_start", "month_from_end", "weekday"]],
        on="date",
        how="left",
    )

