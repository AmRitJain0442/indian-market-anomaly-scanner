"""Generate one visual atlas per stock, covering every configured strategy."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from config import CONFIG
from src.plotting.stock_atlas import generate_stock_gallery


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=CONFIG.results_dir / "stock_gallery")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, help="render a smaller validation subset")
    parser.add_argument("--namespace", help="read a namespaced research run")
    args = parser.parse_args()
    config = replace(CONFIG, artifact_namespace=args.namespace)
    output = args.output if args.output != CONFIG.results_dir / "stock_gallery" else config.results_dir / "stock_gallery"
    manifest = generate_stock_gallery(config, output, args.workers, args.limit)
    print(
        f"Gallery ready: {output / 'index.html'} "
        f"({manifest['stock_count']:,} stocks, {manifest['chart_count']:,} charts)"
    )


if __name__ == "__main__":
    main()
