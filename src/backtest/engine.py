"""Common vectorized accounting engine for every stock-strategy pair."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from config import ResearchConfig
from src.backtest.costs import apply_round_trip_cost
from src.backtest.metrics import calculate_metrics
from src.backtest.ranking import breadth_summary, rank_strategy
from src.strategies.base import Strategy


@dataclass
class StrategyRun:
    strategy: Strategy
    ranking: pd.DataFrame
    summary: dict
    curve_path: Path
    trade_path: Path
    equal_weight_curve: pd.DataFrame


class BacktestEngine:
    def __init__(
        self,
        features: pd.DataFrame,
        security_master: pd.DataFrame,
        evaluation_dates: pd.DatetimeIndex,
        config: ResearchConfig,
    ):
        self.features = features[features["date"].isin(evaluation_dates)].copy()
        self.master = security_master.copy()
        self.dates = evaluation_dates
        self.config = config
        self.curve_dir = config.results_dir / "equity_curves"
        self.trade_dir = config.results_dir / "trades"
        self.ranking_dir = config.results_dir / "rankings"
        for directory in (self.curve_dir, self.trade_dir, self.ranking_dir):
            directory.mkdir(parents=True, exist_ok=True)

    def _calendar_grid(self) -> pd.DataFrame:
        index = pd.MultiIndex.from_product(
            [self.master["isin"], self.dates], names=["isin", "date"]
        )
        return index.to_frame(index=False)

    def run(self, strategy: Strategy) -> StrategyRun:
        generated = strategy.generate_returns(self.features)
        observed = self.features[
            ["date", "isin", "ret_cc", "corporate_action_flag", "circuit_like_flag"]
        ].rename(columns={"ret_cc": "buy_hold_return"})
        generated = generated.merge(observed, on=["date", "isin"], how="left")
        curve = self._calendar_grid().merge(generated, on=["isin", "date"], how="left")
        curve = curve.merge(self.master[["isin", "symbol"]], on="isin", how="left", suffixes=("", "_latest"))
        curve["symbol"] = curve["symbol"].fillna(curve["symbol_latest"])
        curve = curve.drop(columns="symbol_latest")
        curve["missing_session_flag"] = curve["gross_return"].isna()
        curve["signal"] = curve["signal"].fillna(0.0)
        curve["gross_return"] = curve["gross_return"].fillna(0.0)
        curve["buy_hold_return"] = curve["buy_hold_return"].fillna(0.0)
        curve["corporate_action_flag"] = curve["corporate_action_flag"].fillna(False)
        curve["circuit_like_flag"] = curve["circuit_like_flag"].fillna(False)
        curve["active"] = curve["signal"].ne(0.0)
        curve["net_return"] = apply_round_trip_cost(
            curve["gross_return"], curve["active"], self.config.one_way_cost_bps
        )
        curve["strategy"] = strategy.name
        curve = curve.sort_values(["isin", "date"]).reset_index(drop=True)
        grouped = curve.groupby("isin", sort=False)
        curve["gross_equity"] = self.config.initial_capital * grouped["gross_return"].transform(
            lambda returns: (1.0 + returns).cumprod()
        )
        curve["net_equity"] = self.config.initial_capital * grouped["net_return"].transform(
            lambda returns: (1.0 + returns).cumprod()
        )
        curve["drawdown"] = curve["net_equity"] / grouped["net_equity"].cummax() - 1.0

        metric_rows = []
        for isin, stock_curve in curve.groupby("isin", sort=False):
            row = {"isin": isin, **calculate_metrics(
                stock_curve,
                self.config.initial_capital,
                self.config.cost_sensitivity_bps,
            )}
            metric_rows.append(row)
        metrics = pd.DataFrame(metric_rows).merge(self.master, on="isin", how="left")
        metrics["strategy"] = strategy.name
        metrics["parameters"] = strategy.parameter_text
        metrics["execution_class"] = strategy.execution_class
        metrics["evaluation_start"] = self.dates.min()
        metrics["evaluation_end"] = self.dates.max()
        ranking = rank_strategy(metrics)

        comparable = rank_strategy(
            metrics[metrics["coverage_ratio"].ge(self.config.comparable_coverage_ratio)]
        )
        ranking.to_csv(self.ranking_dir / f"{strategy.name}.csv", index=False)
        comparable.to_csv(self.ranking_dir / f"{strategy.name}_comparable.csv", index=False)

        eligible = curve[~curve["missing_session_flag"]]
        ew = eligible.groupby("date", as_index=False)["net_return"].mean()
        ew["net_equity"] = self.config.initial_capital * (1.0 + ew["net_return"]).cumprod()
        equal_weight_pnl = float(ew["net_equity"].iloc[-1] - self.config.initial_capital)
        summary = breadth_summary(metrics, equal_weight_pnl)
        for bps in self.config.cost_sensitivity_bps:
            column = f"pnl_{int(bps)}bps"
            summary[f"pct_profitable_{int(bps)}bps"] = float(metrics[column].gt(0).mean())
            summary[f"median_pnl_{int(bps)}bps"] = float(metrics[column].median())

        curve_path = self.curve_dir / f"{strategy.name}.parquet"
        curve_columns = [
            "date", "symbol", "isin", "strategy", "signal", "gross_return", "net_return",
            "gross_equity", "net_equity", "drawdown", "missing_session_flag",
            "corporate_action_flag", "circuit_like_flag",
        ]
        curve[curve_columns].to_parquet(curve_path, index=False)

        trades = curve[curve["active"]].copy()
        trades["side"] = np.where(trades["signal"] > 0, "LONG", "SHORT")
        capital_before = grouped["net_equity"].shift(1).fillna(self.config.initial_capital)
        trades["capital_before"] = capital_before.loc[trades.index]
        trades["capital_after"] = trades["net_equity"]
        trades["pnl"] = trades["capital_after"] - trades["capital_before"]
        trades["estimated_cost"] = 2.0 * self.config.one_way_cost_bps / 10_000.0
        trades["signal_date"] = trades["date"]
        trade_columns = [
            "strategy", "symbol", "isin", "signal_date", "entry_date", "entry_price",
            "exit_date", "exit_price", "side", "gross_return", "estimated_cost",
            "net_return", "capital_before", "pnl", "capital_after",
        ]
        trade_path = self.trade_dir / f"{strategy.name}.parquet"
        trades[trade_columns].to_parquet(trade_path, index=False)
        return StrategyRun(strategy, ranking, summary, curve_path, trade_path, ew)
