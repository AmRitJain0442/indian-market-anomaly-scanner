"""Dated 30-session operating calendar for the INR 10,000 pilot."""

from __future__ import annotations

from datetime import date, timedelta

NSE_HOLIDAYS = {
    date(2026, 9, 14),  # Ganesh Chaturthi
    date(2026, 10, 2),  # Mahatma Gandhi Jayanti
}

DAY_FOCUS = [
    ("Baseline the workflow", "Complete every log field; zero live capital and zero unrecorded decisions."),
    ("Opening-price discipline", "Measure fill slippage; simulated entry must remain within 10 bps of the official open."),
    ("Cost ledger", "Capture brokerage, taxes, fees, and slippage separately; compute net PnL only after all costs."),
    ("Long-leg rehearsal", "If a gap-down signal appears, execute the paper long exactly; otherwise record NO TRADE."),
    ("Short-leg rehearsal", "Confirm Zerodha intraday-short availability before simulating a gap-up fade."),
    ("Spread filter", "Skip any opening spread above 0.50%; target zero exceptions."),
    ("Priority rule", "When signals collide, select only the highest-ranked watchlist name."),
    ("Stop mechanics", "Record the exact 1% stop trigger and achievable stop fill; never widen it."),
    ("No-trade discipline", "Do not manufacture a trade when no eligible ±1% gap exists."),
    ("Checkpoint one", "Audit the first ten sessions; target 100% rule adherence and reconcile every rupee."),
    ("Post-holiday reset", "Refresh prior closes and restrictions after the exchange holiday; assume nothing carried over."),
    ("Fill repeatability", "Keep average absolute entry slippage at or below 10 bps."),
    ("Long/short balance", "Verify both directions are being logged; do not force the missing side."),
    ("Liquidity check", "Confirm normal order depth and reject any circuit or surveillance-constrained setup."),
    ("Ranking fidelity", "Use the frozen priority order; target zero discretionary substitutions."),
    ("Loss-sequence drill", "After three consecutive losses, mark the pilot PAUSED and take no further signals."),
    ("High-water mark", "Update simulated closing equity and peak equity; recompute the 5% drawdown boundary."),
    ("Exit discipline", "Close or simulate close by 15:15 IST; target zero overnight positions."),
    ("Pre-gate audit", "Count valid signals and identify missing evidence; extend paper mode if any gate is incomplete."),
    ("Paper gate decision", "PASS only with ≥10 signals, positive net PnL, ≤10 bps mean slippage, <3% drawdown, and no breaches."),
    ("Conditional half-size launch", "If the gate passed, risk 0.25% of current equity; otherwise continue paper mode."),
    ("First-live reconciliation", "Match broker contract note to the log before the next trade; target zero unexplained charges."),
    ("Compounding check", "Use yesterday's settled closing equity—not INR 10,000—to calculate today's size."),
    ("Execution stability", "Target a valid fill within 10 bps; skip rather than chase."),
    ("Mid-pilot review", "Keep aggregate half-size PnL net positive and live drawdown below 3%; otherwise return to paper."),
    ("Stop-loss audit", "Verify planned loss equals at most 0.25% of current equity at half size."),
    ("Restriction audit", "Recheck MIS/short availability and surveillance status before any order."),
    ("Behaviour audit", "No revenge trade, second trade, averaging down, or rule change after a loss."),
    ("Final signal collection", "Complete the tenth half-size signal only if eligible; elapsed days alone do not pass the gate."),
    ("Thirty-session decision", "Scale no further unless ten live signals are net positive, slippage ≤10 bps, drawdown <3%, and breaches = 0."),
]


def trading_sessions(start: date, count: int, holidays: set[date] | None = None) -> list[date]:
    """Return weekday sessions, excluding the supplied exchange holidays."""
    excluded = holidays or set()
    sessions = []
    current = start
    while len(sessions) < count:
        if current.weekday() < 5 and current not in excluded:
            sessions.append(current)
        current += timedelta(days=1)
    return sessions


def build_thirty_day_calendar(start: date = date(2026, 8, 31)) -> list[dict]:
    sessions = trading_sessions(start, 30, NSE_HOLIDAYS)
    calendar = []
    for index, (session, focus) in enumerate(zip(sessions, DAY_FOCUS), start=1):
        paper = index <= 20
        calendar.append(
            {
                "day": index,
                "date": session.isoformat(),
                "weekday": session.strftime("%A"),
                "phase": "PAPER" if paper else "HALF-SIZE IF GATE PASSED",
                "focus": focus[0],
                "target": focus[1],
                "risk_rule": "No live capital" if paper else "0.25% of current equity; 25% maximum notional",
                "decision": (
                    "Log the qualifying trade as if live, including skip/reject outcomes."
                    if paper
                    else "Trade half-size only if Day 20 passed; otherwise perform the identical action on paper."
                ),
            }
        )
    return calendar
