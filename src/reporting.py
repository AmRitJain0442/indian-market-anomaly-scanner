"""Write a compact, versionable findings snapshot."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd


def _money(value: float) -> str:
    return f"₹{value:,.0f}"


def _table(frame: pd.DataFrame, columns: list[str]) -> str:
    rows = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for _, row in frame[columns].iterrows():
        values = []
        for column in columns:
            value = row[column]
            if column.endswith("pnl") or column in ("net_pnl", "median_net_pnl", "equal_weight_pnl"):
                values.append(_money(float(value)))
            elif column.startswith("pct_"):
                values.append(f"{float(value):.1%}")
            elif isinstance(value, float):
                values.append(f"{value:.3f}")
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def write_findings(
    all_results: pd.DataFrame,
    summary: pd.DataFrame,
    metadata: dict,
    figures_dir: Path,
    findings_root: Path,
) -> Path:
    end_date = metadata["evaluation_end"]
    output = findings_root / end_date
    output.mkdir(parents=True, exist_ok=True)
    top = all_results.sort_values(["strategy", "net_pnl"], ascending=[True, False]).groupby("strategy").head(10)
    bottom = all_results.sort_values(["strategy", "net_pnl"], ascending=[True, True]).groupby("strategy").head(10)
    summary.to_csv(output / "strategy_overview.csv", index=False)
    top.to_csv(output / "top10_by_strategy.csv", index=False)
    bottom.to_csv(output / "bottom10_by_strategy.csv", index=False)
    (output / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    lines = [
        f"# NSE anomaly findings through {end_date}",
        "",
        f"Evaluation window: **{metadata['evaluation_start']} to {metadata['evaluation_end']}** "
        f"({metadata['evaluation_sessions']} completed NSE sessions); "
        f"**{metadata['number_of_symbols']:,}** historical ordinary equities; "
        f"₹{metadata['initial_capital']:,.0f} per stock-strategy; "
        f"{metadata['one_way_cost_bps']:.0f} bps per side.",
        "",
        "> These are in-sample discovery rankings, not trading recommendations. Short returns are theoretical, extreme discontinuities are conservatively excluded, and no result establishes persistence.",
        "",
        "## Strategy breadth",
        "",
        _table(
            summary.sort_values("median_net_pnl", ascending=False),
            ["strategy", "stocks_tested", "pct_profitable", "median_net_pnl", "equal_weight_pnl", "median_sharpe"],
        ),
        "",
    ]

    pivot = all_results.pivot(index="isin", columns="strategy", values="net_pnl")
    if {"close_to_open", "open_to_close"}.issubset(pivot.columns):
        dominance = (pivot["close_to_open"] > pivot["open_to_close"]).mean()
        lines.extend([
            "## Cross-strategy comparisons",
            "",
            f"- Close-to-open beat open-to-close for **{dominance:.1%}** of securities with both results.",
        ])
        for left, right, label in (
            ("gap_continuation_050", "gap_fade_050", "0.5% gaps favored continuation"),
            ("momentum_1d", "reversal_1d", "one-day moves favored momentum"),
            ("momentum_5d", "reversal_5d", "five-day moves favored momentum"),
        ):
            if {left, right}.issubset(pivot.columns):
                share = (pivot[left] > pivot[right]).mean()
                lines.append(f"- {label} for **{share:.1%}** of securities.")
        lines.append("")

    lines.extend(["## Leaders by net PnL", ""])
    leaders = top.groupby("strategy").head(3)
    lines.append(_table(leaders, ["strategy", "pnl_rank", "symbol", "net_pnl", "number_of_trades", "coverage_ratio", "liquidity_flag"]))
    lines.extend([
        "",
        "## Reproduction",
        "",
        "```bash",
        f"python run_research.py --end-date {end_date}",
        "```",
        "",
        "The CSV files beside this report contain the complete compact overview and top/bottom ten rows for every strategy. Full rankings, curves, and trades are generated locally and excluded from Git because of their size.",
    ])
    (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    for filename in (
        "strategy_breadth.png",
        "strategy_cost_sensitivity.png",
        "close_to_open_distribution.png",
        "close_to_open_equal_weight.png",
        "close_to_open_top20.png",
    ):
        source = figures_dir / filename
        if source.exists():
            shutil.copy2(source, output / filename)
    return output

