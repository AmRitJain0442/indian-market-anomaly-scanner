# Short-horizon forecast method

This project predicts each stock's close-to-close return over the next 1, 3, and 5 consecutive NSE trading sessions. The predictions are research forecasts. They are not guaranteed prices, trading signals, or investment advice.

## Research basis

The primary paper is Shihao Gu, Bryan Kelly, and Dacheng Xiu, [Empirical Asset Pricing via Machine Learning](https://doi.org/10.1093/rfs/hhaa009), published in *The Review of Financial Studies* in 2020.

The paper models expected stock returns with one shared function across stocks and time:

$$
E[r_{i,t+1}\mid z_{i,t}] = g(z_{i,t})
$$

Here, (i) identifies a stock, (t) identifies time, (r) is its future return, and (z) is the information known at the forecast date. Pooling observations across stocks gives the model much more training data than fitting one small model per stock. The paper finds that recent price trends, liquidity, and volatility are among the most influential predictor groups.

This implementation adapts that framework to daily NSE data. It is not an exact reproduction of the paper. The paper studies US equities at a monthly horizon with a much larger characteristic set and compares several machine learning models. This project uses a transparent ridge regression baseline at daily horizons.

The forecast ranges are motivated by Yaniv Romano, Evan Patterson, and Emmanuel Candès, [Conformalized Quantile Regression](https://arxiv.org/abs/1905.03222). This project uses a simpler time-ordered, volatility-scaled residual calibration. Financial returns are not exchangeable, so the paper's formal finite-sample coverage guarantee does not apply here.

## Target mathematics

Let (C_{i,t}) be stock (i)'s closing price on session (t). For horizon (h\in\{1,3,5\}), the target is the forward log return:

$$
y_{i,t,h}=\log\left(\frac{C_{i,t+h}}{C_{i,t}}\right)
$$

Rows are valid only when (t) through (t+h) are consecutive market sessions for that stock. A target is removed when the source data flags a corporate-action discontinuity inside the horizon.

The predicted price is derived from the predicted log return:

$$
\widehat{C}_{i,t+h}=C_{i,t}\exp(\widehat{y}_{i,t,h})
$$

This is a conditional model estimate. It is not a price target.

## Information available at the close

The model uses only values known after session (t) closes:

- 1, 5, and 20-session returns
- same-session intraday return
- overnight return into session (t)
- high-low range
- 5 and 20-session realized volatility
- volume relative to its trailing history
- traded value as a liquidity measure
- distance from the 20-session moving average
- drawdown from the trailing 20-session high

Each characteristic is converted to a same-date cross-sectional percentile rank and centered around zero. This follows the broad normalization logic in the primary paper. It also reduces sensitivity to extreme raw values.

## Ridge model

For each horizon, the model is:

$$
\widehat{y}_{i,t,h}=\beta_{0,h}+z_{i,t}^{\mathsf T}\beta_h
$$

The coefficient estimate minimizes:

$$
\frac{1}{N}\sum_{i,t}\left(y_{i,t,h}-\beta_{0,h}-z_{i,t}^{\mathsf T}\beta_h\right)^2
+\lambda\lVert\beta_h\rVert_2^2
$$

The fixed penalty is (lambda=0.001). The intercept is not penalized. Training targets are clipped to their training-only 0.5 and 99.5 percent quantiles so isolated extremes do not dominate the fit.

## Walk-forward evaluation

The last 60 observable forecast dates are reserved for evaluation. The model is refitted every 20 sessions. For a test session (s), every training target must end before (s):

$$
t+h<s
$$

This rule prevents future closing prices from entering the training sample. Each fit uses at most the preceding 756 sessions. Final live research forecasts are fitted only after the held-out evaluation is complete.

The report includes:

- mean absolute error
- root mean squared error
- direction accuracy
- out-of-sample (R^2) against a zero-return forecast
- empirical interval coverage

An out-of-sample (R^2) below zero means the model had more squared error than simply predicting a zero return.

## Forecast range

For each held-out observation, define the scaled absolute residual:

$$
s_{i,t,h}=\frac{\left|y_{i,t,h}-\widehat{y}_{i,t,h}\right|}
{\max(\sigma_{i,t,20},0.002)\sqrt{h}}
$$

The value (q_{0.80,h}) is the finite-sample-adjusted 80th percentile of held-out scores. The displayed range is:

$$
\left[
\widehat{y}_{i,t,h}-q_{0.80,h}\sigma_{i,t,20}\sqrt{h},
\widehat{y}_{i,t,h}+q_{0.80,h}\sigma_{i,t,20}\sqrt{h}
\right]
$$

The endpoints are converted to prices using the exponential relationship above. The range describes historical residual calibration. It does not bound what the market can do.

## Reproduce the forecasts

Generate the standard research snapshot:

```bash
python generate_short_horizon_forecasts.py
```

Generate the separate 10-year research snapshot:

```bash
python generate_short_horizon_forecasts.py --namespace ten_year
```

The generated artifacts are written to `results/forecasts/` or `results/ten_year/forecasts/`:

- `latest_stock_forecasts.csv` contains the current stock-level forecasts
- `walk_forward_predictions.parquet` contains every held-out observation
- `walk_forward_metrics.csv` contains horizon-level validation results
- `forecast_metadata.json` records settings, papers, and limitations

## Current interpretation

In the snapshot through 27 August 2026, the three models achieved only about 51 percent direction accuracy. Their out-of-sample (R^2) values against a zero-return baseline were negative. The correct research conclusion is that this baseline did not demonstrate a reliable tradable edge. The forecast panels should be read as model diagnostics, not recommendations.
