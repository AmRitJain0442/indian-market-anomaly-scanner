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

  plan.calendar.forEach((item) => {
    const card = document.createElement("article");
    const live = item.day > 20;
    card.className = `day-card ${live ? "conditional" : "paper"}`;
    const date = new Date(`${item.date}T00:00:00`).toLocaleDateString("en-IN", {day: "2-digit", month: "short", year: "numeric"});
    card.innerHTML = `<header><span>DAY ${String(item.day).padStart(2, "0")}</span><time>${item.weekday.toUpperCase()} · ${date.toUpperCase()}</time></header><p class="phase">${item.phase}</p><h3>${item.focus}</h3><p class="decision">${item.decision}</p><details><summary>What to do and when</summary><ol><li><b>08:45</b> Update equity, prior close, restrictions, and short availability.</li><li><b>09:15</b> Calculate gaps; choose only the highest-ranked eligible signal.</li><li><b>09:16</b> Fill within 10 bps or skip; install the 1% stop.</li><li><b>15:15</b> Exit regardless of PnL; never carry overnight.</li><li><b>15:40</b> Log costs and set closing equity as tomorrow’s sizing base.</li></ol></details><div class="day-target"><span>TARGET / PASS CONDITION</span><p>${item.target}</p></div><small>${item.risk_rule}</small>`;
    $("calendar").appendChild(card);
  });

  function calculate() {
    const price = Number($("entryPrice").value);
    const equity = Number($("accountEquity").value);
    const multiplier = $("liveStage").value === "half" ? 0.5 : 1;
    if (!Number.isFinite(price) || price <= 0 || !Number.isFinite(equity) || equity <= 0) return;
    const notionalCap = equity * plan.max_position_ratio * multiplier;
    const riskCap = equity * plan.risk_per_trade_ratio * multiplier;
    const quantity = Math.floor(Math.min(notionalCap / price, riskCap / (price * plan.stop_distance)));
    const notional = quantity * price;
    $("quantity").textContent = quantity.toLocaleString();
    $("notional").textContent = money(notional);
    $("plannedRisk").textContent = money(notional * plan.stop_distance);
    $("cashRemaining").textContent = money(equity - notional);
    $("dynamicDailyStop").textContent = money(equity * plan.daily_loss_ratio);
    $("dynamicPause").textContent = money(equity * plan.drawdown_ratio);
  }
  $("accountEquity").addEventListener("input", calculate);
  $("entryPrice").addEventListener("input", calculate);
  $("liveStage").addEventListener("change", calculate);
  calculate();
})();
