"""Pure, deliberately approximate minute-bar evaluator for the small-capital pilot.

This is not a quote replay. It assumes broker permission, cannot check spreads or
depth, and substitutes a completed 09:15 candle and a 09:17 opening fill for the
proposed 09:16 quote decision. Missing candles never imply successful liquidation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP
from typing import Mapping, Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PilotConfig:
    notional_fraction: float = 0.50
    planned_risk_fraction: float = 0.005
    stop_fraction: float = 0.01
    minimum_gap: float = 0.01
    minimum_target_distance: float = 0.0075
    entry_limit_fraction: float = 0.0005
    slippage_bps: float = 5.0
    allowance_fraction: float = 0.002
    maximum_drawdown: float = 0.05


ASSUMPTIONS = [
    "MINUTE_BAR_APPROXIMATION, not a replay of the proposed quote strategy",
    "Decision uses the completed 09:15 minute close at 09:16 IST",
    "Entry uses the 09:17 minute open with adverse slippage and tick rounding",
    "No measured bid/ask, spread, depth, queue, or one-second execution latency",
    "Broker intraday permission is assumed, not historically confirmed",
    "Caller supplies the session-specific historical tick size",
    "Stops round toward entry and targets round to the nearest tick, half up",
    "Stop wins ambiguous intrabar stop/target ordering unless the open resolves it",
    "Targets require a price strictly through the limit and fill at the limit",
    "Target limits have no extra adverse slippage below their limit price",
    "Missing candles after entry leave an unresolved position and block new entries",
]


def _d(value: float | int) -> Decimal:
    return Decimal(str(value))


def _positive(value: float, name: str) -> float:
    value = float(value)
    if not np.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def _direction(side: str) -> int:
    if side not in ("LONG", "SHORT"):
        raise ValueError("side must be LONG or SHORT")
    return 1 if side == "LONG" else -1


def _tick(price: float, tick_size: float, rounding: str) -> float:
    return float((_d(price) / _d(tick_size)).to_integral_value(rounding=rounding) * _d(tick_size))


def estimate_charges(side: str, quantity: int, entry_price: float, exit_price: float) -> dict:
    """Frozen indicative Zerodha cash-intraday fees, not a contract-note engine.

    Every component, including each brokerage leg, is rounded upward to one paisa.
    GST uses unrounded brokerage, exchange, SEBI and IPFT charges. STT is rounded
    upward to a paisa here, not aggregated under a broker's contract-note rules.
    """
    direction = _direction(side)
    if isinstance(quantity, bool) or int(quantity) != quantity or quantity < 0:
        raise ValueError("quantity must be a nonnegative integer")
    _positive(entry_price, "entry_price")
    _positive(exit_price, "exit_price")
    entry = _d(quantity) * _d(entry_price)
    exit_value = _d(quantity) * _d(exit_price)
    buy, sell = (entry, exit_value) if direction == 1 else (exit_value, entry)
    turnover = entry + exit_value
    brokerage_entry = min(Decimal("20"), entry * Decimal("0.0003"))
    brokerage_exit = min(Decimal("20"), exit_value * Decimal("0.0003"))
    exchange = turnover * Decimal("0.0000307")
    sebi = turnover * Decimal("0.000001")
    ipft = turnover * Decimal("0.000000001")  # INR 0.01 per crore
    raw = {
        "brokerage_entry": brokerage_entry,
        "brokerage_exit": brokerage_exit,
        "stt": sell * Decimal("0.00025"),
        "exchange": exchange,
        "sebi": sebi,
        "ipft": ipft,
        "stamp_duty": buy * Decimal("0.00003"),
        "gst": (brokerage_entry + brokerage_exit + exchange + sebi + ipft) * Decimal("0.18"),
    }
    rounded = {key: value.quantize(Decimal("0.01"), rounding=ROUND_CEILING) for key, value in raw.items()}
    return {**{key: float(value) for key, value in rounded.items()}, "total": float(sum(rounded.values()))}


def _bars(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"open", "high", "low", "close"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Missing bar columns: {sorted(required - set(frame.columns))}")
    work = frame.copy()
    timestamps = work.pop("timestamp") if "timestamp" in work else work.index
    index = pd.DatetimeIndex(pd.to_datetime(timestamps))
    index = index.tz_localize("Asia/Kolkata") if index.tz is None else index.tz_convert("Asia/Kolkata")
    if index.has_duplicates or index.isna().any():
        raise ValueError("Minute timestamps must be unique and nonmissing")
    work.index = index
    work = work.sort_index()
    if len(work) and len(set(work.index.date)) != 1:
        raise ValueError("evaluate_candidate requires exactly one trading session")
    return work


def _valid_bar(row: pd.Series) -> bool:
    values = row[["open", "high", "low", "close"]].to_numpy(dtype=float)
    return bool(np.isfinite(values).all() and (values > 0).all()
                and row.low <= min(row.open, row.close)
                and row.high >= max(row.open, row.close) and row.low <= row.high)


def _distance(direction: int, reference: float, entry: float) -> float:
    return direction * (reference / entry - 1.0)


def _position(side: str, entry: float, reference: float, equity: float, tick_size: float,
              cfg: PilotConfig, maximum_quantity: int | None = None) -> dict:
    direction = _direction(side)
    stop = _tick(entry * (1 - direction * cfg.stop_fraction), tick_size,
                 ROUND_CEILING if direction == 1 else ROUND_FLOOR)
    target = _tick(reference, tick_size, ROUND_HALF_UP)
    if stop <= 0 or direction * (entry - stop) <= 0 or _distance(direction, target, entry) < cfg.minimum_target_distance - 1e-12:
        return {"quantity": 0, "stop": stop, "target": target}
    maximum = int((_d(equity) * _d(cfg.notional_fraction) / _d(entry)).to_integral_value(rounding=ROUND_FLOOR))
    if maximum_quantity is not None:
        maximum = min(maximum, maximum_quantity)
    for quantity in range(maximum, 0, -1):
        fees = estimate_charges(side, quantity, entry, stop)
        allowance = quantity * max(cfg.allowance_fraction * entry, 2 * tick_size)
        planned = quantity * abs(entry - stop) + fees["total"] + allowance
        if planned <= equity * cfg.planned_risk_fraction + 1e-9:
            return {"quantity": quantity, "stop": stop, "target": target,
                    "notional": quantity * entry, "planned_loss": planned,
                    "estimated_stop_charges": fees, "adverse_fill_allowance": allowance}
    return {"quantity": 0, "stop": stop, "target": target}


def _slipped(price: float, direction: int, tick_size: float, cfg: PilotConfig, *, entering: bool) -> float:
    adverse_direction = direction if entering else -direction
    return _tick(price * (1 + adverse_direction * cfg.slippage_bps / 10_000), tick_size,
                 ROUND_CEILING if adverse_direction == 1 else ROUND_FLOOR)


def evaluate_candidate(
    bars: pd.DataFrame, side: str, reference: float, equity: float,
    tick_size: float, slippage_bps: float = 5.0, config: PilotConfig | None = None,
) -> dict:
    """Evaluate one candidate already passing the daily gap and universe filters.

    NOT_QUALIFIED is determined exclusively at 09:16 and allows another candidate.
    Once decision_qualified is true, every later failure consumes the day's attempt.
    exit_bar_time identifies an interval, not a reconstructed second-level fill.
    """
    direction = _direction(side)
    reference, equity, tick_size = (_positive(reference, "reference"), _positive(equity, "equity"), _positive(tick_size, "tick_size"))
    cfg = replace(config or PilotConfig(), slippage_bps=slippage_bps)
    if not np.isfinite(slippage_bps) or slippage_bps < 0:
        raise ValueError("slippage_bps must be finite and nonnegative")
    work = _bars(bars)
    result = {"status": "INCOMPLETE_DATA", "reason": "MISSING_DECISION_BAR", "side": side,
              "reference": reference, "tick_size": tick_size, "starting_equity": equity,
              "decision_qualified": False, "attempted": False, "quantity": 0,
              "gross_pnl": None, "net_pnl": None, "ending_equity": equity,
              "unresolved": False, "ambiguity_flags": [], "assumptions": ASSUMPTIONS.copy()}
    if work.empty:
        return result
    day = work.index[0].normalize()
    decision_bar = day + pd.Timedelta(hours=9, minutes=15)
    decision_at = day + pd.Timedelta(hours=9, minutes=16)
    entry_at = day + pd.Timedelta(hours=9, minutes=17)
    timed_exit = day + pd.Timedelta(hours=15)
    result.update(decision_time=decision_at.isoformat(), entry_time=entry_at.isoformat())
    if decision_bar not in work.index or not _valid_bar(work.loc[decision_bar]):
        return result
    decision_price = float(work.loc[decision_bar, "close"])
    result["decision_price"] = decision_price
    decision_position = _position(side, decision_price, reference, equity, tick_size, cfg)
    result["decision_quantity"] = decision_position["quantity"]
    if _distance(direction, reference, decision_price) < cfg.minimum_target_distance - 1e-12:
        return {**result, "status": "NOT_QUALIFIED", "reason": "DECISION_TARGET_DISTANCE"}
    if decision_position["quantity"] == 0:
        return {**result, "status": "NOT_QUALIFIED", "reason": "DECISION_RISK_OR_QUANTITY"}
    result.update(decision_qualified=True, attempted=True)
    if entry_at not in work.index or not _valid_bar(work.loc[entry_at]):
        return {**result, "status": "INCOMPLETE_DATA", "reason": "MISSING_ENTRY_BAR"}
    opening = float(work.loc[entry_at, "open"])
    entry = _slipped(opening, direction, tick_size, cfg, entering=True)
    result.update(entry_bar_open=opening, modeled_entry_price=entry)
    if direction * (entry / decision_price - 1) > cfg.entry_limit_fraction + 1e-12:
        return {**result, "status": "NO_FILL", "reason": "ENTRY_ADVERSE_LIMIT"}
    if _distance(direction, reference, entry) < cfg.minimum_target_distance - 1e-12:
        return {**result, "status": "NO_FILL", "reason": "ENTRY_TARGET_DISTANCE"}
    position = _position(side, entry, reference, equity, tick_size, cfg,
                         maximum_quantity=decision_position["quantity"])
    if position["quantity"] == 0:
        return {**result, "status": "NO_FILL", "reason": "ENTRY_RISK_OR_QUANTITY"}
    result.update(position)
    result["entry_price"] = entry
    quantity, stop, target = position["quantity"], position["stop"], position["target"]
    last_mark = entry

    def close(price: float, when: pd.Timestamp, reason: str) -> dict:
        charges = estimate_charges(side, quantity, entry, price)
        gross = direction * quantity * (price - entry)
        net = gross - charges["total"]
        return {**result, "status": "CLOSED", "reason": reason, "exit_price": price,
                "exit_bar_time": when.isoformat(), "charges": charges, "gross_pnl": gross,
                "net_pnl": net, "ending_equity": equity + net, "unresolved": False}

    for when in pd.date_range(entry_at, timed_exit, freq="min"):
        if when not in work.index or not _valid_bar(work.loc[when]):
            mark_charges = estimate_charges(side, quantity, entry, last_mark)
            return {**result, "status": "UNRESOLVED", "reason": "MISSING_POSITION_BAR",
                    "missing_bar_time": when.isoformat(), "unresolved": True,
                    "ending_equity": None, "last_observed_mark": last_mark,
                    "last_observed_marked_equity": equity + direction * quantity * (last_mark - entry) - mark_charges["total"],
                    "mark_is_stale": True}
        row = work.loc[when]
        opening = float(row.open)
        # Known opening prices resolve ordering before an unknown intrabar path.
        if direction * (opening - stop) <= 0:
            return close(_slipped(opening, direction, tick_size, cfg, entering=False), when, "STOP_GAP")
        if direction * (opening - target) > 1e-12:
            return close(target, when, "TARGET_TRADE_THROUGH")
        if when == timed_exit:
            return close(_slipped(opening, direction, tick_size, cfg, entering=False), when, "TIMED_EXIT")
        stop_hit = row.low <= stop if direction == 1 else row.high >= stop
        target_hit = row.high > target + 1e-12 if direction == 1 else row.low < target - 1e-12
        if stop_hit and target_hit:
            result["ambiguity_flags"].append("STOP_AND_TARGET_SAME_BAR_STOP_FIRST")
        if stop_hit:
            return close(_slipped(stop, direction, tick_size, cfg, entering=False), when, "STOP_FIRST" if target_hit else "STOP")
        if target_hit:
            return close(target, when, "TARGET_TRADE_THROUGH")
        last_mark = float(row.close)
    raise AssertionError("Timed exit loop did not return")


def simulate_session(
    session_date, candidates: Sequence[dict], bars_by_symbol: Mapping[str, pd.DataFrame],
    starting_equity: float = 1_000.0, config: PilotConfig | None = None, halted: bool = False,
) -> dict:
    """Select causally from an already frozen, ranked shortlist of at most five."""
    cfg = config or PilotConfig()
    equity = _positive(starting_equity, "starting_equity")
    date_string = pd.Timestamp(session_date).date().isoformat()
    base = {"date": date_string, "starting_equity": equity, "ending_equity": equity,
            "status": "HALTED" if halted else "NO_TRADE", "reason": "ACCOUNT_HALTED" if halted else "NO_QUALIFYING_CANDIDATE",
            "attempted": False, "quantity": 0, "net_pnl": 0.0, "gross_pnl": 0.0,
            "unresolved": False, "candidate_checks": [], "assumptions": ASSUMPTIONS.copy()}
    if halted:
        return base
    if len(candidates) > 5:
        raise ValueError("Pass only the frozen top-five shortlist")
    for rank, candidate in enumerate(candidates, 1):
        symbol = candidate["symbol"]
        if candidate.get("series") != "EQ":
            base["candidate_checks"].append({"symbol": symbol, "reason": "NON_EQ_OR_UNKNOWN_SERIES"})
            continue
        reference = _positive(candidate["reference"], "reference")
        gap = float(candidate["gap"]) if "gap" in candidate else _positive(candidate["official_open"], "official_open") / reference - 1
        if not np.isfinite(gap):
            base["candidate_checks"].append({"symbol": symbol, "reason": "UNKNOWN_GAP"})
            continue
        if abs(gap) < cfg.minimum_gap - 1e-12:
            base["candidate_checks"].append({"symbol": symbol, "reason": "GAP_BELOW_THRESHOLD"})
            continue
        side = "LONG" if gap < 0 else "SHORT"
        if symbol not in bars_by_symbol:
            return {**base, "symbol": symbol, "status": "INCOMPLETE_DATA", "reason": "MISSING_CANDIDATE_BARS", "net_pnl": None}
        bars = _bars(bars_by_symbol[symbol])
        if len(bars) and bars.index[0].date().isoformat() != date_string:
            raise ValueError("Candidate bars do not match session_date")
        checked = evaluate_candidate(bars, side, reference, equity, candidate["tick_size"], cfg.slippage_bps, cfg)
        base["candidate_checks"].append({"symbol": symbol, "status": checked["status"], "reason": checked["reason"]})
        if checked["status"] == "NOT_QUALIFIED":
            continue
        return {**base, **checked, "symbol": symbol, "isin": candidate.get("isin"), "gap": gap, "shortlist_rank": rank}
    return base


def simulate_pilot(sessions: Sequence[dict], initial_capital: float = 1_000.0, config: PilotConfig | None = None) -> dict:
    """Sequential realized ledger with no reuse of unresolved-position capital."""
    cfg = config or PilotConfig()
    equity = _positive(initial_capital, "initial_capital")
    peak = equity
    worst_drawdown = 0.0
    halt_reason = None
    daily = []
    unresolved = None
    incomplete = False
    previous_date = None
    for session in sessions:
        date_value = pd.Timestamp(session["date"]).date()
        if previous_date is not None and date_value <= previous_date:
            raise ValueError("Sessions must be unique and chronological")
        previous_date = date_value
        result = simulate_session(session["date"], session["candidates"], session["bars_by_symbol"], equity, cfg, halted=halt_reason is not None)
        if halt_reason:
            result["reason"] = halt_reason
            if incomplete:
                result["ending_equity"] = None
        elif result["unresolved"]:
            unresolved = result
            incomplete = True
            halt_reason = "UNRESOLVED_POSITION"
        elif result["status"] == "INCOMPLETE_DATA":
            incomplete = True
            result["ending_equity"] = None
            halt_reason = "INCOMPLETE_DATA"
        elif result["status"] == "CLOSED":
            equity = result["ending_equity"]
            peak = max(peak, equity)
            drawdown = equity / peak - 1
            worst_drawdown = min(worst_drawdown, drawdown)
            if drawdown <= -cfg.maximum_drawdown + 1e-12:
                halt_reason = "DRAWDOWN_LIMIT"
        result["realized_high_water_mark"] = peak
        result["realized_drawdown"] = None if incomplete else equity / peak - 1
        daily.append(result)
    return {"initial_investment": initial_capital, "ending_equity": None if incomplete else equity,
            "realized_profit": None if incomplete else equity - initial_capital,
            "completed_trades_net_pnl": equity - initial_capital,
            "max_realized_drawdown": worst_drawdown,
            "closed_trades": sum(row["status"] == "CLOSED" for row in daily),
            "incomplete_sessions": sum(row["status"] == "INCOMPLETE_DATA" for row in daily),
            "unresolved_position": unresolved, "incomplete": incomplete, "halt_reason": halt_reason, "daily": daily,
            "config": asdict(cfg), "assumptions": ASSUMPTIONS.copy()}
