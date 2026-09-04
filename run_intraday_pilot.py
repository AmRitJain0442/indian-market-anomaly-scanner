"""Run a local data audit or explicitly selected one-minute pilot approximation."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, replace
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from config import CONFIG
from src.data.bhavcopy_parser import parse_bhavcopy
from src.data.nse_downloader import NSEDownloader
from src.data.pilot_history import MinuteHistory, watchlist


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (pd.Timestamp, date)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return json_safe(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def dump_json(path: Path, value):
    path.write_text(json.dumps(json_safe(value), indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("audit", "minute-proxy"), default="audit")
    parser.add_argument("--capital", type=float, default=1000.0)
    parser.add_argument("--end-date", type=date.fromisoformat, default=date(2026, 9, 4))
    parser.add_argument("--sessions", type=int, default=20)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--output", type=Path, default=Path("results/findings/2026-09-05-pilot20"))
    args = parser.parse_args()
    if args.capital <= 0 or not np.isfinite(args.capital) or args.sessions < 1:
        raise ValueError("Positive finite capital and session count required")
    args.output.mkdir(parents=True, exist_ok=True)
    cfg = replace(CONFIG, artifact_namespace="paper20", request_retries=2, request_timeout_seconds=15)
    archive = NSEDownloader(cfg)
    sources = archive.collect_sessions(args.sessions + 20, args.end_date)
    market = pd.concat([parse_bhavcopy(item.path, cfg) for item in sources], ignore_index=True)
    cfg.processed_dir.mkdir(parents=True, exist_ok=True)
    market.to_parquet(cfg.processed_dir / "equity_daily.parquet", index=False)
    evaluation = sources[-args.sessions:]
    start = evaluation[0].session_date
    finish = evaluation[-1].session_date
    provider = MinuteHistory(cfg.raw_dir / "pilot_minute")
    downloaded = {}
    download_errors = {}
    candidates_log = []
    coverage_log = []
    ledger = []
    equity = args.capital
    peak = equity
    halted = False
    incomplete = False
    if args.mode == "minute-proxy":
        from src.backtest.intraday_pilot import PilotConfig, simulate_session
        pilot_config = PilotConfig(slippage_bps=args.slippage_bps)
    for source in evaluation:
        session = pd.Timestamp(source.session_date)
        candidates = watchlist(market, session, equity)
        daily_bars = {}
        for row in candidates:
            row["initial_investment"] = args.capital
            row["sizing_equity"] = equity
            row["gap"] = row["official_open"] / row["reference"] - 1 if row["official_open"] else None
            gap_pass = row["gap"] is not None and abs(row["gap"]) >= 0.01 - 1e-12
            row["opening_gap_pass"] = gap_pass
            row["exact_execution_status"] = "MISSING_QUOTES_AND_PERMISSION_HISTORY" if gap_pass else "NO_GAP_SIGNAL"
            candidates_log.append(row.copy())
            if not gap_pass:
                continue
            symbol = row["symbol"]
            if symbol not in downloaded and symbol not in download_errors:
                try:
                    downloaded[symbol] = provider.fetch(symbol, start, finish + timedelta(days=1))
                    print(f"Downloaded {symbol}: {len(downloaded[symbol])} minute bars", flush=True)
                except (ValueError, OSError, KeyError, requests.RequestException) as exc:
                    # A provider failure is missing evidence, never a no-trade market outcome.
                    download_errors[symbol] = f"{type(exc).__name__}: {exc}"
            if symbol in downloaded:
                bars = downloaded[symbol]
                bars = bars.loc[bars.index.date == source.session_date]
                daily_bars[symbol] = bars
                required = pd.date_range(f"{source.session_date} 09:15", f"{source.session_date} 15:00", freq="min", tz="Asia/Kolkata")
                present = bars.reindex(required)
                valid = present[["open", "high", "low", "close"]].notna().all(axis=1)
                valid &= present[["open", "high", "low", "close"]].gt(0).all(axis=1)
                first_open = float(present.open.iloc[0]) if valid.iloc[0] else None
                open_difference = abs(first_open - row["official_open"]) if first_open is not None else None
                official = market.loc[market.date.eq(session) & market["isin"].eq(row["isin"])].iloc[0]
                coverage_log.append({
                    "date": str(source.session_date), "symbol": symbol,
                    "expected_bars_through_exit": len(required), "valid_bars": int(valid.sum()),
                    "missing_or_invalid_bars": int((~valid).sum()),
                    "official_open": row["official_open"], "minute_first_open": first_open,
                    "opening_price_difference": open_difference,
                    "official_daily_high": float(official.high), "minute_daily_high": float(bars.high.max()),
                    "official_daily_low": float(official.low), "minute_daily_low": float(bars.low.min()),
                    "bid_ask_depth_available": False, "broker_permission_verified": False,
                })
            else:
                coverage_log.append({"date": str(source.session_date), "symbol": symbol, "download_error": download_errors[symbol]})
            # No adjusted reference is guessed when the two daily sources disagree.
            if not row["reference_matches"] or row["tick_size"] is None:
                row["series"] = "UNVERIFIED_REFERENCE_OR_TICK"
        if args.mode == "minute-proxy":
            result = simulate_session(source.session_date, candidates, daily_bars, starting_equity=equity, config=pilot_config, halted=halted or incomplete)
            result["initial_investment"] = args.capital
            if incomplete:
                result["ending_equity"] = None
                result["net_pnl"] = None
                result["reason"] = "PRIOR_SESSION_INCOMPLETE"
            ledger.append(result)
            status = result.get("status", "")
            ending = result.get("ending_equity")
            if ending is not None and np.isfinite(ending):
                equity = float(ending)
                peak = max(peak, equity)
                halted = halted or equity / peak - 1 <= -0.05
            incomplete = incomplete or status in ("UNRESOLVED", "INCOMPLETE_DATA") or "UNVERIFIED" in status
        else:
            ledger.append({
                "date": str(source.session_date), "initial_investment": args.capital,
                "watchlist_size": len(candidates),
                "gap_candidates": sum(bool(r["opening_gap_pass"]) for r in candidates),
                "status": "EXACT_BACKTEST_UNAVAILABLE", "net_pnl": None, "ending_equity": None,
            })
    candidate_frame = pd.DataFrame(candidates_log)
    candidate_frame.to_csv(args.output / "daily_watchlists.csv", index=False)
    pd.DataFrame(coverage_log).to_csv(args.output / "minute_data_coverage.csv", index=False)
    pd.DataFrame(ledger).to_csv(args.output / "daily_ledger.csv", index=False)
    dump_json(args.output / "daily_ledger.json", ledger)
    dump_json(args.output / "data_sources.json", {
        "daily": [{"date": s.session_date, "url": s.url, "sha256": s.sha256} for s in sources],
        "minute": provider.manifest, "download_errors": download_errors,
    })
    code_paths = [Path("run_intraday_pilot.py"), Path("src/data/pilot_history.py"), Path("src/backtest/intraday_pilot.py")]
    summary = {
        "mode": args.mode, "start": str(start), "end": str(finish),
        "evaluation_sessions": len(evaluation), "warmup_sessions": 20,
        "initial_investment": args.capital, "real_money_deployed": 0,
        "exact_strategy_validated": False,
        "gap_candidates": int(candidate_frame.opening_gap_pass.sum()),
        "gap_signal_days": int(candidate_frame.loc[candidate_frame.opening_gap_pass, "date"].nunique()),
        "download_errors": download_errors,
        "limitations": [
            "One-minute candles cannot test bid/ask spreads, depth, or one-second execution.",
            "Historical broker permissions and corporate-action notices are unverified.",
            "Historical EQ series is checked but does not prove broker permission.",
            "Past data overlaps the already inspected study, so this is not independent validation.",
            "Fixed platform, data, and account charges are excluded from trade PnL.",
        ],
        "code_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in code_paths if p.exists()},
    }
    if args.mode == "minute-proxy":
        summary.update({"config": asdict(pilot_config), "ending_equity": equity if not incomplete else None,
                        "net_pnl": equity - args.capital if not incomplete else None,
                        "incomplete": incomplete, "halted": halted,
                        "closed_trades": sum(r["status"] == "CLOSED" for r in ledger),
                        "status_counts": pd.Series([r["status"] for r in ledger]).value_counts().to_dict()})
    else:
        summary.update({"ending_equity": None, "net_pnl": None})
    dump_json(args.output / "summary.json", summary)
    print(json.dumps(json_safe(summary), indent=2))


if __name__ == "__main__":
    main()
