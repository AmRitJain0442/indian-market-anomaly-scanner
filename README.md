# Indian Market Anomaly Scanner

A reproducible, exchange-wide scanner for daily anomalies in NSE cash equities. It downloads official NSE bhavcopies, constructs the historical universe from each session, evaluates every stock over the latest 252 completed sessions, applies trading costs, and publishes stock and strategy rankings.

The source brief is preserved in [`indian_market_anomaly_scanner_252d.md`](indian_market_anomaly_scanner_252d.md).

## EQ-only ranking for the INR 1,000 research budget

The [new screened rankings](results/findings/2026-09-05-eligibility-ranking/README.md) exclude both BE and BZ, check every historical entry and exit series, and separate current broker-list membership from profitability. The practical view adds a INR 500 unleveraged cash cap, a INR 5 illustrative planned-risk limit, liquidity and sample checks. It contains **667 pairs across 66 stocks** for one year and **497 pairs across 44 stocks** for ten years. The searchable pages include individual exclusion reasons and retain the existing color theme. Historical profit figures still refer to the original INR 100,000 theoretical account, not a validated INR 1,000 strategy.

## Execution review, 5 September 2026

The [SITINET execution review and INR 1,000 paper strategy](results/findings/2026-09-05-execution-review/README.md) identifies a critical limitation in the historical rankings. All 174 SITINET gap-fade trades occurred in BZ, where intraday trading is prohibited. VHLTD has the same problem in BE, and some stocks changed series during the study. Assumed opening and closing fills, full-capital compounding, and retrospective selection introduce further limitations. The review includes reproducible trade evidence and a proposed 30-session paper experiment. The original strategy engine and historical outputs have not yet been corrected.

The [local 20-session data audit](results/findings/2026-09-05-pilot20/README.md) covers 10 August through 4 September 2026. It finds eight opening-gap candidates and available minute candles, but not the historical quotes and permissions needed to establish the exact strategy's profit. The subsequently approved [one-minute approximation](results/findings/2026-09-05-pilot20-minute/README.md) starts with INR 1,000 and ends at INR 992.90, a modeled loss of INR 7.10 after estimated trading charges. Two trades filled and both hit their stops. This is not a validated live-trading result.

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

## Short-horizon predictions

The pipeline now produces pooled, leakage-safe research forecasts for the next 1, 3, and 5 consecutive NSE sessions. The implementation adapts the cross-sectional framework in Gu, Kelly, and Xiu's *Empirical Asset Pricing via Machine Learning* and validates each horizon with a time-ordered 60-session walk-forward test.

The current models have not demonstrated a reliable out-of-sample edge. Direction accuracy is about 51 percent and out-of-sample (R^2) is below zero. Forecasts and calibrated ranges remain visible as diagnostics, not recommendations.

Read [`FORECAST_METHOD.md`](FORECAST_METHOD.md) for the paper links, equations, predictor definitions, leakage controls, forecast-range calculation, and exact reproduction commands.

## Close-to-open strategy mathematics

The close-to-open strategy isolates the return earned while the market is closed. For one stock, the strategy buys at the closing price of trading session \(t\) and sells at the opening price of the next consecutive trading session \(t+1\).

```text
Session t close: buy
Overnight: hold the position
Session t+1 open: sell
Session t+1 intraday: hold cash
Session t+1 close: enter the next overnight trade
```

### Notation

For overnight trade \(t\):

- \(C_t\) is the stock's closing price on session \(t\)
- \(O_{t+1}\) is the stock's opening price on the next consecutive session
- \(b\) is the assumed one-way transaction cost in basis points
- \(V_{t-1}\) is the capital available immediately before the trade
- \(V_t\) is the capital after the trade and estimated costs

One basis point is \(0.01\%\). The baseline uses \(b=10\) basis points on entry and \(b=10\) basis points on exit.

### Gross return

The gross overnight return is:

$$
r^{\text{gross}}_t
= \frac{O_{t+1}}{C_t}-1
$$

An equivalent percentage form is:

$$
r^{\text{gross percentage}}_t
= \left(\frac{O_{t+1}-C_t}{C_t}\right)\times100
$$

If the next opening price is above the previous close, the long trade makes a gross profit. If it is below the previous close, the trade makes a gross loss.

### Estimated transaction costs

The backtest applies the same one-way cost to both sides of every active trade. The estimated round-trip cost rate is:

$$
c = \frac{2b}{10{,}000}
$$

At the baseline value of \(b=10\):

$$
c = \frac{2\times10}{10{,}000}=0.002=0.20\%
$$

The net return used by the backtest is:

$$
r^{\text{net}}_t
= r^{\text{gross}}_t-c
= \left(\frac{O_{t+1}}{C_t}-1\right)-\frac{2b}{10{,}000}
$$

This is a transparent research cost approximation. It does not separately calculate brokerage, STT, exchange charges, GST, stamp duty, bid-ask spread, market impact, or opening and closing price slippage.

### Full-capital reinvestment

The backtest compounds the entire available capital after every valid trade:

$$
V_t = V_{t-1}\left(1+r^{\text{net}}_t\right)
$$

After \(n\) overnight trades:

$$
V_n
= V_0\prod_{t=1}^{n}\left(1+r^{\text{net}}_t\right)
$$

Final net profit and total net return are:

$$
\text{Net PnL}=V_n-V_0
$$

$$
\text{Total net return}=\frac{V_n}{V_0}-1
$$

Each stock and strategy combination is compounded independently. The standard research rankings use \(V_0=\text{INR }100{,}000\) for every combination. A personal allocation of INR 10,000 uses the same return percentages with \(V_0=\text{INR }10{,}000\).

### INR 10,000 worked example

Assume:

```text
Initial capital             INR 10,000
Today's closing price       INR 100
Next session opening price  INR 102
One-way cost                10 basis points
```

The gross return is:

$$
r^{\text{gross}}
= \frac{102}{100}-1
= 0.02
= 2.00\%
$$

The net return after the modelled \(0.20\%\) round-trip cost is:

$$
r^{\text{net}}
= 2.00\%-0.20\%
= 1.80\%
$$

The capital after the trade is:

$$
V_1
= 10{,}000\times(1+0.018)
= \text{INR }10{,}180
$$

Therefore:

```text
Initial investment  INR 10,000
Gross profit        INR 200
Estimated costs     INR 20
Net profit          INR 180
Ending capital      INR 10,180
```

If the next valid trade earns a net return of \(1.00\%\), the strategy reinvests INR 10,180 rather than the original INR 10,000:

$$
V_2
= 10{,}180\times(1+0.01)
= \text{INR }10{,}281.80
$$

### What qualifies as a valid trade

The implementation records a trade only when the stock has both today's close and the next consecutive market session's open. The last observation has no known next open and is excluded. A gap in the stock's observations is not treated as an ordinary one-session overnight trade.

Detected corporate-action discontinuities are also excluded from the close-to-open return. This prevents a likely split, bonus issue, or similar mechanical price change from being counted as an exploitable overnight gain or loss.

The model uses the reported daily close and next open. Real orders may fill at different prices, and whole-share rounding can leave part of a small account uninvested. The reported results are historical research estimates rather than guaranteed executable returns.

## Complete stock × strategy visual atlas

After a research run, generate one atlas for every stock. Each image contains all 13 strategy curves, so the current findings produce 2,652 images covering 34,476 stock-strategy graphs:

```bash
python generate_stock_gallery.py
```

Open `results/stock_gallery/index.html` for the searchable gallery. Search by symbol, company, or ISIN. Filter for liquid or ≥95%-coverage securities. Navigate with the arrow keys and download any full-resolution WebP. The complete generated snapshot is also published in the [atlas-2026-08-27 GitHub release](https://github.com/AmRitJain0442/indian-market-anomaly-scanner/releases/tag/atlas-2026-08-27).

Both the 252-session and 10-year galleries include a **Glossary** tab and an **Insights from Amrit** tab. The guide defines strategies, money fields, chart elements, risk statistics, evidence labels, and data-quality flags in plain language. It also compares the leading strategies across both windows and provides a five-question decision lens before capital is considered.

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
