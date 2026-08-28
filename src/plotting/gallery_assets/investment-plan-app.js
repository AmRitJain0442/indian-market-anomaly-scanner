(() => {
  const plan = window.INVESTMENT_PLAN;
  const $ = (id) => document.getElementById(id);
  const money = (value, signed = false) => `${signed ? (value >= 0 ? "+" : "−") : ""}INR ${Math.abs(value).toLocaleString(undefined, {maximumFractionDigits: 0})}`;

  $("evaluationEnd").textContent = plan.evaluation_end;
  $("capital").textContent = money(plan.capital);
  $("maxPosition").textContent = money(plan.max_position);
  $("tradeRisk").textContent = money(plan.risk_per_trade);
  $("drawdownLimit").textContent = money(plan.drawdown_limit);

  plan.watchlist.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>0${item.rank}</td><td><strong>${item.symbol}</strong><small>${item.company}</small></td><td class="score">${item.score.toFixed(1)}</td><td>${item.combination_rank.toLocaleString()}</td><td class="positive">${money(item.historical_pnl, true)}</td><td>${money(item.historical_ending)}</td><td class="positive">${money(item.pnl_30bps_scaled, true)}</td><td class="positive">${money(item.long_pnl, true)}<small>${item.long_trades} trades</small></td><td class="positive">${money(item.short_pnl, true)}<small>${item.short_trades} trades</small></td><td><a href="index.html#${item.isin}">Open →</a></td>`;
    $("watchlist").appendChild(row);
  });

  function calculate() {
    const price = Number($("entryPrice").value);
    const multiplier = $("liveStage").value === "half" ? 0.5 : 1;
    if (!Number.isFinite(price) || price <= 0) return;
    const notionalCap = plan.max_position * multiplier;
    const riskCap = plan.risk_per_trade * multiplier;
    const quantity = Math.floor(Math.min(notionalCap / price, riskCap / (price * plan.stop_distance)));
    const notional = quantity * price;
    $("quantity").textContent = quantity.toLocaleString();
    $("notional").textContent = money(notional);
    $("plannedRisk").textContent = money(notional * plan.stop_distance);
    $("cashRemaining").textContent = money(plan.capital - notional);
  }
  $("entryPrice").addEventListener("input", calculate);
  $("liveStage").addEventListener("change", calculate);
  calculate();
})();
