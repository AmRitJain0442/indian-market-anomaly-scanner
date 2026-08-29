(() => {
  const data = window.STRATEGY_RANKING;
  document.getElementById("windowSummary").textContent = `Market-wide evidence ledger · ${data.stock_count.toLocaleString()} stocks · ${data.session_count.toLocaleString()} completed sessions`;
  if (data.session_count > 1000) document.getElementById("planLink").href = "../../stock_gallery/investment-plan.html";
  const money = (value) => {
    const absolute = Math.abs(value);
    const amount = absolute >= 1e12
      ? absolute.toExponential(2)
      : absolute.toLocaleString(undefined, {maximumFractionDigits: 0});
    return `${value >= 0 ? "+" : "−"}INR ${amount}`;
  };
  const pct = (value) => `${(value * 100).toFixed(1)}%`;
  const tone = (value) => value >= 0 ? "positive" : "negative";
  const tierTone = (tier) => tier.includes("POSITIVE") ? "positive" : tier.includes("NEGATIVE") ? "negative" : "";
  const podium = document.getElementById("podium");
  data.strategies.slice(0,3).forEach((item) => {
    const card = document.createElement("article"); card.className="winner"; card.dataset.rank=item.rank;
    card.innerHTML=`<span class="rank">RANK 0${item.rank}</span><h3>${item.strategy.replaceAll("_"," ")}</h3><div class="score">${item.score.toFixed(1)} / 100</div><span class="tier ${tierTone(item.tier)}">${item.tier} · ${item.positive_pillars}/5</span>`;
    podium.appendChild(card);
  });
  const body=document.getElementById("rankingBody");
  data.strategies.forEach((item)=>{
    const row=document.createElement("tr");
    row.innerHTML=`<td>${item.rank}</td><td class="strategy">${item.strategy.replaceAll("_"," ").toUpperCase()}</td><td class="score-cell">${item.score.toFixed(1)}</td><td class="tier ${tierTone(item.tier)}">${item.tier}<br>${item.positive_pillars}/5</td><td class="${tone(item.median_pnl)}">${money(item.median_pnl)}</td><td>${pct(item.breadth)}</td><td class="${tone(item.equal_weight_pnl)}">${money(item.equal_weight_pnl)}</td><td class="${tone(item.median_sharpe)}">${item.median_sharpe.toFixed(2)}</td><td>${pct(item.cost_breadth)}</td>`;
    body.appendChild(row);
  });
})();
