# Twenty-session local strategy test

Requested starting investment: INR 1,000. Real money deployed: INR 0. The server and the original research outputs were not changed.

## Current result

The local data audit completed for 20 exchange-confirmed sessions from 10 August through 4 September 2026. The exact quote-based strategy cannot be backtested with the available data. Its net profit, ending balance and win rate are unavailable, not zero.

There are eight opening-gap candidates across eight sessions. These are signals, not completed trades. The other twelve sessions have no opening-gap candidate in the frozen shortlist.

| Session | Stock | Official opening gap | Candidate direction |
|---|---|---:|---|
| 2026-08-10 | CUPID | +1.5145% | SHORT |
| 2026-08-12 | CUPID | +1.5724% | SHORT |
| 2026-08-18 | CUPID | +2.1248% | SHORT |
| 2026-08-19 | HFCL | +1.2911% | SHORT |
| 2026-08-20 | ETERNAL | +1.2031% | SHORT |
| 2026-08-24 | ETERNAL | -1.5244% | LONG |
| 2026-08-26 | GROWW | -1.4925% | LONG |
| 2026-09-04 | GROWW | +1.4508% | SHORT |

## What was run

The run loads 40 official NSE daily bhavcopies. The first 20 sessions provide the trailing history for the first evaluation day. Every subsequent day uses only the preceding 20 completed sessions for liquidity, coverage and previous price. It does not rank using the evaluation day's eventual turnover or return.

The shortlist contains at most five ordinary shares, ordered by trailing median traded value and then symbol. Names need all 20 preceding sessions, previous-session EQ series, a previous close between INR 100 and half the screening equity, and median daily traded value of at least INR 50 crore. Current-session series is then attached for the eligibility check without replacing a restricted name with a sixth candidate.

The audit uses INR 1,000 as fixed screening equity. This is a data-readiness audit, not a reinvested portfolio simulation. A performance run must recompute affordability from reconciled equity every session.

The gap is official open divided by prior close, minus one. A magnitude of at least 1% creates a candidate. The archive's prior-close reference is compared with the previous observed close. A disagreement cannot be silently treated as a verified corporate-action adjustment. These eight references match, but point-in-time corporate-action notices and broker restrictions have not been independently reconstructed.

## Minute-data check

Public Yahoo chart responses supplied one-minute OHLCV bars for CUPID, HFCL, ETERNAL and GROWW across the evaluation window. Responses were cached locally and hashed. These files are not broker execution records or historical order books.

All eight signal days have 346 nonmissing positive-price bars from 09:15 through 15:00 inclusive. Every minute-data source URL, requested interval and response hash is recorded in the source manifest. Out-of-range appended quotes are removed, timestamps are converted to India time, and symbol, currency and one-minute granularity are checked.

The first minute's open sometimes differs from NSE's official opening price. The reported minute highs and lows on signal days remain inside the exchange's full-day range, but the vendor series misses some official extremes. A vendor's first recorded trade is not assumed to equal an executable auction fill. The opening-price differences are retained in the coverage file.

## Why exact profit is unavailable

The [proposed strategy](../2026-09-05-execution-review/README.md) requires a 09:16 decision using a quote no older than one second, a bid/ask spread check, visible opposite-side size, a later fill inside a narrow limit, and quote-based exits. Daily data cannot establish these. One-minute OHLCV cannot establish them either.

The available records do not contain:

- Historical bid and ask prices, sizes and one-second timestamps
- Historical broker product and short permissions
- Full point-in-time surveillance and corporate-action notices
- Order acknowledgements, partial fills or queue position

The broker historical-candle APIs also describe OHLCV records, not this missing execution evidence. Obtaining candles alone does not repair that distinction. [Kite historical-data specification](https://kite.trade/docs/connect/v3/historical/)

## Optional minute approximation

A separate approximation can use the completed 09:15 minute for a decision at 09:16, then the 09:17 bar's open with fixed adverse slippage. It must use whole shares, estimated costs, the INR 500 initial notional cap and INR 5 initial planned-risk cap. Stops and targets must be handled conservatively when both occur inside one bar.

This changes the timing and cannot test the original spread, depth or five-second fill requirements. It must be labeled an approximation, not the exact strategy. The user was asked whether to run this alternative. The current audit artifacts contain no approximate trade results.

Any retrospective result here also overlaps data already inspected in the larger research project. It would be a diagnostic, not independent forward validation or evidence of reliable next-month profit.

## Files and reproduction

Run locally with the existing Python environment:

    python run_intraday_pilot.py --mode audit --capital 1000 --end-date 2026-09-04 --sessions 20

- [Summary](summary.json)
- [All daily watchlists](daily_watchlists.csv)
- [Twenty-session status ledger](daily_ledger.csv)
- [Minute-data coverage and source differences](minute_data_coverage.csv)
- [Exchange and minute-data source hashes](data_sources.json)
- [Runner](../../../run_intraday_pilot.py)

NSE daily archives and public minute responses are cached under the ignored data directory. No broker account was connected and no paid data subscription was purchased.
