"""Causal watchlists and cached public minute data for a labeled pilot diagnostic."""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests

IST = ZoneInfo("Asia/Kolkata")


def watchlist(market: pd.DataFrame, session: pd.Timestamp, equity: float) -> list[dict]:
    """Freeze five names using only twenty completed sessions before this day."""
    session = pd.Timestamp(session).normalize()
    dates = pd.DatetimeIndex(sorted(market.date.unique()))
    preceding = dates[dates < session][-20:]
    if len(preceding) != 20:
        raise ValueError("Watchlist needs twenty preceding exchange sessions")
    history = market.loc[market.date.isin(preceding)].copy()
    if history.duplicated(["date", "isin"]).any():
        raise ValueError("Ambiguous historical ISIN/session identity")
    stats = history.groupby("isin").agg(
        history_sessions=("date", "nunique"),
        median_daily_value=("traded_value", "median"),
    )
    last = history.loc[history.date.eq(preceding[-1])].set_index("isin")
    ranked = last.join(stats)
    ranked = ranked.loc[
        ranked.history_sessions.eq(20)
        & ranked.series.eq("EQ")
        & ranked.close.between(100.0, equity * 0.5)
        & ranked.median_daily_value.ge(500_000_000.0)
    ].sort_values(["median_daily_value", "symbol"], ascending=[False, True]).head(5)
    today = market.loc[market.date.eq(session)].set_index("isin")
    if today.index.duplicated().any():
        raise ValueError("Ambiguous current ISIN/session identity")
    month_start = session.replace(day=1)
    prior_month = market.loc[market.date.lt(month_start)]
    month_end = prior_month.loc[prior_month.date.eq(prior_month.date.max())].set_index("isin")
    result = []
    for priority, (isin, row) in enumerate(ranked.iterrows(), start=1):
        current = today.loc[isin] if isin in today.index else None
        month_close = float(month_end.loc[isin, "close"]) if isin in month_end.index else None
        tick = (0.01 if month_close < 250 else 0.05) if month_close is not None else None
        reference = float(row.close)
        exchange_reference = float(current.previous_close) if current is not None else None
        reference_matches = bool(
            exchange_reference is not None and np.isfinite(exchange_reference)
            and abs(exchange_reference - reference) <= 0.0051
        )
        result.append({
            "date": session.date().isoformat(), "priority": priority,
            "symbol": str(current.symbol if current is not None else row.symbol),
            "isin": str(isin),
            "series": str(current.series) if current is not None else "UNKNOWN",
            "reference": reference,
            "exchange_reference": exchange_reference,
            "reference_matches": reference_matches,
            "official_open": float(current.open) if current is not None else None,
            "median_daily_value": float(row.median_daily_value),
            "history_sessions": int(row.history_sessions),
            "history_start": preceding[0].date().isoformat(),
            "history_end": preceding[-1].date().isoformat(),
            "tick_size": tick,
            "tick_reference_date": prior_month.date.max().date().isoformat() if len(prior_month) else None,
            "tick_reference_close": month_close,
            "broker_permission": "UNVERIFIED",
            "corporate_action_notice_check": "UNVERIFIED",
        })
    return result


def decode_chart(payload: dict, start: date, end: date) -> pd.DataFrame:
    chart = payload.get("chart", {})
    if chart.get("error") or not chart.get("result"):
        raise ValueError(f"Minute provider returned no result: {chart.get('error')}")
    item = chart["result"][0]
    meta = item.get("meta", {})
    if meta.get("currency") != "INR" or meta.get("dataGranularity") != "1m":
        raise ValueError("Expected INR one-minute unadjusted candles")
    quote = item["indicators"]["quote"][0]
    frame = pd.DataFrame({name: quote.get(name, []) for name in ("open", "high", "low", "close", "volume")})
    frame["timestamp"] = pd.to_datetime(item.get("timestamp", []), unit="s", utc=True).tz_convert(IST)
    lower = pd.Timestamp(start, tz=IST)
    upper = pd.Timestamp(end, tz=IST)
    # Some responses append the latest quote outside the requested interval.
    frame = frame.loc[frame.timestamp.ge(lower) & frame.timestamp.lt(upper)]
    frame = frame.loc[frame.timestamp.dt.time.ge(datetime.strptime("09:15", "%H:%M").time())]
    frame = frame.loc[frame.timestamp.dt.time.lt(datetime.strptime("15:30", "%H:%M").time())]
    return frame.set_index("timestamp").sort_index()


class MinuteHistory:
    """Small public chart downloads. No broker keys or subscriptions are used."""

    def __init__(self, cache: Path):
        self.cache = cache
        self.cache.mkdir(parents=True, exist_ok=True)
        self.manifest: list[dict] = []

    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        frames = []
        cursor = start
        while cursor < end:
            next_date = min(cursor + timedelta(days=7), end)
            cache_name = f"{symbol}_{cursor}_{next_date}_1m.json"
            cache_path = self.cache / cache_name
            params = {
                "period1": int(datetime.combine(cursor, datetime.min.time(), IST).timestamp()),
                "period2": int(datetime.combine(next_date, datetime.min.time(), IST).timestamp()),
                "interval": "1m",
            }
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.NS"
            prepared = requests.Request("GET", url, params=params).prepare().url
            if cache_path.exists():
                raw = cache_path.read_bytes()
            else:
                response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
                response.raise_for_status()
                raw = response.content
                decode_chart(json.loads(raw), cursor, next_date)
                cache_path.write_bytes(raw)
            payload = json.loads(raw)
            frame = decode_chart(payload, cursor, next_date)
            if payload["chart"]["result"][0]["meta"].get("symbol") != f"{symbol}.NS":
                raise ValueError("Minute provider returned the wrong symbol")
            self.manifest.append({
                "symbol": symbol, "start": str(cursor), "end_exclusive": str(next_date),
                "url": prepared, "cache_file": cache_name,
                "sha256": hashlib.sha256(raw).hexdigest(), "bars": len(frame),
            })
            frames.append(frame)
            cursor = next_date
        if not frames:
            raise ValueError("Empty requested range")
        result = pd.concat(frames).sort_index()
        if result.index.duplicated().any():
            raise ValueError(f"Duplicate minute timestamps for {symbol}")
        return result
