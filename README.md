# Indian Market Anomaly Scanner

A reproducible, exchange-wide scanner for daily anomalies in NSE cash equities. It downloads official NSE bhavcopies, constructs the historical universe from each session, evaluates every stock over the latest 252 completed sessions, applies trading costs, and publishes stock and strategy rankings.

The source brief is preserved in [`indian_market_anomaly_scanner_252d.md`](indian_market_anomaly_scanner_252d.md).

## Latest executed findings

The committed full-market snapshot through 27 August 2026 is in [`results/findings/2026-08-27/`](results/findings/2026-08-27/README.md). It covers 2,652 historical ordinary equities over 252 completed sessions after a 550-session data build. The snapshot includes the strategy overview, raw and liquid/comparable leaders, bottom rankings, cost sensitivity, and selected figures.

## Quick start

```bash
python -m pip install -r requirements.txt
python run_research.py
```

Useful options:

```bash
python run_research.py --history-sessions 550 --evaluation-sessions 252
python run_research.py --no-download          # reuse processed data
python run_research.py --end-date 2026-08-27 # reproduce a dated run
```

The command writes normalized Parquet data under `data/processed/` and complete research artifacts under `results/`. Raw and processed market files are intentionally ignored by Git; curated, dated findings live in `results/findings/`.

## Scope and caveats

- Universe: NSE main-board ordinary equities identified from daily exchange files (`INE` ISINs in `EQ`, `BE`, or `BZ` series), excluding temporary rights entitlements (`*-RE`, `*-RE1`, etc.). SME, ETFs, debt, REITs/InvITs, preference shares, and warrants are excluded by default.
- Identity: ISIN is the stable grouping key, with the latest symbol retained for display.
- Survivorship: the universe is the union of securities present in every downloaded daily file, including new listings, disappeared symbols, and suspended names.
- Corporate actions: raw close-to-close discontinuities above 30% are flagged and the affected observations are not treated as strategy returns. This is conservative detection, not a fully adjusted-price service.
- Costs: the baseline deducts 10 bps per side for each active round trip and reports 0/5/10/20/30 bps sensitivity.
- Shorts: all shorts are theoretical research returns. Intraday cash short availability and execution are not guaranteed.
- Rankings are descriptive discovery results, not evidence of future predictability. Multiple testing, slippage, circuit limits, and out-of-sample persistence require separate study.

## Strategies

The first full-market set follows the brief: close-to-next-open, open-to-close, 0.5% and 1% gap fade/continuation, 2% previous-day reversal/momentum, 5-day reversal/momentum, turn-of-month, and volume-shock continuation/reversal.

## Outputs

- `results/run_metadata.json`: reproducibility settings and evaluation dates
- `results/market_summary.csv`: breadth and equal-weight strategy statistics
- `results/strategy_results/`: every stock-strategy metric row
- `results/rankings/`: all-stock and comparable-history leaderboards
- `results/equity_curves/`: every daily stock-strategy curve
- `results/trades/`: every executed signal
- `results/figures/`: top/bottom curves, distributions, rankings, breadth, and diagnostics
- `results/findings/`: compact committed snapshot and interpretation of the executed run

## Data provenance

Market data comes from [NSE's official daily report archive](https://www.nseindia.com/all-reports). UDiFF bhavcopies are used from 8 July 2024 onward and legacy CM bhavcopies before that date; NSE publishes the [UDiFF format resources here](https://www.nseindia.com/static/resources/forms-formats-members). The downloader caches each ZIP and records SHA-256 hashes in a manifest.
