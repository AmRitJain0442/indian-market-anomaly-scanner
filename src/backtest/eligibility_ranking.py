"""Strict EQ-history screening and budget-aware research ranks, not trade approval."""

from __future__ import annotations

from html.parser import HTMLParser
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR

import numpy as np
import pandas as pd

from src.backtest.combination_ranking import rank_stock_strategy_combinations
from src.backtest.intraday_pilot import estimate_charges


class BrokerTableParser(HTMLParser):
    """Read only explicit MIS rows from Zerodha's public equity margin table."""

    def __init__(self):
        super().__init__()
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "tr" and "data-scrip" in attributes:
            self.rows.append({
                "symbol": attributes["data-scrip"],
                "mis_margin_percent": float(attributes["data-mis_margin"]),
                "listed_mis_multiplier": float(attributes["data-mis_multiplier"]),
            })


def broker_table(html: str) -> pd.DataFrame:
    parser = BrokerTableParser()
    parser.feed(html)
    frame = pd.DataFrame(parser.rows)
    if frame.empty or frame.symbol.duplicated().any():
        raise ValueError("Broker table missing or contains ambiguous symbols")
    return frame


def audit_trade_series(trades: pd.DataFrame, series_map: pd.Series) -> pd.DataFrame:
    """Check both legs by ISIN/session and correct initial-capital drawdown."""
    if series_map.index.has_duplicates:
        raise ValueError("Series history has duplicate ISIN/session keys")
    if trades.empty:
        return pd.DataFrame(columns=["isin", "audited_trades", "restricted_trades", "unknown_series_trades",
                                     "non_eq_trades", "short_trades", "corrected_drawdown"])
    work = trades.sort_values(["isin", "entry_date"]).copy()
    entry_keys = pd.MultiIndex.from_arrays([work["isin"], work["entry_date"]])
    exit_keys = pd.MultiIndex.from_arrays([work["isin"], work["exit_date"]])
    entry = series_map.reindex(entry_keys).to_numpy()
    exit_series = series_map.reindex(exit_keys).to_numpy()
    work["restricted"] = np.isin(entry, ["BE", "BZ"]) | np.isin(exit_series, ["BE", "BZ"])
    work["unknown"] = pd.isna(entry) | pd.isna(exit_series)
    work["non_eq"] = (entry != "EQ") | (exit_series != "EQ")
    work["short"] = work.side.eq("SHORT")
    # Missing/no-trade sessions have zero return and do not alter a running peak.
    work["growth"] = 1 + work.net_return
    work["path"] = work.groupby("isin", sort=False).growth.cumprod()
    peaks = work.groupby("isin", sort=False).path.cummax().clip(lower=1.0)
    work["drawdown"] = work.path / peaks - 1
    audit = work.groupby("isin", as_index=False).agg(
        audited_trades=("entry_date", "size"), restricted_trades=("restricted", "sum"),
        unknown_series_trades=("unknown", "sum"), non_eq_trades=("non_eq", "sum"),
        short_trades=("short", "sum"), corrected_drawdown=("drawdown", "min"),
    )
    return audit


def screen_and_rank(results: pd.DataFrame, audit: pd.DataFrame, latest: pd.DataFrame,
                    recent: pd.DataFrame, broker: pd.DataFrame, budget: float = 1000.0) -> pd.DataFrame:
    """Keep historical ranking economics separate from today's cash-cap screen."""
    if not np.isfinite(budget) or budget <= 0:
        raise ValueError("Budget must be finite and positive")
    frame = results.merge(audit, on=["isin", "strategy"], how="left", validate="one_to_one")
    counts = ["audited_trades", "restricted_trades", "unknown_series_trades", "non_eq_trades", "short_trades"]
    frame[counts] = frame[counts].fillna(0).astype(int)
    if not frame.audited_trades.eq(frame.number_of_trades).all():
        raise ValueError("Trade counts do not reconcile with original ranking")
    frame["original_max_drawdown"] = frame.max_drawdown
    frame["max_drawdown"] = frame.corrected_drawdown.fillna(0)
    status = latest[["isin", "symbol", "series", "close", "tick_size"]].rename(columns={
        "symbol": "current_symbol", "series": "current_series", "close": "snapshot_price",
    })
    frame = frame.merge(status, on="isin", how="left", validate="many_to_one")
    frame = frame.merge(recent, on="isin", how="left", validate="many_to_one")
    frame = frame.merge(broker, left_on="current_symbol", right_on="symbol", how="left", suffixes=("", "_broker"), validate="many_to_one")
    frame["broker_listed"] = frame.mis_margin_percent.gt(0) & frame.listed_mis_multiplier.ge(1)
    frame["budget"] = budget
    frame["notional_cap"] = budget * 0.5
    frame["cash_cap_shares"] = np.floor((budget * 0.5) / frame.snapshot_price.where(frame.snapshot_price.gt(0))).fillna(0).astype(int)
    risk_rows = []
    for row in status.itertuples(index=False):
        price, tick = row.snapshot_price, row.tick_size
        sizing = {"isin": row.isin, "illustrative_risk_shares": None, "illustrative_planned_loss": None}
        if np.isfinite(price) and 100 <= price <= budget * 0.5 and pd.notna(tick) and tick > 0:
            long_stop = float((Decimal(str(price)) * Decimal("0.99") / Decimal(str(tick))).to_integral_value(rounding=ROUND_CEILING) * Decimal(str(tick)))
            short_stop = float((Decimal(str(price)) * Decimal("1.01") / Decimal(str(tick))).to_integral_value(rounding=ROUND_FLOOR) * Decimal(str(tick)))
            sizing["illustrative_risk_shares"] = 0
            for quantity in range(int((budget * 0.5) // price), 0, -1):
                allowance = quantity * max(0.002 * price, 2 * tick)
                long_risk = quantity * abs(price - long_stop) + estimate_charges("LONG", quantity, price, long_stop)["total"] + allowance
                short_risk = quantity * abs(price - short_stop) + estimate_charges("SHORT", quantity, price, short_stop)["total"] + allowance
                risk = max(long_risk, short_risk)
                if risk <= budget * 0.005 + 1e-9:
                    sizing.update(illustrative_risk_shares=quantity, illustrative_planned_loss=risk)
                    break
        risk_rows.append(sizing)
    frame = frame.merge(pd.DataFrame(risk_rows), on="isin", how="left", validate="many_to_one")
    frame["risk_budget"] = budget * 0.005
    frame["intraday"] = frame.strategy.ne("close_to_open")
    frame["screen_reasons"] = ""
    rules = [
        (~frame.current_series.eq("EQ"), "Latest NSE series is not EQ or is unavailable"),
        (frame.restricted_trades.gt(0), "Historical trades include BE or BZ"),
        (frame.unknown_series_trades.gt(0), "Historical leg series is missing"),
        (frame.non_eq_trades.gt(frame.restricted_trades + frame.unknown_series_trades), "Historical leg is not EQ"),
        (frame.audited_trades.eq(0), "No historical trades"),
    ]
    for mask, reason in rules:
        frame.loc[mask, "screen_reasons"] += reason + " | "
    frame["screen_reasons"] = frame.screen_reasons.str.rstrip(" |")
    frame["eq_screen_pass"] = frame.screen_reasons.eq("")
    frame["worklist_reasons"] = frame.screen_reasons
    practical = [
        (~frame.broker_listed, "Not listed in dated Zerodha MIS table"),
        (~frame.intraday, "Overnight strategy needs separate delivery and settlement review"),
        (frame.snapshot_price.lt(100) | frame.snapshot_price.isna(), "Below INR 100 pilot price floor or missing price"),
        (frame.cash_cap_shares.lt(1), "One share exceeds INR 500 cash cap"),
        (frame.snapshot_price.between(100, budget * 0.5) & ~frame.illustrative_risk_shares.ge(1), "No whole share fits illustrative 1% stop and INR 5 planned-risk limit, or tick is missing"),
        (frame.recent_sessions.ne(20) | frame.recent_median_value.lt(500_000_000) | frame.recent_median_value.isna(), "Fails 20-session INR 50 crore liquidity screen"),
        (frame.coverage_ratio.lt(0.95) | frame.number_of_trades.lt(20), "Historical coverage below 95% or fewer than 20 trades"),
    ]
    for mask, reason in practical:
        frame.loc[mask, "worklist_reasons"] += " | " + reason
    frame["worklist_reasons"] = frame.worklist_reasons.str.strip(" |")
    frame["worklist_pass"] = frame.worklist_reasons.eq("")
    frame["research_score"] = np.nan
    frame["eq_rank"] = pd.Series(pd.NA, index=frame.index, dtype="Int64")
    frame["worklist_rank"] = pd.Series(pd.NA, index=frame.index, dtype="Int64")
    accepted = frame.loc[frame.eq_screen_pass].copy()
    if len(accepted):
        accepted = accepted.drop(columns=["combination_rank", "profit_rank", "comparable_rank"], errors="ignore")
        ranked = rank_stock_strategy_combinations(accepted)
        keys = pd.MultiIndex.from_frame(frame[["isin", "strategy"]])
        lookup = ranked.set_index(["isin", "strategy"])
        frame["eq_rank"] = pd.array(lookup.combination_rank.reindex(keys).to_numpy(), dtype="Int64")
        frame["research_score"] = lookup.combination_score.reindex(keys).to_numpy()
        indices = frame.loc[frame.worklist_pass].sort_values("eq_rank").index
        frame.loc[indices, "worklist_rank"] = pd.array(range(1, len(indices) + 1), dtype="Int64")
    frame["execution_validated"] = False
    return frame.sort_values(["eq_rank", "symbol", "strategy"], na_position="last").reset_index(drop=True)
