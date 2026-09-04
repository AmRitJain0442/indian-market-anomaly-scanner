# EQ-only and budget-screened rankings

Built on 5 September 2026. The exchange and published Zerodha MIS list are dated 4 September 2026. Your screening budget is INR 1,000, with no leverage, a INR 500 position cap and a INR 5 illustrative planned-risk limit.

| Historical study | Original pairs | Strict EQ-only pairs | Practical research pairs | Practical stocks |
|---|---:|---:|---:|---:|
| 1 year, 252 sessions | 34,476 | 24,205 | 667 | 66 |
| 10 years, 2,468 sessions | 43,264 | 20,558 | 497 | 44 |

## Open the rankings

- [One-year interactive page](one_year/index.html)
- [Ten-year interactive page](ten_year/index.html)
- [One-year findings and top pairs](one_year/README.md)
- [Ten-year findings and top pairs](ten_year/README.md)

The HTML pages work locally without a build step. GitHub renders the findings documents, not the interactive HTML. For a local browser server, run this from the repository root:

    python -m http.server 8765 --bind 127.0.0.1 --directory results

Then open the one-year page at:

    http://127.0.0.1:8765/findings/2026-09-05-eligibility-ranking/one_year/index.html

The existing local stock atlas and combination-ranking pages also have an EQ-only ranking link. No GCP deployment was performed.

## What you can work on

These are stock-strategy combinations that pass the current research and affordability screen. They are suitable candidates for the next execution test, not approved orders or proven profitable algorithms.

| Study | Leading combination | Snapshot price | Cash-cap shares | Illustrative risk shares |
|---|---|---:|---:|---:|
| 1 year | BANDHANBNK + gap continuation 1% | INR 164.95 | 3 | 2 |
| 1 year | POWERGRID + gap fade 0.5% | INR 266.00 | 1 | 1 |
| 1 year | POWERGRID + gap fade 1% | INR 266.00 | 1 | 1 |
| 10 years | EPL + gap fade 1% | INR 247.10 | 2 | 1 |
| 10 years | NTPC + gap fade 1% | INR 332.50 | 1 | 1 |
| 10 years | EPL + gap fade 0.5% | INR 247.10 | 2 | 1 |

Share counts use the INR 1,000 budget above. The risk illustration includes a tick-rounded 1% stop, estimated trading charges and an adverse-fill allowance. It is not an instruction to buy these quantities and does not guarantee a maximum loss. The historical strategy profits do not incorporate this new sizing illustration.

The practical screen additionally requires the published Zerodha MIS listing, price of at least INR 100, 20 recent sessions with median traded value of at least INR 50 crore, at least 95% historical coverage and at least 20 historical trades. It excludes overnight strategies pending a separate delivery and settlement review. The INR 100 floor and liquidity threshold are pilot choices, not legal trading prohibitions.

## Why stocks disappear from the list

- SITINET and VHLTD fail the current or historical EQ checks. Excluding only BZ would still leave the BE intraday restriction problem.
- ARFIN has historical BE trades. A current EQ label does not repair the original pair's history.
- AMD Industries, AMDIND, passes the one-year EQ-history screen but is absent from the dated Zerodha MIS list. It also falls below the pilot price and liquidity thresholds. This does not prove that every broker permanently forbids intraday trading in it.
- A stock may fit the INR 500 cash cap but fail the INR 5 planned-risk illustration after charges. The interface shows both share counts.

Use the All EQ-only, Excluded or All audited views to search a name and open Checks for its precise reasons. No historical return is silently recalculated by deleting restricted trades. A contaminated pair is excluded intact.

## Limits of the evidence

The original backtest reference account is INR 100,000. Historical profit, ending value and return columns continue to describe that theoretical account, not your INR 1,000 account. Exact opening fills, fractional compounding, future-dependent exclusions, historical broker restrictions and selection bias remain unresolved. Initial-capital drawdown was corrected for this ranking.

The default practical rank is the order of the existing five-pillar score after strict EQ screening, restricted to the practical candidates. No profitability claim follows from a high rank. The current-status filter is for finding research candidates today, not a reconstruction of a historically investable portfolio.

Zerodha's public list is a useful dated check, but your account, order type, current exchange restrictions and current liquidity still need checking. Dhan availability was not independently verified. [Zerodha MIS table](https://zerodha.com/margin-calculator/Equity/), [additional intraday restrictions](https://support.zerodha.com/category/trading-and-markets/charts-and-orders/order/articles/intraday-orders-not-allowed-for-some-stocks), [NSE series definitions](https://www.nseindia.com/static/market-data/legend-of-series)

The complete per-window exports include rejection reasons, source hashes, historical capital, original modeled profit, corrected drawdown and snapshot sizing. The frontend-design skill was used to retain the existing dark-green and gold palette in a plain, searchable research table.

Reproduce both windows:

    python generate_eligibility_ranking.py --windows both --snapshot-date 2026-09-04 --budget 1000
    python -m pytest -q

No broker login was used, no trades were placed and the original research outputs were preserved.
