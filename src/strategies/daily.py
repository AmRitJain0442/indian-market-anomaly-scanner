"""Daily OHLCV anomaly strategy library."""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import ResearchConfig
from src.strategies.base import Strategy, output_frame


class CloseToOpen(Strategy):
    def generate_returns(self, frame: pd.DataFrame) -> pd.DataFrame:
        signal = frame["ret_close_to_next_open"].notna().astype(float)
        return output_frame(
            frame,
            signal,
            frame["ret_close_to_next_open"],
            entry_price=frame["close"],
            exit_date=frame["next_date"],
            exit_price=frame["next_open"],
        )


class OpenToClose(Strategy):
    def generate_returns(self, frame: pd.DataFrame) -> pd.DataFrame:
        signal = frame["ret_intraday"].notna().astype(float)
        return output_frame(frame, signal, frame["ret_intraday"])


class GapStrategy(Strategy):
    direction: float

    def __init__(self, name: str, threshold: float, direction: float):
        super().__init__(
            name=name,
            execution_class="INTRADAY_SHORT_ALLOWED_RESEARCH",
            parameters={"gap_threshold": threshold},
        )
        object.__setattr__(self, "direction", direction)

    def generate_returns(self, frame: pd.DataFrame) -> pd.DataFrame:
        threshold = float(self.parameters["gap_threshold"])
        signal = np.sign(frame["ret_overnight"]) * self.direction
        signal = signal.where(frame["ret_overnight"].abs().ge(threshold), 0.0)
        return output_frame(frame, signal, signal * frame["ret_intraday"])


class LaggedMoveStrategy(Strategy):
    feature: str
    direction: float

    def __init__(self, name: str, feature: str, threshold: float, direction: float):
        super().__init__(
            name=name,
            execution_class="INTRADAY_SHORT_ALLOWED_RESEARCH",
            parameters={"move_threshold": threshold, "signal_feature": feature},
        )
        object.__setattr__(self, "feature", feature)
        object.__setattr__(self, "direction", direction)

    def generate_returns(self, frame: pd.DataFrame) -> pd.DataFrame:
        threshold = float(self.parameters["move_threshold"])
        signal = np.sign(frame[self.feature]) * self.direction
        signal = signal.where(frame[self.feature].abs().ge(threshold), 0.0)
        return output_frame(frame, signal, signal * frame["ret_intraday"])


class TurnOfMonth(Strategy):
    def generate_returns(self, frame: pd.DataFrame) -> pd.DataFrame:
        days = int(self.parameters["days"])
        active = frame["month_from_start"].le(days) | frame["month_from_end"].le(days)
        signal = active.astype(float)
        return output_frame(frame, signal, signal * frame["ret_intraday"])


class VolumeShockStrategy(Strategy):
    direction: float

    def __init__(self, name: str, volume_ratio: float, move_threshold: float, direction: float):
        super().__init__(
            name=name,
            execution_class="INTRADAY_SHORT_ALLOWED_RESEARCH",
            parameters={"volume_ratio": volume_ratio, "move_threshold": move_threshold},
        )
        object.__setattr__(self, "direction", direction)

    def generate_returns(self, frame: pd.DataFrame) -> pd.DataFrame:
        move = frame["previous_cc_signal"]
        active = (
            frame["previous_volume_ratio"].ge(float(self.parameters["volume_ratio"]))
            & move.abs().ge(float(self.parameters["move_threshold"]))
        )
        signal = (np.sign(move) * self.direction).where(active, 0.0)
        return output_frame(frame, signal, signal * frame["ret_intraday"])


def default_strategies(config: ResearchConfig) -> list[Strategy]:
    strategies: list[Strategy] = [
        CloseToOpen("close_to_open", "LONG_ONLY"),
        OpenToClose("open_to_close", "LONG_ONLY"),
    ]
    for threshold in config.gap_thresholds:
        suffix = f"{int(round(threshold * 10_000)):03d}"
        strategies.extend(
            [
                GapStrategy(f"gap_fade_{suffix}", threshold, -1.0),
                GapStrategy(f"gap_continuation_{suffix}", threshold, 1.0),
            ]
        )
    strategies.extend(
        [
            LaggedMoveStrategy(
                "reversal_1d", "previous_cc_signal", config.reversal_1d_threshold, -1.0
            ),
            LaggedMoveStrategy(
                "momentum_1d", "previous_cc_signal", config.reversal_1d_threshold, 1.0
            ),
            LaggedMoveStrategy(
                "reversal_5d", "previous_5d_signal", config.reversal_5d_threshold, -1.0
            ),
            LaggedMoveStrategy(
                "momentum_5d", "previous_5d_signal", config.reversal_5d_threshold, 1.0
            ),
            TurnOfMonth(
                "turn_of_month",
                "LONG_ONLY",
                parameters={"days": config.turn_of_month_days},
            ),
            VolumeShockStrategy(
                "volume_continuation",
                config.volume_ratio_threshold,
                config.volume_move_threshold,
                1.0,
            ),
            VolumeShockStrategy(
                "volume_reversal",
                config.volume_ratio_threshold,
                config.volume_move_threshold,
                -1.0,
            ),
        ]
    )
    return strategies

