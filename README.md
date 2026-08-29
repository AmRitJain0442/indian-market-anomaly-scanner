# Indian Market Anomaly Scanner

A reproducible, exchange-wide scanner for daily anomalies in NSE cash equities. It downloads official NSE bhavcopies, constructs the historical universe from each session, evaluates every stock over the latest 252 completed sessions, applies trading costs, and publishes stock and strategy rankings.

The source brief is preserved in [`indian_market_anomaly_scanner_252d.md`](indian_market_anomaly_scanner_252d.md).

## Latest executed findings

The committed full-market snapshot through 27 August 2026 is in [`results/findings/2026-08-27/`](results/findings/2026-08-27/README.md). It covers 2,652 historical ordinary equities over 252 completed sessions after a 550-session data build. The snapshot includes the strategy overview, raw and liquid/comparable leaders, bottom rankings, cost sensitivity, and selected figures.

## Executed 10-year section

The separate decade study is in [`results/findings/2026-08-27-ten-year/`](results/findings/2026-08-27-ten-year/README.md). It covers the exact trailing calendar decade from 29 August 2016 through 27 August 2026: **2,468 completed sessions**, **3,328 historical ordinary equities**, **13 strategies**, and **43,264 stock-strategy combinations**. The searchable local atlas contains one image per stock and all 43,264 strategy graphs.

Run the isolated decade pipeline without overwriting the 252-session artifacts:

```bash
python run_research.py --start-date 2016-08-28 --end-date 2026-08-27 --namespace ten_year --sparse-curves
python generate_stock_gallery.py --namespace ten_year --workers 8
python generate_strategy_ranking.py --namespace ten_year
python generate_combination_ranking.py --namespace ten_year
python publish_decade_findings.py
```

Open `results/ten_year/stock_gallery/index.html`, or use the **10-year analysis** switch in the standard gallery. The decade’s collective leaders are `gap_fade_050`, `gap_fade_100`, and `close_to_open`. These remain in-sample research results; the very large theoretical compounded gap-fade values require special caution around short availability, liquidity, circuits, slippage, and point-in-time tradability.

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

## Complete stock × strategy visual atlas

After a research run, generate one atlas for every stock. Each image contains all 13 strategy curves, so the current findings produce 2,652 images covering 34,476 stock-strategy graphs:

```bash
python generate_stock_gallery.py
```

Open `results/stock_gallery/index.html` for the searchable gallery. Search by symbol, company, or ISIN; filter for liquid or ≥95%-coverage securities; navigate with the arrow keys; and download any full-resolution WebP. The complete generated snapshot is also published in the [atlas-2026-08-27 GitHub release](https://github.com/AmRitJain0442/indian-market-anomaly-scanner/releases/tag/atlas-2026-08-27).

Generate the market-wide collective strategy leaderboard with:

```bash
python generate_strategy_ranking.py
```

This ranks strategies using five equally weighted pillars: median stock net PnL, profitable-stock breadth, equal-weight universe PnL, median stock Sharpe, and profitable breadth at 30 bps per side. The gallery links to the resulting interactive leaderboard.

Rank every individual stock-strategy pair with:

```bash
python generate_combination_ranking.py
```

This creates a searchable leaderboard for all 34,476 combinations. Every row shows the INR 100,000 initial investment, realised profit, ending value, composite score, pure-profit rank, cost sensitivity, risk, evidence tier, and sample-quality label. It also publishes a separate comparable rank for liquid securities with at least 95% history and 20 trades.

Generate the rules-based INR 10,000 pilot plan with:

```bash
python generate_investment_plan.py
```

The plan uses a strict, direction-checked 1% gap-fade watchlist and a three-stage paper → half-size → full-pilot gate. It caps one-position exposure at INR 5,000, planned risk at INR 50 per trade, daily loss at INR 100, and cumulative pilot drawdown at INR 500. These execution controls are deliberately stricter than the historical scanner and must be paper-validated before capital is used.

The same page includes a dated 30-session operating calendar from 31 August through 13 October 2026, excluding NSE holidays. Each day has an explicit decision, fixed execution clock, measurable process target, and conditional phase. Reinvestment is percentage-based: the prior closing equity becomes the next day's sizing base, while exposure and risk remain capped at 25%/0.25% during half-size validation and 50%/0.5% during the full pilot.

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
- `results/stock_gallery/`: searchable atlas with one all-strategy image per stock
- `results/combination_rankings/`: complete stock × strategy leaderboard and compressed export
- `results/findings/`: compact committed snapshot and interpretation of the executed run

## Data provenance

Market data comes from [NSE's official daily report archive](https://www.nseindia.com/all-reports). UDiFF bhavcopies are used from 8 July 2024 onward and legacy CM bhavcopies before that date; NSE publishes the [UDiFF format resources here](https://www.nseindia.com/static/resources/forms-formats-members). The downloader caches each ZIP and records SHA-256 hashes in a manifest.
