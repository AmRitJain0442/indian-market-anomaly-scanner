"""Fast Pillow renderer for one all-strategy atlas per security."""

from __future__ import annotations

import json
import math
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from config import ResearchConfig

CANVAS = (1760, 1420)
BACKGROUND = "#111512"
PANEL = "#191f1b"
PANEL_ALT = "#151a17"
INK = "#efe8d3"
MUTED = "#929d91"
GRID = "#303a33"
GREEN = "#68d391"
RED = "#f37a6b"
GOLD = "#e6ba62"
CYAN = "#78c6d0"


@dataclass(frozen=True)
class StockRecord:
    index: int
    isin: str
    symbol: str
    company_name: str
    coverage_ratio: float
    liquidity_flag: str
    sessions_available: int
    median_daily_value: float
    corporate_action_observations: int
    circuit_like_sessions: int


@dataclass
class AtlasDataset:
    strategies: list[str]
    records: list[StockRecord]
    equity: dict[str, np.ndarray]
    metrics: dict[str, pd.DataFrame]
    dates: pd.DatetimeIndex
    initial_capital: float
    forecasts: pd.DataFrame
    forecast_metrics: dict[int, dict]


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def _fonts() -> dict[str, ImageFont.FreeTypeFont]:
    return {
        "display": _font(r"C:\Windows\Fonts\georgiab.ttf", 42),
        "title": _font(r"C:\Windows\Fonts\georgiab.ttf", 22),
        "body": _font(r"C:\Windows\Fonts\bahnschrift.ttf", 18),
        "small": _font(r"C:\Windows\Fonts\bahnschrift.ttf", 15),
        "tiny": _font(r"C:\Windows\Fonts\bahnschrift.ttf", 13),
    }


def _compact_money(value: float) -> str:
    sign = "+" if value >= 0 else "-"
    amount = abs(value)
    if amount >= 1_000_000_000_000:
        return f"{sign}INR {amount:.1e}"
    if amount >= 10_000_000:
        return f"{sign}INR {amount / 10_000_000:.1f}cr"
    if amount >= 100_000:
        return f"{sign}INR {amount / 100_000:.1f}L"
    if amount >= 1_000:
        return f"{sign}INR {amount / 1_000:.1f}k"
    return f"{sign}INR {amount:.0f}"


def _ellipsis(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> str:
    if draw.textlength(text, font=font) <= max_width:
        return text
    shortened = text
    while shortened and draw.textlength(shortened + "…", font=font) > max_width:
        shortened = shortened[:-1]
    return shortened + "…"


def _draw_curve_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    strategy: str,
    values: np.ndarray,
    metric: pd.Series,
    fonts: dict,
    initial_capital: float,
) -> None:
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=12, fill=PANEL, outline="#28322b", width=1)
    draw.text((left + 18, top + 16), strategy.replace("_", " ").upper(), font=fonts["small"], fill=INK)
    pnl = float(metric["net_pnl"])
    color = GREEN if pnl >= 0 else RED
    draw.text(
        (right - 18, top + 12),
        f"INV INR {initial_capital:,.0f}",
        font=fonts["tiny"],
        fill=MUTED,
        anchor="ra",
    )
    draw.text(
        (right - 18, top + 35),
        f"PNL {_compact_money(pnl)}",
        font=fonts["tiny"],
        fill=color,
        anchor="ra",
    )

    chart = (left + 18, top + 67, right - 18, bottom - 45)
    x0, y0, x1, y1 = chart
    finite = values[np.isfinite(values)]
    if not len(finite):
        draw.text(((x0 + x1) // 2, (y0 + y1) // 2), "NO DATA", font=fonts["body"], fill=MUTED, anchor="mm")
        return
    low = min(float(finite.min()), 100_000.0)
    high = max(float(finite.max()), 100_000.0)
    if math.isclose(low, high):
        low -= 1.0
        high += 1.0
    padding = (high - low) * 0.08
    low -= padding
    high += padding
    for fraction in (0.0, 0.5, 1.0):
        y = int(y1 - fraction * (y1 - y0))
        draw.line((x0, y, x1, y), fill=GRID, width=1)
    baseline_y = int(y1 - (100_000.0 - low) / (high - low) * (y1 - y0))
    draw.line((x0, baseline_y, x1, baseline_y), fill=GOLD, width=1)
    points = []
    denominator = max(len(values) - 1, 1)
    for index, value in enumerate(values):
        if not np.isfinite(value):
            continue
        x = int(x0 + index / denominator * (x1 - x0))
        y = int(y1 - (float(value) - low) / (high - low) * (y1 - y0))
        points.append((x, y))
    if len(points) > 1:
        draw.line(points, fill=color, width=3, joint="curve")
    elif points:
        draw.ellipse((points[0][0] - 2, points[0][1] - 2, points[0][0] + 2, points[0][1] + 2), fill=color)
    trades = int(metric["number_of_trades"])
    win_rate = metric.get("win_rate", np.nan)
    win_text = "—" if pd.isna(win_rate) else f"{float(win_rate):.0%} wins"
    footer = f"{trades} trades   ·   {win_text}   ·   DD {float(metric['max_drawdown']):.0%}"
    draw.text((left + 18, bottom - 29), footer, font=fonts["tiny"], fill=MUTED)


def _draw_info_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    heading: str,
    lines: list[tuple[str, str]],
    fonts: dict,
) -> None:
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=12, fill=PANEL_ALT, outline="#28322b", width=1)
    draw.text((left + 18, top + 16), heading, font=fonts["small"], fill=GOLD)
    y = top + 58
    for label, value in lines:
        draw.text((left + 18, y), label.upper(), font=fonts["tiny"], fill=MUTED)
        draw.text((right - 18, y), value, font=fonts["small"], fill=INK, anchor="ra")
        y += 34


def _draw_forecast_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    forecast: pd.DataFrame | None,
    metrics: dict[int, dict],
    fonts: dict,
) -> None:
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=12, fill=PANEL_ALT, outline="#315055", width=1)
    draw.text((left + 18, top + 16), "SHORT-HORIZON FORECAST", font=fonts["small"], fill=CYAN)
    draw.text((right - 18, top + 18), "NOT A TARGET", font=fonts["tiny"], fill=RED, anchor="ra")
    if forecast is None or forecast.empty:
        draw.text(
            ((left + right) // 2, (top + bottom) // 2 - 8),
            "NO CURRENT FORECAST",
            font=fonts["body"],
            fill=MUTED,
            anchor="mm",
        )
        draw.text(
            ((left + right) // 2, (top + bottom) // 2 + 25),
            "Needs 20 clean sessions and a current close",
            font=fonts["tiny"],
            fill=MUTED,
            anchor="mm",
        )
        return

    ordered = forecast.sort_values("horizon")
    rows = {int(row.horizon): row for row in ordered.itertuples(index=False)}
    if not all(horizon in rows for horizon in (1, 3, 5)):
        return _draw_forecast_panel(draw, box, None, metrics, fonts)

    chart = (left + 22, top + 58, right - 22, bottom - 82)
    x0, y0, x1, y1 = chart
    horizons = (0, 1, 3, 5)
    point_values = [0.0, *(float(rows[h].predicted_return) for h in horizons[1:])]
    lower_values = [0.0, *(float(rows[h].lower_return) for h in horizons[1:])]
    upper_values = [0.0, *(float(rows[h].upper_return) for h in horizons[1:])]
    low = min(lower_values)
    high = max(upper_values)
    padding = max((high - low) * 0.08, 0.001)
    low -= padding
    high += padding

    def position(horizon: int, value: float) -> tuple[int, int]:
        x = int(x0 + horizon / 5 * (x1 - x0))
        y = int(y1 - (value - low) / (high - low) * (y1 - y0))
        return x, y

    upper_points = [position(horizon, value) for horizon, value in zip(horizons, upper_values)]
    lower_points = [position(horizon, value) for horizon, value in zip(horizons, lower_values)]
    draw.polygon(upper_points + list(reversed(lower_points)), fill="#203b3d")
    zero_y = position(0, 0.0)[1]
    draw.line((x0, zero_y, x1, zero_y), fill=GOLD, width=1)
    point_positions = [position(horizon, value) for horizon, value in zip(horizons, point_values)]
    draw.line(point_positions, fill=CYAN, width=3, joint="curve")
    for horizon, (x, y) in zip(horizons, point_positions):
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=CYAN)
        draw.text(
            (x, y1 + 8),
            "NOW" if horizon == 0 else f"{horizon}S",
            font=fonts["tiny"],
            fill=MUTED,
            anchor="ma",
        )

    summary = "  |  ".join(
        f"{h}S {float(rows[h].predicted_return):+.1%} P(up) {float(rows[h].probability_up):.0%}"
        for h in (1, 3, 5)
    )
    draw.text((left + 18, bottom - 55), summary, font=fonts["tiny"], fill=INK)
    accuracies = [float(metrics[h]["direction_accuracy"]) for h in (1, 3, 5) if h in metrics]
    accuracy = f"{min(accuracies):.1%} to {max(accuracies):.1%}" if accuracies else "not available"
    draw.text(
        (left + 18, bottom - 29),
        f"HELD-OUT DIRECTION {accuracy}  |  NO VERIFIED EDGE",
        font=fonts["tiny"],
        fill=RED,
    )


def load_atlas_dataset(config: ResearchConfig) -> AtlasDataset:
    metadata = json.loads((config.results_dir / "run_metadata.json").read_text(encoding="utf-8"))
    strategies = [entry["name"] for entry in metadata["strategies"]]
    evaluation_sessions = int(metadata["evaluation_sessions"])
    equity: dict[str, np.ndarray] = {}
    metrics: dict[str, pd.DataFrame] = {}
    reference_isins: np.ndarray | None = None
    dates: pd.DatetimeIndex | None = None

    sparse = metadata.get("curve_storage") == "sparse_observed_sessions"
    for strategy in strategies:
        curve = pd.read_parquet(
            config.results_dir / "equity_curves" / f"{strategy}.parquet",
            columns=["date", "isin", "net_equity"],
        ).sort_values(["isin", "date"])
        metrics[strategy] = pd.read_csv(
            config.results_dir / "rankings" / f"{strategy}.csv"
        ).set_index("isin")
        if sparse:
            strategy_isins = np.sort(metrics[strategy].index.astype(str).to_numpy())
            if reference_isins is None:
                reference_isins = strategy_isins
                dates = pd.date_range(
                    metadata["evaluation_start"],
                    metadata["evaluation_end"],
                    freq="D",
                )
                observed_dates = pd.DatetimeIndex(sorted(curve["date"].unique()))
                dates = observed_dates
            elif not np.array_equal(reference_isins, strategy_isins):
                raise ValueError(f"{strategy} security ordering differs from the other curves")
            matrix = (
                curve.pivot(index="isin", columns="date", values="net_equity")
                .reindex(index=reference_isins, columns=dates)
                .ffill(axis=1)
                .fillna(float(metadata["initial_capital"]))
            )
            # Decade-long theoretical compounding can exceed float32 even when
            # the underlying daily returns remain finite. Preserve every curve.
            equity[strategy] = matrix.to_numpy(dtype=np.float64)
        else:
            if len(curve) % evaluation_sessions:
                raise ValueError(f"{strategy} curve rows do not align to the evaluation window")
            stock_count = len(curve) // evaluation_sessions
            strategy_isins = curve["isin"].to_numpy()[::evaluation_sessions]
            if reference_isins is None:
                reference_isins = strategy_isins
                dates = pd.DatetimeIndex(curve["date"].iloc[:evaluation_sessions])
            elif not np.array_equal(reference_isins, strategy_isins):
                raise ValueError(f"{strategy} security ordering differs from the other curves")
            equity[strategy] = curve["net_equity"].to_numpy(dtype=np.float32).reshape(
                stock_count, evaluation_sessions
            )

    assert reference_isins is not None and dates is not None
    first = metrics[strategies[0]]
    records = []
    for index, isin in enumerate(reference_isins):
        row = first.loc[isin]
        records.append(
            StockRecord(
                index=index,
                isin=str(isin),
                symbol=str(row["symbol"]),
                company_name=str(row["company_name"]),
                coverage_ratio=float(row["coverage_ratio"]),
                liquidity_flag=str(row["liquidity_flag"]),
                sessions_available=int(row["sessions_available"]),
                median_daily_value=float(row["median_daily_value"]),
                corporate_action_observations=int(row["corporate_action_observations"]),
                circuit_like_sessions=int(row["circuit_like_sessions"]),
            )
        )
    forecast_path = config.results_dir / "forecasts" / "latest_stock_forecasts.csv"
    forecast_metrics_path = config.results_dir / "forecasts" / "walk_forward_metrics.csv"
    forecasts = pd.read_csv(forecast_path) if forecast_path.exists() else pd.DataFrame()
    forecast_metrics = {}
    if forecast_metrics_path.exists():
        forecast_metrics = {
            int(row.horizon): row._asdict()
            for row in pd.read_csv(forecast_metrics_path).itertuples(index=False)
        }
    return AtlasDataset(
        strategies,
        records,
        equity,
        metrics,
        dates,
        float(metadata["initial_capital"]),
        forecasts,
        forecast_metrics,
    )


def render_stock_atlas(dataset: AtlasDataset, record: StockRecord, output: Path) -> Path:
    fonts = _fonts()
    image = Image.new("RGB", CANVAS, BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 12, CANVAS[1]), fill=GOLD)
    draw.text((48, 35), record.symbol, font=fonts["display"], fill=INK)
    company = _ellipsis(draw, record.company_name, fonts["body"], 740)
    draw.text((50, 90), company, font=fonts["body"], fill=MUTED)
    draw.text((1710, 42), "NSE ANOMALY ATLAS", font=fonts["title"], fill=GOLD, anchor="ra")
    draw.text(
        (1710, 84),
        f"{dataset.dates.min():%d %b %Y}  —  {dataset.dates.max():%d %b %Y}  ·  10 BPS/SIDE",
        font=fonts["small"],
        fill=MUTED,
        anchor="ra",
    )

    margin_x, gap_x, gap_y = 48, 18, 18
    grid_top, grid_bottom = 132, 1376
    columns, rows = 4, 4
    panel_width = (CANVAS[0] - margin_x * 2 - gap_x * (columns - 1)) // columns
    panel_height = (grid_bottom - grid_top - gap_y * (rows - 1)) // rows
    boxes = []
    for row in range(rows):
        for column in range(columns):
            left = margin_x + column * (panel_width + gap_x)
            top = grid_top + row * (panel_height + gap_y)
            boxes.append((left, top, left + panel_width, top + panel_height))

    for strategy, box in zip(dataset.strategies, boxes):
        metric = dataset.metrics[strategy].loc[record.isin]
        _draw_curve_panel(
            draw,
            box,
            strategy,
            dataset.equity[strategy][record.index],
            metric,
            fonts,
            dataset.initial_capital,
        )

    stock_forecast = None
    if not dataset.forecasts.empty:
        stock_forecast = dataset.forecasts.loc[dataset.forecasts["isin"].eq(record.isin)]
    _draw_forecast_panel(
        draw,
        boxes[13],
        stock_forecast,
        dataset.forecast_metrics,
        fonts,
    )
    _draw_info_panel(
        draw,
        boxes[14],
        "COVERAGE + EXECUTION",
        [
            ("Sessions", f"{record.sessions_available}/{len(dataset.dates)}"),
            ("Coverage", f"{record.coverage_ratio:.1%}"),
            ("Liquidity flag", record.liquidity_flag),
            ("Circuit-like", str(record.circuit_like_sessions)),
        ],
        fonts,
    )
    _draw_info_panel(
        draw,
        boxes[15],
        "READ THIS FIRST",
        [
            ("Capital", f"INR {dataset.initial_capital:,.0f}"),
            ("Identity", record.isin),
            ("Backtests", "IN-SAMPLE"),
            ("Forecast", "OOS CHECKED"),
        ],
        fonts,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, "WEBP", quality=82, method=4)
    return output


def generate_stock_gallery(
    config: ResearchConfig,
    output_dir: Path,
    workers: int = 8,
    limit: int | None = None,
) -> dict:
    dataset = load_atlas_dataset(config)
    records = dataset.records[:limit] if limit else dataset.records
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    assets_source = Path(__file__).resolve().parent / "gallery_assets"
    shutil.copy2(assets_source / "index.html", output_dir / "index.html")
    shutil.copy2(assets_source / "style.css", output_dir / "style.css")
    shutil.copy2(assets_source / "app.js", output_dir / "app.js")

    completed = 0
    with ThreadPoolExecutor(max_workers=max(workers, 1)) as pool:
        futures = {
            pool.submit(render_stock_atlas, dataset, record, images_dir / f"{record.isin}.webp"): record
            for record in records
        }
        for future in as_completed(futures):
            future.result()
            completed += 1
            if completed % 100 == 0 or completed == len(records):
                print(f"Rendered {completed}/{len(records)} stock atlases", flush=True)

    manifest = {
        "generated_from": str(config.results_dir / "run_metadata.json"),
        "analysis_namespace": metadata_namespace(config),
        "evaluation_start": dataset.dates.min().date().isoformat(),
        "evaluation_end": dataset.dates.max().date().isoformat(),
        "evaluation_sessions": len(dataset.dates),
        "initial_capital": dataset.initial_capital,
        "stock_count": len(records),
        "strategy_count": len(dataset.strategies),
        "chart_count": len(records) * len(dataset.strategies),
        "forecast_count": int(dataset.forecasts["isin"].nunique()) if not dataset.forecasts.empty else 0,
        "forecast_horizons": [1, 3, 5],
        "forecast_metrics": dataset.forecast_metrics,
        "strategies": dataset.strategies,
        "stocks": [
            {
                "isin": record.isin,
                "symbol": record.symbol,
                "company": record.company_name,
                "coverage": record.coverage_ratio,
                "liquidity": record.liquidity_flag,
                "image": f"images/{record.isin}.webp",
            }
            for record in records
        ],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (output_dir / "manifest.js").write_text(
        "window.STOCK_ATLAS = " + json.dumps(manifest, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    summary_path = config.results_dir / "market_summary.csv"
    if summary_path.exists():
        from src.backtest.strategy_ranking import rank_strategies_collectively
        from src.plotting.collective_ranking import write_gallery_ranking

        collective = rank_strategies_collectively(pd.read_csv(summary_path))
        write_gallery_ranking(collective, output_dir, len(dataset.dates), len(dataset.records))
    combination_path = config.results_dir / "strategy_results" / "all_stock_strategy_results.csv"
    if combination_path.exists():
        from src.backtest.combination_ranking import rank_stock_strategy_combinations
        from src.plotting.combination_ranking import write_combination_gallery

        combinations = rank_stock_strategy_combinations(pd.read_csv(combination_path))
        write_combination_gallery(combinations, output_dir, dataset.initial_capital)
    from src.plotting.research_guide import write_research_guide

    write_research_guide(config, output_dir)
    return manifest


def metadata_namespace(config: ResearchConfig) -> str:
    return config.artifact_namespace or "default"
