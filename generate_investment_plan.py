"""Generate the INR 10,000 controlled-pilot plan from completed research."""

from __future__ import annotations

import json
import shutil

import pandas as pd

from config import CONFIG
from src.planning.investment_plan import build_investment_plan
from src.planning.thirty_day_plan import build_thirty_day_calendar
from src.plotting.investment_plan import write_investment_plan_gallery, write_investment_plan_report


def main() -> None:
    metadata = json.loads((CONFIG.results_dir / "run_metadata.json").read_text(encoding="utf-8"))
    ranked = pd.read_csv(CONFIG.results_dir / "combination_rankings" / "stock_strategy_combination_ranking.csv")
    trades = pd.read_parquet(CONFIG.results_dir / "trades" / "gap_fade_100.parquet")
    plan = build_investment_plan(ranked, trades, float(metadata["initial_capital"]))

    output_dir = CONFIG.results_dir / "investment_plan_10000"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "watchlist.csv"
    plan.to_csv(csv_path, index=False)
    write_investment_plan_gallery(plan, CONFIG.results_dir / "stock_gallery", metadata["evaluation_end"])

    log_columns = [
        "session_day", "session_date", "phase", "account_equity_start", "high_water_mark",
        "symbol", "watchlist_rank", "prior_close", "opening_price",
        "gap_pct", "side", "planned_entry", "actual_entry", "entry_slippage_bps",
        "quantity", "stop_price", "exit_deadline", "actual_exit", "gross_pnl",
        "brokerage", "taxes_fees", "net_pnl", "short_available", "order_rejected",
        "rule_breach", "skip_reason", "notes", "account_equity_close", "drawdown_pct",
        "consecutive_losses", "running_pilot_pnl",
    ]
    log_path = output_dir / "pilot_trade_log_template.csv"
    pd.DataFrame(columns=log_columns).to_csv(log_path, index=False)
    shutil.copy2(log_path, CONFIG.results_dir / "stock_gallery" / log_path.name)
    calendar_path = output_dir / "investment_plan_30_sessions.csv"
    pd.DataFrame(build_thirty_day_calendar()).to_csv(calendar_path, index=False)
    shutil.copy2(calendar_path, CONFIG.results_dir / "stock_gallery" / calendar_path.name)

    findings = CONFIG.results_dir / "findings" / metadata["evaluation_end"]
    plan.to_csv(findings / "investment_plan_10000_watchlist.csv", index=False)
    shutil.copy2(log_path, findings / log_path.name)
    shutil.copy2(calendar_path, findings / calendar_path.name)
    write_investment_plan_report(plan, findings / "INVESTMENT_PLAN_10000.md", metadata["evaluation_end"])
    print(plan[["watchlist_rank", "symbol", "combination_score", "historical_pnl_10k", "long_pnl_10k", "short_pnl_10k"]].to_string(index=False))
    print(f"Plan ready: {CONFIG.results_dir / 'stock_gallery' / 'investment-plan.html'}")


if __name__ == "__main__":
    main()
