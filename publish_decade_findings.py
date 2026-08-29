"""Publish compact, versionable artifacts from the namespaced decade run."""

from __future__ import annotations

import json
import shutil
from dataclasses import replace
from pathlib import Path

from config import CONFIG


CURATED_FILES = (
    "README.md",
    "run_metadata.json",
    "strategy_overview.csv",
    "collective_strategy_ranking.csv",
    "collective_strategy_ranking.png",
    "top10_by_strategy.csv",
    "bottom10_by_strategy.csv",
    "top10_liquid_comparable.csv",
    "strategy_breadth.png",
    "strategy_cost_sensitivity.png",
    "close_to_open_distribution.png",
    "close_to_open_equal_weight.png",
    "close_to_open_top20.png",
    "STOCK_STRATEGY_COMBINATION_RANKING.md",
    "stock_strategy_combination_ranking.csv.gz",
    "stock_strategy_combination_leaders.png",
    "top500_stock_strategy_combinations.csv",
    "COLLECTIVE_STRATEGY_RANKING.md",
)


def publish() -> Path:
    config = replace(CONFIG, artifact_namespace="ten_year")
    metadata = json.loads((config.results_dir / "run_metadata.json").read_text(encoding="utf-8"))
    source = config.results_dir / "findings" / metadata["evaluation_end"]
    destination = CONFIG.results_dir / "findings" / f"{metadata['evaluation_end']}-ten-year"
    destination.mkdir(parents=True, exist_ok=True)
    for filename in CURATED_FILES:
        candidate = source / filename
        if candidate.exists():
            shutil.copy2(candidate, destination / filename)

    manifest = config.results_dir / "stock_gallery" / "manifest.json"
    if manifest.exists():
        shutil.copy2(manifest, destination / "stock_atlas_manifest.json")
    return destination


if __name__ == "__main__":
    print(publish())
