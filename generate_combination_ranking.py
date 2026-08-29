"""Rank and publish all stock-strategy combinations in the research run."""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import replace

import pandas as pd

from config import CONFIG
from src.backtest.combination_ranking import rank_stock_strategy_combinations
from src.plotting.combination_ranking import (
    plot_combination_leaders,
    write_combination_gallery,
    write_combination_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", help="read a namespaced research run")
    args = parser.parse_args()
    config = replace(CONFIG, artifact_namespace=args.namespace)
    source = config.results_dir / "strategy_results" / "all_stock_strategy_results.csv"
    metadata = json.loads((config.results_dir / "run_metadata.json").read_text(encoding="utf-8"))
    ranked = rank_stock_strategy_combinations(pd.read_csv(source))
    output_dir = config.results_dir / "combination_rankings"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "stock_strategy_combination_ranking.csv"
    gzip_path = output_dir / "stock_strategy_combination_ranking.csv.gz"
    chart_path = output_dir / "stock_strategy_combination_leaders.png"
    ranked.to_csv(csv_path, index=False)
    ranked.to_csv(gzip_path, index=False, compression={"method": "gzip", "mtime": 0})
    plot_combination_leaders(ranked, chart_path)
    write_combination_gallery(ranked, config.results_dir / "stock_gallery", float(metadata["initial_capital"]))
    shutil.copy2(gzip_path, config.results_dir / "stock_gallery" / gzip_path.name)

    findings = config.results_dir / "findings" / metadata["evaluation_end"]
    shutil.copy2(gzip_path, findings / gzip_path.name)
    shutil.copy2(chart_path, findings / chart_path.name)
    ranked.head(500).to_csv(findings / "top500_stock_strategy_combinations.csv", index=False)
    write_combination_report(
        ranked,
        findings / "STOCK_STRATEGY_COMBINATION_RANKING.md",
        float(metadata["initial_capital"]),
    )
    print(
        ranked.head(25)[
            [
                "combination_rank",
                "symbol",
                "strategy",
                "combination_score",
                "net_pnl",
                "evidence_tier",
                "sample_tier",
            ]
        ].to_string(index=False)
    )
    print(f"Complete ranking: {csv_path} ({len(ranked):,} combinations)")
    print(f"Interactive ranking: {config.results_dir / 'stock_gallery' / 'combination-ranking.html'}")


if __name__ == "__main__":
    main()
