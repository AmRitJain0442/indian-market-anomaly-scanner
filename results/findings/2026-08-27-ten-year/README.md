# NSE anomaly findings through 2026-08-27

Evaluation window: **2016-08-29 to 2026-08-27** (2468 completed NSE sessions); **3,328** historical ordinary equities; INR 100,000 per stock-strategy; 10 bps per side.

> These are in-sample discovery rankings, not trading recommendations. Short returns are theoretical, extreme discontinuities are conservatively excluded, and no result establishes persistence.

## Strategy breadth

| strategy | stocks_tested | pct_profitable | median_net_pnl | equal_weight_pnl | median_sharpe |
|---|---|---|---|---|---|
| gap_fade_050 | 3328 | 89.2% | INR 1,533,502 | INR 26,185,882,185 | 1.393 |
| gap_fade_100 | 3328 | 91.1% | INR 839,993 | INR 11,366,765,936 | 1.382 |
| close_to_open | 3328 | 78.9% | INR 208,556 | INR 17,065,436 | 0.893 |
| volume_reversal | 3328 | 45.8% | INR 0 | INR 20,044 | 0.050 |
| volume_continuation | 3328 | 13.9% | INR -30,359 | INR -60,737 | -0.375 |
| reversal_5d | 3328 | 23.6% | INR -36,265 | INR -60,982 | -0.182 |
| reversal_1d | 3328 | 18.8% | INR -49,606 | INR -76,379 | -0.285 |
| momentum_1d | 3328 | 10.6% | INR -66,892 | INR -90,531 | -0.465 |
| momentum_5d | 3328 | 7.3% | INR -74,363 | INR -92,916 | -0.575 |
| turn_of_month | 3328 | 7.1% | INR -75,980 | INR -94,815 | -0.771 |
| gap_continuation_100 | 3328 | 1.5% | INR -98,503 | INR -100,000 | -2.053 |
| gap_continuation_050 | 3328 | 1.5% | INR -99,851 | INR -100,000 | -2.511 |
| open_to_close | 3328 | 3.8% | INR -99,874 | INR -100,000 | -1.895 |

## Collective strategy ranking

The collective score equally weights relative ranks for median stock PnL, profitable-stock breadth, equal-weight universe PnL, median Sharpe, and profitable breadth at 30 bps per side. The score is relative; the evidence tier separately counts absolute positive pillars.

| collective_rank | strategy | collective_score | evidence_tier | positive_pillars | median_net_pnl | pct_profitable | equal_weight_pnl |
|---|---|---|---|---|---|---|---|
| 1 | gap_fade_050 | 96.7 | ROBUST POSITIVE | 5 | INR 1,533,502 | 89.2% | INR 26,185,882,185 |
| 2 | gap_fade_100 | 95.0 | ROBUST POSITIVE | 5 | INR 839,993 | 91.1% | INR 11,366,765,936 |
| 3 | close_to_open | 83.3 | BROAD POSITIVE | 4 | INR 208,556 | 78.9% | INR 17,065,436 |
| 4 | volume_reversal | 75.0 | MIXED | 2 | INR 0 | 45.8% | INR 20,044 |
| 5 | reversal_5d | 61.7 | WEAK / NEGATIVE | 0 | INR -36,265 | 23.6% | INR -60,982 |
| 6 | volume_continuation | 60.0 | WEAK / NEGATIVE | 0 | INR -30,359 | 13.9% | INR -60,737 |
| 7 | reversal_1d | 53.3 | WEAK / NEGATIVE | 0 | INR -49,606 | 18.8% | INR -76,379 |
| 8 | momentum_1d | 40.0 | WEAK / NEGATIVE | 0 | INR -66,892 | 10.6% | INR -90,531 |
| 9 | momentum_5d | 31.7 | WEAK / NEGATIVE | 0 | INR -74,363 | 7.3% | INR -92,916 |
| 10 | turn_of_month | 28.3 | WEAK / NEGATIVE | 0 | INR -75,980 | 7.1% | INR -94,815 |
| 11 | open_to_close | 13.3 | WEAK / NEGATIVE | 0 | INR -99,874 | 3.8% | INR -100,000 |
| 12 | gap_continuation_100 | 10.0 | WEAK / NEGATIVE | 0 | INR -98,503 | 1.5% | INR -100,000 |
| 13 | gap_continuation_050 | 1.7 | WEAK / NEGATIVE | 0 | INR -99,851 | 1.5% | INR -100,000 |

## Main observations

- At the baseline 10 bps per side, **gap_fade_050, gap_fade_100, close_to_open** had a positive median stock PnL.
- The broadest result was **gap_fade_100**: 91.1% of stocks were profitable and its equal-weight PnL was INR 11,366,765,936.
- The strongest breadth at 30 bps per side was **gap_fade_100** (74.8%).
- Close-to-open breadth fell from 94.7% at zero cost to 78.9% at 10 bps and 21.7% at 30 bps, so its result is cost-sensitive.
- Large raw leaders often carry low-liquidity or circuit-like-session flags. Treat the liquid/comparable table below as the more inspectable shortlist, not as an execution claim.

## Cross-strategy comparisons

- Close-to-open beat open-to-close for **94.7%** of securities with both results.
- 0.5% gap continuation beat fade for **3.0%** of securities; fade beat continuation for **97.0%**.
- one-day moves favored momentum for **41.7%** of securities.
- five-day moves favored momentum for **28.4%** of securities.

## Decade interpretation guardrails

- Compounding magnifies small model errors over thousands of sessions. Extremely large values are mathematical backtest outputs, not executable wealth forecasts.
- Gap-fade results include theoretical intraday shorts. Borrow availability, broker restrictions, price bands, auction risk, impact, taxes, and slippage are not fully modeled.
- The `OK` liquidity threshold is a screening floor, not proof that the displayed position could have been filled throughout the decade.
- The entire window is in-sample. A walk-forward, point-in-time tradability study is required before using the ranking for capital allocation.

## Raw all-stock leaders by net PnL

| strategy | pnl_rank | symbol | net_pnl | number_of_trades | coverage_ratio | liquidity_flag |
|---|---|---|---|---|---|---|
| close_to_open | 1 | FCSSOFT | INR 6.187e+15 | 2320 | 0.953 | OK |
| close_to_open | 2 | PNC | INR 2.312e+14 | 2463 | 0.999 | LOW |
| close_to_open | 3 | CALSOFT | INR 2.077e+14 | 2255 | 0.934 | LOW |
| gap_continuation_050 | 1 | KMEW | INR 38,204 | 97 | 0.068 | OK |
| gap_continuation_050 | 2 | GARUDA | INR 29,818 | 242 | 0.187 | OK |
| gap_continuation_050 | 3 | SUPTANERY | INR 29,699 | 8 | 0.004 | OK |
| gap_continuation_100 | 1 | EIEL | INR 42,344 | 108 | 0.175 | OK |
| gap_continuation_100 | 2 | KMEW | INR 37,478 | 54 | 0.068 | OK |
| gap_continuation_100 | 3 | GARUDA | INR 35,381 | 117 | 0.187 | OK |
| gap_fade_050 | 1 | VISESHINFO | INR 3.436e+44 | 418 | 0.572 | OK |
| gap_fade_050 | 2 | RAJRAYON | INR 2.999e+36 | 433 | 0.490 | LOW |
| gap_fade_050 | 3 | KSERASERA | INR 1.678e+34 | 301 | 0.436 | LOW |
| gap_fade_100 | 1 | VISESHINFO | INR 3.436e+44 | 418 | 0.572 | OK |
| gap_fade_100 | 2 | RAJRAYON | INR 2.999e+36 | 433 | 0.490 | LOW |
| gap_fade_100 | 3 | KSERASERA | INR 1.678e+34 | 301 | 0.436 | LOW |
| momentum_1d | 1 | VISESHINFO | INR 5.014e+17 | 488 | 0.572 | OK |
| momentum_1d | 2 | KSERASERA | INR 17,027,818,651 | 327 | 0.436 | LOW |
| momentum_1d | 3 | UVSL | INR 216,336,701 | 363 | 0.423 | LOW |
| momentum_5d | 1 | VISESHINFO | INR 2.012e+17 | 538 | 0.572 | OK |
| momentum_5d | 2 | UVSL | INR 36,397,259,362 | 465 | 0.423 | LOW |
| momentum_5d | 3 | RAJRAYON | INR 414,206,660 | 434 | 0.490 | LOW |
| open_to_close | 1 | ANTGRAPHIC | INR 4.401e+12 | 2118 | 0.858 | LOW |
| open_to_close | 2 | SMPL | INR 104,089,065,557 | 1014 | 0.434 | LOW |
| open_to_close | 3 | AUSTRAL | INR 48,231,453,206 | 256 | 0.107 | LOW |
| reversal_1d | 1 | PRAKASHSTL | INR 5,174,161 | 998 | 0.910 | LOW |
| reversal_1d | 2 | GAYAHWS | INR 4,799,079 | 1077 | 0.717 | LOW |
| reversal_1d | 3 | SAMBHAAV | INR 2,977,600 | 1273 | 1.000 | LOW |
| reversal_5d | 1 | ANTGRAPHIC | INR 4,559,928 | 1039 | 0.858 | LOW |
| reversal_5d | 2 | TAINWALCHM | INR 2,540,424 | 947 | 0.992 | LOW |
| reversal_5d | 3 | HECPROJECT | INR 2,503,859 | 530 | 0.466 | LOW |
| turn_of_month | 1 | SMPL | INR 60,436,228 | 293 | 0.434 | LOW |
| turn_of_month | 2 | ANTGRAPHIC | INR 26,866,141 | 621 | 0.858 | LOW |
| turn_of_month | 3 | VISESHINFO | INR 10,451,586 | 332 | 0.572 | OK |
| volume_continuation | 1 | VISESHINFO | INR 7,833,821 | 68 | 0.572 | OK |
| volume_continuation | 2 | UVSL | INR 424,770 | 61 | 0.423 | LOW |
| volume_continuation | 3 | KSERASERA | INR 333,694 | 56 | 0.436 | LOW |
| volume_reversal | 1 | RAJSREESUG | INR 1,300,267 | 239 | 1.000 | OK |
| volume_reversal | 2 | PNC | INR 1,090,808 | 274 | 0.999 | LOW |
| volume_reversal | 3 | MENONBE | INR 747,584 | 197 | 1.000 | OK |

## Liquid, comparable-history leaders

| strategy | symbol | net_pnl | number_of_trades | coverage_ratio | circuit_like_sessions |
|---|---|---|---|---|---|
| close_to_open | FCSSOFT | INR 6.187e+15 | 2320 | 0.953 | 154 |
| close_to_open | MINDTECK | INR 3.849e+12 | 2465 | 1.000 | 47 |
| close_to_open | PILITA | INR 1.793e+12 | 2467 | 1.000 | 29 |
| gap_continuation_050 | LT | INR -77,872 | 804 | 1.000 | 0 |
| gap_continuation_050 | TMPV | INR -83,043 | 1197 | 1.000 | 0 |
| gap_continuation_050 | VEDL | INR -85,286 | 1299 | 1.000 | 0 |
| gap_continuation_100 | PFC | INR -8,108 | 343 | 1.000 | 0 |
| gap_continuation_100 | UPL | INR -21,672 | 279 | 1.000 | 0 |
| gap_continuation_100 | LT | INR -39,762 | 259 | 1.000 | 0 |
| gap_fade_050 | FCSSOFT | INR 4.349e+25 | 1306 | 0.953 | 154 |
| gap_fade_050 | SPLIL | INR 3.346e+18 | 1871 | 1.000 | 21 |
| gap_fade_050 | VIPULLTD | INR 5.057e+16 | 1828 | 1.000 | 136 |
| gap_fade_100 | FCSSOFT | INR 2.132e+25 | 1174 | 0.953 | 154 |
| gap_fade_100 | SPLIL | INR 9.283e+17 | 1526 | 1.000 | 21 |
| gap_fade_100 | KERNEX | INR 4.874e+16 | 1611 | 1.000 | 101 |
| momentum_1d | PNBHOUSING | INR 222,763 | 866 | 0.982 | 7 |
| momentum_1d | NIITLTD | INR 115,844 | 909 | 1.000 | 0 |
| momentum_1d | VHL | INR 109,177 | 649 | 0.998 | 2 |
| momentum_5d | ASIANTILES | INR 156,707 | 1005 | 1.000 | 0 |
| momentum_5d | KAJARIACER | INR -25,841 | 609 | 0.990 | 0 |
| momentum_5d | WIPRO | INR -28,989 | 358 | 1.000 | 0 |
| open_to_close | INDIGO | INR -98,606 | 2468 | 1.000 | 0 |
| open_to_close | ICICIBANK | INR -99,294 | 2468 | 1.000 | 0 |
| open_to_close | ADANIENT | INR -99,406 | 2468 | 1.000 | 0 |
| reversal_1d | SURANASOL | INR 1,746,235 | 1001 | 1.000 | 59 |
| reversal_1d | LLOYDSENGG | INR 903,891 | 1479 | 1.000 | 200 |
| reversal_1d | GTLINFRA | INR 835,831 | 1388 | 1.000 | 200 |
| reversal_5d | VIDHIING | INR 808,272 | 720 | 1.000 | 0 |
| reversal_5d | GARFIBRES | INR 724,810 | 574 | 1.000 | 0 |
| reversal_5d | RTNPOWER | INR 260,688 | 1091 | 1.000 | 107 |
| turn_of_month | SAIL | INR -836 | 723 | 1.000 | 0 |
| turn_of_month | NATIONALUM | INR -30,384 | 723 | 1.000 | 0 |
| turn_of_month | NMDC | INR -37,663 | 722 | 1.000 | 0 |
| volume_continuation | JSWHL | INR 85,907 | 162 | 1.000 | 0 |
| volume_continuation | ICIL | INR 53,780 | 207 | 0.980 | 5 |
| volume_continuation | CARERATING | INR 51,127 | 129 | 1.000 | 0 |
| volume_reversal | RAJSREESUG | INR 1,300,267 | 239 | 1.000 | 34 |
| volume_reversal | MENONBE | INR 747,584 | 197 | 1.000 | 3 |
| volume_reversal | 20MICRONS | INR 740,878 | 202 | 1.000 | 45 |

## Reproduction

```bash
python run_research.py --start-date 2016-08-29 --end-date 2026-08-27 --namespace ten_year --sparse-curves
```

The CSV files beside this report contain the complete compact overview and top/bottom ten rows for every strategy. Full rankings, curves, and trades are generated locally and excluded from Git because of their size.
