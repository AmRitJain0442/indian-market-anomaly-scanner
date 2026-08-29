"""One-command NSE market anomaly research pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import platform
import subprocess
from dataclasses import asdict, replace
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import scipy

from config import CONFIG, ResearchConfig
from src import __version__
from src.backtest.engine import BacktestEngine
from src.data.bhavcopy_parser import build_market_dataset
from src.data.calendar import evaluation_window
from src.data.nse_downloader import NSEDownloader, latest_completed_candidate
from src.data.universe import build_security_master
from src.features.returns import add_return_features
from src.plotting.research import plot_strategy_breadth, plot_strategy_suite
from src.reporting import write_findings
from src.strategies import default_strategies

LOGGER = logging.getLogger("research")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--end-date", type=date.fromisoformat, help="latest session candidate (YYYY-MM-DD)")
    parser.add_argument(
        "--start-date",
        type=date.fromisoformat,
        help="inclusive calendar start; evaluates every completed session in the range",
    )
    parser.add_argument("--history-sessions", type=int, default=CONFIG.raw_history_target)
    parser.add_argument("--evaluation-sessions", type=int, default=CONFIG.evaluation_sessions)
    parser.add_argument("--namespace", help="write processed data and results to a separate subdirectory")
    parser.add_argument(
        "--sparse-curves",
        action="store_true",
        help="store only observed stock sessions (recommended for multi-year runs)",
    )
    parser.add_argument("--no-download", action="store_true", help="reuse data/processed/equity_daily.parquet")
    parser.add_argument("--skip-plots", action="store_true")
    parser.add_argument("--strategies", nargs="*", help="optional subset of strategy names")
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    return parser.parse_args()


def _git_commit(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _metadata(
    config: ResearchConfig,
    dates: pd.DatetimeIndex,
    master: pd.DataFrame,
    strategies,
    validation: dict,
) -> dict:
    return {
        "scanner_version": __version__,
        "git_commit": _git_commit(config.project_root),
        "generated_at_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "evaluation_sessions": len(dates),
        "evaluation_start": dates.min().date().isoformat(),
        "evaluation_end": dates.max().date().isoformat(),
        "analysis_namespace": config.artifact_namespace or "default",
        "curve_storage": "sparse_observed_sessions" if config.sparse_curve_storage else "dense_calendar_grid",
        "initial_capital": config.initial_capital,
        "one_way_cost_bps": config.one_way_cost_bps,
        "cost_model": "symmetric fixed bps per side; every active signal is a round trip",
        "cost_sensitivity_bps": list(config.cost_sensitivity_bps),
        "universe_definition": "historical NSE ordinary equities; INE ISIN and EQ/BE/BZ series; rights entitlements excluded",
        "ordinary_equity_series": list(config.ordinary_equity_series),
        "include_sme": config.include_sme,
        "number_of_symbols": int(master["isin"].nunique()),
        "data_source": "National Stock Exchange of India official daily report archives",
        "strategies": [
            {"name": strategy.name, "parameters": strategy.parameters, "execution_class": strategy.execution_class}
            for strategy in strategies
        ],
        "validation": validation,
        "runtime": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }


def run(args: argparse.Namespace) -> Path:
    config = replace(
        CONFIG,
        evaluation_sessions=args.evaluation_sessions,
        raw_history_target=args.history_sessions,
        artifact_namespace=args.namespace,
        sparse_curve_storage=args.sparse_curves,
    )
    config.results_dir.mkdir(parents=True, exist_ok=True)
    if args.no_download:
        market = pd.read_parquet(config.processed_dir / "equity_daily.parquet")
        validation_path = config.processed_dir / "validation_report.json"
        validation = json.loads(validation_path.read_text(encoding="utf-8")) if validation_path.exists() else {}
    else:
        downloader = NSEDownloader(config)
        if args.start_date:
            end_date = args.end_date or latest_completed_candidate()
            LOGGER.info("Downloading official NSE sessions from %s to %s", args.start_date, end_date)
            sessions = downloader.collect_date_range(args.start_date, end_date)
        else:
            LOGGER.info("Downloading %d official NSE sessions", config.raw_history_target)
            sessions = downloader.collect_sessions(config.raw_history_target, args.end_date)
        LOGGER.info("Parsing %d bhavcopies", len(sessions))
        market, validation = build_market_dataset(sessions, config)

    if args.start_date:
        end_date = pd.Timestamp(args.end_date or market["date"].max())
        available = market.loc[
            market["date"].between(pd.Timestamp(args.start_date), end_date), "date"
        ]
        dates = pd.DatetimeIndex(sorted(available.dropna().unique()))
        if dates.empty:
            raise ValueError("No processed sessions fall inside the requested date range")
    else:
        dates = evaluation_window(market, config.evaluation_sessions)
    LOGGER.info("Evaluation window: %s to %s", dates.min().date(), dates.max().date())
    features = add_return_features(market)
    master = build_security_master(market, dates, config)
    strategies = default_strategies(config)
    if args.strategies:
        requested = set(args.strategies)
        strategies = [strategy for strategy in strategies if strategy.name in requested]
        missing = requested - {strategy.name for strategy in strategies}
        if missing:
            raise ValueError(f"Unknown strategies: {sorted(missing)}")

    engine = BacktestEngine(features, master, dates, config)
    runs = []
    figures_dir = config.results_dir / "figures"
    for index, strategy in enumerate(strategies, start=1):
        LOGGER.info("Running strategy %d/%d: %s", index, len(strategies), strategy.name)
        result = engine.run(strategy)
        runs.append(result)
        result.equal_weight_curve.assign(strategy=strategy.name).to_parquet(
            config.results_dir / "equity_curves" / f"{strategy.name}_equal_weight.parquet",
            index=False,
        )
        if not args.skip_plots:
            plot_strategy_suite(
                strategy.name,
                result.ranking,
                result.curve_path,
                result.equal_weight_curve,
                figures_dir,
                config.plot_top_n,
            )

    all_results = pd.concat([item.ranking for item in runs], ignore_index=True)
    strategy_dir = config.results_dir / "strategy_results"
    strategy_dir.mkdir(parents=True, exist_ok=True)
    all_results.to_parquet(strategy_dir / "all_stock_strategy_results.parquet", index=False)
    all_results.to_csv(strategy_dir / "all_stock_strategy_results.csv", index=False)
    summary = pd.DataFrame([item.summary for item in runs]).sort_values(
        "median_net_pnl", ascending=False
    )
    summary.to_csv(config.results_dir / "market_summary.csv", index=False)
    if not args.skip_plots:
        plot_strategy_breadth(summary, figures_dir)

    metadata = _metadata(config, dates, master, strategies, validation)
    (config.results_dir / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    findings = write_findings(
        all_results,
        summary,
        metadata,
        figures_dir,
        config.results_dir / "findings",
    )
    LOGGER.info("Research complete: %s", findings)
    return findings


if __name__ == "__main__":
    arguments = parse_args()
    logging.basicConfig(
        level=getattr(logging, arguments.log_level),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    run(arguments)
