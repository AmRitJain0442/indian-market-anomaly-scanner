# EQ-only stock and strategy ranking

Historical window: 2016-08-29 to 2026-08-27, 2468 sessions. Current status snapshot: 2026-09-04.

43,264 original pairs checked. 20,558 pairs pass the strict EQ-history screen. 497 pairs across 44 stocks pass the INR 1,000 practical research screen.

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
| 1 | EPL | gap_fade_100 | INR 247.10 | 2 | 1 | 94.2 | INR 100,000 | INR 12,664,298.59 | INR 12,764,298.59 | 639 |
| 2 | NTPC | gap_fade_100 | INR 332.50 | 1 | 1 | 92.7 | INR 100,000 | INR 349,455.12 | INR 449,455.12 | 278 |
| 3 | EPL | gap_fade_050 | INR 247.10 | 2 | 1 | 92.0 | INR 100,000 | INR 18,838,272.72 | INR 18,938,272.72 | 1255 |
| 4 | POWERGRID | gap_fade_100 | INR 266.00 | 1 | 1 | 91.2 | INR 100,000 | INR 262,031.69 | INR 362,031.69 | 294 |
| 5 | TIMETECHNO | gap_fade_100 | INR 188.49 | 2 | 2 | 89.6 | INR 100,000 | INR 1,335,418.66 | INR 1,435,418.66 | 653 |
| 6 | MARKSANS | gap_fade_100 | INR 326.75 | 1 | 1 | 88.4 | INR 100,000 | INR 985,787.94 | INR 1,085,787.94 | 601 |
| 7 | PNB | volume_reversal | INR 117.00 | 4 | 3 | 88.1 | INR 100,000 | INR 84,096.65 | INR 184,096.65 | 135 |
| 8 | CUB | gap_fade_100 | INR 236.01 | 2 | 1 | 87.9 | INR 100,000 | INR 424,939.81 | INR 524,939.81 | 396 |
| 9 | REDINGTON | gap_fade_100 | INR 371.30 | 1 | 1 | 84.4 | INR 100,000 | INR 843,661.72 | INR 943,661.72 | 571 |
| 10 | PETRONET | gap_fade_100 | INR 288.10 | 1 | 1 | 84.2 | INR 100,000 | INR 149,092.47 | INR 249,092.47 | 279 |
| 11 | CROMPTON | gap_fade_100 | INR 232.40 | 2 | 1 | 83.2 | INR 100,000 | INR 196,651.07 | INR 296,651.07 | 374 |
| 12 | ONGC | volume_reversal | INR 234.65 | 2 | 1 | 82.9 | INR 100,000 | INR 47,211.39 | INR 147,211.39 | 96 |
| 13 | PNB | gap_fade_100 | INR 117.00 | 4 | 3 | 82.8 | INR 100,000 | INR 298,110.42 | INR 398,110.42 | 463 |
| 14 | NTPC | gap_fade_050 | INR 332.50 | 1 | 1 | 82.2 | INR 100,000 | INR 494,962.90 | INR 594,962.90 | 851 |
| 15 | INDUSTOWER | gap_fade_100 | INR 376.80 | 1 | 1 | 81.6 | INR 100,000 | INR 276,831.54 | INR 376,831.54 | 434 |
| 16 | POWERGRID | gap_fade_050 | INR 266.00 | 1 | 1 | 80.7 | INR 100,000 | INR 519,650.56 | INR 619,650.56 | 858 |
| 17 | CROMPTON | gap_fade_050 | INR 232.40 | 2 | 1 | 80.3 | INR 100,000 | INR 1,195,734.63 | INR 1,295,734.63 | 1059 |
| 18 | PETRONET | volume_reversal | INR 288.10 | 1 | 1 | 79.2 | INR 100,000 | INR 37,615.12 | INR 137,615.12 | 91 |
| 19 | BANKBARODA | volume_reversal | INR 239.00 | 2 | 1 | 77.6 | INR 100,000 | INR 23,007.88 | INR 123,007.88 | 109 |
| 20 | TMPV | volume_reversal | INR 311.50 | 1 | 1 | 77.6 | INR 100,000 | INR 17,174.27 | INR 117,174.27 | 102 |
| 21 | PETRONET | gap_fade_050 | INR 288.10 | 1 | 1 | 76.8 | INR 100,000 | INR 252,563.20 | INR 352,563.20 | 915 |
| 22 | REDINGTON | gap_fade_050 | INR 371.30 | 1 | 1 | 76.4 | INR 100,000 | INR 2,166,614.15 | INR 2,266,614.15 | 1276 |
| 23 | TIMETECHNO | gap_fade_050 | INR 188.49 | 2 | 2 | 75.4 | INR 100,000 | INR 2,020,495.66 | INR 2,120,495.66 | 1403 |
| 24 | TATAPOWER | gap_fade_050 | INR 368.00 | 1 | 1 | 75.3 | INR 100,000 | INR 485,684.02 | INR 585,684.02 | 1009 |
| 25 | MARKSANS | gap_fade_050 | INR 326.75 | 1 | 1 | 75.2 | INR 100,000 | INR 1,442,289.39 | INR 1,542,289.39 | 1378 |
| 26 | NTPC | volume_reversal | INR 332.50 | 1 | 1 | 75.2 | INR 100,000 | INR 28,322.41 | INR 128,322.41 | 84 |
| 27 | IOC | gap_fade_100 | INR 137.60 | 3 | 2 | 73.8 | INR 100,000 | INR 48,454.80 | INR 148,454.80 | 420 |
| 28 | ENGINERSIN | gap_fade_100 | INR 279.45 | 1 | 1 | 73.5 | INR 100,000 | INR 103,782.21 | INR 203,782.21 | 402 |
| 29 | CUB | gap_fade_050 | INR 236.01 | 2 | 1 | 73.2 | INR 100,000 | INR 430,162.29 | INR 530,162.29 | 1132 |
| 30 | MRPL | gap_fade_050 | INR 174.83 | 2 | 2 | 73.1 | INR 100,000 | INR 1,091,734.60 | INR 1,191,734.60 | 1262 |

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
