"""Compact, non-interactive research plots."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

RUPEES = FuncFormatter(lambda value, _: f"₹{value / 1_000:.0f}k")


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _selected_curves(curve: pd.DataFrame, ranking: pd.DataFrame, top: bool, n: int) -> pd.DataFrame:
    selected = ranking.head(n) if top else ranking.tail(n)
    return curve[curve["isin"].isin(selected["isin"])]


def plot_strategy_suite(
    strategy: str,
    ranking: pd.DataFrame,
    curve_path: Path,
    equal_weight: pd.DataFrame,
    output_dir: Path,
    top_n: int = 20,
) -> list[Path]:
    curve = pd.read_parquet(curve_path)
    paths: list[Path] = []
    for top, suffix in ((True, "top20"), (False, "bottom20")):
        selected = _selected_curves(curve, ranking, top, min(top_n, len(ranking)))
        fig, ax = plt.subplots(figsize=(11, 6))
        for symbol, stock in selected.groupby("symbol"):
            ax.plot(stock["date"], stock["net_equity"], linewidth=1.0, alpha=0.8, label=symbol)
        ax.axhline(100_000, color="black", linewidth=0.8, linestyle="--")
        ax.set(title=f"{strategy}: {suffix.replace('20', ' 20 ')} net equity", ylabel="Equity")
        ax.yaxis.set_major_formatter(RUPEES)
        ax.legend(ncol=4, fontsize=7, frameon=False)
        path = output_dir / f"{strategy}_{suffix}.png"
        _save(fig, path)
        paths.append(path)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(ranking["net_pnl"].dropna(), bins=50, color="#35618f", alpha=0.85)
    ax.axvline(0, color="black", linewidth=1)
    ax.axvline(ranking["net_pnl"].median(), color="#d67b22", linestyle="--", label="Median")
    ax.axvline(ranking["net_pnl"].mean(), color="#8c3b6f", linestyle=":", label="Mean")
    session_count = int(pd.DatetimeIndex(curve["date"]).nunique())
    ax.set(
        title=f"{strategy}: {session_count:,}-session net PnL distribution",
        xlabel="Net PnL",
        ylabel="Stocks",
    )
    ax.xaxis.set_major_formatter(RUPEES)
    ax.legend(frameon=False)
    path = output_dir / f"{strategy}_distribution.png"
    _save(fig, path)
    paths.append(path)

    display_n = min(30, len(ranking))
    display = pd.concat([ranking.head(display_n), ranking.tail(display_n)]).drop_duplicates("isin")
    colors = np.where(display["net_pnl"] >= 0, "#2a9d6f", "#d65555")
    fig, ax = plt.subplots(figsize=(12, max(6, len(display) * 0.19)))
    ax.barh(display["symbol"], display["net_pnl"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.invert_yaxis()
    ax.set(title=f"{strategy}: top and bottom net PnL", xlabel="Net PnL")
    ax.xaxis.set_major_formatter(RUPEES)
    path = output_dir / f"{strategy}_ranking.png"
    _save(fig, path)
    paths.append(path)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].scatter(ranking["number_of_trades"], ranking["net_pnl"], s=10, alpha=0.45)
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set(xlabel="Trades", ylabel="Net PnL", title="PnL vs trades")
    axes[0].yaxis.set_major_formatter(RUPEES)
    liquidity = ranking["median_daily_value"].where(ranking["median_daily_value"] > 0)
    axes[1].scatter(np.log10(liquidity), ranking["net_pnl"], s=10, alpha=0.45, color="#8c3b6f")
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set(xlabel="log10 median daily traded value", ylabel="Net PnL", title="PnL vs liquidity")
    axes[1].yaxis.set_major_formatter(RUPEES)
    path = output_dir / f"{strategy}_diagnostics.png"
    _save(fig, path)
    paths.append(path)

    best_isin = ranking.iloc[0]["isin"]
    best_symbol = ranking.iloc[0]["symbol"]
    best = curve[curve["isin"].eq(best_isin)]
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    axes[0].plot(best["date"], best["gross_equity"], label="Gross", linewidth=1.5)
    axes[0].plot(best["date"], best["net_equity"], label="Net", linewidth=1.5)
    axes[0].set(title=f"{strategy}: gross vs net for rank 1 ({best_symbol})", ylabel="Equity")
    axes[0].yaxis.set_major_formatter(RUPEES)
    axes[0].legend(frameon=False)
    axes[1].fill_between(best["date"], best["drawdown"], 0, color="#d65555", alpha=0.7)
    axes[1].set(ylabel="Drawdown", xlabel="Date")
    path = output_dir / f"{strategy}_gross_net_drawdown.png"
    _save(fig, path)
    paths.append(path)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(equal_weight["date"], equal_weight["net_equity"], color="#35618f", linewidth=1.8)
    ax.axhline(100_000, color="black", linestyle="--", linewidth=0.8)
    ax.set(title=f"{strategy}: equal-weight universe equity", ylabel="Equity", xlabel="Date")
    ax.yaxis.set_major_formatter(RUPEES)
    path = output_dir / f"{strategy}_equal_weight.png"
    _save(fig, path)
    paths.append(path)
    return paths


def plot_strategy_breadth(summary: pd.DataFrame, output_dir: Path) -> list[Path]:
    paths: list[Path] = []
    ordered = summary.sort_values("pct_profitable")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    axes[0].barh(ordered["strategy"], ordered["pct_profitable"] * 100, color="#35618f")
    axes[0].axvline(50, color="black", linestyle="--", linewidth=0.8)
    axes[0].set(xlabel="Profitable stocks (%)", title="Strategy breadth after costs")
    axes[1].barh(ordered["strategy"], ordered["median_net_pnl"], color="#d67b22")
    axes[1].axvline(0, color="black", linewidth=0.8)
    axes[1].set(xlabel="Median stock net PnL", title="Median stock outcome")
    axes[1].xaxis.set_major_formatter(RUPEES)
    path = output_dir / "strategy_breadth.png"
    _save(fig, path)
    paths.append(path)

    cost_columns = [column for column in summary if column.startswith("pct_profitable_")]
    fig, ax = plt.subplots(figsize=(11, 6))
    for _, row in summary.iterrows():
        x = [int(column.removeprefix("pct_profitable_").removesuffix("bps")) for column in cost_columns]
        y = [row[column] * 100 for column in cost_columns]
        ax.plot(x, y, marker="o", linewidth=1, label=row["strategy"])
    ax.axhline(50, color="black", linestyle="--", linewidth=0.8)
    ax.set(xlabel="One-way cost (bps)", ylabel="Profitable stocks (%)", title="Cost sensitivity")
    ax.legend(ncol=3, fontsize=7, frameon=False)
    path = output_dir / "strategy_cost_sensitivity.png"
    _save(fig, path)
    paths.append(path)
    return paths
