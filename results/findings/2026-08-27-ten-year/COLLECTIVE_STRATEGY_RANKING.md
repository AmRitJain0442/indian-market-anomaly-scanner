# Collective strategy ranking

The collective score is the equal-weight average of five relative percentile scores: median stock net PnL, profitable-stock breadth, equal-weight universe PnL, median stock Sharpe, and profitable-stock breadth at 30 bps per side.

The score is relative—not a probability of success. The evidence tier separately counts how many pillars are positive in absolute terms.

| Rank | Strategy | Score | Tier | Positive pillars | Median PnL | Profitable | Equal-weight PnL | Median Sharpe | Profitable at 30 bps |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | gap_fade_050 | 96.7 | ROBUST POSITIVE | 5/5 | INR 1,533,502 | 89.2% | INR 26,185,882,185 | 1.39 | 60.8% |
| 2 | gap_fade_100 | 95.0 | ROBUST POSITIVE | 5/5 | INR 839,993 | 91.1% | INR 11,366,765,936 | 1.38 | 74.8% |
| 3 | close_to_open | 83.3 | BROAD POSITIVE | 4/5 | INR 208,556 | 78.9% | INR 17,065,436 | 0.89 | 21.7% |
| 4 | volume_reversal | 75.0 | MIXED | 2/5 | INR 0 | 45.8% | INR 20,044 | 0.05 | 17.8% |
| 5 | reversal_5d | 61.7 | WEAK / NEGATIVE | 0/5 | INR -36,265 | 23.6% | INR -60,982 | -0.18 | 4.3% |
| 6 | volume_continuation | 60.0 | WEAK / NEGATIVE | 0/5 | INR -30,359 | 13.9% | INR -60,737 | -0.37 | 5.7% |
| 7 | reversal_1d | 53.3 | WEAK / NEGATIVE | 0/5 | INR -49,606 | 18.8% | INR -76,379 | -0.29 | 4.2% |
| 8 | momentum_1d | 40.0 | WEAK / NEGATIVE | 0/5 | INR -66,892 | 10.6% | INR -90,531 | -0.47 | 2.9% |
| 9 | momentum_5d | 31.7 | WEAK / NEGATIVE | 0/5 | INR -74,363 | 7.3% | INR -92,916 | -0.58 | 2.3% |
| 10 | turn_of_month | 28.3 | WEAK / NEGATIVE | 0/5 | INR -75,980 | 7.1% | INR -94,815 | -0.77 | 3.2% |
| 11 | open_to_close | 13.3 | WEAK / NEGATIVE | 0/5 | INR -99,874 | 3.8% | INR -100,000 | -1.90 | 1.9% |
| 12 | gap_continuation_100 | 10.0 | WEAK / NEGATIVE | 0/5 | INR -98,503 | 1.5% | INR -100,000 | -2.05 | 0.7% |
| 13 | gap_continuation_050 | 1.7 | WEAK / NEGATIVE | 0/5 | INR -99,851 | 1.5% | INR -100,000 | -2.51 | 0.7% |

## Evidence tiers

- **ROBUST POSITIVE:** 5/5 pillars positive.
- **BROAD POSITIVE:** 4/5 pillars positive.
- **MIXED:** 2–3 pillars positive.
- **WEAK / NEGATIVE:** 0–1 pillars positive.

> This is an in-sample discovery ranking, not evidence of future profitability.
