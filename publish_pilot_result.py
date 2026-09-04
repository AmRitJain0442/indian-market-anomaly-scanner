"""Summarize a completed pilot approximation without changing its trade decisions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def summarize(summary: dict, ledger: list[dict]) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    if summary["mode"] != "minute-proxy" or summary.get("incomplete"):
        raise ValueError("Only a complete minute approximation can report account performance")
    if len(ledger) != summary["evaluation_sessions"]:
        raise ValueError("Session count does not reconcile")
    initial = float(summary["initial_investment"])
    equity = initial
    peak = initial
    worst = 0.0
    sessions, trades = [], []
    for row in ledger:
        status = row["status"]
        if status not in {"NO_TRADE", "NO_FILL", "CLOSED", "HALTED"}:
            raise ValueError(f"Unverified ledger status: {status}")
        if not np.isclose(row["starting_equity"], equity):
            raise ValueError("Starting equity does not reconcile")
        net = float(row["net_pnl"]) if status == "CLOSED" else 0.0
        if status == "CLOSED":
            direction = 1 if row["side"] == "LONG" else -1
            gross = direction * row["quantity"] * (row["exit_price"] - row["entry_price"])
            charges = float(row["charges"]["total"])
            if not np.isclose(gross - charges, net):
                raise ValueError("Trade prices and charges do not reconcile")
            trades.append({
                "date": row["date"], "symbol": row["symbol"], "side": row["side"],
                "initial_investment": initial, "account_before": equity,
                "quantity": row["quantity"], "entry_time": row["entry_time"],
                "entry_price": row["entry_price"], "position_value": row["notional"],
                "planned_loss": row["planned_loss"], "stop": row["stop"], "target": row["target"],
                "exit_bar_time": row["exit_bar_time"], "exit_price": row["exit_price"],
                "exit_reason": row["reason"], "gross_pnl": gross,
                "estimated_charges": charges, "net_pnl": net, "account_after": equity + net,
            })
        equity += net
        if not np.isclose(row["ending_equity"], equity):
            raise ValueError("Ending equity does not reconcile")
        peak = max(peak, equity)
        drawdown = equity / peak - 1
        worst = min(worst, drawdown)
        detail = row["reason"]
        if status == "NO_TRADE":
            checks = [c for c in row.get("candidate_checks", []) if c.get("status") == "NOT_QUALIFIED"]
            detail = ", ".join(f"{c['symbol']}: {c['reason']}" for c in checks) or "NO_OPENING_GAP_SIGNAL"
        sessions.append({
            "date": row["date"], "initial_investment": initial,
            "status": status, "symbol": row.get("symbol", ""), "reason": detail,
            "quantity": row.get("quantity", 0), "net_pnl": net,
            "cumulative_pnl": equity - initial, "ending_equity": equity,
            "realized_drawdown": drawdown,
        })
    if not np.isclose(equity, summary["ending_equity"]):
        raise ValueError("Final summary does not reconcile")
    metrics = {
        "initial_investment": initial, "ending_equity": equity,
        "net_pnl": equity - initial, "return_fraction": equity / initial - 1,
        "evaluation_sessions": len(sessions), "closed_trades": len(trades),
        "winning_trades": sum(t["net_pnl"] > 0 for t in trades),
        "losing_trades": sum(t["net_pnl"] < 0 for t in trades),
        "gross_pnl": sum(t["gross_pnl"] for t in trades),
        "estimated_trading_charges": sum(t["estimated_charges"] for t in trades),
        "max_realized_drawdown": worst,
        "no_fill_sessions": sum(r["status"] == "NO_FILL" for r in ledger),
        "no_trade_sessions": sum(r["status"] == "NO_TRADE" for r in ledger),
        "fixed_platform_costs_included": False, "exact_quote_strategy_validated": False,
    }
    return metrics, pd.DataFrame(sessions), pd.DataFrame(trades)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--findings", type=Path, default=Path("results/findings/2026-09-05-pilot20-minute"))
    args = parser.parse_args()
    summary = json.loads((args.findings / "summary.json").read_text(encoding="utf-8"))
    ledger = json.loads((args.findings / "daily_ledger.json").read_text(encoding="utf-8"))
    metrics, sessions, trades = summarize(summary, ledger)
    (args.findings / "metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    sessions.to_csv(args.findings / "session_summary.csv", index=False)
    trades.to_csv(args.findings / "trade_summary.csv", index=False)
    background, panel, ink, muted, gold = "#0e120f", "#151a17", "#efe8d3", "#9aa49a", "#e6ba62"
    with plt.rc_context({"figure.facecolor": background, "axes.facecolor": panel,
                         "text.color": ink, "axes.labelcolor": ink, "xtick.color": muted,
                         "ytick.color": muted, "axes.edgecolor": "#2b352e", "font.size": 10}):
        fig, ax = plt.subplots(figsize=(10, 4.5))
        values = [metrics["initial_investment"], *sessions.ending_equity.tolist()]
        ax.step(range(len(values)), values, where="post", color=gold, linewidth=2)
        ax.axhline(metrics["initial_investment"], color=muted, linestyle="--", linewidth=0.8)
        positions = [3, 9, 15, 20]
        positions = [x for x in positions if x <= len(sessions)]
        ax.set_xticks([0, *positions], ["Start", *[pd.Timestamp(sessions.date.iloc[x-1]).strftime("%d %b") for x in positions]])
        ax.set_ylabel("Modeled account value, INR")
        ax.set_title("One-minute approximation, 20 trading sessions", loc="left", pad=18)
        ax.grid(axis="y", color="#2b352e", alpha=0.6)
        ax.set_ylim(min(values) - 2, max(values) + 2)
        fig.text(0.12, 0.02,
                 f"Initial INR {metrics['initial_investment']:,.2f}  |  Ending INR {metrics['ending_equity']:,.2f}  |  Zoomed vertical scale\n"
                 "Estimated trading charges included. Quote execution and broker permissions unverified.",
                 color=muted, fontsize=9)
        fig.tight_layout(rect=(0, 0.12, 1, 1))
        fig.savefig(args.findings / "account_curve.png", dpi=160)
        plt.close(fig)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
