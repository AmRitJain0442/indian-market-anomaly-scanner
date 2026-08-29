"""Artifacts for the complete stock-strategy combination leaderboard."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.backtest.combination_ranking import COMBINATION_PILLARS


def _report_money(value: float) -> str:
    if abs(value) >= 1_000_000_000_000:
        return f"INR {value:.3e}"
    return f"INR {value:,.0f}"

COLORS = {
    "ROBUST POSITIVE": "#68d391",
    "BROAD POSITIVE": "#e6ba62",
    "MIXED": "#78c6d0",
    "WEAK / NEGATIVE": "#f37a6b",
}


def _pair_label(frame: pd.DataFrame) -> pd.Series:
    return frame["symbol"] + "  /  " + frame["strategy"].str.replace("_", " ").str.upper()


def plot_combination_leaders(ranked: pd.DataFrame, output: Path, top_n: int = 15) -> Path:
    """Plot overall and comparable leaders side by side."""
    overall = ranked.head(top_n).sort_values("combination_score")
    comparable = ranked[ranked["sample_tier"].eq("COMPARABLE")].head(top_n).sort_values("combination_score")
    figure, axes = plt.subplots(1, 2, figsize=(18, 10), facecolor="#0e120f")
    figure.subplots_adjust(left=0.14, right=0.98, wspace=0.56)
    for axis, frame, title in zip(
        axes,
        (overall, comparable),
        ("OVERALL · ALL PAIRS", "COMPARABLE · LIQUID + FULL HISTORY"),
    ):
        axis.set_facecolor("#0e120f")
        colors = [COLORS[value] for value in frame["evidence_tier"]]
        bars = axis.barh(_pair_label(frame), frame["combination_score"], color=colors, height=0.68)
        axis.set_xlim(0, 102)
        axis.set_title(title, loc="left", color="#efe8d3", fontsize=15, pad=18)
        axis.set_xlabel("COMBINATION SCORE / 100", color="#929d91", fontsize=9)
        axis.tick_params(colors="#efe8d3", labelsize=8)
        axis.grid(axis="x", color="#303a33", alpha=0.7, linewidth=0.7)
        axis.set_axisbelow(True)
        for spine in axis.spines.values():
            spine.set_visible(False)
        for bar, score in zip(bars, frame["combination_score"]):
            axis.text(
                float(score) - 1.0,
                bar.get_y() + bar.get_height() / 2,
                f"{score:.1f}",
                va="center",
                ha="right",
                color="#111512",
                fontsize=8,
                fontweight="bold",
            )
    figure.suptitle(
        "NSE STOCK × STRATEGY LEADERBOARD",
        x=0.055,
        y=0.985,
        ha="left",
        color="#e6ba62",
        fontsize=24,
        fontfamily="serif",
    )
    figure.text(
        0.055,
        0.945,
        "Every stock-strategy pair ranked across profit, risk, cost survival, drawdown, and buy-and-hold excess.",
        color="#929d91",
        fontsize=9,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=170, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)
    return output


def _clean_number(value, digits: int = 4):
    if pd.isna(value):
        return None
    return round(float(value), digits)


def combination_records(ranked: pd.DataFrame, initial_capital: float) -> list[dict]:
    """Use compact keys to keep the offline 34k-row browser payload small."""
    records = []
    for row in ranked.itertuples(index=False):
        records.append(
            {
                "r": int(row.combination_rank),
                "cr": None if pd.isna(row.comparable_rank) else int(row.comparable_rank),
                "pr": int(row.profit_rank),
                "sy": row.symbol,
                "co": row.company_name,
                "id": row.isin,
                "st": row.strategy,
                "sc": round(float(row.combination_score), 2),
                "et": row.evidence_tier,
                "pp": int(row.positive_pillars),
                "qt": row.sample_tier,
                "inv": round(initial_capital, 2),
                "pnl": round(float(row.net_pnl), 2),
                "end": round(initial_capital + float(row.net_pnl), 2),
                "p30": round(float(row.pnl_30bps), 2),
                "sh": _clean_number(row.sharpe),
                "dd": _clean_number(row.max_drawdown, 6),
                "tr": int(row.number_of_trades),
                "wr": _clean_number(row.win_rate, 6),
                "cv": round(float(row.coverage_ratio), 6),
                "liq": row.liquidity_flag,
            }
        )
    return records


def write_combination_gallery(
    ranked: pd.DataFrame,
    gallery_dir: Path,
    initial_capital: float,
) -> Path:
    assets = Path(__file__).resolve().parent / "gallery_assets"
    for filename in (
        "combination-ranking.html",
        "combination-ranking.css",
        "combination-ranking-app.js",
    ):
        shutil.copy2(assets / filename, gallery_dir / filename)
    payload = {
        "count": len(ranked),
        "stock_count": int(ranked["isin"].nunique()),
        "strategy_count": int(ranked["strategy"].nunique()),
        "session_count": int(ranked["sessions_available"].max()),
        "initial_capital": initial_capital,
        "method": "Five-pillar cross-combination percentile score",
        "pillars": [
            {"key": column, "label": label, "weight": weight}
            for column, (label, weight) in COMBINATION_PILLARS.items()
        ],
        "rows": combination_records(ranked, initial_capital),
    }
    output = gallery_dir / "combination-ranking-data.js"
    output.write_text(
        "window.COMBINATION_RANKING=" + json.dumps(payload, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    return output


def write_combination_report(ranked: pd.DataFrame, output: Path, initial_capital: float) -> Path:
    lines = [
        "# Stock × strategy combination ranking",
        "",
        f"All **{len(ranked):,}** stock-strategy combinations are ranked from an initial investment of **INR {initial_capital:,.0f}** per pair.",
        "",
        "The relative combination score weights net PnL (25%), Sharpe (20%), PnL at 30 bps per side (20%), excess PnL versus buy-and-hold (20%), and drawdown resilience (15%). The profit rank is also retained independently.",
        "",
        "A pair is comparable when it has at least 95% history, an `OK` liquidity flag, and at least 20 trades. Every non-comparable pair remains in the overall table and is explicitly labelled.",
        "",
        "## Top 25 overall",
        "",
        "| Rank | Stock | Strategy | Score | Initial | Profit | Ending value | Sharpe | 30 bps PnL | Evidence | Sample |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in ranked.head(25).itertuples(index=False):
        lines.append(
            f"| {row.combination_rank} | {row.symbol} | {row.strategy} | {row.combination_score:.1f} | "
            f"{_report_money(initial_capital)} | {_report_money(row.net_pnl)} | {_report_money(initial_capital + row.net_pnl)} | "
            f"{row.sharpe:.2f} | {_report_money(row.pnl_30bps)} | {row.evidence_tier} ({row.positive_pillars}/5) | {row.sample_tier} |"
        )
    lines.extend(
        [
            "",
            "## Top 25 comparable",
            "",
            "| Comparable rank | Overall rank | Stock | Strategy | Score | Initial | Profit | Ending value | Sharpe | 30 bps PnL |",
            "|---:|---:|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in ranked[ranked["sample_tier"].eq("COMPARABLE")].head(25).itertuples(index=False):
        lines.append(
            f"| {row.comparable_rank} | {row.combination_rank} | {row.symbol} | {row.strategy} | "
            f"{row.combination_score:.1f} | {_report_money(initial_capital)} | {_report_money(row.net_pnl)} | "
            f"{_report_money(initial_capital + row.net_pnl)} | {row.sharpe:.2f} | {_report_money(row.pnl_30bps)} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The combination score is a relative discovery score, not a probability or forecast.",
            "- `ROBUST POSITIVE` requires positive net PnL, Sharpe, 30 bps PnL, excess PnL, and a positive 95% mean-trade confidence floor.",
            "- Low-liquidity and limited-sample leaders can be economically implausible; use the comparable rank as the more inspectable shortlist.",
            "- Full results are provided in the adjacent compressed CSV and in the offline interactive atlas release.",
            "",
            "> In-sample research only; not a trading recommendation.",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output
