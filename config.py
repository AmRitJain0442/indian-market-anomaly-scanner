"""Default configuration for the NSE anomaly research run."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ResearchConfig:
    project_root: Path = Path(__file__).resolve().parent
    evaluation_sessions: int = 252
    raw_history_target: int = 550
    initial_capital: float = 100_000.0
    one_way_cost_bps: float = 10.0
    cost_sensitivity_bps: tuple[float, ...] = (0.0, 5.0, 10.0, 20.0, 30.0)
    include_mainboard: bool = True
    include_sme: bool = False
    include_etf: bool = False
    include_reit_invit: bool = False
    include_pref_shares: bool = False
    include_warrants: bool = False
    ordinary_equity_series: tuple[str, ...] = ("EQ", "BE", "BZ")
    extreme_return_threshold: float = 0.30
    comparable_coverage_ratio: float = 0.95
    low_liquidity_value_inr: float = 1_000_000.0
    near_zero_volume: int = 100
    download_workers: int = 6
    request_timeout_seconds: int = 30
    request_retries: int = 3
    plot_top_n: int = 20
    gap_thresholds: tuple[float, ...] = (0.005, 0.010)
    reversal_1d_threshold: float = 0.020
    reversal_5d_threshold: float = 0.050
    turn_of_month_days: int = 3
    volume_ratio_threshold: float = 2.0
    volume_move_threshold: float = 0.020
    user_agent: str = (
        "Mozilla/5.0 (compatible; indian-market-anomalies/0.1; "
        "+https://github.com/AmRitJain0442)"
    )
    raw_dir: Path = field(init=False)
    processed_dir: Path = field(init=False)
    results_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "raw_dir", self.project_root / "data" / "raw")
        object.__setattr__(self, "processed_dir", self.project_root / "data" / "processed")
        object.__setattr__(self, "results_dir", self.project_root / "results")


CONFIG = ResearchConfig()

