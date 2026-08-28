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

All settled gains and losses are reinvested mechanically: the next session starts from the prior session's closing account equity. Full-pilot maximum notional is 50% of current equity and planned risk is 0.5%; half-size validation uses 25% and 0.25%. Therefore position size is `floor(min(current_equity × stage_notional_pct / entry, current_equity × stage_risk_pct / (entry × 1%)))`.

There is no daily rupee profit target. The tested setup exits at the close, so forcing a monetary target would add an untested rule and encourage overtrading. Each day instead has an execution target and a 15:15 exit target.

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

## Fixed daily clock

- **08:45–09:00:** update current equity/high-water mark, prior closes, watchlist order, broker restrictions, and short availability.
- **09:00–09:08:** observe NSE pre-open; do not place a discretionary trade.
- **09:15–09:16:** calculate all five gaps, apply the ±1% threshold, choose the highest-priority eligible name, size from current equity, and fill within 10 bps or skip.
- **After entry:** place the 1% protective stop; no widening, averaging, or second position.
- **15:15:** exit the position regardless of PnL. The price target is the market outcome at the timed exit—not an invented fixed return.
- **15:40 onward:** reconcile fills, costs, net PnL, closing equity, high-water mark, drawdown, and next-session limits.

## Next 30 NSE trading sessions

The calendar starts on 31 August 2026 and excludes NSE holidays on 14 September and 2 October. Every session follows the fixed clock above; the row supplies that day's extra decision and measurable target.

| Day | Date | Phase | Daily focus | Decision | Target / pass condition |
|---:|---|---|---|---|---|
| 1 | 2026-08-31 (Mon) | PAPER | Baseline the workflow | Log the qualifying trade as if live, including skip/reject outcomes. | Complete every log field; zero live capital and zero unrecorded decisions. |
| 2 | 2026-09-01 (Tue) | PAPER | Opening-price discipline | Log the qualifying trade as if live, including skip/reject outcomes. | Measure fill slippage; simulated entry must remain within 10 bps of the official open. |
| 3 | 2026-09-02 (Wed) | PAPER | Cost ledger | Log the qualifying trade as if live, including skip/reject outcomes. | Capture brokerage, taxes, fees, and slippage separately; compute net PnL only after all costs. |
| 4 | 2026-09-03 (Thu) | PAPER | Long-leg rehearsal | Log the qualifying trade as if live, including skip/reject outcomes. | If a gap-down signal appears, execute the paper long exactly; otherwise record NO TRADE. |
| 5 | 2026-09-04 (Fri) | PAPER | Short-leg rehearsal | Log the qualifying trade as if live, including skip/reject outcomes. | Confirm Zerodha intraday-short availability before simulating a gap-up fade. |
| 6 | 2026-09-07 (Mon) | PAPER | Spread filter | Log the qualifying trade as if live, including skip/reject outcomes. | Skip any opening spread above 0.50%; target zero exceptions. |
| 7 | 2026-09-08 (Tue) | PAPER | Priority rule | Log the qualifying trade as if live, including skip/reject outcomes. | When signals collide, select only the highest-ranked watchlist name. |
| 8 | 2026-09-09 (Wed) | PAPER | Stop mechanics | Log the qualifying trade as if live, including skip/reject outcomes. | Record the exact 1% stop trigger and achievable stop fill; never widen it. |
| 9 | 2026-09-10 (Thu) | PAPER | No-trade discipline | Log the qualifying trade as if live, including skip/reject outcomes. | Do not manufacture a trade when no eligible ±1% gap exists. |
| 10 | 2026-09-11 (Fri) | PAPER | Checkpoint one | Log the qualifying trade as if live, including skip/reject outcomes. | Audit the first ten sessions; target 100% rule adherence and reconcile every rupee. |
| 11 | 2026-09-15 (Tue) | PAPER | Post-holiday reset | Log the qualifying trade as if live, including skip/reject outcomes. | Refresh prior closes and restrictions after the exchange holiday; assume nothing carried over. |
| 12 | 2026-09-16 (Wed) | PAPER | Fill repeatability | Log the qualifying trade as if live, including skip/reject outcomes. | Keep average absolute entry slippage at or below 10 bps. |
| 13 | 2026-09-17 (Thu) | PAPER | Long/short balance | Log the qualifying trade as if live, including skip/reject outcomes. | Verify both directions are being logged; do not force the missing side. |
| 14 | 2026-09-18 (Fri) | PAPER | Liquidity check | Log the qualifying trade as if live, including skip/reject outcomes. | Confirm normal order depth and reject any circuit or surveillance-constrained setup. |
| 15 | 2026-09-21 (Mon) | PAPER | Ranking fidelity | Log the qualifying trade as if live, including skip/reject outcomes. | Use the frozen priority order; target zero discretionary substitutions. |
| 16 | 2026-09-22 (Tue) | PAPER | Loss-sequence drill | Log the qualifying trade as if live, including skip/reject outcomes. | After three consecutive losses, mark the pilot PAUSED and take no further signals. |
| 17 | 2026-09-23 (Wed) | PAPER | High-water mark | Log the qualifying trade as if live, including skip/reject outcomes. | Update simulated closing equity and peak equity; recompute the 5% drawdown boundary. |
| 18 | 2026-09-24 (Thu) | PAPER | Exit discipline | Log the qualifying trade as if live, including skip/reject outcomes. | Close or simulate close by 15:15 IST; target zero overnight positions. |
| 19 | 2026-09-25 (Fri) | PAPER | Pre-gate audit | Log the qualifying trade as if live, including skip/reject outcomes. | Count valid signals and identify missing evidence; extend paper mode if any gate is incomplete. |
| 20 | 2026-09-28 (Mon) | PAPER | Paper gate decision | Log the qualifying trade as if live, including skip/reject outcomes. | PASS only with ≥10 signals, positive net PnL, ≤10 bps mean slippage, <3% drawdown, and no breaches. |
| 21 | 2026-09-29 (Tue) | HALF-SIZE IF GATE PASSED | Conditional half-size launch | Trade half-size only if Day 20 passed; otherwise perform the identical action on paper. | If the gate passed, risk 0.25% of current equity; otherwise continue paper mode. |
| 22 | 2026-09-30 (Wed) | HALF-SIZE IF GATE PASSED | First-live reconciliation | Trade half-size only if Day 20 passed; otherwise perform the identical action on paper. | Match broker contract note to the log before the next trade; target zero unexplained charges. |
| 23 | 2026-10-01 (Thu) | HALF-SIZE IF GATE PASSED | Compounding check | Trade half-size only if Day 20 passed; otherwise perform the identical action on paper. | Use yesterday's settled closing equity—not INR 10,000—to calculate today's size. |
| 24 | 2026-10-05 (Mon) | HALF-SIZE IF GATE PASSED | Execution stability | Trade half-size only if Day 20 passed; otherwise perform the identical action on paper. | Target a valid fill within 10 bps; skip rather than chase. |
| 25 | 2026-10-06 (Tue) | HALF-SIZE IF GATE PASSED | Mid-pilot review | Trade half-size only if Day 20 passed; otherwise perform the identical action on paper. | Keep aggregate half-size PnL net positive and live drawdown below 3%; otherwise return to paper. |
| 26 | 2026-10-07 (Wed) | HALF-SIZE IF GATE PASSED | Stop-loss audit | Trade half-size only if Day 20 passed; otherwise perform the identical action on paper. | Verify planned loss equals at most 0.25% of current equity at half size. |
| 27 | 2026-10-08 (Thu) | HALF-SIZE IF GATE PASSED | Restriction audit | Trade half-size only if Day 20 passed; otherwise perform the identical action on paper. | Recheck MIS/short availability and surveillance status before any order. |
| 28 | 2026-10-09 (Fri) | HALF-SIZE IF GATE PASSED | Behaviour audit | Trade half-size only if Day 20 passed; otherwise perform the identical action on paper. | No revenge trade, second trade, averaging down, or rule change after a loss. |
| 29 | 2026-10-12 (Mon) | HALF-SIZE IF GATE PASSED | Final signal collection | Trade half-size only if Day 20 passed; otherwise perform the identical action on paper. | Complete the tenth half-size signal only if eligible; elapsed days alone do not pass the gate. |
| 30 | 2026-10-13 (Tue) | HALF-SIZE IF GATE PASSED | Thirty-session decision | Trade half-size only if Day 20 passed; otherwise perform the identical action on paper. | Scale no further unless ten live signals are net positive, slippage ≤10 bps, drawdown <3%, and breaches = 0. |

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
- [NSE capital-market trading holidays for 2026](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf)
- [NSE equity market timings](https://www.nseindia.com/static/market-data/market-timings)

> This is a research-derived pilot protocol, not personalized investment advice or an assurance of returns.
