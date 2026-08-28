"""Stock-strategy performance and statistical diagnostics."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats


def _compound(returns: pd.Series, capital: float) -> float:
    return float(capital * (1.0 + returns.fillna(0.0)).prod())


def calculate_metrics(
    group: pd.DataFrame,
    initial_capital: float,
    cost_sensitivity_bps: tuple[float, ...],
) -> dict[str, float | int]:
    net = group["net_return"].fillna(0.0)
    gross = group["gross_return"].fillna(0.0)
    active_mask = group["active"]
    trades = net[active_mask]
    final_net = _compound(net, initial_capital)
    final_gross = _compound(gross, initial_capital)
    volatility = float(net.std(ddof=1))
    downside = float(net[net < 0].std(ddof=1))
    positive_sum = float(trades[trades > 0].sum())
    negative_sum = float(trades[trades < 0].sum())
    standard_error = float(trades.std(ddof=1) / math.sqrt(len(trades))) if len(trades) > 1 else np.nan
    if len(trades) > 1 and trades.std(ddof=1) > 0:
        t_stat, p_value = stats.ttest_1samp(trades, popmean=0.0, nan_policy="omit")
        confidence = stats.t.interval(
            0.95,
            len(trades) - 1,
            loc=float(trades.mean()),
            scale=standard_error,
        )
    else:
        t_stat, p_value, confidence = np.nan, np.nan, (np.nan, np.nan)
    monthly = (
        group.assign(_return=net.to_numpy())
        .set_index("date")["_return"]
        .resample("ME")
        .apply(lambda values: (1.0 + values).prod() - 1.0)
    )
    equity = initial_capital * (1.0 + net).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    buy_hold_final = _compound(group["buy_hold_return"], initial_capital)
    result: dict[str, float | int] = {
        "number_of_signals": int(active_mask.sum()),
        "number_of_trades": int(active_mask.sum()),
        "gross_pnl": final_gross - initial_capital,
        "net_pnl": final_net - initial_capital,
        "gross_return_pct": final_gross / initial_capital - 1.0,
        "net_return_pct": final_net / initial_capital - 1.0,
        "annualized_volatility": volatility * math.sqrt(252),
        "sharpe": float(net.mean() / volatility * math.sqrt(252)) if volatility > 0 else np.nan,
        "sortino": float(net.mean() / downside * math.sqrt(252)) if downside > 0 else np.nan,
        "max_drawdown": float(drawdown.min()) if len(drawdown) else np.nan,
        "win_rate": float((trades > 0).mean()) if len(trades) else np.nan,
        "average_trade_return": float(trades.mean()) if len(trades) else np.nan,
        "median_trade_return": float(trades.median()) if len(trades) else np.nan,
        "profit_factor": positive_sum / abs(negative_sum) if negative_sum < 0 else np.nan,
        "best_trade": float(trades.max()) if len(trades) else np.nan,
        "worst_trade": float(trades.min()) if len(trades) else np.nan,
        "exposure_pct": float(active_mask.mean()),
        "turnover": float(active_mask.sum() * 2.0),
        "trade_std": float(trades.std(ddof=1)) if len(trades) > 1 else np.nan,
        "standard_error": standard_error,
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "confidence_95_low": float(confidence[0]),
        "confidence_95_high": float(confidence[1]),
        "positive_months": int((monthly > 0).sum()),
        "negative_months": int((monthly < 0).sum()),
        "best_month": float(monthly.max()) if len(monthly) else np.nan,
        "worst_month": float(monthly.min()) if len(monthly) else np.nan,
        "monthly_return_std": float(monthly.std(ddof=1)) if len(monthly) > 1 else np.nan,
        "buy_hold_pnl": buy_hold_final - initial_capital,
        "excess_pnl": (final_net - initial_capital) - (buy_hold_final - initial_capital),
    }
    for bps in cost_sensitivity_bps:
        label = f"pnl_{int(bps)}bps"
        sensitivity = gross - active_mask.astype(float) * (2.0 * bps / 10_000.0)
        result[label] = _compound(sensitivity, initial_capital) - initial_capital
    return result

