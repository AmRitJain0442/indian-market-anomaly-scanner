"""Interactive and written artifacts for the ₹10,000 research pilot."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

from src.planning.investment_plan import (
    DAILY_LOSS_LIMIT,
    DAILY_LOSS_RATIO,
    ELIGIBILITY_RULES,
    MAX_POSITION,
    MAX_POSITION_RATIO,
    PILOT_DRAWDOWN_LIMIT,
    PILOT_DRAWDOWN_RATIO,
    PLAN_CAPITAL,
    PRIMARY_STRATEGY,
    RISK_PER_TRADE,
    RISK_PER_TRADE_RATIO,
    STOP_DISTANCE,
)
from src.planning.thirty_day_plan import build_thirty_day_calendar


def plan_records(plan: pd.DataFrame) -> list[dict]:
    records = []
    for row in plan.itertuples(index=False):
        records.append(
            {
                "rank": int(row.watchlist_rank),
                "symbol": row.symbol,
                "company": row.company_name,
                "isin": row.isin,
                "combination_rank": int(row.combination_rank),
                "score": round(float(row.combination_score), 2),
                "historical_pnl": round(float(row.historical_pnl_10k), 2),
                "historical_ending": round(float(row.historical_ending_10k), 2),
                "pnl_30bps_scaled": round(float(row.pnl_30bps) * PLAN_CAPITAL / 100_000.0, 2),
                "sharpe": round(float(row.sharpe), 3),
                "drawdown": round(float(row.max_drawdown), 6),
                "trades": int(row.number_of_trades),
                "win_rate": round(float(row.win_rate), 6),
                "median_daily_value": round(float(row.median_daily_value), 2),
                "long_trades": int(row.long_trades),
                "long_pnl": round(float(row.long_pnl_10k), 2),
                "short_trades": int(row.short_trades),
                "short_pnl": round(float(row.short_pnl_10k), 2),
            }
        )
    return records


def write_investment_plan_gallery(plan: pd.DataFrame, gallery_dir: Path, evaluation_end: str) -> Path:
    assets = Path(__file__).resolve().parent / "gallery_assets"
    for filename in (
        "index.html",
        "combination-ranking.html",
        "strategy-ranking.html",
        "investment-plan.html",
        "investment-plan.css",
        "investment-plan-app.js",
    ):
        shutil.copy2(assets / filename, gallery_dir / filename)
    payload = {
        "capital": PLAN_CAPITAL,
        "max_position": MAX_POSITION,
        "risk_per_trade": RISK_PER_TRADE,
        "daily_loss_limit": DAILY_LOSS_LIMIT,
        "drawdown_limit": PILOT_DRAWDOWN_LIMIT,
        "stop_distance": STOP_DISTANCE,
        "max_position_ratio": MAX_POSITION_RATIO,
        "risk_per_trade_ratio": RISK_PER_TRADE_RATIO,
        "daily_loss_ratio": DAILY_LOSS_RATIO,
        "drawdown_ratio": PILOT_DRAWDOWN_RATIO,
        "strategy": PRIMARY_STRATEGY,
        "evaluation_end": evaluation_end,
        "eligibility": ELIGIBILITY_RULES,
        "watchlist": plan_records(plan),
        "calendar": build_thirty_day_calendar(),
    }
    output = gallery_dir / "investment-plan-data.js"
    output.write_text(
        "window.INVESTMENT_PLAN=" + json.dumps(payload, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    return output


def write_investment_plan_report(plan: pd.DataFrame, output: Path, evaluation_end: str) -> Path:
    lines = [
        "# INR 10,000 controlled anomaly pilot",
        "",
        "## Decision",
        "",
        "The most defensible use of this research is **not immediate full-capital trading**. The proposed plan is a paper test lasting at least 20 sessions and 10 valid signals, followed by a ten-trade half-size live gate, and only then a maximum INR 5,000 position. The remaining cash is an execution and loss buffer.",
        "",
        f"The primary setup is `{PRIMARY_STRATEGY}` because it led the market-wide collective ranking and retained majority profitable breadth at 30 bps per side. Results are in-sample through **{evaluation_end}**, so no return is forecast.",
        "",
        "## Capital controls",
        "",
        f"- Total capital: **INR {PLAN_CAPITAL:,.0f}**",
        f"- Maximum full-pilot position: **INR {MAX_POSITION:,.0f}**",
        f"- Planned risk per trade: **INR {RISK_PER_TRADE:,.0f}** using a {STOP_DISTANCE:.0%} stop overlay",
        f"- Daily loss ceiling: **INR {DAILY_LOSS_LIMIT:,.0f}**",
        f"- Pause and review after cumulative pilot drawdown: **INR {PILOT_DRAWDOWN_LIMIT:,.0f}**",
        "- One position at a time; no averaging down; no overnight carry.",
        "",
        "All settled gains and losses are reinvested mechanically: the next session starts from the prior session's closing account equity. Full-pilot maximum notional is 50% of current equity and planned risk is 0.5%; half-size validation uses 25% and 0.25%. Therefore position size is `floor(min(current_equity × stage_notional_pct / entry, current_equity × stage_risk_pct / (entry × 1%)))`.",
        "",
        "There is no daily rupee profit target. The tested setup exits at the close, so forcing a monetary target would add an untested rule and encourage overtrading. Each day instead has an execution target and a 15:15 exit target.",
        "",
        "## Three-stage gate",
        "",
        "1. **At least 20 completed sessions and 10 valid signals, paper only.** Extend the paper stage until both are satisfied. Record the achievable entry, exit, fees, slippage, rejects, and short availability. Do not risk capital. Pass only if net PnL after every charge is positive, average absolute slippage is at most 10 bps, and drawdown is below INR 300.",
        "2. **Next 10 valid signals, half size.** Maximum INR 2,500 position and INR 25 planned risk. Continue only if net PnL after every charge is positive, average absolute slippage is at most 10 bps, and drawdown is below INR 300.",
        "3. **Full pilot.** Maximum INR 5,000 position and INR 50 planned risk. Stop after INR 100 lost in a day or INR 500 cumulative drawdown; return to paper mode before changing any rule.",
        "",
        "## Daily rule card",
        "",
        "1. Use the prior NSE close and the current opening price. `gap = open / prior_close - 1`.",
        "2. If gap is at most -1%, buy at the open; if gap is at least +1%, sell short intraday. Otherwise do nothing.",
        "3. Trade only a watchlist name below. If several qualify, take the highest watchlist rank only.",
        "4. Skip when the stock is under an execution restriction, a normal order is rejected, the opening spread is above 0.50%, or a fill cannot be obtained within 10 bps of the recorded open.",
        "5. Apply the 1% protective stop. Exit by 15:15 IST regardless of PnL. A same-day short must be closed; do not create a delivery obligation.",
        "",
        "The stop, fill tolerance, 15:15 exit, and stricter liquidity screen are safety overlays and were **not** separately backtested in the 252-session result. That is why paper validation is mandatory.",
        "",
        "## Fixed daily clock",
        "",
        "- **08:45–09:00:** update current equity/high-water mark, prior closes, watchlist order, broker restrictions, and short availability.",
        "- **09:00–09:08:** observe NSE pre-open; do not place a discretionary trade.",
        "- **09:15–09:16:** calculate all five gaps, apply the ±1% threshold, choose the highest-priority eligible name, size from current equity, and fill within 10 bps or skip.",
        "- **After entry:** place the 1% protective stop; no widening, averaging, or second position.",
        "- **15:15:** exit the position regardless of PnL. The price target is the market outcome at the timed exit—not an invented fixed return.",
        "- **15:40 onward:** reconcile fills, costs, net PnL, closing equity, high-water mark, drawdown, and next-session limits.",
        "",
        "## Next 30 NSE trading sessions",
        "",
        "The calendar starts on 31 August 2026 and excludes NSE holidays on 14 September and 2 October. Every session follows the fixed clock above; the row supplies that day's extra decision and measurable target.",
        "",
        "| Day | Date | Phase | Daily focus | Decision | Target / pass condition |",
        "|---:|---|---|---|---|---|",
    ]
    for day in build_thirty_day_calendar():
        lines.append(
            f"| {day['day']} | {day['date']} ({day['weekday'][:3]}) | {day['phase']} | "
            f"{day['focus']} | {day['decision']} | {day['target']} |"
        )
    lines.extend(
        [
            "",
            "## Strict watchlist",
            "",
            "Candidates require 99% history, at least 50 signals, median daily value of at least INR 5 crore, no detected corporate-action discontinuity, at most two circuit-like sessions, positive confidence floor, and separately positive long and short legs.",
            "",
            "| Priority | Stock | Score | Overall pair rank | Historical PnL on scaled INR 10,000 | Ending value | 30 bps PnL | Long leg | Short leg |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in plan.itertuples(index=False):
        lines.append(
            f"| {row.watchlist_rank} | {row.symbol} | {row.combination_score:.1f} | {row.combination_rank:,} | "
            f"INR {row.historical_pnl_10k:,.0f} | INR {row.historical_ending_10k:,.0f} | "
            f"INR {row.pnl_30bps * PLAN_CAPITAL / 100_000:,.0f} | INR {row.long_pnl_10k:,.0f} ({int(row.long_trades)}) | "
            f"INR {row.short_pnl_10k:,.0f} ({int(row.short_trades)}) |"
        )
    lines.extend(
        [
            "",
            "Historical values scale the research equity curve from INR 100,000 to INR 10,000. They are descriptive, not expected returns, and do not represent the new safety overlay.",
            "",
            "## Go/no-go checklist",
            "",
            "Proceed only when all are true: emergency savings and near-term obligations are separate; the entire INR 10,000 can be lost without affecting essentials; broker charges are recorded; intraday short availability is confirmed; and the paper gate passes without changing rules. Use the adjacent `pilot_trade_log_template.csv` to record every eligible signal, including skipped and rejected orders.",
            "",
            "Do not proceed after any rule breach, missing market data, broker restriction, three consecutive losing trades, INR 100 daily loss, or INR 500 cumulative pilot drawdown.",
            "",
            "## Regulatory and risk references",
            "",
            "- [SEBI study: 7 out of 10 individual equity-cash intraday traders made losses](https://www.sebi.gov.in/media-and-notifications/press-releases/jul-2024/sebi-study-finds-that-7-out-of-10-individual-intraday-traders-in-equity-cash-segment-make-losses_84948.html)",
            "- [SEBI framework for short selling](https://www.sebi.gov.in/legal/circulars/jan-2024/framework-for-short-selling_80448.html)",
            "- [NSE implementation standards for retail API/algo access](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf)",
            "- [NSE capital-market trading holidays for 2026](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf)",
            "- [NSE equity market timings](https://www.nseindia.com/static/market-data/market-timings)",
            "",
            "> This is a research-derived pilot protocol, not personalized investment advice or an assurance of returns.",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output
