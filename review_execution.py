"""Reproduce the dated SITINET execution review without changing research results."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from config import CONFIG
from src.backtest.metrics import calculate_metrics
from src.data.bhavcopy_parser import parse_bhavcopy
from src.data.nse_downloader import NSEDownloader


SYMBOLS = ("SITINET", "VHLTD", "SEAMECLTD", "ETHOSLTD", "EFCIL", "ARFIN", "THELEELA")
STRATEGIES = ("gap_fade_050", "gap_fade_100")
MARKET_COLUMNS = [
    "date", "isin", "symbol", "series", "open", "high", "low", "close",
    "last_price", "previous_close", "volume", "traded_value", "circuit_like_flag",
]


def money_result(returns: pd.Series, capital: float) -> dict:
    """Compound diagnostic returns with initial capital included in drawdown."""
    values = returns.to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values <= -1).any():
        raise ValueError("Diagnostic contains invalid returns or account insolvency")
    path = capital * np.cumprod(np.r_[1.0, 1.0 + values])
    return {
        "initial_investment": capital,
        "ending_value": float(path[-1]),
        "profit": float(path[-1] - capital),
        "max_drawdown": float((path / np.maximum.accumulate(path) - 1).min()),
        "trades": int(len(values)),
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capital", type=float, default=1_000.0)
    parser.add_argument("--latest-date", type=date.fromisoformat, default=date(2026, 9, 4))
    parser.add_argument("--output", type=Path, default=Path("results/findings/2026-09-05-execution-review"))
    args = parser.parse_args()
    if not np.isfinite(args.capital) or args.capital <= 0:
        raise ValueError("Capital must be finite and positive")
    args.output.mkdir(parents=True, exist_ok=True)
    root = CONFIG.results_dir
    metadata = json.loads((root / "run_metadata.json").read_text(encoding="utf-8"))
    rankings = pd.read_csv(root / "strategy_results/all_stock_strategy_results.csv")
    market_path = CONFIG.processed_dir / "equity_daily.parquet"
    market = pd.read_parquet(market_path, columns=MARKET_COLUMNS)
    evaluation = market.loc[market.date.between(metadata["evaluation_start"], metadata["evaluation_end"])]
    source_paths = [
        market_path,
        root / "strategy_results/all_stock_strategy_results.csv",
        root / "run_metadata.json",
        CONFIG.project_root / "src/strategies/daily.py",
        CONFIG.project_root / "src/strategies/base.py",
        CONFIG.project_root / "src/features/returns.py",
        CONFIG.project_root / "src/backtest/engine.py",
        CONFIG.project_root / "src/backtest/metrics.py",
        CONFIG.project_root / "src/backtest/combination_ranking.py",
    ]
    summary = {
        "review_date": "2026-09-05",
        "historical_evaluation_start": metadata["evaluation_start"],
        "historical_evaluation_end": metadata["evaluation_end"],
        "initial_investment": args.capital,
        "research_initial_capital": metadata["initial_capital"],
        "limitations": [
            "Historical price diagnostics are not executable returns or predictions.",
            "EQ-only filtering checks session series, not historical broker permission.",
            "Tick stresses are hypothetical adverse fills, not measured spreads.",
            "Last-price substitution is not a timed, executable exit.",
            "Liquidity ratios use realized daily totals for audit only, not trading signals.",
            "The September 4 snapshot does not update the historical backtest.",
        ],
    }
    pair_rows = []
    sitinet = None
    for strategy in STRATEGIES:
        path = root / "trades" / f"{strategy}.parquet"
        source_paths.append(path)
        trades = pd.read_parquet(path, filters=[("symbol", "in", list(SYMBOLS))])
        joined = trades.merge(
            evaluation.drop(columns="symbol"),
            left_on=["isin", "entry_date"],
            right_on=["isin", "date"],
            how="left",
            validate="many_to_one",
        )
        assert joined.series.notna().all(), "Missing session-level series evidence"
        for symbol, selected in joined.groupby("symbol"):
            selected = selected.sort_values("entry_date")
            original = money_result(selected.net_return, args.capital)
            ranked_row = rankings.loc[rankings.symbol.eq(symbol) & rankings.strategy.eq(strategy)].iloc[0]
            expected = ranked_row.net_pnl * args.capital / metadata["initial_capital"]
            assert np.isclose(original["profit"], expected), (symbol, strategy)
            eq = selected.loc[selected.series.eq("EQ")]
            eq_result = money_result(eq.net_return, args.capital)
            daily = evaluation.loc[evaluation.symbol.eq(symbol)]
            pair_rows.append({
                "symbol": symbol, "strategy": strategy,
                "initial_investment": args.capital,
                "modeled_profit": original["profit"],
                "modeled_ending_value": original["ending_value"],
                "modeled_trades": len(selected),
                "short_trades": int(selected.side.eq("SHORT").sum()),
                "long_trades": int(selected.side.eq("LONG").sum()),
                "t2t_trades": int(selected.series.isin(["BE", "BZ"]).sum()),
                "eq_series_trades": len(eq),
                "eq_only_ideal_fill_profit": eq_result["profit"],
                "median_daily_traded_value": float(daily.traded_value.median()),
                "one_year_win_rate": float(selected.net_return.gt(0).mean()),
                "one_year_sharpe": float(ranked_row.sharpe),
                "circuit_like_sessions": int(daily.circuit_like_flag.sum()),
                "latest_historical_series": daily.sort_values("date").series.iloc[-1],
            })
            if symbol == "SITINET" and strategy == "gap_fade_050":
                sitinet = selected.copy()
    pairs = pd.DataFrame(pair_rows).sort_values(["strategy", "modeled_profit"], ascending=[True, False])
    pairs.to_csv(args.output / "selected_pair_audit.csv", index=False)
    assert sitinet is not None
    s = sitinet
    side = np.where(s.side.eq("LONG"), 1.0, -1.0)
    cost = 2 * metadata["one_way_cost_bps"] / 10_000
    adverse_entry = s.entry_price + side * 0.01
    stresses = {
        "original_ideal_open_and_close": s.net_return,
        "one_paise_adverse_entry": side * (s.exit_price / adverse_entry - 1) - cost,
        "one_paise_adverse_entry_and_exit": side * ((s.exit_price - side * 0.01) / adverse_entry - 1) - cost,
        "last_price_instead_of_close": side * (s.last_price / s.entry_price - 1) - cost,
    }
    summary["sitinet_price_diagnostics"] = {
        label: money_result(returns, args.capital) for label, returns in stresses.items()
    }
    s["scaled_modeled_notional"] = s.capital_before * args.capital / metadata["initial_capital"]
    s["scaled_notional_div_daily_value"] = s.scaled_modeled_notional / s.traded_value
    s["research_notional_div_daily_value"] = s.capital_before / s.traded_value
    s["one_paise_fraction_of_entry"] = 0.01 / s.entry_price
    s["official_close_differs_from_last"] = ~np.isclose(s.exit_price, s.last_price)
    s["eligible_same_day_intraday_by_series"] = s.series.eq("EQ")
    s.to_csv(args.output / "sitinet_trade_audit.csv", index=False)
    summary["sitinet"] = {
        "observed_series": s.series.unique().tolist(),
        "trades": len(s),
        "short_trades": int(s.side.eq("SHORT").sum()),
        "long_trades": int(s.side.eq("LONG").sum()),
        "series_eligible_intraday_trades": int(s.eligible_same_day_intraday_by_series.sum()),
        "median_entry": float(s.entry_price.median()),
        "minimum_entry": float(s.entry_price.min()),
        "maximum_entry": float(s.entry_price.max()),
        "one_paise_entry_fraction_median": float(s.one_paise_fraction_of_entry.median()),
        "trades_close_differs_from_last": int(s.official_close_differs_from_last.sum()),
        "scaled_notional_over_full_daily_value_count": int(s.scaled_notional_div_daily_value.gt(1).sum()),
        "scaled_notional_div_daily_value_median": float(s.scaled_notional_div_daily_value.median()),
        "scaled_notional_div_daily_value_max": float(s.scaled_notional_div_daily_value.max()),
        "last_trade": {
            "date": s.entry_date.iloc[-1].date().isoformat(),
            "entry": float(s.entry_price.iloc[-1]),
            "close": float(s.exit_price.iloc[-1]),
            "last_price": float(s.last_price.iloc[-1]),
            "research_capital_before": float(s.capital_before.iloc[-1]),
            "scaled_capital_before": float(s.scaled_modeled_notional.iloc[-1]),
            "whole_day_traded_value": float(s.traded_value.iloc[-1]),
        },
    }
    leaderboard_path = root / "findings/2026-08-27/top500_stock_strategy_combinations.csv"
    leaderboard = pd.read_csv(leaderboard_path)
    latest_series = evaluation.sort_values("date").groupby("isin").tail(1)[["isin", "series"]]
    leaderboard = leaderboard.drop(columns="series", errors="ignore").merge(latest_series, on="isin", validate="many_to_one")
    leaderboard["research_initial_investment"] = metadata["initial_capital"]
    leaderboard.head(20)[[
        "combination_rank", "symbol", "strategy", "series", "research_initial_investment", "net_pnl",
        "sample_tier", "evidence_tier", "median_daily_value",
    ]].to_csv(args.output / "top20_latest_historical_series.csv", index=False)
    source_paths.append(leaderboard_path)
    summary["leaderboard_latest_series_only"] = {
        f"top{n}_BE_or_BZ_rows": int(leaderboard.head(n).series.isin(["BE", "BZ"]).sum())
        for n in (20, 100, 500)
    }
    drawdown_fixture = pd.DataFrame({
        "date": pd.bdate_range("2026-01-01", periods=3),
        "net_return": [-0.10, 0.02, 0.01],
        "gross_return": [-0.10, 0.02, 0.01],
        "buy_hold_return": [0.0, 0.0, 0.0],
        "active": [True, True, True],
    })
    summary["initial_loss_drawdown_diagnostic"] = {
        "returns": drawdown_fixture.net_return.tolist(),
        "existing_metrics_drawdown": calculate_metrics(drawdown_fixture, args.capital, ())["max_drawdown"],
        "drawdown_including_initial_capital": money_result(drawdown_fixture.net_return, args.capital)["max_drawdown"],
    }
    downloader = NSEDownloader(replace(CONFIG, request_retries=2, request_timeout_seconds=15))
    downloaded = downloader.download_one(args.latest_date)
    if downloaded is None:
        raise ValueError(f"No official latest snapshot for {args.latest_date}")
    latest = parse_bhavcopy(downloaded.path, CONFIG)
    latest = latest.loc[latest.symbol.isin(SYMBOLS)]
    latest.to_csv(args.output / "latest_exchange_snapshot.csv", index=False)
    summary["latest_source"] = {
        "url": downloaded.url, "sha256": downloaded.sha256,
        "date": args.latest_date.isoformat(),
    }
    summary["input_sha256"] = {
        str(path.relative_to(CONFIG.project_root)): sha256(path) for path in source_paths
    }
    (args.output / "audit_summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8",
    )
    print(pairs.to_string(index=False))
    print(json.dumps({k: v for k, v in summary.items() if k != "input_sha256"}, indent=2))
    print(f"Audit written to {args.output}")


if __name__ == "__main__":
    main()
