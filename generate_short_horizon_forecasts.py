"""Generate 1, 3, and 5-session NSE research forecasts."""

from __future__ import annotations

import argparse
from dataclasses import replace

import pandas as pd

from config import CONFIG
from src.forecasting.short_horizon import ForecastConfig, generate_short_horizon_forecasts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", help="read and write a namespaced research run")
    parser.add_argument("--evaluation-sessions", type=int, default=60)
    parser.add_argument("--refit-every", type=int, default=20)
    parser.add_argument("--training-sessions", type=int, default=756)
    args = parser.parse_args()
    config = replace(CONFIG, artifact_namespace=args.namespace)
    market = pd.read_parquet(config.processed_dir / "equity_daily.parquet")
    settings = ForecastConfig(
        evaluation_sessions=args.evaluation_sessions,
        refit_every_sessions=args.refit_every,
        training_sessions=args.training_sessions,
    )
    output = generate_short_horizon_forecasts(market, config, settings)
    print(f"Forecast research ready: {output}")


if __name__ == "__main__":
    main()
