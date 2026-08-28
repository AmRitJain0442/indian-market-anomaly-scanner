# Indian Market Anomaly Scanner and 252-Day PnL Ranking

## Goal

Build a reproducible research system that:

1. Pulls **actual Indian cash-market data**.
2. Builds the universe of **every ordinary equity that was tradable during the test window**, rather than only the NIFTY 50 or today's surviving stocks.
3. Tests a library of market anomalies independently on **every stock**.
4. Uses the most recent **252 completed trading sessions** as the evaluation window.
5. Calculates a daily equity curve and PnL for each `stock × strategy`.
6. Includes trading-cost assumptions.
7. Saves the trades and metrics.
8. Plots cumulative PnL curves.
9. Ranks stocks primarily by **net PnL over the past 252 sessions** for each anomaly.
10. Produces cross-strategy leaderboards so we can see which effects, if any, actually appear in Indian equities.

The central output is not:

> "Does gap fade work on NIFTY?"

It is:

> "Across the complete Indian equity universe, which stocks showed the strongest close-to-open, gap-fade, reversal, momentum, calendar, volume, and intraday effects during the last 252 sessions?"

---

# 1. Market Scope

## Version 1: NSE Cash Equities

The first implementation should use the NSE cash-equity market.

Use official NSE files wherever practical:

- **Securities available for Equity segment**
- **CM-MII Security File**
- **CM-UDiFF Common Bhavcopy Final**
- **Security-wise Delivery Positions / Full Bhavcopy and Security Deliverable data**
- Corporate-action information when required
- NSE trading calendar / holiday information

Useful official pages:

```text
https://www.nseindia.com/static/market-data/securities-available-for-trading
https://www.nseindia.com/all-reports/
```

Do not manually maintain a list of stock symbols.

The system should derive the universe from exchange data.

---

# 2. What Does "Every Tradable Stock" Mean?

This needs a precise definition.

There are two possible universes.

## Universe A: Current tradable universe

Take every ordinary equity that is tradable on NSE today and backtest it over the previous 252 sessions.

This is easy, but it creates survivorship bias because stocks that disappeared from the exchange during the period are missing.

## Universe B: Historical tradable universe

For every trading date in the 252-session period:

1. Read that day's cash-market bhavcopy/security information.
2. Identify ordinary equities that were eligible/traded on that date.
3. Take the union of all such symbols over the period.

Then the universe is:

\[
U = \bigcup_{t=1}^{252} U_t
\]

where \(U_t\) is the equity universe on trading day \(t\).

This is the preferred design.

It naturally captures:

- Stocks that listed during the period.
- Stocks that delisted during the period.
- Stocks that were suspended for some sessions.
- Symbol changes.
- Securities that did not survive until today.

---

# 3. Instrument Filtering

Do not treat every NSE security as a stock.

The exchange also contains instruments such as:

- ETFs
- Mutual funds
- Preference shares
- Warrants
- REITs / InvITs
- Debt instruments
- IDRs
- SME securities
- Other special categories

The primary research universe should be:

```text
Ordinary listed cash equities
```

Create configuration flags:

```python
INCLUDE_MAINBOARD = True
INCLUDE_SME = False
INCLUDE_ETF = False
INCLUDE_REIT_INVIT = False
INCLUDE_PREF_SHARES = False
INCLUDE_WARRANTS = False
```

If the intention later becomes literally every listed share including SME securities, run them as a separate universe rather than mixing them with main-board equities.

The reason is liquidity and market microstructure are very different.

---

# 4. Do Not Throw Away Illiquid Stocks

Because the goal is to test **every tradable stock**, do not initially discard low-liquidity names.

Instead, calculate liquidity diagnostics and attach flags.

For each stock calculate:

```text
Median daily traded value
Median volume
Percentage of zero/near-zero volume sessions
Number of valid sessions
Average daily range
Number of upper/lower circuit-like sessions if identifiable
```

Then rank all stocks, but add:

```text
liquidity_flag
coverage_flag
new_listing_flag
suspension_flag
corporate_action_flag
```

This lets us distinguish:

> High PnL because an effect genuinely appeared

from:

> High PnL because the stock barely traded or had one abnormal event.

---

# 5. Test Window

The evaluation window is exactly:

```text
Last 252 completed NSE trading sessions
```

Do not use the last 252 calendar days.

The workflow should first determine the latest completed market session and then select the latest 252 valid trading dates.

Conceptually:

```python
evaluation_dates = all_trading_dates[-252:]
start_date = evaluation_dates[0]
end_date = evaluation_dates[-1]
```

---

# 6. Warm-Up History

Although PnL is evaluated only over 252 sessions, several signals need older data.

Examples:

| Feature | Approximate warm-up |
|---|---:|
| 20-day volume average | 20 sessions |
| 60-day delivery z-score | 60 sessions |
| 5-day reversal | 5 sessions |
| 3-month momentum | ~63 sessions |
| 6-month momentum | ~126 sessions |
| 52-week high | ~252 sessions |
| 12-month momentum | ~252 sessions |

Therefore:

```text
EVALUATION_WINDOW = 252
RAW_HISTORY_TARGET = 550 to 650 trading sessions
```

Download enough history first.

Then calculate all signals.

Finally evaluate only:

```text
last 252 trading sessions
```

This avoids losing the first part of the evaluation period to rolling-window NaNs.

---

# 7. Recommended Raw Data Architecture

Do not download one ticker at a time if exchange-wide bhavcopy data is available.

That will be unnecessarily slow and fragile.

Preferred architecture:

```text
One exchange file per trading day
        ↓
Parse all equities in that file
        ↓
Append to master dataset
```

For 252 evaluation sessions plus warm-up:

```text
~550 daily market files
```

Each file contains prices for a large fraction of the market.

That is much more suitable for an exchange-wide study.

---

# 8. Raw Dataset

Create one normalized table:

```text
date
symbol
isin
series
open
high
low
close
last_price
previous_close
volume
traded_value
number_of_trades
delivery_quantity
delivery_percentage
instrument_type
```

Not every source will provide every column.

Minimum requirement:

```text
date
symbol
open
high
low
close
volume
```

---

# 9. Storage Format

Do not repeatedly parse hundreds of ZIP/CSV files every time a strategy runs.

After downloading and cleaning, save a master columnar dataset:

```text
data/processed/equity_daily.parquet
```

Recommended partitioning:

```text
data/processed/daily/
    year=2025/
    year=2026/
```

or simply one Parquet file if the data remains manageable.

Parquet is preferable to CSV because:

- Faster reads.
- Smaller files.
- Preserves types.
- Better for repeated stock/strategy scans.

---

# 10. Suggested Project Structure

```text
indian-market-anomalies/
│
├── README.md
├── requirements.txt
├── config.py
│
├── data/
│   ├── raw/
│   │   ├── bhavcopy/
│   │   ├── security_master/
│   │   ├── delivery/
│   │   ├── holidays/
│   │   └── corporate_actions/
│   ├── processed/
│   │   ├── equity_daily.parquet
│   │   ├── security_master.parquet
│   │   └── trading_calendar.parquet
│   └── cache/
│
├── src/
│   ├── data/
│   │   ├── nse_downloader.py
│   │   ├── bhavcopy_parser.py
│   │   ├── universe.py
│   │   ├── calendar.py
│   │   ├── corporate_actions.py
│   │   └── validate.py
│   ├── features/
│   │   ├── returns.py
│   │   ├── volume.py
│   │   ├── liquidity.py
│   │   └── calendar_features.py
│   ├── strategies/
│   │   ├── close_to_open.py
│   │   ├── open_to_close.py
│   │   ├── gap_fade.py
│   │   ├── gap_continuation.py
│   │   ├── reversal_1d.py
│   │   ├── momentum_1d.py
│   │   ├── reversal_5d.py
│   │   ├── momentum_5d.py
│   │   ├── turn_of_month.py
│   │   ├── weekday.py
│   │   ├── volume_shock.py
│   │   └── delivery_shock.py
│   ├── backtest/
│   │   ├── engine.py
│   │   ├── costs.py
│   │   ├── metrics.py
│   │   └── ranking.py
│   ├── intraday/
│   │   ├── loader.py
│   │   └── strategies.py
│   └── plotting/
│       ├── equity.py
│       ├── drawdown.py
│       ├── rankings.py
│       └── diagnostics.py
│
├── notebooks/
│   ├── 01_build_market_dataset.ipynb
│   ├── 02_validate_data.ipynb
│   ├── 03_run_daily_anomalies.ipynb
│   ├── 04_rank_stocks.ipynb
│   └── 05_analyze_results.ipynb
│
└── results/
    ├── rankings/
    ├── strategy_results/
    ├── stock_results/
    ├── trades/
    ├── equity_curves/
    └── figures/
```

---

# 11. Data Validation Before Backtesting

Never trust downloaded market data blindly.

For every `date × symbol` validate:

```python
high >= max(open, close)
low <= min(open, close)
high >= low
open > 0
high > 0
low > 0
close > 0
volume >= 0
```

Check duplicate rows:

```python
df.duplicated(["date", "symbol"]).sum()
```

Check date ordering:

```python
df = df.sort_values(["symbol", "date"])
```

Check extreme returns:

```python
df["cc_return"] = (
    df.groupby("symbol")["close"]
      .pct_change()
)
```

Flag moves such as:

```text
|return| > 30%
```

for manual/corporate-action validation.

Do not automatically delete them.

---

# 12. Corporate Actions

This is critical for an all-stock scan.

Stocks can undergo:

- Splits.
- Bonus issues.
- Rights issues.
- Demergers.
- Dividends.
- Mergers.
- Symbol changes.

A split can look like a catastrophic overnight return in raw OHLC data.

Therefore create:

```text
corporate_action_flag = True / False
```

for affected sessions.

For execution-price strategies such as close-to-open, raw prices are conceptually correct, but mechanical corporate-action changes must not be interpreted as an exploitable anomaly.

At minimum:

1. Detect extreme discontinuities.
2. Cross-check corporate actions.
3. Either correctly adjust the event or exclude that observation from anomaly statistics.

Never let a 1:5 split become the highest-PnL "gap strategy" result.

---

# 13. Symbol Changes

Do not rely only on ticker text as the permanent identifier.

Prefer:

```text
ISIN
```

as the security identity where possible.

Store:

```text
isin
symbol
date
```

This lets the same company remain one security through ticker/name changes.

---

# 14. Daily Return Features

For every symbol, sort by date and calculate:

## Previous close

```python
g = df.groupby("symbol")
df["prev_close"] = g["close"].shift(1)
```

## Overnight return

\[
R^{ON}_t =
\frac{O_t}{C_{t-1}} - 1
\]

```python
df["ret_overnight"] = (
    df["open"] / df["prev_close"] - 1
)
```

## Intraday return

\[
R^{ID}_t =
\frac{C_t}{O_t} - 1
\]

```python
df["ret_intraday"] = (
    df["close"] / df["open"] - 1
)
```

## Close-to-close

\[
R^{CC}_t =
\frac{C_t}{C_{t-1}} - 1
\]

```python
df["ret_cc"] = (
    df["close"] / df["prev_close"] - 1
)
```

## Daily range

```python
df["range_pct"] = (
    (df["high"] - df["low"]) / df["open"]
)
```

## 5-day return

```python
df["ret_5d"] = (
    df["close"] /
    g["close"].shift(5) - 1
)
```

## Volume ratio

```python
df["volume_ma20"] = (
    g["volume"]
    .transform(lambda x: x.rolling(20).mean())
)

df["volume_ratio"] = (
    df["volume"] / df["volume_ma20"]
)
```

---

# 15. Backtest Unit

The fundamental object is:

```text
one stock
×
one strategy
×
252 evaluation sessions
```

For example:

```text
RELIANCE × CloseToOpen
RELIANCE × GapFade
RELIANCE × 1DReversal

TCS × CloseToOpen
TCS × GapFade
TCS × 1DReversal

...

Every stock × Every strategy
```

---

# 16. Same Initial Capital for Every Stock

PnL ranking is meaningless unless each stock starts with the same capital.

Set:

```python
INITIAL_CAPITAL = 100_000
```

Every `stock × strategy` starts with:

```text
₹100,000
```

This means:

```text
Stock A final equity = ₹118,000
Net PnL = ₹18,000

Stock B final equity = ₹108,000
Net PnL = ₹8,000
```

Stock A ranks above Stock B for that strategy.

---

# 17. Position Sizing

For the first research version use:

```text
100% notional exposure whenever a signal exists
0% exposure when there is no signal
```

This makes cross-stock PnL comparable.

The strategy daily return is sufficient:

\[
V_{t+1}
=
V_t (1+r_t)
\]

No need to model integer share quantities in the first anomaly-discovery stage.

Later, execution simulation can convert capital into whole shares.

---

# 18. Gross PnL

For a strategy return series \(r_t\):

```python
equity_gross = (
    INITIAL_CAPITAL
    * (1 + gross_returns.fillna(0)).cumprod()
)
```

Then:

```python
gross_pnl = (
    equity_gross.iloc[-1]
    - INITIAL_CAPITAL
)
```

---

# 19. Net PnL After Costs

Every trade should pay costs.

Start with a configurable basis-point model:

```python
ONE_WAY_COST_BPS = 10
```

For a round-trip trade:

```python
round_trip_cost = (
    2 * ONE_WAY_COST_BPS / 10_000
)
```

Then:

```python
net_return = (
    gross_return - round_trip_cost
)
```

This is only a research approximation.

The cost engine should later support:

```text
brokerage
STT
exchange charges
GST
SEBI charges
stamp duty
bid-ask spread
slippage
```

Because those costs are not symmetric across every transaction type.

Always save:

```text
gross_pnl
net_pnl
```

The primary ranking should use:

```text
net_pnl
```

not gross PnL.

---

# 20. Cost Sensitivity

For every strategy run:

```text
0 bps
5 bps
10 bps
20 bps
30 bps
```

Save:

```text
pnl_0bps
pnl_5bps
pnl_10bps
pnl_20bps
pnl_30bps
```

This is especially important for:

- Gap strategies.
- One-day reversal.
- One-day momentum.
- Opening-range strategies.
- High-turnover anomalies.

If a strategy disappears at 5–10 bps, that is important information.

---

# 21. Strategy 1: Close → Next Open

## Question

Does holding this stock only overnight outperform holding it during the session?

## Trade

```text
Entry: Close on day t
Exit: Open on day t+1
Direction: Long
```

Return:

\[
r_t =
\frac{O_{t+1}}{C_t} - 1
\]

Implementation:

```python
df["next_open"] = (
    df.groupby("symbol")["open"].shift(-1)
)

df["strategy_return"] = (
    df["next_open"] / df["close"] - 1
)
```

Remove the final unavailable exit.

For every stock calculate:

```text
252-day gross PnL
252-day net PnL
Sharpe
Max drawdown
Win rate
Number of trades
Average overnight return
Median overnight return
```

Then rank all stocks:

```text
Rank 1 = highest net PnL
Rank N = lowest net PnL
```

---

# 22. Strategy 2: Open → Close

## Trade

```text
Buy at open
Sell at close
```

Return:

\[
r_t =
\frac{C_t}{O_t} - 1
\]

This should be tested on every stock.

Then compare:

```text
Close→Open PnL
versus
Open→Close PnL
```

A useful derived metric:

\[
OvernightDominance =
PnL_{close\to open}
-
PnL_{open\to close}
\]

Rank stocks by this as a secondary study.

---

# 23. Strategy 3: Gap Fade

Define:

\[
Gap_t =
\frac{O_t}{C_{t-1}} - 1
\]

For threshold \(x\):

```text
Gap > +x → short open to close
Gap < -x → long open to close
Otherwise → no trade
```

Test:

```text
0.25%
0.50%
0.75%
1.00%
1.50%
2.00%
```

For each threshold create a separate result.

Do not select the best threshold using the same sample and call it predictive.

Save threshold-level ranking:

```text
gap_fade_025
gap_fade_050
gap_fade_075
gap_fade_100
gap_fade_150
gap_fade_200
```

---

# 24. Strategy 4: Gap Continuation

Exact opposite.

```text
Gap > +x → long open to close
Gap < -x → short open to close
```

Run on exactly the same threshold grid.

This tells us whether each stock historically behaved as:

```text
gap-fading
or
gap-following
```

---

# 25. Gap Behaviour Score

For each stock:

```python
gap_behavior_score = (
    gap_continuation_net_pnl
    - gap_fade_net_pnl
)
```

Interpretation:

```text
Large positive → continuation dominated
Large negative → fading dominated
Near zero → no clear structure
```

This score can itself be ranked.

---

# 26. Strategy 5: Previous-Day Reversal

Calculate previous daily close-to-close return.

Example threshold:

```text
Yesterday > +2% → short today's open → close
Yesterday < -2% → long today's open → close
```

Test:

```text
1%
2%
3%
4%
5%
```

This tests whether large daily moves reverse.

---

# 27. Strategy 6: Previous-Day Momentum

Exact opposite:

```text
Yesterday > +2% → long today's open → close
Yesterday < -2% → short today's open → close
```

Compare:

```text
reversal PnL
vs
momentum PnL
```

for every stock.

---

# 28. Strategy 7: 5-Day Reversal

Calculate:

\[
R_{5,t} =
\frac{C_t}{C_{t-5}} - 1
\]

Example:

```text
Large positive five-day move → short
Large negative five-day move → long
```

Entry:

```text
next session open
```

Exit initially:

```text
same session close
```

Later test:

```text
1-day hold
3-day hold
5-day hold
```

---

# 29. Strategy 8: 5-Day Momentum

Opposite of 5-day reversal.

```text
Recent winners → long
Recent losers → short
```

Again calculate separate stock rankings.

---

# 30. Strategy 9: Day-of-Week Effect

For each stock calculate separate strategies:

```text
Long only Monday
Long only Tuesday
Long only Wednesday
Long only Thursday
Long only Friday
```

Test both:

```text
Open → Close
Close → Next Open
```

This gives ten simple calendar-return decompositions per stock.

Because a one-year window contains only roughly 50 observations per weekday, treat this primarily as exploratory.

---

# 31. Strategy 10: Weekend Effect

Compare:

```text
Friday Close → Monday Open
```

against ordinary one-session overnight returns.

For every stock calculate:

```text
weekend_mean_return
ordinary_overnight_mean_return
difference
weekend_pnl
```

---

# 32. Strategy 11: Turn-of-the-Month

Mark:

```text
Last 3 trading sessions of each month
First 3 trading sessions of next month
```

Strategy:

```text
Long during turn-of-month window
Cash otherwise
```

Test:

```text
[-1,+1]
[-2,+2]
[-3,+3]
```

Run independently on every stock.

---

# 33. Strategy 12: Volume-Shock Continuation

Calculate:

```python
volume_ratio = (
    volume /
    rolling_20_day_mean_volume
)
```

Signal example:

```text
Volume ratio >= 2
AND daily return > threshold
    → long next session

Volume ratio >= 2
AND daily return < -threshold
    → short next session
```

Test a small predefined grid:

```text
Volume ratio:
1.5x
2.0x
2.5x
3.0x

Price move:
1%
2%
3%
5%
```

Do not exhaustively data-mine hundreds of parameter combinations in the first run.

---

# 34. Strategy 13: Volume-Shock Reversal

Exact opposite.

```text
High-volume positive move → short next session
High-volume negative move → long next session
```

Compare stock-level continuation vs reversal.

---

# 35. Strategy 14: Delivery-Volume Continuation

Once NSE delivery data is included:

```python
delivery_pct = (
    delivery_quantity /
    traded_quantity
)
```

Build a rolling delivery z-score:

```python
delivery_z = (
    delivery_pct
    - rolling_mean
) / rolling_std
```

Potential signal:

```text
Large price move
+ volume shock
+ high delivery z-score
```

Test whether it continues the following session.

---

# 36. Strategy 15: Delivery-Volume Reversal

Run the opposite direction.

This allows us to answer:

> Does unusually high delivery participation make high-volume price moves more persistent?

---

# 37. Cross-Sectional Strategies

In addition to stock-by-stock ranking, the same dataset can answer a different question:

> If I must choose stocks each day, which recent winners/losers should I buy?

Example:

1. Rank all tradable stocks by yesterday's return.
2. Long bottom decile.
3. Short top decile.
4. Equal weight.
5. Hold one session.

This is different from the primary stock-ranking project.

Keep cross-sectional portfolio results in a separate folder.

---

# 38. Intraday Phase

Daily exchange data will support the first large research pass.

After that, add intraday OHLCV data to test:

```text
09:15–09:30 reversal
09:15–09:30 continuation
First-hour breakout
First-hour reversal
Last-hour momentum
Last-hour reversal
Close momentum → next open
Expiry-session intraday behaviour
```

Because downloading 5-minute data for every stock is significantly heavier, do this only after the daily engine works.

A useful approach is:

1. Use daily data on the entire market.
2. Identify the most interesting stocks/anomalies.
3. Pull intraday history for the shortlisted subsets.
4. Test microstructure hypotheses more precisely.

---

# 39. Required Trade Table

Every executed signal should generate a row:

```text
strategy
symbol
isin
signal_date
entry_datetime
entry_price
exit_datetime
exit_price
side
gross_return
estimated_cost
net_return
capital_before
pnl
capital_after
```

Save efficiently as partitioned Parquet, for example by:

```text
strategy
symbol
```

---

# 40. Required Stock × Strategy Summary

One row per:

```text
symbol × strategy × parameter_set
```

Columns:

```text
symbol
isin
company_name
strategy
parameters
evaluation_start
evaluation_end
sessions_available
coverage_ratio
number_of_signals
number_of_trades
gross_pnl
net_pnl
gross_return_pct
net_return_pct
annualized_volatility
sharpe
sortino
max_drawdown
win_rate
average_trade_return
median_trade_return
profit_factor
best_trade
worst_trade
exposure_pct
turnover
t_stat
p_value
median_daily_value
liquidity_flag
corporate_action_observations
```

Save:

```text
results/strategy_results/all_stock_strategy_results.parquet
results/strategy_results/all_stock_strategy_results.csv
```

---

# 41. Primary Ranking Rule

The requested ranking is:

> Rank every stock on the basis of PnL over the past 252 trading days.

Therefore, for each strategy:

```python
ranking = (
    results[
        results["strategy"] == strategy
    ]
    .sort_values(
        "net_pnl",
        ascending=False
    )
)
```

Assign:

```python
ranking["pnl_rank"] = (
    ranking["net_pnl"]
    .rank(
        method="min",
        ascending=False
    )
)
```

Primary order:

```text
1. Net PnL
```

Secondary columns shown next to it:

```text
2. Net return %
3. Sharpe
4. Max drawdown
5. Number of trades
6. Win rate
7. Coverage
8. Liquidity
```

Do not change the requested ranking into a Sharpe ranking.

PnL remains the primary rank.

---

# 42. Example Leaderboard

For `close_to_open`:

| PnL Rank | Symbol | Net PnL | Net Return | Sharpe | Max DD | Trades | Win Rate | Coverage |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | STOCK_A | ₹... | ...% | ... | ...% | ... | ...% | ...% |
| 2 | STOCK_B | ₹... | ...% | ... | ...% | ... | ...% | ...% |
| 3 | STOCK_C | ₹... | ...% | ... | ...% | ... | ...% | ...% |

Repeat for every strategy.

---

# 43. Ranking Directory

Create:

```text
results/rankings/
│
├── close_to_open.csv
├── open_to_close.csv
├── gap_fade_050.csv
├── gap_fade_100.csv
├── gap_continuation_050.csv
├── gap_continuation_100.csv
├── reversal_1d.csv
├── momentum_1d.csv
├── reversal_5d.csv
├── momentum_5d.csv
├── turn_of_month.csv
├── volume_continuation.csv
└── volume_reversal.csv
```

Each CSV should contain **every stock**, not only the winners.

---

# 44. Strict Comparison Ranking vs All-Stock Ranking

A newly listed stock may have only 40 sessions while an older stock has all 252.

Still include it because the stated goal is every tradable stock.

But publish two ranking views.

## A. All-stock ranking

Includes every stock with at least one valid strategy trade.

Columns include:

```text
sessions_available
coverage_ratio
```

## B. Comparable-history ranking

Example requirement:

```python
coverage_ratio >= 0.95
```

or:

```text
at least 240 of 252 sessions
```

This prevents a newly listed stock from being directly compared with a stock that has a full year of history without context.

Do not delete partial-history stocks.

Flag them.

---

# 45. Absolute PnL vs Percentage Return

Because every stock receives the same starting capital:

\[
PnL = V_T - V_0
\]

and:

\[
Return =
\frac{PnL}{V_0}
\]

the two rankings will be identical under the initial fractional-notional model.

Still save both because later:

- integer shares,
- position limits,
- liquidity limits,
- slippage,

may make them diverge.

---

# 46. Metrics

Calculate at minimum:

## Net PnL

\[
PnL = V_T - V_0
\]

## Total return

\[
R =
\frac{V_T}{V_0} - 1
\]

## Annualized volatility

\[
\sigma_{ann}
=
\sigma_{daily}\sqrt{252}
\]

## Sharpe

\[
Sharpe =
\frac{\bar r}{\sigma_r}\sqrt{252}
\]

## Maximum drawdown

```python
running_max = equity.cummax()
drawdown = equity / running_max - 1
max_drawdown = drawdown.min()
```

## Win rate

```python
win_rate = (
    trade_returns > 0
).mean()
```

## Profit factor

\[
PF =
\frac{\sum positive\ PnL}
{|\sum negative\ PnL|}
\]

## Exposure

```text
percentage of evaluation sessions with an active position
```

---

# 47. Statistical Diagnostics

For every stock-strategy pair calculate:

```text
N trades
Mean trade return
Median trade return
Standard deviation
Standard error
t-statistic
p-value
95% confidence interval
```

However, do **not** interpret `p < 0.05` naively.

If we test:

```text
2,000 stocks × 15 strategies × multiple parameters
```

we are conducting tens of thousands of statistical tests.

Some "significant" results will appear purely by chance.

Therefore later add multiple-testing corrections such as:

```text
Benjamini-Hochberg false discovery rate
```

and/or perform out-of-sample validation.

---

# 48. Multiple-Testing Problem

This project is particularly vulnerable to data mining.

Suppose:

```text
2,000 stocks
× 20 strategy variants
= 40,000 tests
```

At a 5% significance threshold, random data alone can produce many apparently significant observations.

Therefore the leaderboard is:

```text
a discovery tool
```

not proof of a durable trading edge.

The correct workflow is:

```text
252-day discovery
        ↓
find strongest / most consistent anomalies
        ↓
freeze the strategy definition
        ↓
test on older unseen periods
        ↓
walk-forward test
        ↓
paper execution
```

---

# 49. PnL Curve for Every Stock

For every stock-strategy pair save its daily equity curve.

Schema:

```text
date
symbol
strategy
signal
gross_return
net_return
gross_equity
net_equity
drawdown
```

Store efficiently in Parquet.

Do not generate thousands of PNGs by default.

Instead:

1. Save all curves as data.
2. Generate figures for:
   - Top 20 stocks.
   - Bottom 20 stocks.
   - User-selected stock.
   - Median-performing stock.
   - Aggregate strategy statistics.

---

# 50. Required Plot 1: Top-N PnL Curves

For each strategy plot the top:

```text
10 or 20 stocks by net PnL
```

Normalize each to:

```text
₹100,000
```

Title:

```text
Close → Open: Top 20 Stocks by 252-Day Net PnL
```

---

# 51. Required Plot 2: Bottom-N PnL Curves

Plot the worst 10/20.

This is important.

If the effect is structural, we want to know whether it appears broadly or only in a handful of names.

---

# 52. Required Plot 3: PnL Ranking Bar Chart

For each strategy:

```text
stock symbol
vs
net PnL
```

Plot top 30 and bottom 30 separately.

Do not try to put ~2,000 stock labels on one chart.

---

# 53. Required Plot 4: Distribution Across Stocks

Histogram:

```text
x = stock 252-day net PnL
y = number of stocks
```

Add:

```text
median PnL
mean PnL
zero line
```

This is one of the most useful graphs.

It answers:

> Is the anomaly broadly positive across the market, or driven by a tiny number of stocks?

---

# 54. Required Plot 5: Percentage of Stocks Profitable

For every strategy calculate:

```python
pct_profitable = (
    results["net_pnl"] > 0
).mean()
```

This is often more informative than the best individual PnL.

---

# 55. Required Plot 6: Median / Equal-Weight Market Equity

Construct the strategy return across stocks using either:

```text
median stock daily return
```

or an equal-weight universe portfolio.

This answers whether the anomaly exists at the market level rather than only in selected stocks.

---

# 56. Required Plot 7: Gross vs Net

For top-ranked stocks show:

```text
Gross equity curve
Net equity curve after assumed costs
```

If the two diverge massively, the anomaly is turnover-driven and potentially unusable.

---

# 57. Required Plot 8: Drawdown

For every displayed top stock:

```python
drawdown = (
    equity / equity.cummax() - 1
)
```

Plot drawdown separately.

---

# 58. Required Plot 9: PnL vs Number of Trades

Scatter:

```text
x = number of trades
y = net PnL
```

This identifies stocks ranked highly because of only one or two lucky observations.

---

# 59. Required Plot 10: PnL vs Liquidity

Scatter:

```text
x = log(median daily traded value)
y = net PnL
```

This tells us whether apparent profitability is concentrated in illiquid names.

---

# 60. Strategy-Level Breadth Metrics

For each strategy calculate:

```text
Number of stocks tested
Number profitable
Percentage profitable
Median net PnL
Mean net PnL
25th percentile
75th percentile
90th percentile
10th percentile
Median Sharpe
Median drawdown
```

Example summary:

| Strategy | Stocks | % Profitable | Median PnL | Mean PnL | Median Sharpe |
|---|---:|---:|---:|---:|---:|
| Close→Open | | | | | |
| Open→Close | | | | | |
| Gap Fade | | | | | |
| Gap Continue | | | | | |

---

# 61. Strategy Ranking

We also want to rank the anomalies themselves.

Do **not** rank strategies by the single best stock.

Instead use market-wide statistics such as:

```text
Median stock net PnL
Percentage of stocks profitable
Equal-weight strategy PnL
Median Sharpe
Cost survival
```

A phenomenon is much more interesting if:

```text
65% of the universe shows it
```

than if:

```text
3 stocks make extraordinary PnL
and 1,900 do nothing.
```

---

# 62. Market-Wide Equal-Weight Strategy

For each date and strategy:

1. Calculate each stock's strategy return.
2. Take the equal-weight average across eligible stocks.

\[
R_{EW,t}
=
\frac{1}{N_t}
\sum_{i=1}^{N_t} R_{i,t}
\]

Then:

```python
market_equity = (
    INITIAL_CAPITAL
    * (1 + ew_returns).cumprod()
)
```

This gives a clean measure of whether the anomaly exists across the market.

---

# 63. Ranking Function

```python
def rank_strategy(
    results,
    strategy_name
):
    x = (
        results[
            results["strategy"] == strategy_name
        ]
        .copy()
    )

    x = x.sort_values(
        "net_pnl",
        ascending=False
    )

    x["pnl_rank"] = range(
        1,
        len(x) + 1
    )

    return x
```

---

# 64. Metrics Function

```python
import numpy as np

def calculate_metrics(
    returns,
    initial_capital=100_000
):
    returns = returns.dropna()

    equity = (
        initial_capital
        * (1 + returns).cumprod()
    )

    pnl = (
        equity.iloc[-1] - initial_capital
        if len(equity)
        else 0
    )

    total_return = (
        equity.iloc[-1] / initial_capital - 1
        if len(equity)
        else 0
    )

    vol = returns.std()

    sharpe = (
        returns.mean() / vol * np.sqrt(252)
        if vol > 0
        else np.nan
    )

    running_max = equity.cummax()

    drawdown = (
        equity / running_max - 1
    )

    max_dd = (
        drawdown.min()
        if len(drawdown)
        else np.nan
    )

    active = returns[returns != 0]

    win_rate = (
        (active > 0).mean()
        if len(active)
        else np.nan
    )

    return {
        "net_pnl": pnl,
        "net_return_pct": total_return,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "number_of_trades": len(active),
        "win_rate": win_rate
    }
```

---

# 65. Universe-Wide Execution Pattern

Avoid slow nested Python loops where possible.

Conceptually:

```python
for strategy in strategies:
    strategy_returns = strategy.generate(
        market_data
    )

    metrics = (
        strategy_returns
        .groupby("symbol")
        .apply(calculate_metrics)
    )

    save_results(metrics)
```

For a few thousand securities and ~600 daily observations, vectorized pandas/Polars operations should be manageable.

If performance becomes an issue:

```text
Polars
DuckDB
PyArrow
```

are natural upgrades.

---

# 66. Suggested Strategy Interface

```python
class Strategy:
    name: str

    def generate_returns(
        self,
        df
    ):
        """
        Input:
            Normalized market DataFrame

        Output columns:
            date
            symbol
            signal
            gross_return
            net_return
        """
        raise NotImplementedError
```

Each strategy should contain signal logic only.

The common backtest engine handles:

```text
capital
costs
metrics
ranking
plotting
saving
```

This prevents duplicated logic.

---

# 67. Avoid Look-Ahead Bias

For every signal ask:

> At the assumed entry time, would I actually know this value?

Examples:

### Valid

Yesterday's close used to trade today's open.

### Invalid

Today's close used to decide a trade supposedly entered at today's open.

### Valid

09:15–09:30 return used for a 09:35 entry.

### Invalid

Entire day's high used to claim an entry at 10:00.

Use `.shift()` deliberately.

---

# 68. Do Not Use Same-Candle Breakout Prices

Suppose a 5-minute candle has:

```text
Open = 100
High = 105
Close = 104
```

If a strategy triggers when price crosses 104, do not assume entry at the candle's open of 100.

The signal did not exist then.

Use:

```text
next candle open
```

or a realistic trigger/slippage model.

---

# 69. Suspensions and Missing Sessions

A stock may not trade every market session.

Never forward-fill prices to create artificial trades.

Bad:

```python
stock_df["close"] = (
    stock_df["close"].ffill()
)
```

for backtesting.

Instead:

```text
No valid market price
→ no trade
→ preserve missing-session flag
```

Coverage should be explicitly reported.

---

# 70. Limit/Circuit Behaviour

Some Indian equities can remain near price bands with little/no executable liquidity.

A daily OHLC backtest can falsely assume easy execution at a theoretical open or close.

Flag stocks with suspicious patterns such as:

```text
open == high == low == close
```

combined with:

```text
very low volume
```

Do not necessarily exclude them from the raw leaderboard, but show the liquidity/execution warning.

---

# 71. Short-Selling Constraint

Some research strategies require overnight or multi-day shorts.

A theoretical stock-level short PnL does not automatically mean the strategy is executable as a cash-equity trade.

Classify every strategy:

```text
LONG_ONLY
INTRADAY_SHORT_ALLOWED_RESEARCH
OVERNIGHT_SHORT_RESEARCH_ONLY
DERIVATIVE_IMPLEMENTABLE
```

The anomaly study can still calculate theoretical short returns.

Just keep:

```text
research result
```

separate from:

```text
executable trading implementation
```

---

# 72. Benchmarking

For each stock, also calculate buy-and-hold over the same available evaluation interval.

Then store:

```text
strategy_net_pnl
buy_hold_pnl
excess_pnl
```

For example:

\[
ExcessPnL =
PnL_{strategy}
-
PnL_{buyhold}
\]

This helps distinguish:

> Strategy made money

from:

> The stock simply went up massively all year.

---

# 73. Stock-Level Plots

When a user selects a symbol, generate:

```text
1. Price chart
2. Strategy signals on price
3. Gross equity
4. Net equity
5. Buy-and-hold equity
6. Drawdown
7. Trade return histogram
8. Monthly PnL
```

This turns the leaderboard into an inspectable research tool.

---

# 74. Monthly Stability

For every stock-strategy:

```python
monthly_returns = (
    daily_returns
    .resample("ME")
    .apply(
        lambda x:
        (1 + x).prod() - 1
    )
)
```

Store:

```text
positive_months
negative_months
best_month
worst_month
monthly_return_std
```

A stock earning all of its PnL in one month should not look as robust as one earning steadily.

---

# 75. Rolling PnL

Calculate rolling:

```text
21-session PnL
63-session PnL
126-session PnL
```

This can reveal whether the anomaly:

```text
worked throughout the year
```

or:

```text
worked only during one regime
```

---

# 76. Market Regime Labels

Optional later.

Label each day by NIFTY state:

```text
Market up/down
High/low volatility
Above/below 50-day moving average
```

Then calculate stock anomaly PnL conditional on regime.

Do this only after the base study is complete.

---

# 77. Recommended First Full-Market Strategy Set

Do not start with 25 complicated strategies.

First run these across the entire universe:

```text
1. Close → Next Open
2. Open → Close
3. Gap Fade, 0.5%
4. Gap Fade, 1.0%
5. Gap Continuation, 0.5%
6. Gap Continuation, 1.0%
7. Previous-Day Reversal, 2%
8. Previous-Day Momentum, 2%
9. 5-Day Reversal
10. 5-Day Momentum
11. Turn-of-Month
12. Volume-Shock Continuation
13. Volume-Shock Reversal
```

These can mostly be implemented from daily OHLCV.

Once the pipeline is correct, add:

```text
delivery
earnings
bulk/block deals
expiry
intraday
index inclusion
```

---

# 78. Master Output

At the end of one run, generate:

```text
results/
│
├── run_metadata.json
├── market_summary.csv
├── strategy_results/
│   ├── all_stock_strategy_results.parquet
│   └── all_stock_strategy_results.csv
├── rankings/
│   ├── close_to_open.csv
│   ├── open_to_close.csv
│   ├── gap_fade_050.csv
│   ├── gap_fade_100.csv
│   ├── gap_continuation_050.csv
│   ├── gap_continuation_100.csv
│   ├── reversal_1d.csv
│   ├── momentum_1d.csv
│   ├── reversal_5d.csv
│   ├── momentum_5d.csv
│   ├── turn_of_month.csv
│   ├── volume_continuation.csv
│   └── volume_reversal.csv
├── equity_curves/
│   └── ...
├── trades/
│   └── ...
└── figures/
    ├── close_to_open_top20.png
    ├── close_to_open_distribution.png
    ├── gap_fade_top20.png
    ├── gap_fade_distribution.png
    ├── strategy_breadth.png
    ├── pnl_vs_liquidity.png
    └── ...
```

---

# 79. Run Metadata

Every experiment must save enough information to reproduce it.

Example:

```json
{
  "evaluation_sessions": 252,
  "evaluation_start": "...",
  "evaluation_end": "...",
  "initial_capital": 100000,
  "cost_model": "...",
  "universe_definition": "historical NSE ordinary equities",
  "include_sme": false,
  "number_of_symbols": 0,
  "data_source": "NSE",
  "strategies": []
}
```

---

# 80. Final Research Dashboard/Table

The main result should have two levels.

## Level 1: Strategy overview

| Strategy | Stocks Tested | % Profitable | Median PnL | Mean PnL | Equal-Weight PnL | Median Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| Close→Open | | | | | | |
| Open→Close | | | | | | |
| Gap Fade | | | | | | |
| Gap Continue | | | | | | |
| 1D Reversal | | | | | | |
| 1D Momentum | | | | | | |

## Level 2: Stock ranking

Select a strategy and show every stock:

| Rank | Symbol | Net PnL | Return | Sharpe | Max DD | Trades | Win Rate | Sessions | Liquidity |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | | | | | | | | | |
| 2 | | | | | | | | | |
| ... | | | | | | | | | |

---

# 81. Core Questions the Research Should Answer

At the end, we should be able to answer:

### Overnight anomaly

```text
What percentage of Indian stocks made more money
close→open than open→close?
```

### Stock ranking

```text
Which stocks had the highest 252-day net PnL
for close→open?
```

### Gap behaviour

```text
Which stocks consistently faded opening gaps?
Which consistently continued them?
```

### Reversal vs momentum

```text
For each stock, did short-term reversal
or continuation dominate?
```

### Breadth

```text
Did an anomaly work across hundreds of stocks,
or only in a few outliers?
```

### Stability

```text
Was PnL distributed through the year,
or generated in one isolated period?
```

### Liquidity

```text
Does apparent profitability survive after
restricting attention to liquid stocks?
```

### Costs

```text
Which effects survive 5, 10, 20 and 30 bps
of assumed round-trip friction?
```

---

# 82. Important Interpretation Rule

The top of the leaderboard is **not automatically a trading strategy**.

If we search thousands of securities after seeing the outcomes and pick:

```text
the stock with the highest 252-day historical PnL
```

we have performed selection on past performance.

That result is useful for discovering patterns, but it is not enough to establish predictability.

The next test must be:

```text
Did a stock that ranked highly in one historical window
continue showing the same anomaly in the next unseen window?
```

That becomes the second stage of the project.

---

# 83. Stage 2: Persistence Test

Once the 252-day scanner works, split longer history into windows:

```text
Window 1: 252 sessions
Window 2: next 63 sessions
Window 3: next 63 sessions
...
```

At the end of Window 1:

1. Rank every stock by anomaly PnL.
2. Freeze the ranking.
3. Trade/test the top names in Window 2.
4. Measure whether rank predicts future anomaly PnL.

This is much more informative than simply asking which stocks had the best historical backtest.

---

# 84. Rank Persistence

Calculate:

\[
Corr(
Rank_{t},
PnL_{t+1}
)
\]

or use Spearman rank correlation:

```python
from scipy.stats import spearmanr
```

The major question becomes:

> Does past anomaly strength predict future anomaly strength?

If not, the 252-day leaderboard may only be descriptive.

If yes, that becomes a substantially more interesting result.

---

# 85. Minimal Technology Stack

Recommended:

```text
Python
pandas or Polars
NumPy
SciPy
PyArrow
Matplotlib
requests/httpx
```

Optional:

```text
DuckDB
Plotly
Streamlit
```

A clean first version can be built entirely using:

```text
pandas
numpy
scipy
matplotlib
pyarrow
requests
```

---

# 86. First Implementation Order

Build in this order.

## Step 1

Create NSE downloader.

Output:

```text
raw bhavcopy files
```

## Step 2

Create parser and normalized Parquet dataset.

Output:

```text
equity_daily.parquet
```

## Step 3

Build historical universe.

Output:

```text
security_master.parquet
```

## Step 4

Determine latest 252 completed sessions.

## Step 5

Calculate reusable features:

```text
prev_close
overnight return
intraday return
daily return
5-day return
volume ratio
weekday
month boundary
```

## Step 6

Implement:

```text
Close→Open
Open→Close
```

across every stock.

## Step 7

Calculate:

```text
equity curves
net PnL
Sharpe
drawdown
trades
```

## Step 8

Generate complete stock rankings.

## Step 9

Add:

```text
gap fade
gap continuation
```

## Step 10

Add:

```text
1D reversal
1D momentum
5D reversal
5D momentum
```

## Step 11

Add calendar and volume effects.

## Step 12

Add full plots and strategy breadth analysis.

Only after this should intraday/event data be added.

---

# 87. Definition of Done for Version 1

Version 1 is complete when one command can:

```bash
python run_research.py
```

and automatically:

1. Finds the correct 252-session evaluation window.
2. Loads/pulls NSE market data.
3. Builds the full historical equity universe.
4. Runs every configured daily strategy on every stock.
5. Applies the configured transaction-cost model.
6. Produces daily PnL curves.
7. Calculates metrics.
8. Ranks every stock by 252-day net PnL.
9. Saves full rankings.
10. Produces top/bottom/distribution plots.
11. Produces strategy-level breadth statistics.
12. Saves run metadata for reproducibility.

---

# 88. Most Important First Result

Before building complex signals, the first complete result should simply be:

```text
EVERY NSE STOCK
×
CLOSE → NEXT OPEN
×
LAST 252 SESSIONS
```

For every stock produce:

```text
Rank
Symbol
Company
Sessions
Trades
Gross PnL
Net PnL
Net Return
Sharpe
Max Drawdown
Win Rate
Median Daily Traded Value
```

and plot:

```text
Top 20 equity curves
Bottom 20 equity curves
Full-stock PnL distribution
PnL vs liquidity
% of stocks profitable
Equal-weight market-wide close→open equity
```

Then repeat the identical framework for:

```text
Open→Close
Gap Fade
Gap Continuation
Reversal
Momentum
...
```

That gives one consistent anomaly-research engine instead of a collection of unrelated notebooks.
