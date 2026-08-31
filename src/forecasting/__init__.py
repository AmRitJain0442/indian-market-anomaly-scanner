"""Short-horizon return forecasting for the research atlas."""

from src.forecasting.short_horizon import (
    ForecastConfig,
    build_forecast_frame,
    generate_short_horizon_forecasts,
)

__all__ = [
    "ForecastConfig",
    "build_forecast_frame",
    "generate_short_horizon_forecasts",
]
