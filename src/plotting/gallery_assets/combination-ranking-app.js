(() => {
  const dataset = window.COMBINATION_RANKING;
  const rows = dataset.rows;
  const pageSize = 100;
  let filtered = rows;
  let page = 0;
  const $ = (id) => document.getElementById(id);
  const money = (value) => `${value >= 0 ? "+" : "−"}INR ${Math.abs(value).toLocaleString(undefined, {maximumFractionDigits: 0})}`;
  const plainMoney = (value) => `INR ${value.toLocaleString(undefined, {maximumFractionDigits: 0})}`;
  const tone = (value) => value >= 0 ? "positive" : "negative";
  const tierTone = (tier) => tier.includes("POSITIVE") ? "positive" : tier.includes("NEGATIVE") ? "negative" : "";
  const strategyName = (value) => value.replaceAll("_", " ").toUpperCase();

  $("pairCount").textContent = dataset.count.toLocaleString();
  $("heroInvestment").textContent = plainMoney(dataset.initial_capital);
  [...new Set(rows.map((row) => row.st))].sort().forEach((strategy) => {
    const option = document.createElement("option");
    option.value = strategy;
    option.textContent = strategyName(strategy);
    $("strategy").appendChild(option);
  });

  rows.slice(0, 3).forEach((item) => {
    const card = document.createElement("article");
    card.className = "winner";
    card.dataset.rank = item.r;
    card.innerHTML = `<span class="rank">OVERALL RANK ${String(item.r).padStart(2, "0")}</span><h3>${item.sy}</h3><span class="strategy">${strategyName(item.st)}</span><div class="score">${item.sc.toFixed(1)} / 100</div><div class="money">${money(item.pnl)} <small>profit on ${plainMoney(item.inv)}</small></div><span class="tier ${tierTone(item.et)}">${item.et} · ${item.pp}/5</span><a href="index.html#${item.id}" aria-label="Open ${item.sy} atlas"></a>`;
    $("podium").appendChild(card);
  });

  function comparator(order) {
    if (order === "profit") return (a, b) => b.pnl - a.pnl || a.r - b.r;
    if (order === "comparable") return (a, b) => (a.cr ?? Infinity) - (b.cr ?? Infinity) || a.r - b.r;
    if (order === "sharpe") return (a, b) => (b.sh ?? -Infinity) - (a.sh ?? -Infinity) || a.r - b.r;
    if (order === "cost") return (a, b) => b.p30 - a.p30 || a.r - b.r;
    return (a, b) => a.r - b.r;
  }

  function applyFilters() {
    const query = $("search").value.trim().toLowerCase();
    const strategy = $("strategy").value;
    const sample = $("sample").value;
    const evidence = $("evidence").value;
    filtered = rows.filter((item) => {
      const text = `${item.sy} ${item.co} ${item.id}`.toLowerCase();
      return (!query || text.includes(query))
        && (strategy === "all" || item.st === strategy)
        && (sample === "all" || item.qt === sample)
        && (evidence === "all" || item.et === evidence);
    }).sort(comparator($("sort").value));
    page = 0;
    render();
  }

  function render() {
    const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
    page = Math.min(page, pages - 1);
    const visible = filtered.slice(page * pageSize, (page + 1) * pageSize);
    $("resultCount").textContent = filtered.length.toLocaleString();
    $("page").textContent = `PAGE ${page + 1} / ${pages}`;
    $("previous").disabled = page === 0;
    $("next").disabled = page >= pages - 1;
    const body = $("rankingBody");
    body.replaceChildren();
    visible.forEach((item) => {
      const row = document.createElement("tr");
      const comparableRank = item.cr ? `<small>C ${item.cr.toLocaleString()}</small>` : "";
      const profitRank = `<small>P ${item.pr.toLocaleString()}</small>`;
      const sampleClass = item.qt === "COMPARABLE" ? "comparable" : item.qt === "LIMITED SAMPLE" ? "limited" : "";
      row.innerHTML = `<td class="rank-cell">${item.r.toLocaleString()}${profitRank}${comparableRank}</td><td class="pair"><strong>${item.sy} × ${strategyName(item.st)}</strong><small>${item.co} · ${item.id}</small></td><td class="score">${item.sc.toFixed(1)}</td><td class="evidence ${tierTone(item.et)}">${item.et}<br>${item.pp}/5</td><td>${plainMoney(item.inv)}</td><td class="${tone(item.pnl)}">${money(item.pnl)}</td><td class="${tone(item.end - item.inv)}">${plainMoney(item.end)}</td><td class="${tone(item.sh ?? -1)}">${item.sh == null ? "—" : item.sh.toFixed(2)}</td><td class="${tone(item.p30)}">${money(item.p30)}</td><td>${(item.dd * 100).toFixed(1)}%</td><td>${item.tr.toLocaleString()}</td><td class="sample ${sampleClass}">${item.qt}</td>`;
      row.addEventListener("click", () => { location.href = `index.html#${item.id}`; });
      body.appendChild(row);
    });
    document.querySelector(".table-wrap").scrollTop = 0;
  }

  ["search", "strategy", "sample", "evidence", "sort"].forEach((id) => {
    $(id).addEventListener(id === "search" ? "input" : "change", applyFilters);
  });
  $("previous").addEventListener("click", () => { if (page > 0) { page -= 1; render(); } });
  $("next").addEventListener("click", () => { if ((page + 1) * pageSize < filtered.length) { page += 1; render(); } });
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && document.activeElement !== $("search")) { event.preventDefault(); $("search").focus(); }
  });
  render();
})();
