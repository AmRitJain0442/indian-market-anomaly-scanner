"""Collective strategy ranking chart, report, and gallery data."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.backtest.strategy_ranking import COLLECTIVE_PILLARS

TIER_COLORS = {
    "ROBUST POSITIVE": "#68d391",
    "BROAD POSITIVE": "#e6ba62",
    "MIXED": "#78c6d0",
    "WEAK / NEGATIVE": "#f37a6b",
}


def plot_collective_ranking(ranked: pd.DataFrame, output: Path) -> Path:
    ordered = ranked.sort_values("collective_rank", ascending=False)
    strategies = ordered["strategy"].str.replace("_", " ").str.upper()
    components = [f"score_{column}" for column in COLLECTIVE_PILLARS]
    labels = list(COLLECTIVE_PILLARS.values())
    figure = plt.figure(figsize=(16, 9), facecolor="#111512")
    grid = figure.add_gridspec(1, 2, width_ratios=[1.05, 1.4], wspace=0.22)
    bar_ax = figure.add_subplot(grid[0, 0], facecolor="#111512")
    heat_ax = figure.add_subplot(grid[0, 1], facecolor="#111512")

    colors = [TIER_COLORS[tier] for tier in ordered["evidence_tier"]]
    bars = bar_ax.barh(strategies, ordered["collective_score"], color=colors, height=0.68)
    bar_ax.set_xlim(0, 104)
    bar_ax.set_xlabel("COLLECTIVE SCORE / 100", color="#929d91", fontsize=9)
    bar_ax.set_title("MARKET-WIDE STRATEGY RANK", color="#efe8d3", loc="left", fontsize=16, pad=18)
    bar_ax.tick_params(colors="#efe8d3", labelsize=8)
    bar_ax.grid(axis="x", color="#303a33", linewidth=0.7, alpha=0.8)
    bar_ax.set_axisbelow(True)
    for spine in bar_ax.spines.values():
        spine.set_visible(False)
    for bar, score in zip(bars, ordered["collective_score"]):
        bar_ax.text(
            min(score + 1.2, 99),
            bar.get_y() + bar.get_height() / 2,
            f"{score:.1f}",
            va="center",
            color="#efe8d3",
            fontsize=8,
        )

    matrix = ordered[components].to_numpy()
    heat = heat_ax.imshow(
        matrix,
        aspect="auto",
        cmap="RdYlGn",
        vmin=0,
        vmax=100,
        origin="lower",
    )
    heat_ax.set_xticks(range(len(labels)), labels, rotation=28, ha="right", color="#efe8d3", fontsize=8)
    heat_ax.set_yticks(range(len(strategies)), [f"{value}/5" for value in ordered["positive_pillars"]], color="#929d91", fontsize=8)
    heat_ax.set_ylabel("POSITIVE PILLARS", color="#929d91", fontsize=9)
    heat_ax.set_title("FIVE EQUALLY WEIGHTED PILLARS", color="#efe8d3", loc="left", fontsize=16, pad=18)
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            heat_ax.text(column, row, f"{matrix[row, column]:.0f}", ha="center", va="center", color="#111512", fontsize=8, fontweight="bold")
    for spine in heat_ax.spines.values():
        spine.set_visible(False)
    colorbar = figure.colorbar(heat, ax=heat_ax, fraction=0.028, pad=0.03)
    colorbar.ax.tick_params(colors="#929d91", labelsize=7)
    colorbar.outline.set_edgecolor("#303a33")
    figure.suptitle(
        "NSE ANOMALY COLLECTIVE LEADERBOARD",
        color="#e6ba62",
        fontsize=24,
        fontfamily="serif",
        x=0.05,
        ha="left",
        y=0.98,
    )
    figure.text(
        0.05,
        0.925,
        "Relative score ranks strategies against one another; evidence tier separately requires absolute positive outcomes.",
        color="#929d91",
        fontsize=9,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=170, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)
    return output


def ranking_records(ranked: pd.DataFrame) -> list[dict]:
    records = []
    for _, row in ranked.iterrows():
        record = {
            "rank": int(row["collective_rank"]),
            "strategy": row["strategy"],
            "score": round(float(row["collective_score"]), 2),
            "tier": row["evidence_tier"],
            "positive_pillars": int(row["positive_pillars"]),
            "median_pnl": round(float(row["median_net_pnl"]), 2),
            "breadth": round(float(row["pct_profitable"]), 6),
            "equal_weight_pnl": round(float(row["equal_weight_pnl"]), 2),
            "median_sharpe": round(float(row["median_sharpe"]), 4),
            "cost_breadth": round(float(row["pct_profitable_30bps"]), 6),
            "components": {
                label: round(float(row[f"score_{column}"]), 2)
                for column, label in COLLECTIVE_PILLARS.items()
            },
        }
        records.append(record)
    return records


def write_gallery_ranking(ranked: pd.DataFrame, gallery_dir: Path) -> None:
    assets = Path(__file__).resolve().parent / "gallery_assets"
    for filename in (
        "index.html",
        "style.css",
        "app.js",
        "strategy-ranking.html",
        "strategy-ranking.css",
        "strategy-ranking-app.js",
    ):
        shutil.copy2(assets / filename, gallery_dir / filename)
    data = {
        "method": "Equal-weight average of five cross-strategy percentile scores",
        "weights": {label: 0.20 for label in COLLECTIVE_PILLARS.values()},
        "strategies": ranking_records(ranked),
    }
    (gallery_dir / "strategy-ranking-data.js").write_text(
        "window.STRATEGY_RANKING = " + json.dumps(data, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def write_markdown_report(ranked: pd.DataFrame, output: Path) -> Path:
    lines = [
        "# Collective strategy ranking",
        "",
        "The collective score is the equal-weight average of five relative percentile scores: median stock net PnL, profitable-stock breadth, equal-weight universe PnL, median stock Sharpe, and profitable-stock breadth at 30 bps per side.",
        "",
        "The score is relative—not a probability of success. The evidence tier separately counts how many pillars are positive in absolute terms.",
        "",
        "| Rank | Strategy | Score | Tier | Positive pillars | Median PnL | Profitable | Equal-weight PnL | Median Sharpe | Profitable at 30 bps |",
        "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in ranked.iterrows():
        lines.append(
            f"| {int(row['collective_rank'])} | {row['strategy']} | {row['collective_score']:.1f} | "
            f"{row['evidence_tier']} | {int(row['positive_pillars'])}/5 | INR {row['median_net_pnl']:,.0f} | "
            f"{row['pct_profitable']:.1%} | INR {row['equal_weight_pnl']:,.0f} | {row['median_sharpe']:.2f} | "
            f"{row['pct_profitable_30bps']:.1%} |"
        )
    lines.extend(
        [
            "",
            "## Evidence tiers",
            "",
            "- **ROBUST POSITIVE:** 5/5 pillars positive.",
            "- **BROAD POSITIVE:** 4/5 pillars positive.",
            "- **MIXED:** 2–3 pillars positive.",
            "- **WEAK / NEGATIVE:** 0–1 pillars positive.",
            "",
            "> This is an in-sample discovery ranking, not evidence of future profitability.",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output
