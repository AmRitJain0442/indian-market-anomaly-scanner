"""Generate one visual atlas per stock, covering every configured strategy."""

from __future__ import annotations

import argparse
from pathlib import Path

from config import CONFIG
from src.plotting.stock_atlas import generate_stock_gallery


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=CONFIG.results_dir / "stock_gallery")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, help="render a smaller validation subset")
    args = parser.parse_args()
    manifest = generate_stock_gallery(CONFIG, args.output, args.workers, args.limit)
    print(
        f"Gallery ready: {args.output / 'index.html'} "
        f"({manifest['stock_count']:,} stocks, {manifest['chart_count']:,} charts)"
    )


if __name__ == "__main__":
    main()

