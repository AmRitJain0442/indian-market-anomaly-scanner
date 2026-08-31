"""Leakage-safe pooled forecasts for the next 1, 3, and 5 NSE sessions.

The panel model follows the shared cross-sectional prediction function in Gu,
Kelly, and Xiu (2020).  The implementation is deliberately a transparent ridge
baseline rather than an exact reproduction of their monthly US-equity study.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from config import ResearchConfig


FEATURE_COLUMNS = (
    "return_1",
    "return_5",
    "return_20",
    "intraday_return",
    "overnight_return",
    "range_pct",
    "volatility_5",
    "volatility_20",
    "volume_surprise",
    "liquidity",
    "ma_gap_20",
    "drawdown_20",
)


@dataclass(frozen=True)
class ForecastConfig:
    horizons: tuple[int, ...] = (1, 3, 5)
    evaluation_sessions: int = 60
    refit_every_sessions: int = 20
    training_sessions: int = 756
    minimum_training_sessions: int = 126
    minimum_training_rows: int = 10_000
    ridge_alpha: float = 0.001
    interval_coverage: float = 0.80


@dataclass(frozen=True)
class RidgeModel:
    intercept: float
    coefficients: np.ndarray
    target_low: float
    target_high: float

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        values = frame.loc[:, FEATURE_COLUMNS].to_numpy(dtype=np.float64)
        prediction = self.intercept + values @ self.coefficients
        return np.clip(prediction, self.target_low, self.target_high)


def _consecutive_ratio(
    work: pd.DataFrame,
    grouped,
    periods: int,
) -> pd.Series:
    lag_close = grouped["close"].shift(periods)
    lag_session = grouped["session_number"].shift(periods)
    consecutive = work["session_number"].sub(lag_session).eq(periods)
    return np.log(work["close"] / lag_close).where(consecutive)


def build_forecast_frame(market: pd.DataFrame, horizons: tuple[int, ...] = (1, 3, 5)) -> pd.DataFrame:
    """Build close-time predictors and forward returns on consecutive sessions."""
    work = market.sort_values(["isin", "date"]).copy()
    calendar = pd.DatetimeIndex(sorted(work["date"].dropna().unique()))
    session_number = pd.Series(np.arange(len(calendar), dtype=np.int32), index=calendar)
    work["session_number"] = work["date"].map(session_number).astype("int32")
    grouped = work.groupby("isin", sort=False)

    work["return_1"] = _consecutive_ratio(work, grouped, 1)
    work["return_5"] = _consecutive_ratio(work, grouped, 5)
    work["return_20"] = _consecutive_ratio(work, grouped, 20)
    work["intraday_return"] = np.log(work["close"] / work["open"])

    previous_close = grouped["close"].shift(1)
    previous_session = grouped["session_number"].shift(1)
    work["overnight_return"] = np.log(work["open"] / previous_close).where(
        work["session_number"].sub(previous_session).eq(1)
    )
    work["range_pct"] = (work["high"] - work["low"]) / work["open"]
    work["volatility_5"] = grouped["return_1"].transform(
        lambda values: values.rolling(5, min_periods=5).std()
    )
    work["volatility_20"] = grouped["return_1"].transform(
        lambda values: values.rolling(20, min_periods=20).std()
    )
    work["forecast_scale"] = work["volatility_20"].clip(lower=0.002)

    log_volume = np.log1p(work["volume"].clip(lower=0))
    work["volume_surprise"] = log_volume - log_volume.groupby(work["isin"], sort=False).transform(
        lambda values: values.shift(1).rolling(20, min_periods=20).mean()
    )
    work["liquidity"] = np.log1p(work["traded_value"].clip(lower=0))
    mean_20 = grouped["close"].transform(lambda values: values.rolling(20, min_periods=20).mean())
    high_20 = grouped["close"].transform(lambda values: values.rolling(20, min_periods=20).max())
    work["ma_gap_20"] = np.log(work["close"] / mean_20)
    work["drawdown_20"] = np.log(work["close"] / high_20)

    bad_today = work["corporate_action_flag"].fillna(False).astype(bool)
    work.loc[bad_today, list(FEATURE_COLUMNS)] = np.nan

    # Cross-sectional ranks make unlike characteristics comparable and limit
    # the influence of extreme observations. Only same-session data is used.
    ranked = work.groupby("date", sort=False)[list(FEATURE_COLUMNS)].rank(pct=True, method="average")
    work.loc[:, FEATURE_COLUMNS] = ranked - 0.5

    for horizon in horizons:
        future_close = grouped["close"].shift(-horizon)
        future_session = grouped["session_number"].shift(-horizon)
        consecutive = future_session.sub(work["session_number"]).eq(horizon)
        future_bad = pd.Series(False, index=work.index)
        for step in range(1, horizon + 1):
            future_bad |= grouped["corporate_action_flag"].shift(-step, fill_value=False).astype(bool)
        target = np.log(future_close / work["close"]).where(consecutive & ~future_bad & ~bad_today)
        work[f"target_{horizon}"] = target
        work[f"target_end_session_{horizon}"] = future_session.where(target.notna())

    keep = [
        "date",
        "session_number",
        "symbol",
        "isin",
        "company_name",
        "close",
        "forecast_scale",
        *FEATURE_COLUMNS,
    ]
    for horizon in horizons:
        keep.extend((f"target_{horizon}", f"target_end_session_{horizon}"))
    return work.loc[:, keep].reset_index(drop=True)


def _fit_ridge(training: pd.DataFrame, target_column: str, alpha: float) -> RidgeModel:
    x = training.loc[:, FEATURE_COLUMNS].to_numpy(dtype=np.float64)
    y_raw = training[target_column].to_numpy(dtype=np.float64)
    target_low, target_high = np.quantile(y_raw, [0.005, 0.995])
    y = np.clip(y_raw, target_low, target_high)
    x_mean = x.mean(axis=0)
    y_mean = float(y.mean())
    centered_x = x - x_mean
    covariance = centered_x.T @ centered_x / len(x)
    cross_product = centered_x.T @ (y - y_mean) / len(x)
    penalty = np.eye(len(FEATURE_COLUMNS), dtype=np.float64) * alpha
    coefficients = np.linalg.solve(covariance + penalty, cross_product)
    intercept = y_mean - float(x_mean @ coefficients)
    return RidgeModel(intercept, coefficients, float(target_low), float(target_high))


def _valid_rows(frame: pd.DataFrame, horizon: int) -> pd.DataFrame:
    required = [*FEATURE_COLUMNS, f"target_{horizon}", f"target_end_session_{horizon}"]
    return frame.dropna(subset=required)


def _minimum_training_ok(training: pd.DataFrame, settings: ForecastConfig) -> bool:
    return (
        len(training) >= settings.minimum_training_rows
        and training["session_number"].nunique() >= settings.minimum_training_sessions
    )


def _walk_forward(
    frame: pd.DataFrame,
    horizon: int,
    settings: ForecastConfig,
) -> tuple[pd.DataFrame, dict]:
    target_column = f"target_{horizon}"
    end_column = f"target_end_session_{horizon}"
    valid = _valid_rows(frame, horizon)
    last_session = int(frame["session_number"].max())
    eligible_test = valid.loc[valid[end_column].le(last_session)]
    evaluation_dates = np.sort(eligible_test["session_number"].unique())[-settings.evaluation_sessions :]
    predictions: list[pd.DataFrame] = []

    for start in range(0, len(evaluation_dates), settings.refit_every_sessions):
        fold_sessions = evaluation_dates[start : start + settings.refit_every_sessions]
        first_test = int(fold_sessions[0])
        training_floor = first_test - settings.training_sessions
        training = valid.loc[
            valid[end_column].lt(first_test)
            & valid["session_number"].ge(training_floor)
        ]
        if not _minimum_training_ok(training, settings):
            continue
        model = _fit_ridge(training, target_column, settings.ridge_alpha)
        test = valid.loc[valid["session_number"].isin(fold_sessions)].copy()
        test["predicted_return"] = model.predict(test)
        test["actual_return"] = test[target_column]
        test["horizon"] = horizon
        test["training_cutoff_session"] = first_test - 1
        predictions.append(
            test[
                [
                    "date",
                    "session_number",
                    "symbol",
                    "isin",
                    "actual_return",
                    "predicted_return",
                    "forecast_scale",
                    "horizon",
                    "training_cutoff_session",
                ]
            ]
        )

    if not predictions:
        raise ValueError(f"Insufficient history for a leakage-safe {horizon}-session evaluation")
    output = pd.concat(predictions, ignore_index=True)
    residual = output["actual_return"] - output["predicted_return"]
    scaled_error = residual.abs() / (output["forecast_scale"] * np.sqrt(horizon))
    quantile_level = min(
        1.0,
        np.ceil((len(scaled_error) + 1) * settings.interval_coverage) / len(scaled_error),
    )
    interval_multiplier = float(np.quantile(scaled_error, quantile_level, method="higher"))
    half_width = interval_multiplier * output["forecast_scale"] * np.sqrt(horizon)
    output["lower_return"] = output["predicted_return"] - half_width
    output["upper_return"] = output["predicted_return"] + half_width

    actual = output["actual_return"].to_numpy()
    predicted = output["predicted_return"].to_numpy()
    baseline_error = float(np.square(actual).sum())
    metrics = {
        "horizon": horizon,
        "observations": int(len(output)),
        "evaluation_sessions": int(output["session_number"].nunique()),
        "evaluation_start": output["date"].min().date().isoformat(),
        "evaluation_end": output["date"].max().date().isoformat(),
        "mae": float(np.abs(actual - predicted).mean()),
        "rmse": float(np.sqrt(np.square(actual - predicted).mean())),
        "direction_accuracy": float((np.sign(actual) == np.sign(predicted)).mean()),
        "oos_r_squared_vs_zero": float(1.0 - np.square(actual - predicted).sum() / baseline_error)
        if baseline_error
        else None,
        "interval_coverage": float(
            ((actual >= output["lower_return"]) & (actual <= output["upper_return"])).mean()
        ),
        "mean_interval_width": float((output["upper_return"] - output["lower_return"]).mean()),
        "interval_multiplier": interval_multiplier,
    }
    return output, metrics


def fit_forecasts(
    market: pd.DataFrame,
    settings: ForecastConfig | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    """Return current stock forecasts, walk-forward observations, and metrics."""
    settings = settings or ForecastConfig()
    frame = build_forecast_frame(market, settings.horizons)
    last_session = int(frame["session_number"].max())
    latest = frame.loc[frame["session_number"].eq(last_session)].dropna(subset=list(FEATURE_COLUMNS)).copy()
    all_evaluations: list[pd.DataFrame] = []
    all_latest: list[pd.DataFrame] = []
    metrics: list[dict] = []

    for horizon in settings.horizons:
        evaluation, summary = _walk_forward(frame, horizon, settings)
        residual = evaluation["actual_return"] - evaluation["predicted_return"]
        interval_multiplier = float(summary["interval_multiplier"])

        valid = _valid_rows(frame, horizon)
        training = valid.loc[
            valid[f"target_end_session_{horizon}"].le(last_session)
            & valid["session_number"].ge(last_session - settings.training_sessions)
        ]
        if not _minimum_training_ok(training, settings):
            raise ValueError(f"Insufficient history to fit the current {horizon}-session forecast")
        model = _fit_ridge(training, f"target_{horizon}", settings.ridge_alpha)
        current = latest.copy()
        current["predicted_return"] = model.predict(current)
        current["horizon"] = horizon
        half_width = interval_multiplier * current["forecast_scale"] * np.sqrt(horizon)
        current["lower_return"] = current["predicted_return"] - half_width
        current["upper_return"] = current["predicted_return"] + half_width
        current["probability_up"] = [
            float(np.mean(residual.to_numpy() > -prediction))
            for prediction in current["predicted_return"].to_numpy()
        ]
        current["predicted_price"] = current["close"] * np.exp(current["predicted_return"])
        current["lower_price"] = current["close"] * np.exp(current["lower_return"])
        current["upper_price"] = current["close"] * np.exp(current["upper_return"])
        current["model_direction_accuracy"] = summary["direction_accuracy"]
        current["model_interval_coverage"] = summary["interval_coverage"]
        all_latest.append(
            current[
                [
                    "date",
                    "symbol",
                    "isin",
                    "company_name",
                    "close",
                    "horizon",
                    "predicted_return",
                    "lower_return",
                    "upper_return",
                    "probability_up",
                    "predicted_price",
                    "lower_price",
                    "upper_price",
                    "model_direction_accuracy",
                    "model_interval_coverage",
                ]
            ]
        )
        all_evaluations.append(evaluation)
        metrics.append(summary)

    return (
        pd.concat(all_latest, ignore_index=True),
        pd.concat(all_evaluations, ignore_index=True),
        metrics,
    )


def generate_short_horizon_forecasts(
    market: pd.DataFrame,
    config: ResearchConfig,
    settings: ForecastConfig | None = None,
) -> Path:
    """Fit, evaluate, and persist short-horizon forecast artifacts."""
    settings = settings or ForecastConfig()
    latest, evaluation, metrics = fit_forecasts(market, settings)
    output_dir = config.results_dir / "forecasts"
    output_dir.mkdir(parents=True, exist_ok=True)
    latest.to_csv(output_dir / "latest_stock_forecasts.csv", index=False)
    latest.to_parquet(output_dir / "latest_stock_forecasts.parquet", index=False)
    evaluation.to_parquet(output_dir / "walk_forward_predictions.parquet", index=False)
    pd.DataFrame(metrics).to_csv(output_dir / "walk_forward_metrics.csv", index=False)
    metadata = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "forecast_as_of": latest["date"].max().date().isoformat(),
        "model": "pooled cross-sectional ridge regression",
        "target": "forward close-to-close log return on consecutive NSE sessions",
        "features": list(FEATURE_COLUMNS),
        "settings": asdict(settings),
        "papers": [
            {
                "title": "Empirical Asset Pricing via Machine Learning",
                "authors": "Shihao Gu, Bryan Kelly, and Dacheng Xiu",
                "doi": "10.1093/rfs/hhaa009",
                "role": "pooled cross-sectional return prediction and predictor families",
            },
            {
                "title": "Conformalized Quantile Regression",
                "authors": "Yaniv Romano, Evan Patterson, and Emmanuel J. Candes",
                "url": "https://arxiv.org/abs/1905.03222",
                "role": "motivation for calibrated predictive ranges",
            },
        ],
        "important_limit": (
            "The residual ranges are time-ordered conformal-style diagnostics. Financial returns are not "
            "exchangeable, so the formal finite-sample conformal guarantee does not apply."
        ),
        "metrics": metrics,
    }
    output = output_dir / "forecast_metadata.json"
    output.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output
