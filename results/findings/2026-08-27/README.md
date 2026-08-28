# NSE anomaly findings through 2026-08-27

Evaluation window: **2025-08-20 to 2026-08-27** (252 completed NSE sessions); **2,652** historical ordinary equities; INR 100,000 per stock-strategy; 10 bps per side.

> These are in-sample discovery rankings, not trading recommendations. Short returns are theoretical, extreme discontinuities are conservatively excluded, and no result establishes persistence.

## Strategy breadth

| strategy | stocks_tested | pct_profitable | median_net_pnl | equal_weight_pnl | median_sharpe |
|---|---|---|---|---|---|
| gap_fade_050 | 2652 | 69.0% | INR 25,035 | INR 114,691 | 1.264 |
| gap_fade_100 | 2652 | 71.9% | INR 21,152 | INR 107,657 | 1.310 |
| close_to_open | 2652 | 57.2% | INR 6,040 | INR 33,608 | 0.554 |
| volume_reversal | 2652 | 42.3% | INR 0 | INR -397 | -0.049 |
| volume_continuation | 2652 | 28.1% | INR -4,225 | INR -6,259 | -0.502 |
| reversal_5d | 2652 | 31.0% | INR -7,467 | INR -10,545 | -0.383 |
| reversal_1d | 2652 | 30.3% | INR -10,503 | INR -11,935 | -0.451 |
| momentum_5d | 2652 | 17.8% | INR -14,470 | INR -17,585 | -0.786 |
| momentum_1d | 2652 | 20.6% | INR -16,088 | INR -19,197 | -0.764 |
| turn_of_month | 2652 | 15.9% | INR -19,346 | INR -24,609 | -1.088 |
| gap_continuation_100 | 2652 | 10.3% | INR -33,360 | INR -64,780 | -2.128 |
| gap_continuation_050 | 2652 | 6.7% | INR -49,036 | INR -72,393 | -2.652 |
| open_to_close | 2652 | 4.2% | INR -62,108 | INR -71,278 | -2.515 |

## Collective strategy ranking

The collective score equally weights relative ranks for median stock PnL, profitable-stock breadth, equal-weight universe PnL, median Sharpe, and profitable breadth at 30 bps per side. The score is relative; the evidence tier separately counts absolute positive pillars.

| collective_rank | strategy | collective_score | evidence_tier | positive_pillars | median_net_pnl | pct_profitable | equal_weight_pnl |
|---|---|---|---|---|---|---|---|
| 1 | gap_fade_100 | 96.7 | ROBUST POSITIVE | 5 | INR 21,152 | 71.9% | INR 107,657 |
| 2 | gap_fade_050 | 95.0 | BROAD POSITIVE | 4 | INR 25,035 | 69.0% | INR 114,691 |
| 3 | close_to_open | 81.7 | BROAD POSITIVE | 4 | INR 6,040 | 57.2% | INR 33,608 |
| 4 | volume_reversal | 76.7 | WEAK / NEGATIVE | 0 | INR 0 | 42.3% | INR -397 |
| 5 | reversal_5d | 61.7 | WEAK / NEGATIVE | 0 | INR -7,467 | 31.0% | INR -10,545 |
| 6 | volume_continuation | 60.0 | WEAK / NEGATIVE | 0 | INR -4,225 | 28.1% | INR -6,259 |
| 7 | reversal_1d | 53.3 | WEAK / NEGATIVE | 0 | INR -10,503 | 30.3% | INR -11,935 |
| 8 | momentum_1d | 38.3 | WEAK / NEGATIVE | 0 | INR -16,088 | 20.6% | INR -19,197 |
| 9 | momentum_5d | 36.7 | WEAK / NEGATIVE | 0 | INR -14,470 | 17.8% | INR -17,585 |
| 10 | turn_of_month | 24.2 | WEAK / NEGATIVE | 0 | INR -19,346 | 15.9% | INR -24,609 |
| 11 | gap_continuation_100 | 17.5 | WEAK / NEGATIVE | 0 | INR -33,360 | 10.3% | INR -64,780 |
| 12 | open_to_close | 5.0 | WEAK / NEGATIVE | 0 | INR -62,108 | 4.2% | INR -71,278 |
| 13 | gap_continuation_050 | 3.3 | WEAK / NEGATIVE | 0 | INR -49,036 | 6.7% | INR -72,393 |

## Main observations

- At the baseline 10 bps per side, only **gap_fade_050, gap_fade_100, close_to_open** had a positive median stock PnL.
- The broadest result was **gap_fade_100**: 71.9% of stocks were profitable and its equal-weight PnL was INR 107,657.
- The 1% gap fade was the only positive-median effect that retained majority breadth at 30 bps per side (55.1%).
- Close-to-open breadth fell from 93.1% at zero cost to 57.2% at 10 bps and 17.5% at 30 bps, so its result is cost-sensitive.
- Large raw leaders often carry low-liquidity or circuit-like-session flags. Treat the liquid/comparable table below as the more inspectable shortlist, not as an execution claim.

## Cross-strategy comparisons

- Close-to-open beat open-to-close for **92.2%** of securities with both results.
- 0.5% gap continuation beat fade for **16.3%** of securities; fade beat continuation for **83.7%**.
- one-day moves favored momentum for **43.5%** of securities.
- five-day moves favored momentum for **40.4%** of securities.

## Raw all-stock leaders by net PnL

| strategy | pnl_rank | symbol | net_pnl | number_of_trades | coverage_ratio | liquidity_flag |
|---|---|---|---|---|---|---|
| close_to_open | 1 | KEEPLEARN | INR 17,324,087 | 251 | 1.000 | LOW |
| close_to_open | 2 | FILATFASH | INR 7,526,508 | 251 | 1.000 | OK |
| close_to_open | 3 | WILLAMAGOR | INR 4,239,513 | 251 | 1.000 | LOW |
| gap_continuation_050 | 1 | GMDCLTD | INR 74,422 | 114 | 1.000 | OK |
| gap_continuation_050 | 2 | WOCKPHARMA | INR 71,202 | 81 | 1.000 | OK |
| gap_continuation_050 | 3 | TEJASNET | INR 66,478 | 103 | 1.000 | OK |
| gap_continuation_100 | 1 | GENESYS | INR 93,935 | 58 | 1.000 | OK |
| gap_continuation_100 | 2 | TBZ | INR 74,646 | 54 | 1.000 | OK |
| gap_continuation_100 | 3 | BANDHANBNK | INR 60,712 | 37 | 1.000 | OK |
| gap_fade_050 | 1 | KEEPLEARN | INR 20,484,891 | 194 | 1.000 | LOW |
| gap_fade_050 | 2 | INFOMEDIA | INR 15,723,200 | 161 | 0.925 | LOW |
| gap_fade_050 | 3 | BOHRAIND | INR 15,285,656 | 195 | 0.996 | LOW |
| gap_fade_100 | 1 | KEEPLEARN | INR 22,234,093 | 174 | 1.000 | LOW |
| gap_fade_100 | 2 | BOHRAIND | INR 13,200,480 | 185 | 0.996 | LOW |
| gap_fade_100 | 3 | AKI | INR 12,482,172 | 169 | 1.000 | LOW |
| momentum_1d | 1 | REGAAL | INR 167,180 | 122 | 1.000 | OK |
| momentum_1d | 2 | ELITECON | INR 164,136 | 46 | 0.361 | OK |
| momentum_1d | 3 | URAVIDEF | INR 160,783 | 106 | 1.000 | OK |
| momentum_5d | 1 | FILATFASH | INR 369,115 | 134 | 1.000 | OK |
| momentum_5d | 2 | URAVIDEF | INR 178,375 | 103 | 1.000 | OK |
| momentum_5d | 3 | FLEXITUFF | INR 176,478 | 139 | 1.000 | LOW |
| open_to_close | 1 | MAHASTEEL | INR 385,543 | 252 | 1.000 | OK |
| open_to_close | 2 | STALLION | INR 141,549 | 252 | 1.000 | OK |
| open_to_close | 3 | GLOBAL | INR 112,833 | 252 | 1.000 | OK |
| reversal_1d | 1 | NKIND | INR 257,463 | 102 | 0.980 | LOW |
| reversal_1d | 2 | UNITEDPOLY | INR 244,861 | 145 | 1.000 | OK |
| reversal_1d | 3 | LCCINFOTEC | INR 192,108 | 173 | 1.000 | LOW |
| reversal_5d | 1 | LCCINFOTEC | INR 571,554 | 122 | 1.000 | LOW |
| reversal_5d | 2 | CREATIVEYE | INR 167,743 | 56 | 1.000 | LOW |
| reversal_5d | 3 | NRAIL | INR 131,184 | 78 | 1.000 | OK |
| turn_of_month | 1 | MAHASTEEL | INR 86,904 | 75 | 1.000 | OK |
| turn_of_month | 2 | TEJASNET | INR 76,360 | 75 | 1.000 | OK |
| turn_of_month | 3 | BHAGYANGR | INR 71,585 | 75 | 1.000 | OK |
| volume_continuation | 1 | URAVIDEF | INR 83,631 | 21 | 1.000 | OK |
| volume_continuation | 2 | GSLSU | INR 75,315 | 27 | 1.000 | OK |
| volume_continuation | 3 | TCIFINANCE | INR 72,750 | 18 | 1.000 | LOW |
| volume_reversal | 1 | AKSHOPTFBR | INR 100,236 | 28 | 1.000 | OK |
| volume_reversal | 2 | KHAITANLTD | INR 77,594 | 24 | 1.000 | LOW |
| volume_reversal | 3 | CREATIVEYE | INR 74,710 | 17 | 1.000 | LOW |

## Liquid, comparable-history leaders

| strategy | symbol | net_pnl | number_of_trades | coverage_ratio | circuit_like_sessions |
|---|---|---|---|---|---|
| close_to_open | FILATFASH | INR 7,526,508 | 251 | 1.000 | 16 |
| close_to_open | VHLTD | INR 4,048,896 | 251 | 1.000 | 0 |
| close_to_open | TREJHARA | INR 2,056,041 | 251 | 1.000 | 1 |
| gap_continuation_050 | GMDCLTD | INR 74,422 | 114 | 1.000 | 0 |
| gap_continuation_050 | WOCKPHARMA | INR 71,202 | 81 | 1.000 | 0 |
| gap_continuation_050 | TEJASNET | INR 66,478 | 103 | 1.000 | 0 |
| gap_continuation_100 | GENESYS | INR 93,935 | 58 | 1.000 | 0 |
| gap_continuation_100 | TBZ | INR 74,646 | 54 | 1.000 | 0 |
| gap_continuation_100 | BANDHANBNK | INR 60,712 | 37 | 1.000 | 0 |
| gap_fade_050 | FILATFASH | INR 11,438,035 | 151 | 1.000 | 16 |
| gap_fade_050 | URAVIDEF | INR 7,377,273 | 195 | 1.000 | 1 |
| gap_fade_050 | SUMIT | INR 4,268,704 | 194 | 1.000 | 0 |
| gap_fade_100 | FILATFASH | INR 11,438,035 | 151 | 1.000 | 16 |
| gap_fade_100 | URAVIDEF | INR 6,822,592 | 170 | 1.000 | 1 |
| gap_fade_100 | SUMIT | INR 5,015,412 | 163 | 1.000 | 0 |
| momentum_1d | REGAAL | INR 167,180 | 122 | 1.000 | 0 |
| momentum_1d | URAVIDEF | INR 160,783 | 106 | 1.000 | 1 |
| momentum_1d | GSLSU | INR 123,513 | 138 | 1.000 | 2 |
| momentum_5d | FILATFASH | INR 369,115 | 134 | 1.000 | 16 |
| momentum_5d | URAVIDEF | INR 178,375 | 103 | 1.000 | 1 |
| momentum_5d | BROOKS | INR 151,627 | 133 | 1.000 | 4 |
| open_to_close | MAHASTEEL | INR 385,543 | 252 | 1.000 | 22 |
| open_to_close | STALLION | INR 141,549 | 252 | 1.000 | 13 |
| open_to_close | GLOBAL | INR 112,833 | 252 | 1.000 | 0 |
| reversal_1d | UNITEDPOLY | INR 244,861 | 145 | 1.000 | 21 |
| reversal_1d | GATECH | INR 103,186 | 138 | 1.000 | 7 |
| reversal_1d | STALLION | INR 102,097 | 186 | 1.000 | 13 |
| reversal_5d | NRAIL | INR 131,184 | 78 | 1.000 | 2 |
| reversal_5d | ZEELEARN | INR 119,041 | 83 | 1.000 | 4 |
| reversal_5d | HECPROJECT | INR 111,633 | 79 | 1.000 | 0 |
| turn_of_month | MAHASTEEL | INR 86,904 | 75 | 1.000 | 22 |
| turn_of_month | TEJASNET | INR 76,360 | 75 | 1.000 | 0 |
| turn_of_month | BHAGYANGR | INR 71,585 | 75 | 1.000 | 5 |
| volume_continuation | URAVIDEF | INR 83,631 | 21 | 1.000 | 1 |
| volume_continuation | GSLSU | INR 75,315 | 27 | 1.000 | 2 |
| volume_continuation | MANAKALUCO | INR 66,148 | 25 | 1.000 | 8 |
| volume_reversal | AKSHOPTFBR | INR 100,236 | 28 | 1.000 | 41 |
| volume_reversal | ASHIMASYN | INR 63,019 | 17 | 1.000 | 0 |
| volume_reversal | CENTEXT | INR 61,273 | 17 | 1.000 | 1 |

## Reproduction

```bash
python run_research.py --end-date 2026-08-27
```

The CSV files beside this report contain the complete compact overview and top/bottom ten rows for every strategy. Full rankings, curves, and trades are generated locally and excluded from Git because of their size.
