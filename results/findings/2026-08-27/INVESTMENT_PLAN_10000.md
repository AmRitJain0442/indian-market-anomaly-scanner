# INR 10,000 controlled anomaly pilot

## Decision

The most defensible use of this research is **not immediate full-capital trading**. The proposed plan is a paper test lasting at least 20 sessions and 10 valid signals, followed by a ten-trade half-size live gate, and only then a maximum INR 5,000 position. The remaining cash is an execution and loss buffer.

The primary setup is `gap_fade_100` because it led the market-wide collective ranking and retained majority profitable breadth at 30 bps per side. Results are in-sample through **2026-08-27**, so no return is forecast.

## Capital controls

- Total capital: **INR 10,000**
- Maximum full-pilot position: **INR 5,000**
- Planned risk per trade: **INR 50** using a 1% stop overlay
- Daily loss ceiling: **INR 100**
- Pause and review after cumulative pilot drawdown: **INR 500**
- One position at a time; no averaging down; no overnight carry.

Position size is `floor(min(INR 5,000 / entry, INR 50 / (entry × 1%)))`. Half-size live validation divides both caps by two.

## Three-stage gate

1. **At least 20 completed sessions and 10 valid signals, paper only.** Extend the paper stage until both are satisfied. Record the achievable entry, exit, fees, slippage, rejects, and short availability. Do not risk capital. Pass only if net PnL after every charge is positive, average absolute slippage is at most 10 bps, and drawdown is below INR 300.
2. **Next 10 valid signals, half size.** Maximum INR 2,500 position and INR 25 planned risk. Continue only if net PnL after every charge is positive, average absolute slippage is at most 10 bps, and drawdown is below INR 300.
3. **Full pilot.** Maximum INR 5,000 position and INR 50 planned risk. Stop after INR 100 lost in a day or INR 500 cumulative drawdown; return to paper mode before changing any rule.

## Daily rule card

1. Use the prior NSE close and the current opening price. `gap = open / prior_close - 1`.
2. If gap is at most -1%, buy at the open; if gap is at least +1%, sell short intraday. Otherwise do nothing.
3. Trade only a watchlist name below. If several qualify, take the highest watchlist rank only.
4. Skip when the stock is under an execution restriction, a normal order is rejected, the opening spread is above 0.50%, or a fill cannot be obtained within 10 bps of the recorded open.
5. Apply the 1% protective stop. Exit by 15:15 IST regardless of PnL. A same-day short must be closed; do not create a delivery obligation.

The stop, fill tolerance, 15:15 exit, and stricter liquidity screen are safety overlays and were **not** separately backtested in the 252-session result. That is why paper validation is mandatory.

## Strict watchlist

Candidates require 99% history, at least 50 signals, median daily value of at least INR 5 crore, no detected corporate-action discontinuity, at most two circuit-like sessions, positive confidence floor, and separately positive long and short legs.

| Priority | Stock | Score | Overall pair rank | Historical PnL on scaled INR 10,000 | Ending value | 30 bps PnL | Long leg | Short leg |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | SEAMECLTD | 92.7 | 1,099 | INR 12,423 | INR 22,423 | INR 7,266 | INR 3,990 (22) | INR 6,028 (44) |
| 2 | ETHOSLTD | 91.0 | 1,568 | INR 4,877 | INR 14,877 | INR 1,904 | INR 1,569 (22) | INR 2,859 (34) |
| 3 | EFCIL | 90.9 | 1,619 | INR 6,733 | INR 16,733 | INR 2,766 | INR 1,315 (20) | INR 4,789 (48) |
| 4 | ARFIN | 90.4 | 1,757 | INR 17,101 | INR 27,101 | INR 6,954 | INR 6,052 (36) | INR 6,884 (82) |
| 5 | THELEELA | 89.8 | 1,920 | INR 6,007 | INR 16,007 | INR 2,065 | INR 5,338 (33) | INR 436 (38) |

Historical values scale the research equity curve from INR 100,000 to INR 10,000. They are descriptive, not expected returns, and do not represent the new safety overlay.

## Go/no-go checklist

Proceed only when all are true: emergency savings and near-term obligations are separate; the entire INR 10,000 can be lost without affecting essentials; broker charges are recorded; intraday short availability is confirmed; and the paper gate passes without changing rules. Use the adjacent `pilot_trade_log_template.csv` to record every eligible signal, including skipped and rejected orders.

Do not proceed after any rule breach, missing market data, broker restriction, three consecutive losing trades, INR 100 daily loss, or INR 500 cumulative pilot drawdown.

## Regulatory and risk references

- [SEBI study: 7 out of 10 individual equity-cash intraday traders made losses](https://www.sebi.gov.in/media-and-notifications/press-releases/jul-2024/sebi-study-finds-that-7-out-of-10-individual-intraday-traders-in-equity-cash-segment-make-losses_84948.html)
- [SEBI framework for short selling](https://www.sebi.gov.in/legal/circulars/jan-2024/framework-for-short-selling_80448.html)
- [NSE implementation standards for retail API/algo access](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf)

> This is a research-derived pilot protocol, not personalized investment advice or an assurance of returns.
