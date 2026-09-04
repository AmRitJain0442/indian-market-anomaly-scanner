# SITINET execution review and an INR 1,000 experiment

Reviewed on 5 September 2026. Starting capital is INR 1,000, as clarified by Amrit. The historical study ends on 27 August 2026. A separately downloaded official NSE bhavcopy checks instrument status on 4 September 2026.

## Decision

Do not deploy the SITINET gap-fade strategy with real money. Its historical intraday transactions are incompatible with its trading series. The ranking does not establish an executable profit opportunity.

Investigating an anomaly is reasonable. Expecting this chart to deliver exceptional profits over the next 30 days is not supported by the evidence. Increasing leverage or changing brokers would not repair the problem.

The earlier assistant should have checked trade eligibility before presenting the leaderboard as a basis for an investment plan. This review corrects that framing and supersedes the earlier INR 10,000 pilot for your current budget. Original research outputs remain unchanged so the mistakes can be inspected and reproduced.

My recommendation for the next month is to preserve the INR 1,000 and test the hypothesis on paper. I cannot defend a positive rupee profit target from this dataset.

## Trade evidence

Each selected trade was joined to its own session's NSE series. A security's latest series can differ from its series when a historical trade occurred.

- SITINET has 174 gap-fade trades at either the 0.5% or 1% threshold. All 174 occurred in BZ. There are 139 shorts and 35 longs.
- VHLTD has 202 gap-fade trades at 0.5%, all in BE. Its 175 trades at 1% are also all in BE.
- ARFIN ends the study in EQ, but 33 of its 118 gap-fade-1% trades occurred in BE. Screening only its latest series misses those transactions.
- Twelve of the top 20 stock-strategy combinations have a latest historical series of BE or BZ. This statistic is a leaderboard screen, not a claim that every trade in those twelve rows was in that series.

NSE defines BE and BZ as trade-for-trade. Zerodha explicitly prohibits intraday transactions in BZ, and Dhan also prohibits intraday trading in trade-for-trade shares. Buying shares and selling those purchases later the same day does not replicate the modeled trade. Selling pre-existing holdings and separately buying replacement shares creates delivery obligations and inventory exposure. [NSE series definitions](https://www.nseindia.com/static/market-data/legend-of-series), [Zerodha BZ rule](https://support.zerodha.com/category/trading-and-markets/trading-faqs/trading-categories-and-groups/articles/bz-category), [Dhan risk policy](https://dhan.co/risk-management-policy/)

The official 4 September file still lists SITINET as BZ and VHLTD as BE. SITINET's close is INR 0.29, last price INR 0.30, and whole-day traded value INR 67,079.25. Next-session status and account permissions must still be checked before future trading. [NSE bhavcopy, 4 September 2026](https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20260904_F_0000.csv.zip)

These figures all start with INR 1,000. They proportionally scale the original INR 100,000 research account and preserve its full-capital compounding. They do not simulate an integer-share INR 1,000 account.

| Stock and strategy | Initial investment | Modeled profit | Modeled ending value | BE/BZ trades | Review result |
|---|---:|---:|---:|---:|---|
| SITINET gap fade 0.5% | INR 1,000 | INR 49,949.40 | INR 50,949.40 | 174 / 174 | Reject intraday replication |
| VHLTD gap fade 0.5% | INR 1,000 | INR 36,267.46 | INR 37,267.46 | 202 / 202 | Reject intraday replication |
| ARFIN gap fade 1% | INR 1,000 | INR 1,710.12 | INR 2,710.12 | 33 / 118 | Historical series filtering required |
| SEAMECLTD gap fade 1% | INR 1,000 | INR 1,242.30 | INR 2,242.30 | 0 / 66 | Execution testing required |
| ETHOSLTD gap fade 1% | INR 1,000 | INR 487.67 | INR 1,487.67 | 0 / 56 | Execution testing required |
| EFCIL gap fade 1% | INR 1,000 | INR 673.28 | INR 1,673.28 | 0 / 68 | Execution testing required |
| THELEELA gap fade 1% | INR 1,000 | INR 600.75 | INR 1,600.75 | 0 / 71 | Execution testing required |

Removing ARFIN's BE trades reduces its 1% strategy's ideal-fill profit to INR 758.23 on INR 1,000 initial investment. This remains a price diagnostic, not a validated tradable return. Excluding BE/BZ leaves zero qualifying SITINET and VHLTD trades.

The two SITINET thresholds produce exactly the same trades. They are one piece of evidence appearing twice.

## Problems in the existing backtest

**Opening fills.** The signal in [GapStrategy](../../../src/strategies/daily.py) uses today's open, then [output_frame](../../../src/strategies/base.py) fills at that exact open. A real algorithm observes the price, decides, submits an order, and receives a later fill or rejection. An opening-auction strategy would need a separate rule based on information available before auction order entry closes.

**Price sensitivity.** I reran the same 174 SITINET signals with hypothetical adverse prices. The existing 0.20% round-trip cost deduction remains in every scenario.

| Price assumption | Initial investment | Profit or loss | Ending value |
|---|---:|---:|---:|
| Original official open and close | INR 1,000 | +INR 49,949.40 | INR 50,949.40 |
| Entry one paisa worse | INR 1,000 | -INR 508.11 | INR 491.89 |
| Entry and exit each one paisa worse | INR 1,000 | -INR 996.19 | INR 3.81 |

These are sensitivities, not measured spreads, feasible fill paths, or forecasts. The intraday eligibility failure applies to all three scenarios. One paisa is 3.45% of the latest INR 0.29 close. NSE's tick circular includes a one-paisa increment for low-priced shares. A 10-bps cost assumption is only 0.10%, so it does not establish resilience to price discreteness. [NSE tick-size circular](https://nsearchives.nseindia.com/content/circulars/CMTR67133.pdf)

With direction $s=+1$ for long and $s=-1$ for short, original entry $P$, original exit $X$, and adverse increment $\delta=0.01$:

$$
P'=P+s\delta,\qquad X'=X-s\delta
$$

$$
r_{\mathrm{entry\ only}}=s\left(\frac{X}{P'}-1\right)-0.002
$$

$$
r_{\mathrm{both\ sides}}=s\left(\frac{X'}{P'}-1\right)-0.002
$$

The hypothetical account compounds as $E_{t+1}=E_t(1+r_t)$. Fractional sizing remains in this diagnostic to isolate price sensitivity.

**Closing fills.** On 27 August, SITINET's modeled short enters at INR 0.28 and exits at official close INR 0.27, while last price is INR 0.28. Official close and last price differ on 89 of the 174 trades. Neither a daily official close nor a last price establishes an executable timed exit.

**Capacity.** The original INR 100,000 account reaches INR 4,928,770 before its final SITINET trade, about 18.2 times that day's entire traded value of INR 270,266. At your INR 1,000 starting scale, the same hypothetical last position is INR 49,288, about 18.2% of daily turnover. A smaller initial stake reduces capacity problems but does not establish opening depth or remove trading restrictions.

**Information from the future.** [returns.py](../../../src/features/returns.py) removes trades using discontinuity flags determined from the same day's close, or the next day's close for overnight trades. Those prices are unavailable at entry. The gap calculation also uses the previous observed close instead of consistently validating corporate-action-adjusted references. An executable backtest needs information available at the decision time.

**Selection bias.** The standard study searches 34,476 pairs. Ranking winners and calculating ordinary confidence intervals on the same sample does not establish future performance. The decade includes the short window and repeats the same execution assumptions. The label ROBUST POSITIVE is a descriptive score. The separate return-forecast models do not validate gap fade.

**A different pilot.** The old pilot's 1% stop, 15:15 exit, one-position priority, partial allocation and fill tolerance were never simulated together using intraday data. Scaling independent stock curves does not produce the combined account's return.

**A drawdown bug.** [metrics.py](../../../src/backtest/metrics.py) omits starting capital from the running peak. Returns of -10%, +2%, +1% report zero drawdown instead of -10%. The audit records both calculations. This must be corrected before relying on ranking risk comparisons.

## Economics with INR 1,000

Zerodha lists its data-enabled API at INR 500 per month. Its free Personal API excludes real-time and historical data. Dhan lists its Data API at INR 499 plus taxes every 30 days. One billing period consumes roughly half this capital. Free order API access does not imply free market-data access. [Zerodha API plans](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/what-are-the-charges-for-kite-apis), [Dhan Data API subscription](https://dhan.co/support/platforms/dhanhq-api/how-does-the-dhanhq-data-api-subscription-work/)

Do not buy these subscriptions from this INR 1,000 for this experiment. An existing permitted feed funded separately changes incremental cost, but not the SITINET conclusion. Terminal observations can support a manual learning log. Sparse observations cannot validate automated fills or continuous stop monitoring.

Even a hypothetical 5% monthly return on INR 1,000 would earn INR 50 before expenses. This is arithmetic, not an expected return. An INR 500 subscription would more than consume it.

Whole shares matter. On 4 September, SEAMECLTD closes at INR 1,793.60 and ETHOSLTD at INR 2,792.80. One unleveraged share exceeds this account. EFCIL at INR 193.24 and THELEELA at INR 554.05 are affordable using the whole account, but affordability does not establish profitability. The proposed INR 500 position cap also rules out THELEELA at that price.

Zerodha's published intraday schedule implies approximately INR 1.06 in fees for an illustrative INR 1,000 purchase and INR 1,000 sale, before charge rounding and minor levies, excluding spread, slippage and fixed costs. Brokerage is percentage-based below its cap, not automatically INR 20 on each small order. Actual charges must be reconciled. [Zerodha charges](https://zerodha.com/charges/)

## Proposed paper strategy

Hypothesis: sufficiently large opening gaps sometimes partially reverse in liquid, intraday-eligible cash equities. These proposed thresholds have not been optimized or validated. This is a revision of the historical strategy.

**Universe and capital**

1. Start a simulated INR 1,000 account. Real capital committed for these 30 sessions is INR 0.
2. Require the session's EQ series and confirmed broker permission for the product and direction. Reject BE/BZ, suspensions and relevant exchange or broker restrictions. Unknown permission means no trade.
3. Before the open, require all 20 preceding exchange sessions, a prior close of at least INR 100, and median daily traded value of at least INR 50 crore across those completed sessions. Rank by this past traded value, breaking ties alphabetically. Observe the first five whose previous close is no higher than half simulated equity. Recheck affordability at entry.
4. Check corporate actions and surveillance notices known before trading. Omit names with uncertain adjusted references.
5. Take at most one position daily, using whole shares, at most 50% of equity as notional, and no borrowed exposure.

These filters exclude the SITINET penny-stock mechanism. If nothing qualifies, record no trade. Do not substitute a retrospective winner or derivatives to create activity.

**Entry at 09:16 IST**

With valid official open $O_t$ and verified prior reference $C^*_{t-1}$:

$$
g_t=\frac{O_t}{C^*_{t-1}}-1
$$

If $g_t\leq-0.01$, consider a long. If $g_t\geq+0.01$, consider an intraday short when that direction is supported. Otherwise skip.

At 09:16:00, choose the highest-priority qualifying name. Require a timestamped bid and ask no older than one second, spread at most 0.10% of midpoint, sufficient opposite-side size, and at least 0.75% of remaining distance to the prior reference in the expected reversion direction. Skip a locked market or incomplete data.

Model latency. Use the first valid opposite-side quote at least one second after the decision, waiting no longer than five seconds. Accept a simulated fill only if that quote remains within a 0.05% adverse entry limit relative to the decision quote and sufficient size is visible. Otherwise record no fill. Candle touches alone do not establish fills. Quote-based simulation still cannot prove queue access.

If suitable licensed quote data is unavailable, keep a manual observation log and label executable PnL unverified. Do not fabricate a live feed or fill history.

**Stop, target and timed exit**

Use a 1% stop from filled entry, rounded to a valid tick. Record the resulting actual distance. Set the profit-taking price to the verified prior reference rounded to a valid tick. Skip an entry if its target was already reached.

Exit at the first of stop, reachable target or the timed exit beginning at 15:00 IST. Model long exits against the bid and short exits against the ask. A stop uses the first available quote at least one second after the trigger, not a guaranteed fill at the trigger price. Use the same one-second minimum latency for target and timed exits. When an exit cannot be completed, preserve the exposure and flag the failure. Suspend all new entries until it is reconciled. Do not assume the account is flat.

15:00 is a proposed buffer, not an exchange rule. It makes this a different strategy from the daily-close backtest. Current NSE closing-auction rules and broker intraday cutoffs must be respected. Zerodha describes earlier MIS cutoffs for auction-eligible cash stocks. Dhan's current risk policy says cash square-offs begin at 15:10, while an older support page gives a different time. Reconfirm the applicable cutoff before any future live version. [NSE closing auction](https://www.nseindia.com/static/products-services/closing-auction-session), [Zerodha implementation](https://zerodha.com/z-connect/general/everything-you-need-to-know-about-closing-auction-session-cas), [Dhan risk policy](https://dhan.co/risk-management-policy/)

**Sizing and net profit**

Let $E$ be reconciled simulated equity, $P$ entry, $S$ tick-rounded stop, $q$ whole-share quantity, $F(q)$ estimated round-trip charges and $L(q)$ an adverse-fill allowance. Before the forward sample, save the chosen broker's dated charge schedule and freeze the fee calculation, including its rounding assumptions. Compute $F(q)$ for entry and a stop-price exit. Without a complete fee calculation, the evaluator is not ready.

For this proposed primary experiment, set $L(q)=q\max(0.002P,2\tau)$, where $\tau$ is the current price tick. This reserves the larger of 0.20% of entry notional or two ticks per share for adverse fills. It is an unvalidated risk allowance, not a measured spread or a guarantee. Actual simulated PnL uses the observed fill prices, so do not subtract the allowance again as a fictional charge. Keep the fee calculation, allowance and latency unchanged during the forward sample.

Select the largest nonnegative integer $q$ satisfying:

$$
qP\leq0.5E
$$

$$
q|P-S|+F(q)+L(q)\leq0.005E
$$

For INR 1,000, the initial limits are INR 500 notional and INR 5 planned loss including estimates. If one share cannot fit, skip. Stops cannot guarantee the loss cap during a gap or failed exit.

Example: two shares at INR 200 use INR 400. A stop INR 2 away gives INR 4 price risk, leaving INR 1 for charges and adverse fills within an INR 5 budget. Reduce quantity if that allowance is insufficient. This is a sizing example, not a recommendation.

$$
\mathrm{net\ PnL}=s\,q(P_{\mathrm{exit}}-P_{\mathrm{entry}})-\mathrm{all\ charges}
$$

$$
E_{\mathrm{next}}=E+\mathrm{net\ PnL}
$$

Recompute size after reconciliation. Reinvestment retains net profits in the account. It does not commit all cash on each trade. Never increase the next position using unresolved exits or unrealized gains. During an open position, calculate risk equity using conservative bid valuation for longs and ask valuation for shorts, including unrealized losses and estimated closing charges. Pause at a 1% daily loss or 5% drawdown from the peak including initial capital, preserving all losses in evaluation. Missing quotes make risk equity unknown and block new entries. At the end of the experiment, report cash, unresolved exposure and marked equity separately. Do not describe unresolved positions as realized profit.

## Thirty-session plan

Start on Monday, 7 September 2026. Thirty trading sessions finish on Wednesday, 21 October, excluding 14 September, 2 October and 20 October. Thirty calendar days from 7 September through 6 October contain 20 scheduled sessions. Exchange amendments override this calendar. [NSE 2026 holidays](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf)

Every day has zero real orders. Before 09:00 check instruments, actions and data readiness. At 09:16 log the signal or skip reason. Monitor simulated exits continuously if usable data exists. Begin the timed exit at 15:00 and reconcile after the session. No parameter changes after losses.

| Session | Date | Additional task and measurable target |
|---:|---|---|
| 1 | Sep 7 | Freeze the rule and budget. Verify SITINET exclusion and save the decision record. |
| 2 | Sep 8 | Confirm data entitlement and timestamps. Otherwise record observations only. |
| 3 | Sep 9 | Check session series and permissions. Unknown status must produce a skip. |
| 4 | Sep 10 | Verify adjusted prior references with sources and timestamps. |
| 5 | Sep 11 | Reconcile quantities, fees and latency. Freeze the evaluator before counting forward evidence. |
| 6 | Sep 15 | Start the forward sample only if ready. Otherwise continue setup. |
| 7 | Sep 16 | Log the gap and later entry separately. Never assign the historical opening fill. |
| 8 | Sep 17 | Apply spread and size checks. Record rejected candidates. |
| 9 | Sep 18 | Check target reachability against quotes, not candle touches. |
| 10 | Sep 21 | Audit a reason for every fill, no-fill and no-trade day. |
| 11 | Sep 22 | Verify latency on every simulated fill. |
| 12 | Sep 23 | Verify stop fills include adverse movement after triggering. |
| 13 | Sep 24 | Review long-side evidence without forcing signals. |
| 14 | Sep 25 | Review short-side permissions without forcing signals. |
| 15 | Sep 28 | Test correct inactivity when no setup exists. |
| 16 | Sep 29 | Replay unknown order states. Timeouts must not create duplicates. |
| 17 | Sep 30 | Produce a cash ledger with initial investment, fees and ending equity. |
| 18 | Oct 1 | Check timed exits and explicitly record unresolved exposure. |
| 19 | Oct 5 | Refresh references after the holiday. |
| 20 | Oct 6 | Calendar-month checkpoint. Report simulated results without switching to live. |
| 21 | Oct 7 | Stress costs separately without selecting new parameters. |
| 22 | Oct 8 | Test five-second latency separately from the primary experiment. |
| 23 | Oct 9 | Treat missing quotes as unknown, not automatically profitable or closed. |
| 24 | Oct 12 | Reconcile candidate priority against the saved pre-open list. |
| 25 | Oct 13 | Report concentration of profit in single stocks and the best trade. |
| 26 | Oct 14 | Recompute drawdown from initial INR 1,000 and verify peaks. |
| 27 | Oct 15 | Check fee schedules and preserve rounding assumptions. |
| 28 | Oct 16 | Audit exclusions, restrictions and data gaps. |
| 29 | Oct 19 | Freeze final analysis. Do not search this sample for a better threshold. |
| 30 | Oct 21 | Publish results and failures. Decide to reject or extend paper testing. |

The target is faithful execution and complete evidence, not a daily rupee quota. A trade target is a conditional exit price.

A small number of winning trades cannot establish stable profitability. Twenty-five forward sessions after setup are an initial diagnostic. Report net results, losses, missing observations and stresses. Any statistical interval must account for dependence across days and the small sample. Do not turn a positive paper month into an automatic live-trading gate.

## Before a later live algo

Remaining work includes a portfolio backtest using decision-time data, whole shares, actual trading restrictions, costs and executable prices, followed by an independent evaluation sample. The existing source does not implement that.

A future order system needs permitted live data, broker authentication, static outbound IP where required, order reconciliation, partial-fill handling, duplicate prevention, position limits and a manual stop control. Keep market-data and hosting costs in the economics even when another budget funds them.

Both brokers publish static-IP requirements for API orders. Follow current retail-algo onboarding and tagging requirements even below the threshold for individual strategy registration. The Cloudflare viewing tunnel does not itself supply a static broker-facing outbound IP. [Zerodha static IP](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip), [Dhan authentication](https://dhanhq.co/docs/v2/authentication/), [NSE implementation standards](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf)

Dhan explicitly states that its Sandbox tests API workflows rather than live-market virtual-money performance. A successful sandbox order does not validate this trading hypothesis. [Dhan Sandbox limitations](https://dhan.co/support/platforms/dhanhq-api/can-i-use-dhanhq-sandbox-for-paper-trading-with-virtual-money-and-live-market-data/)

I would not choose a broker, subscribe to paid data, or increase the capital on the strength of SITINET's rank. Correcting and retesting the assumptions comes first.

## Reproduce

Run from the repository root with the existing processed data and trade artifacts:

    python review_execution.py --capital 1000 --latest-date 2026-09-04

The script reconciles base PnL with stored rankings, joins series by ISIN and trade date, computes price sensitivities, checks the drawdown defect, and hashes historical inputs. It downloads or reuses the dated official bhavcopy for the separate current-status check.

- [Summary and input hashes](audit_summary.json)
- [Selected stock-strategy evidence](selected_pair_audit.csv)
- [All 174 SITINET trades with series](sitinet_trade_audit.csv)
- [Top 20 pairs and latest historical series](top20_latest_historical_series.csv)
- [Latest exchange snapshot](latest_exchange_snapshot.csv)
- [Reproduction script](../../../review_execution.py)

This review did not connect a broker account, place orders, change the strategy engine or replace the deployed dashboard. Existing rankings must still be read alongside these findings.
