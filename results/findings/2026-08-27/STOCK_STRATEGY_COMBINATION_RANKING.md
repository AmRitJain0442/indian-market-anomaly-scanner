# Stock × strategy combination ranking

All **34,476** stock-strategy combinations are ranked from an initial investment of **INR 100,000** per pair.

The relative combination score weights net PnL (25%), Sharpe (20%), PnL at 30 bps per side (20%), excess PnL versus buy-and-hold (20%), and drawdown resilience (15%). The profit rank is also retained independently.

A pair is comparable when it has at least 95% history, an `OK` liquidity flag, and at least 20 trades. Every non-comparable pair remains in the overall table and is explicitly labelled.

## Top 25 overall

| Rank | Stock | Strategy | Score | Initial | Profit | Ending value | Sharpe | 30 bps PnL | Evidence | Sample |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | SITINET | gap_fade_050 | 99.2 | INR 100,000 | INR 4,994,940 | INR 5,094,940 | 12.44 | INR 2,476,214 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 2 | SITINET | gap_fade_100 | 99.2 | INR 100,000 | INR 4,994,940 | INR 5,094,940 | 12.44 | INR 2,476,214 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 3 | ANKITMETAL | gap_fade_100 | 98.9 | INR 100,000 | INR 5,709,899 | INR 5,809,899 | 10.98 | INR 3,084,333 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 4 | FEL | gap_fade_050 | 98.8 | INR 100,000 | INR 2,092,955 | INR 2,192,955 | 11.39 | INR 1,005,209 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 5 | FEL | gap_fade_100 | 98.8 | INR 100,000 | INR 2,092,955 | INR 2,192,955 | 11.39 | INR 1,005,209 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 6 | KHANDSE | gap_fade_100 | 98.7 | INR 100,000 | INR 4,170,875 | INR 4,270,875 | 9.17 | INR 2,285,174 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 7 | KHANDSE | gap_fade_050 | 98.7 | INR 100,000 | INR 4,771,368 | INR 4,871,368 | 9.31 | INR 2,372,282 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 8 | MTEDUCARE | gap_fade_050 | 98.6 | INR 100,000 | INR 5,910,028 | INR 6,010,028 | 9.41 | INR 2,952,570 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 9 | SANWARIA | gap_fade_050 | 98.6 | INR 100,000 | INR 5,594,333 | INR 5,694,333 | 10.43 | INR 3,200,782 | ROBUST POSITIVE (5/5) | LIMITED SAMPLE |
| 10 | SANWARIA | gap_fade_100 | 98.6 | INR 100,000 | INR 5,594,333 | INR 5,694,333 | 10.43 | INR 3,200,782 | ROBUST POSITIVE (5/5) | LIMITED SAMPLE |
| 11 | MTEDUCARE | gap_fade_100 | 98.6 | INR 100,000 | INR 4,655,998 | INR 4,755,998 | 9.10 | INR 2,493,997 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 12 | PREMIER | gap_fade_100 | 98.6 | INR 100,000 | INR 1,838,722 | INR 1,938,722 | 8.99 | INR 1,127,173 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 13 | VHLTD | gap_fade_050 | 98.5 | INR 100,000 | INR 3,626,746 | INR 3,726,746 | 11.91 | INR 1,582,293 | ROBUST POSITIVE (5/5) | COMPARABLE |
| 14 | VHLTD | gap_fade_100 | 98.5 | INR 100,000 | INR 3,365,382 | INR 3,465,382 | 12.01 | INR 1,642,612 | ROBUST POSITIVE (5/5) | COMPARABLE |
| 15 | LCCINFOTEC | gap_fade_100 | 98.5 | INR 100,000 | INR 9,456,741 | INR 9,556,741 | 8.95 | INR 4,608,796 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 16 | TOUCHWOOD | gap_fade_100 | 98.4 | INR 100,000 | INR 2,826,794 | INR 2,926,794 | 8.68 | INR 1,626,334 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 17 | INFOMEDIA | gap_fade_100 | 98.4 | INR 100,000 | INR 11,997,701 | INR 12,097,701 | 9.14 | INR 6,847,809 | ROBUST POSITIVE (5/5) | LIMITED SAMPLE |
| 18 | MCCHRLS-B | gap_fade_050 | 98.4 | INR 100,000 | INR 1,021,389 | INR 1,121,389 | 7.26 | INR 724,800 | ROBUST POSITIVE (5/5) | LIMITED SAMPLE |
| 19 | AKI | gap_fade_100 | 98.4 | INR 100,000 | INR 12,482,172 | INR 12,582,172 | 11.95 | INR 6,413,263 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 20 | MCCHRLS-B | gap_fade_100 | 98.4 | INR 100,000 | INR 1,010,909 | INR 1,110,909 | 7.24 | INR 733,600 | ROBUST POSITIVE (5/5) | LIMITED SAMPLE |
| 21 | EUROBOND | gap_fade_100 | 98.4 | INR 100,000 | INR 2,739,364 | INR 2,839,364 | 9.09 | INR 1,445,614 | ROBUST POSITIVE (5/5) | COMPARABLE |
| 22 | LAL | gap_fade_100 | 98.4 | INR 100,000 | INR 6,233,801 | INR 6,333,801 | 10.57 | INR 3,276,465 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 23 | PRUDMOULI | gap_fade_100 | 98.4 | INR 100,000 | INR 10,216,269 | INR 10,316,269 | 10.65 | INR 5,300,390 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 24 | LCCINFOTEC | gap_fade_050 | 98.3 | INR 100,000 | INR 10,001,339 | INR 10,101,339 | 8.89 | INR 4,682,527 | ROBUST POSITIVE (5/5) | LOW LIQUIDITY |
| 25 | OMKARCHEM | gap_fade_050 | 98.3 | INR 100,000 | INR 1,746,468 | INR 1,846,468 | 7.78 | INR 1,054,511 | ROBUST POSITIVE (5/5) | LIMITED SAMPLE |

## Top 25 comparable

| Comparable rank | Overall rank | Stock | Strategy | Score | Initial | Profit | Ending value | Sharpe | 30 bps PnL |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | 13 | VHLTD | gap_fade_050 | 98.5 | INR 100,000 | INR 3,626,746 | INR 3,726,746 | 11.91 | INR 1,582,293 |
| 2 | 14 | VHLTD | gap_fade_100 | 98.5 | INR 100,000 | INR 3,365,382 | INR 3,465,382 | 12.01 | INR 1,642,612 |
| 3 | 21 | EUROBOND | gap_fade_100 | 98.4 | INR 100,000 | INR 2,739,364 | INR 2,839,364 | 9.09 | INR 1,445,614 |
| 4 | 39 | TREJHARA | close_to_open | 98.0 | INR 100,000 | INR 2,056,041 | INR 2,156,041 | 9.29 | INR 697,954 |
| 5 | 46 | VHLTD | close_to_open | 97.9 | INR 100,000 | INR 4,048,896 | INR 4,148,896 | 13.78 | INR 1,439,617 |
| 6 | 48 | VISACHROME | gap_fade_050 | 97.8 | INR 100,000 | INR 3,185,119 | INR 3,285,119 | 7.78 | INR 1,473,695 |
| 7 | 53 | VISACHROME | gap_fade_100 | 97.8 | INR 100,000 | INR 2,832,440 | INR 2,932,440 | 7.65 | INR 1,415,243 |
| 8 | 59 | EUROBOND | gap_fade_050 | 97.8 | INR 100,000 | INR 3,329,156 | INR 3,429,156 | 9.12 | INR 1,510,547 |
| 9 | 76 | INNOVANA | gap_fade_050 | 97.6 | INR 100,000 | INR 1,957,527 | INR 2,057,527 | 7.47 | INR 928,224 |
| 10 | 87 | SHAH | close_to_open | 97.5 | INR 100,000 | INR 1,337,109 | INR 1,437,109 | 9.56 | INR 431,058 |
| 11 | 98 | ORICONENT | gap_fade_100 | 97.4 | INR 100,000 | INR 444,214 | INR 544,214 | 7.79 | INR 268,424 |
| 12 | 99 | HITECHGEAR | gap_fade_100 | 97.4 | INR 100,000 | INR 618,586 | INR 718,586 | 7.42 | INR 344,103 |
| 13 | 109 | SREEL | gap_fade_050 | 97.3 | INR 100,000 | INR 575,306 | INR 675,306 | 8.41 | INR 255,457 |
| 14 | 112 | HITECHGEAR | gap_fade_050 | 97.3 | INR 100,000 | INR 706,232 | INR 806,232 | 7.40 | INR 338,484 |
| 15 | 114 | SUTLEJTEX | gap_fade_100 | 97.3 | INR 100,000 | INR 1,568,253 | INR 1,668,253 | 8.04 | INR 832,005 |
| 16 | 120 | STARTECK | close_to_open | 97.2 | INR 100,000 | INR 759,425 | INR 859,425 | 7.72 | INR 216,935 |
| 17 | 126 | EUROBOND | close_to_open | 97.1 | INR 100,000 | INR 1,558,169 | INR 1,658,169 | 8.23 | INR 513,046 |
| 18 | 131 | ORICONENT | gap_fade_050 | 97.1 | INR 100,000 | INR 537,013 | INR 637,013 | 7.69 | INR 273,531 |
| 19 | 143 | CONSOFINVT | gap_fade_100 | 97.0 | INR 100,000 | INR 600,737 | INR 700,737 | 6.96 | INR 347,131 |
| 20 | 150 | RPPL | gap_fade_100 | 96.9 | INR 100,000 | INR 980,024 | INR 1,080,024 | 6.49 | INR 549,982 |
| 21 | 165 | FILATFASH | gap_fade_050 | 96.9 | INR 100,000 | INR 11,438,035 | INR 11,538,035 | 9.84 | INR 6,316,457 |
| 22 | 166 | FILATFASH | gap_fade_100 | 96.9 | INR 100,000 | INR 11,438,035 | INR 11,538,035 | 9.84 | INR 6,316,457 |
| 23 | 176 | ROSSELLIND | gap_fade_100 | 96.8 | INR 100,000 | INR 1,110,501 | INR 1,210,501 | 8.01 | INR 620,182 |
| 24 | 180 | EIFFL | gap_fade_050 | 96.8 | INR 100,000 | INR 871,476 | INR 971,476 | 6.94 | INR 443,762 |
| 25 | 181 | ROSSELLIND | gap_fade_050 | 96.8 | INR 100,000 | INR 1,128,363 | INR 1,228,363 | 7.88 | INR 577,255 |

## Interpretation

- The combination score is a relative discovery score, not a probability or forecast.
- `ROBUST POSITIVE` requires positive net PnL, Sharpe, 30 bps PnL, excess PnL, and a positive 95% mean-trade confidence floor.
- Low-liquidity and limited-sample leaders can be economically implausible; use the comparable rank as the more inspectable shortlist.
- Full results are provided in the adjacent compressed CSV and in the offline interactive atlas release.

> In-sample research only; not a trading recommendation.
