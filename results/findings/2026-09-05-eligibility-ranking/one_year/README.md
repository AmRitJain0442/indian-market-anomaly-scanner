# EQ-only stock and strategy ranking

Historical window: 2025-08-20 to 2026-08-27, 252 sessions. Current status snapshot: 2026-09-04.

34,476 original pairs checked. 24,205 pairs pass the strict EQ-history screen. 667 pairs across 66 stocks pass the INR 1,000 practical research screen.

## What the two ranks mean

The EQ rank requires a current EQ listing and EQ on both the entry and exit date of every historical trade. A pair with any BE/BZ or missing-series trade is excluded in full. We do not remove its bad trades while retaining its original profit. The same conservative EQ-only rule is applied to overnight strategies, even though some delivery trades in restricted series might otherwise be possible.

The practical rank adds the dated Zerodha MIS table, a current price of at least INR 100, at least one whole share within a INR 500 notional cap and an illustrative INR 5 planned-risk limit, at least INR 50 crore median turnover across the latest 20 completed sessions, at least 95% historical coverage and at least 20 historical trades. Overnight strategies are left for a separate delivery-cost and settlement review. These are research filters, not exchange rules or evidence of profitability.

The cash budget is INR 1,000 with no leverage. Cash-cap shares are the maximum whole shares under the INR 500 notional limit at the snapshot close, not an order quantity or a completed risk calculation. Actual order prices, fees, stop distance and available cash require fresh checks.

Illustrative risk shares additionally use a tick-rounded 1% stop, estimated Zerodha charges, and an adverse-fill allowance of the larger of 0.20% of notional or two ticks per share. The worse of long and short planned loss must fit INR 5. Monthly ticks use the preceding month-end close. This is a current sizing illustration, not a newly backtested stop strategy, guaranteed loss cap or historical whole-share simulation.

Broker-list membership is evidence from a published snapshot, not account-specific permission or a promise of future order acceptance. Absence from the list means this screen has not established MIS availability. Dhan permission has not been checked. Recheck broker restrictions and the exchange series before every session.

## Historical ranking is not a INR 1,000 return forecast

The historical figures below retain the original INR 100,000 reference account and its theoretical fills and fractional full-capital compounding. They are not returns achieved by a INR 1,000 whole-share account. The new screen does not fix opening-fill assumptions, future-dependent exclusions, selection bias, missing historical broker permission or all corporate-action issues in the original engine.

Scores are recomputed within the EQ-screened set using the existing five ranking weights. Drawdown is recalculated from the trade-return path with initial capital included. All other historical metrics are inherited. A high score is relative research priority, not a probability of profit. The latest-status filter is a present-day discovery screen, not a historical investable-universe backtest.

## Practical research shortlist

| Rank | Stock | Strategy | Snapshot price | Cash-cap shares | Illustrative risk shares | Research score | Historical initial | Historical modeled profit | Historical ending | Trades |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | BANDHANBNK | gap_continuation_100 | INR 164.95 | 3 | 2 | 95.6 | INR 100,000 | INR 60,712.21 | INR 160,712.21 | 37 |
| 2 | POWERGRID | gap_fade_050 | INR 266.00 | 1 | 1 | 94.9 | INR 100,000 | INR 59,007.19 | INR 159,007.19 | 79 |
| 3 | POWERGRID | gap_fade_100 | INR 266.00 | 1 | 1 | 94.3 | INR 100,000 | INR 39,771.32 | INR 139,771.32 | 36 |
| 4 | BANDHANBNK | gap_continuation_050 | INR 164.95 | 3 | 2 | 93.4 | INR 100,000 | INR 53,857.74 | INR 153,857.74 | 85 |
| 5 | TATAPOWER | gap_fade_100 | INR 368.00 | 1 | 1 | 90.2 | INR 100,000 | INR 16,235.71 | INR 116,235.71 | 21 |
| 6 | TATAPOWER | gap_fade_050 | INR 368.00 | 1 | 1 | 89.8 | INR 100,000 | INR 21,143.48 | INR 121,143.48 | 51 |
| 7 | NTPC | gap_fade_100 | INR 332.50 | 1 | 1 | 89.4 | INR 100,000 | INR 16,198.64 | INR 116,198.64 | 20 |
| 8 | HAPPSTMNDS | reversal_5d | INR 354.00 | 1 | 1 | 88.2 | INR 100,000 | INR 32,226.97 | INR 132,226.97 | 61 |
| 9 | ONGC | gap_fade_100 | INR 234.65 | 2 | 1 | 88.0 | INR 100,000 | INR 17,687.11 | INR 117,687.11 | 25 |
| 10 | BPCL | momentum_5d | INR 315.70 | 1 | 1 | 87.4 | INR 100,000 | INR 19,421.49 | INR 119,421.49 | 44 |
| 11 | SWIGGY | gap_fade_100 | INR 276.10 | 1 | 1 | 86.9 | INR 100,000 | INR 20,270.15 | INR 120,270.15 | 43 |
| 12 | BANKINDIA | gap_continuation_050 | INR 145.00 | 3 | 2 | 86.6 | INR 100,000 | INR 33,167.83 | INR 133,167.83 | 77 |
| 13 | RAIN | gap_continuation_100 | INR 215.72 | 2 | 1 | 86.5 | INR 100,000 | INR 32,833.84 | INR 132,833.84 | 42 |
| 14 | AWL | gap_fade_100 | INR 187.29 | 2 | 2 | 86.3 | INR 100,000 | INR 24,866.42 | INR 124,866.42 | 43 |
| 15 | BANKBARODA | gap_continuation_100 | INR 239.00 | 2 | 1 | 85.9 | INR 100,000 | INR 14,010.07 | INR 114,010.07 | 34 |
| 16 | PPLPHARMA | gap_fade_100 | INR 214.22 | 2 | 1 | 85.5 | INR 100,000 | INR 21,690.19 | INR 121,690.19 | 31 |
| 17 | CUB | gap_fade_100 | INR 236.01 | 2 | 1 | 85.3 | INR 100,000 | INR 21,961.32 | INR 121,961.32 | 34 |
| 18 | PATANJALI | gap_fade_100 | INR 342.50 | 1 | 1 | 84.4 | INR 100,000 | INR 4,845.01 | INR 104,845.01 | 22 |
| 19 | AWL | gap_fade_050 | INR 187.29 | 2 | 2 | 84.3 | INR 100,000 | INR 32,313.43 | INR 132,313.43 | 84 |
| 20 | IOC | momentum_5d | INR 137.60 | 3 | 2 | 83.9 | INR 100,000 | INR 12,349.85 | INR 112,349.85 | 46 |
| 21 | SAMMAANCAP | gap_continuation_100 | INR 158.39 | 3 | 2 | 83.4 | INR 100,000 | INR 26,820.14 | INR 126,820.14 | 34 |
| 22 | NTPC | gap_fade_050 | INR 332.50 | 1 | 1 | 83.0 | INR 100,000 | INR 13,154.23 | INR 113,154.23 | 57 |
| 23 | M&MFIN | gap_continuation_100 | INR 373.65 | 1 | 1 | 82.0 | INR 100,000 | INR 26,634.31 | INR 126,634.31 | 39 |
| 24 | TMPV | momentum_5d | INR 311.50 | 1 | 1 | 82.0 | INR 100,000 | INR 10,748.52 | INR 110,748.52 | 66 |
| 25 | SAMMAANCAP | volume_continuation | INR 158.39 | 3 | 2 | 81.5 | INR 100,000 | INR 13,408.97 | INR 113,408.97 | 21 |
| 26 | VMM | reversal_1d | INR 106.14 | 4 | 3 | 81.5 | INR 100,000 | INR 9,522.17 | INR 109,522.17 | 61 |
| 27 | ITC | gap_fade_050 | INR 264.10 | 1 | 1 | 81.2 | INR 100,000 | INR 4,259.18 | INR 104,259.18 | 40 |
| 28 | IFCI | gap_continuation_050 | INR 101.38 | 4 | 3 | 80.9 | INR 100,000 | INR 51,404.37 | INR 151,404.37 | 108 |
| 29 | VMM | reversal_5d | INR 106.14 | 4 | 3 | 80.7 | INR 100,000 | INR 5,279.49 | INR 105,279.49 | 31 |
| 30 | SCI | gap_continuation_100 | INR 295.35 | 1 | 1 | 80.3 | INR 100,000 | INR 23,195.55 | INR 123,195.55 | 44 |

## Inspect and reproduce

- [Searchable local ranking](index.html)
- [EQ-only ranking](eq_only_ranking.csv)
- [Practical research shortlist](practical_shortlist.csv)
- [All pairs and exclusion reasons](all_pairs_audit.csv.gz)
- [Source hashes and method](metadata.json)

Run from the repository root:

    python generate_eligibility_ranking.py --windows both --snapshot-date 2026-09-04

Sources: [NSE series definitions](https://www.nseindia.com/static/market-data/legend-of-series), [Zerodha published MIS list](https://zerodha.com/margin-calculator/Equity/), [Zerodha additional restrictions](https://support.zerodha.com/category/trading-and-markets/charts-and-orders/order/articles/intraday-orders-not-allowed-for-some-stocks).

The interface follows the existing dark-green and gold theme. No broker account was connected, no orders were placed and no server deployment was performed.
