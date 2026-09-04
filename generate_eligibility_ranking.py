"""Publish dated EQ-only and INR 1,000 research screens without replacing backtests."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from config import CONFIG
from src.backtest.eligibility_ranking import audit_trade_series, broker_table, screen_and_rank
from src.data.bhavcopy_parser import parse_bhavcopy
from src.data.nse_downloader import NSEDownloader

BROKER_URL = "https://zerodha.com/margin-calculator/Equity/"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def write_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def frontend_records(frame: pd.DataFrame) -> dict:
    columns = ["symbol", "current_symbol", "company_name", "isin", "strategy", "eq_rank", "worklist_rank",
               "research_score", "eq_screen_pass", "worklist_pass", "current_series", "snapshot_price",
               "broker_listed", "cash_cap_shares", "illustrative_risk_shares", "illustrative_planned_loss", "risk_budget", "tick_size", "recent_median_value", "recent_sessions", "number_of_trades",
               "short_trades", "restricted_trades", "unknown_series_trades", "screen_reasons", "worklist_reasons",
               "net_pnl", "pnl_30bps", "sharpe", "max_drawdown", "coverage_ratio", "intraday"]
    compact = frame[columns].copy()
    return {"columns": columns, "rows": json.loads(compact.to_json(orient="values", double_precision=6))}


def write_report(path: Path, frame: pd.DataFrame, metadata: dict, snapshot_date: str, budget: float):
    shortlist = frame.loc[frame.worklist_pass]
    passed = frame.loc[frame.eq_screen_pass]
    initial = metadata["initial_capital"]
    lines = [
        "# EQ-only stock and strategy ranking", "",
        f"Historical window: {metadata['evaluation_start']} to {metadata['evaluation_end']}, {metadata['evaluation_sessions']} sessions. Current status snapshot: {snapshot_date}.", "",
        f"{len(frame):,} original pairs checked. {len(passed):,} pairs pass the strict EQ-history screen. {len(shortlist):,} pairs across {shortlist['isin'].nunique():,} stocks pass the INR 1,000 practical research screen.", "",
        "## What the two ranks mean", "",
        "The EQ rank requires a current EQ listing and EQ on both the entry and exit date of every historical trade. A pair with any BE/BZ or missing-series trade is excluded in full. We do not remove its bad trades while retaining its original profit. The same conservative EQ-only rule is applied to overnight strategies, even though some delivery trades in restricted series might otherwise be possible.", "",
        "The practical rank adds the dated Zerodha MIS table, a current price of at least INR 100, at least one whole share within a INR 500 notional cap and an illustrative INR 5 planned-risk limit, at least INR 50 crore median turnover across the latest 20 completed sessions, at least 95% historical coverage and at least 20 historical trades. Overnight strategies are left for a separate delivery-cost and settlement review. These are research filters, not exchange rules or evidence of profitability.", "",
        "The cash budget is INR 1,000 with no leverage. Cash-cap shares are the maximum whole shares under the INR 500 notional limit at the snapshot close, not an order quantity or a completed risk calculation. Actual order prices, fees, stop distance and available cash require fresh checks.", "",
        "Illustrative risk shares additionally use a tick-rounded 1% stop, estimated Zerodha charges, and an adverse-fill allowance of the larger of 0.20% of notional or two ticks per share. The worse of long and short planned loss must fit INR 5. Monthly ticks use the preceding month-end close. This is a current sizing illustration, not a newly backtested stop strategy, guaranteed loss cap or historical whole-share simulation.", "",
        "Broker-list membership is evidence from a published snapshot, not account-specific permission or a promise of future order acceptance. Absence from the list means this screen has not established MIS availability. Dhan permission has not been checked. Recheck broker restrictions and the exchange series before every session.", "",
        "## Historical ranking is not a INR 1,000 return forecast", "",
        f"The historical figures below retain the original INR {initial:,.0f} reference account and its theoretical fills and fractional full-capital compounding. They are not returns achieved by a INR 1,000 whole-share account. The new screen does not fix opening-fill assumptions, future-dependent exclusions, selection bias, missing historical broker permission or all corporate-action issues in the original engine.", "",
        "Scores are recomputed within the EQ-screened set using the existing five ranking weights. Drawdown is recalculated from the trade-return path with initial capital included. All other historical metrics are inherited. A high score is relative research priority, not a probability of profit. The latest-status filter is a present-day discovery screen, not a historical investable-universe backtest.", "",
        "## Practical research shortlist", "",
        "| Rank | Stock | Strategy | Snapshot price | Cash-cap shares | Illustrative risk shares | Research score | Historical initial | Historical modeled profit | Historical ending | Trades |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in shortlist.sort_values("worklist_rank").head(30).itertuples():
        lines.append(f"| {row.worklist_rank} | {row.current_symbol} | {row.strategy} | INR {row.snapshot_price:,.2f} | {row.cash_cap_shares} | {int(row.illustrative_risk_shares)} | {row.research_score:.1f} | INR {initial:,.0f} | INR {row.net_pnl:,.2f} | INR {initial + row.net_pnl:,.2f} | {row.number_of_trades} |")
    if shortlist.empty:
        lines.extend(["", "No pair passes all practical research filters. No substitute is promoted."])
    lines.extend(["", "## Inspect and reproduce", "",
                  "- [Searchable local ranking](index.html)",
                  "- [EQ-only ranking](eq_only_ranking.csv)",
                  "- [Practical research shortlist](practical_shortlist.csv)",
                  "- [All pairs and exclusion reasons](all_pairs_audit.csv.gz)",
                  "- [Source hashes and method](metadata.json)", "",
                  "Run from the repository root:", "",
                  "    python generate_eligibility_ranking.py --windows both --snapshot-date " + snapshot_date,
                  "", "Sources: [NSE series definitions](https://www.nseindia.com/static/market-data/legend-of-series), [Zerodha published MIS list](https://zerodha.com/margin-calculator/Equity/), [Zerodha additional restrictions](https://support.zerodha.com/category/trading-and-markets/charts-and-orders/order/articles/intraday-orders-not-allowed-for-some-stocks).",
                  "", "The interface follows the existing dark-green and gold theme. No broker account was connected, no orders were placed and no server deployment was performed."])
    report = "\n".join(lines).replace("INR 1,000", f"INR {budget:,.0f}").replace("INR 500", f"INR {budget * 0.5:,.0f}")
    path.write_text(report + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--windows", choices=("one_year", "ten_year", "both"), default="both")
    parser.add_argument("--snapshot-date", type=date.fromisoformat, default=date(2026, 9, 4))
    parser.add_argument("--budget", type=float, default=1000)
    parser.add_argument("--refresh-broker", action="store_true")
    args = parser.parse_args()
    cfg = replace(CONFIG, artifact_namespace="eligibility_rank", request_retries=2, request_timeout_seconds=15)
    downloader = NSEDownloader(cfg)
    sessions = downloader.collect_sessions(40, args.snapshot_date)
    if sessions[-1].session_date != args.snapshot_date:
        raise ValueError("Requested status date is not an available exchange session")
    daily = pd.concat([parse_bhavcopy(s.path, cfg) for s in sessions], ignore_index=True)
    latest = daily.loc[daily.date.eq(pd.Timestamp(args.snapshot_date))].copy()
    month_start = pd.Timestamp(args.snapshot_date).replace(day=1)
    previous_month = daily.loc[daily.date.lt(month_start)]
    month_end = previous_month.loc[previous_month.date.eq(previous_month.date.max())]
    monthly_ticks = month_end.set_index("isin").close.map(lambda price: 0.01 if price < 250 else 0.05)
    latest["tick_size"] = latest["isin"].map(monthly_ticks)
    if latest["isin"].duplicated().any():
        raise ValueError("Ambiguous latest exchange ISIN")
    recent_days = [pd.Timestamp(s.session_date) for s in sessions[-20:]]
    recent = daily.loc[daily.date.isin(recent_days)].groupby("isin", as_index=False).agg(recent_sessions=("date", "nunique"), recent_median_value=("traded_value", "median"))
    root = CONFIG.results_dir / "findings/2026-09-05-eligibility-ranking"
    root.mkdir(parents=True, exist_ok=True)
    cache = CONFIG.raw_dir / "broker_screens"
    cache.mkdir(parents=True, exist_ok=True)
    broker_path = cache / f"zerodha_mis_{args.snapshot_date}.html"
    broker_manifest_path = broker_path.with_suffix(".json")
    if not broker_path.exists() or args.refresh_broker:
        response = requests.get(BROKER_URL, timeout=20)
        response.raise_for_status()
        parsed = broker_table(response.text)
        response_stamp = re.search(r"Last updated:\s*([^<]+)", response.text)
        if response_stamp is None or pd.Timestamp(response_stamp.group(1).strip()).date() != args.snapshot_date:
            raise ValueError("Live broker date differs from requested snapshot. Existing cache preserved.")
        broker_path.write_text(response.text, encoding="utf-8")
        write_json(broker_manifest_path, {"url": BROKER_URL, "retrieved_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()})
    html = broker_path.read_text(encoding="utf-8")
    broker = broker_table(html)
    stamp = re.search(r"Last updated:\s*([^<]+)", html)
    broker_as_of = stamp.group(1).strip() if stamp else "Unknown"
    if broker_as_of == "Unknown" or pd.Timestamp(broker_as_of).date() != args.snapshot_date:
        raise ValueError("Broker list update date does not match requested snapshot")
    broker.to_csv(root / "zerodha_mis_snapshot.csv", index=False)
    latest[["date", "symbol", "isin", "series", "close"]].to_csv(root / "exchange_snapshot.csv", index=False)
    windows = ["one_year", "ten_year"] if args.windows == "both" else [args.windows]
    for window in windows:
        run_cfg = replace(CONFIG, artifact_namespace="ten_year" if window == "ten_year" else None)
        result_path = run_cfg.results_dir / "strategy_results/all_stock_strategy_results.csv"
        run_metadata_path = run_cfg.results_dir / "run_metadata.json"
        run_metadata = json.loads(run_metadata_path.read_text(encoding="utf-8"))
        results = pd.read_csv(result_path)
        history_path = run_cfg.processed_dir / "equity_daily.parquet"
        history = pd.read_parquet(history_path, columns=["isin", "date", "series"])
        series_map = history.set_index(["isin", "date"])["series"]
        audit_rows, input_hashes = [], {str(result_path.relative_to(CONFIG.project_root)): digest(result_path),
                                      str(history_path.relative_to(CONFIG.project_root)): digest(history_path),
                                      str(run_metadata_path.relative_to(CONFIG.project_root)): digest(run_metadata_path)}
        for strategy in run_metadata["strategies"]:
            name = strategy["name"]
            path = run_cfg.results_dir / "trades" / f"{name}.parquet"
            trades = pd.read_parquet(path, columns=["isin", "entry_date", "exit_date", "net_return", "side"])
            audit = audit_trade_series(trades, series_map)
            audit["strategy"] = name
            audit_rows.append(audit)
            input_hashes[str(path.relative_to(CONFIG.project_root))] = digest(path)
            print(f"{window}: audited {name}, {len(trades):,} trades", flush=True)
        frame = screen_and_rank(results, pd.concat(audit_rows, ignore_index=True), latest, recent, broker, args.budget)
        frame["historical_initial_investment"] = run_metadata["initial_capital"]
        frame["historical_ending_value"] = run_metadata["initial_capital"] + frame.net_pnl
        export_columns = ["eq_rank", "worklist_rank", "symbol", "current_symbol", "company_name", "isin", "strategy",
                          "research_score", "eq_screen_pass", "worklist_pass", "current_series", "snapshot_price",
                          "broker_listed", "mis_margin_percent", "budget", "notional_cap", "cash_cap_shares", "illustrative_risk_shares", "illustrative_planned_loss", "risk_budget", "tick_size",
                          "recent_median_value", "recent_sessions", "number_of_trades", "audited_trades", "short_trades",
                          "restricted_trades", "unknown_series_trades", "non_eq_trades", "screen_reasons", "worklist_reasons",
                          "historical_initial_investment", "net_pnl", "historical_ending_value", "pnl_30bps", "sharpe",
                          "max_drawdown", "original_max_drawdown", "excess_pnl", "confidence_95_low", "coverage_ratio",
                          "intraday", "execution_validated"]
        export = frame[export_columns]
        output = root / window
        output.mkdir(parents=True, exist_ok=True)
        export.to_csv(output / "all_pairs_audit.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
        export.loc[export.eq_screen_pass].to_csv(output / "eq_only_ranking.csv", index=False)
        export.loc[export.worklist_pass].sort_values("worklist_rank").to_csv(output / "practical_shortlist.csv", index=False)
        metadata = {
            "window": window, "evaluation_start": run_metadata["evaluation_start"], "evaluation_end": run_metadata["evaluation_end"],
            "sessions": run_metadata["evaluation_sessions"], "snapshot_date": str(args.snapshot_date), "budget": args.budget,
            "notional_cap": args.budget * 0.5, "risk_budget": args.budget * 0.005, "historical_initial_investment": run_metadata["initial_capital"],
            "total_pairs": len(frame), "eq_pairs": int(frame.eq_screen_pass.sum()),
            "practical_pairs": int(frame.worklist_pass.sum()), "practical_stocks": int(frame.loc[frame.worklist_pass, "isin"].nunique()),
            "excluded_pairs": int((~frame.eq_screen_pass).sum()), "execution_validated_pairs": 0,
            "broker_url": BROKER_URL, "broker_updated": broker_as_of, "broker_sha256": digest(broker_path),
            "broker_retrieval": json.loads(broker_manifest_path.read_text(encoding="utf-8")),
            "nse_sources": [{"date": str(s.session_date), "url": s.url, "sha256": s.sha256} for s in sessions],
            "ranking_input_sha256": input_hashes,
            "code_sha256": {p: digest(Path(p)) for p in ["generate_eligibility_ranking.py", "src/backtest/eligibility_ranking.py"]},
            "method": "Strict current and per-trade EQ screen. Contaminated pairs excluded intact. Existing five-pillar score reranked. Initial-capital drawdown corrected. Other backtest assumptions inherited.",
        }
        write_json(output / "metadata.json", metadata)
        write_report(output / "README.md", frame, run_metadata, str(args.snapshot_date), args.budget)
        payload = {"metadata": metadata, **frontend_records(frame)}
        (output / "eligibility-data.js").write_text("window.ELIGIBILITY_DATA=" + json.dumps(payload, separators=(",", ":"), allow_nan=False) + ";\n", encoding="utf-8")
        assets = Path("src/plotting/gallery_assets")
        for source_name, destination in [("eligibility-ranking.html", "index.html"), ("eligibility-ranking.css", "eligibility-ranking.css"), ("eligibility-ranking.js", "eligibility-ranking.js")]:
            if (assets / source_name).exists():
                shutil.copy2(assets / source_name, output / destination)
        print(f"{window}: {metadata['eq_pairs']:,} EQ-only pairs, {metadata['practical_pairs']:,} practical research pairs", flush=True)
        print(frame.loc[frame.worklist_pass, ["worklist_rank", "symbol", "strategy", "research_score", "snapshot_price", "cash_cap_shares", "illustrative_risk_shares"]].head(10).to_string(index=False))
    print(f"Findings: {root}")


if __name__ == "__main__":
    main()
