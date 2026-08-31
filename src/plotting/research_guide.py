"""Generate the offline glossary and interpretation guide for a research run."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

from config import ResearchConfig
from src.backtest.combination_ranking import rank_stock_strategy_combinations
from src.backtest.strategy_ranking import rank_strategies_collectively


GLOSSARY = (
    ("Core", "Strategy", "A fixed set of signal, direction, entry, exit, and sizing rules tested without changing them for individual stocks."),
    ("Core", "Signal", "The rule condition that activates a trade. No signal means the strategy stays in cash for that stock and session."),
    ("Core", "Long", "A position that profits when the stock rises after entry."),
    ("Core", "Short", "A position that profits when the stock falls after entry. Cash market intraday shorting depends on broker and exchange availability."),
    ("Core", "Gap", "The percentage difference between today’s opening price and the previous completed session’s closing price."),
    ("Strategies", "Gap fade", "Trade against the opening gap. A gap up produces a short signal and a gap down produces a long signal."),
    ("Strategies", "Gap continuation", "Trade in the same direction as the opening gap."),
    ("Strategies", "Close to open", "Enter at one session’s close and exit at the next session’s open. This includes overnight exposure."),
    ("Strategies", "Open to close", "Enter at the market open and exit at the same session’s close."),
    ("Strategies", "Reversal", "Trade against a prior price move because the strategy expects part of that move to reverse."),
    ("Strategies", "Momentum", "Trade in the direction of a prior price move because the strategy expects continuation."),
    ("Strategies", "Volume shock", "A signal based on unusually high prior volume combined with a minimum prior price move."),
    ("Strategies", "Turn of month", "A long only rule active during the first and last three completed exchange sessions of each month."),
    ("Money", "Initial investment", "The starting capital assigned to each stock and strategy pair. Every displayed PnL must be read relative to this amount."),
    ("Money", "PnL", "Profit and loss. Positive PnL means the ending value is above the initial investment. Negative PnL means it is below."),
    ("Money", "Net PnL", "Compounded profit after the configured trading cost is deducted for every active round trip."),
    ("Money", "Ending value", "Initial investment plus net PnL after all sessions in the selected research window."),
    ("Money", "Basis point", "One basis point equals 0.01 percent. Ten bps per side means 0.10 percent at entry and 0.10 percent at exit."),
    ("Charts", "Equity curve", "The running value of the initial investment after each session’s strategy return and modeled costs."),
    ("Charts", "Baseline", "The gold horizontal line showing the initial investment. A curve above it is profitable at that point."),
    ("Risk", "Drawdown", "The percentage fall from the strategy’s previous highest equity value to a later low."),
    ("Risk", "Sharpe ratio", "Average daily net return divided by daily volatility, annualized. Higher is better, but it does not measure liquidity or execution feasibility."),
    ("Risk", "Sortino ratio", "A return to downside risk measure that focuses on negative volatility."),
    ("Risk", "Win rate", "The share of active trades with a positive net return."),
    ("Risk", "Profit factor", "Total positive trade returns divided by the absolute total of negative trade returns."),
    ("Evidence", "Breadth", "The percentage of tested stocks with positive net PnL for a strategy."),
    ("Evidence", "Equal weight PnL", "The result of a market wide portfolio that gives the same weight to each eligible stock on each session."),
    ("Evidence", "Coverage", "The share of completed sessions in the research window for which a stock has an observed exchange record."),
    ("Evidence", "Comparable", "A stricter sample label requiring at least 95 percent coverage, an OK liquidity flag, and at least 20 trades."),
    ("Evidence", "Composite score", "A relative score combining profit, Sharpe, severe cost survival, excess return, and drawdown resilience."),
    ("Evidence", "Evidence tier", "An absolute label based on how many positive tests a result passes. It is separate from the relative rank."),
    ("Evidence", "30 bps PnL", "Profit after applying a severe cost assumption of 30 basis points per side."),
    ("Evidence", "In sample", "The same historical observations were used to discover and evaluate the result. This is not a forward test."),
    ("Data quality", "Corporate action flag", "A large close discontinuity that is excluded from strategy returns because it may reflect a split, bonus, or other adjustment."),
    ("Data quality", "Circuit like session", "A session where open, high, low, and close are identical. Execution at the displayed price may have been impossible."),
    ("Data quality", "Historical universe", "The union of securities present during the window, including new listings, suspended names, and securities that later disappeared."),
)


def _window_payload(root: Path) -> dict | None:
    metadata_path = root / "run_metadata.json"
    summary_path = root / "market_summary.csv"
    if not metadata_path.exists() or not summary_path.exists():
        return None
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    summary = pd.read_csv(summary_path)
    selected = summary[summary["strategy"].isin(("gap_fade_050", "gap_fade_100", "close_to_open"))]
    metrics = {
        row.strategy: {
            "median_pnl": float(row.median_net_pnl),
            "breadth": float(row.pct_profitable),
            "cost_breadth": float(row.pct_profitable_30bps),
        }
        for row in selected.itertuples(index=False)
    }
    return {
        "label": "10 year" if int(metadata["evaluation_sessions"]) > 1000 else "252 session",
        "sessions": int(metadata["evaluation_sessions"]),
        "stocks": int(metadata["number_of_symbols"]),
        "start": metadata["evaluation_start"],
        "end": metadata["evaluation_end"],
        "metrics": metrics,
    }


def build_guide_payload(config: ResearchConfig) -> dict:
    metadata = json.loads((config.results_dir / "run_metadata.json").read_text(encoding="utf-8"))
    summary = pd.read_csv(config.results_dir / "market_summary.csv")
    collective = rank_strategies_collectively(summary)
    combinations = rank_stock_strategy_combinations(
        pd.read_csv(config.results_dir / "strategy_results" / "all_stock_strategy_results.csv")
    )
    comparable = combinations[combinations["sample_tier"].eq("COMPARABLE")]
    raw_leader = combinations.iloc[0]
    comparable_leader = comparable.iloc[0]
    broadest = summary.sort_values("pct_profitable", ascending=False).iloc[0]
    severe_cost = summary.sort_values("pct_profitable_30bps", ascending=False).iloc[0]
    windows = [
        item
        for item in (
            _window_payload(config.project_root / "results"),
            _window_payload(config.project_root / "results" / "ten_year"),
        )
        if item is not None
    ]
    is_decade = int(metadata["evaluation_sessions"]) > 1000
    return {
        "window": {
            "label": "10 year" if is_decade else "252 session",
            "sessions": int(metadata["evaluation_sessions"]),
            "stocks": int(metadata["number_of_symbols"]),
            "pairs": int(len(combinations)),
            "start": metadata["evaluation_start"],
            "end": metadata["evaluation_end"],
            "initial_capital": float(metadata["initial_capital"]),
            "other_url": "../../stock_gallery/guide.html" if is_decade else "../ten_year/stock_gallery/guide.html",
        },
        "collective_top": [
            {
                "rank": int(row.collective_rank),
                "strategy": row.strategy,
                "score": float(row.collective_score),
                "tier": row.evidence_tier,
            }
            for row in collective.head(3).itertuples(index=False)
        ],
        "broadest": {
            "strategy": broadest["strategy"],
            "breadth": float(broadest["pct_profitable"]),
        },
        "severe_cost": {
            "strategy": severe_cost["strategy"],
            "breadth": float(severe_cost["pct_profitable_30bps"]),
        },
        "raw_leader": {
            "symbol": raw_leader["symbol"],
            "strategy": raw_leader["strategy"],
            "sample": raw_leader["sample_tier"],
            "score": float(raw_leader["combination_score"]),
        },
        "comparable_leader": {
            "symbol": comparable_leader["symbol"],
            "strategy": comparable_leader["strategy"],
            "score": float(comparable_leader["combination_score"]),
            "trades": int(comparable_leader["number_of_trades"]),
        },
        "windows": windows,
        "glossary": [
            {"category": category, "term": term, "definition": definition}
            for category, term, definition in GLOSSARY
        ],
    }


def write_research_guide(config: ResearchConfig, gallery_dir: Path) -> Path:
    assets = Path(__file__).resolve().parent / "gallery_assets"
    for filename in ("guide.html", "guide.css", "guide-app.js"):
        shutil.copy2(assets / filename, gallery_dir / filename)
    payload = build_guide_payload(config)
    output = gallery_dir / "guide-data.js"
    output.write_text(
        "window.RESEARCH_GUIDE=" + json.dumps(payload, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return output
