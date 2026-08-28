# Collective strategy ranking

The collective score is the equal-weight average of five relative percentile scores: median stock net PnL, profitable-stock breadth, equal-weight universe PnL, median stock Sharpe, and profitable-stock breadth at 30 bps per side.

The score is relative—not a probability of success. The evidence tier separately counts how many pillars are positive in absolute terms.

| Rank | Strategy | Score | Tier | Positive pillars | Median PnL | Profitable | Equal-weight PnL | Median Sharpe | Profitable at 30 bps |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | gap_fade_100 | 96.7 | ROBUST POSITIVE | 5/5 | INR 21,152 | 71.9% | INR 107,657 | 1.31 | 55.1% |
| 2 | gap_fade_050 | 95.0 | BROAD POSITIVE | 4/5 | INR 25,035 | 69.0% | INR 114,691 | 1.26 | 46.2% |
| 3 | close_to_open | 81.7 | BROAD POSITIVE | 4/5 | INR 6,040 | 57.2% | INR 33,608 | 0.55 | 17.5% |
| 4 | volume_reversal | 76.7 | WEAK / NEGATIVE | 0/5 | INR 0 | 42.3% | INR -397 | -0.05 | 26.6% |
| 5 | reversal_5d | 61.7 | WEAK / NEGATIVE | 0/5 | INR -7,467 | 31.0% | INR -10,545 | -0.38 | 9.5% |
| 6 | volume_continuation | 60.0 | WEAK / NEGATIVE | 0/5 | INR -4,225 | 28.1% | INR -6,259 | -0.50 | 15.0% |
| 7 | reversal_1d | 53.3 | WEAK / NEGATIVE | 0/5 | INR -10,503 | 30.3% | INR -11,935 | -0.45 | 7.5% |
| 8 | momentum_1d | 38.3 | WEAK / NEGATIVE | 0/5 | INR -16,088 | 20.6% | INR -19,197 | -0.76 | 5.2% |
| 9 | momentum_5d | 36.7 | WEAK / NEGATIVE | 0/5 | INR -14,470 | 17.8% | INR -17,585 | -0.79 | 3.9% |
| 10 | turn_of_month | 24.2 | WEAK / NEGATIVE | 0/5 | INR -19,346 | 15.9% | INR -24,609 | -1.09 | 3.7% |
| 11 | gap_continuation_100 | 17.5 | WEAK / NEGATIVE | 0/5 | INR -33,360 | 10.3% | INR -64,780 | -2.13 | 3.7% |
| 12 | open_to_close | 5.0 | WEAK / NEGATIVE | 0/5 | INR -62,108 | 4.2% | INR -71,278 | -2.51 | 1.4% |
| 13 | gap_continuation_050 | 3.3 | WEAK / NEGATIVE | 0/5 | INR -49,036 | 6.7% | INR -72,393 | -2.65 | 1.3% |

## Evidence tiers

- **ROBUST POSITIVE:** 5/5 pillars positive.
- **BROAD POSITIVE:** 4/5 pillars positive.
- **MIXED:** 2–3 pillars positive.
- **WEAK / NEGATIVE:** 0–1 pillars positive.

> This is an in-sample discovery ranking, not evidence of future profitability.
