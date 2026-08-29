"""Generate the collective, market-wide anomaly strategy leaderboard."""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import replace

import pandas as pd

from config import CONFIG
from src.backtest.strategy_ranking import rank_strategies_collectively
from src.plotting.collective_ranking import (
    plot_collective_ranking,
    write_gallery_ranking,
    write_markdown_report,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", help="read a namespaced research run")
    args = parser.parse_args()
    config = replace(CONFIG, artifact_namespace=args.namespace)
    summary = pd.read_csv(config.results_dir / "market_summary.csv")
    metadata = json.loads((config.results_dir / "run_metadata.json").read_text(encoding="utf-8"))
    ranked = rank_strategies_collectively(summary)
    output_dir = config.results_dir / "strategy_rankings"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "collective_strategy_ranking.csv"
    chart_path = output_dir / "collective_strategy_ranking.png"
    ranked.to_csv(csv_path, index=False)
    plot_collective_ranking(ranked, chart_path)
    write_gallery_ranking(
        ranked,
        config.results_dir / "stock_gallery",
        int(metadata["evaluation_sessions"]),
        int(metadata["number_of_symbols"]),
    )

    findings = config.results_dir / "findings" / metadata["evaluation_end"]
    shutil.copy2(csv_path, findings / csv_path.name)
    shutil.copy2(chart_path, findings / chart_path.name)
    write_markdown_report(ranked, findings / "COLLECTIVE_STRATEGY_RANKING.md")
    print(ranked[["collective_rank", "strategy", "collective_score", "evidence_tier", "positive_pillars"]].to_string(index=False))
    print(f"Ranking ready: {config.results_dir / 'stock_gallery' / 'strategy-ranking.html'}")


if __name__ == "__main__":
    main()
