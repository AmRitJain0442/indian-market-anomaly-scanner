(() => {
  const manifest = window.STOCK_ATLAS;
  const all = manifest.stocks;
  let visible = all;
  let current = 0;
  let filter = "all";

  const $ = (id) => document.getElementById(id);
  const search = $("search");
  const results = $("results");
  const image = $("atlas");

  $("chartCount").textContent = manifest.chart_count.toLocaleString();
  const isDecade = manifest.analysis_namespace === "ten_year";
  const evaluationSessions = manifest.evaluation_sessions ?? 252;
  const initialCapital = manifest.initial_capital ?? 100000;
  $("windowLabel").textContent = isDecade
    ? `${evaluationSessions.toLocaleString()} sessions · 10-year research archive`
    : `${evaluationSessions.toLocaleString()}-session research archive`;
  $("windowSwitch").textContent = isDecade ? "252-session analysis →" : "10-year analysis →";
  $("windowSwitch").href = isDecade
    ? "../../stock_gallery/index.html"
    : "../ten_year/stock_gallery/index.html";
  if (isDecade) $("planLink").href = "../../stock_gallery/investment-plan.html";
  if ($("eligibilityLink")) $("eligibilityLink").href = isDecade
    ? "../../findings/2026-09-05-eligibility-ranking/ten_year/index.html"
    : "../findings/2026-09-05-eligibility-ranking/one_year/index.html";
  $("methodLine").textContent = `${manifest.strategy_count} strategies · INR ${initialCapital.toLocaleString("en-IN")} initial capital · 10 bps per side`;

  function matchesFilter(stock) {
    if (filter === "liquid") return stock.liquidity === "OK";
    if (filter === "full") return stock.coverage >= 0.95;
    return true;
  }

  function refreshResults() {
    const query = search.value.trim().toLowerCase();
    visible = all.filter((stock) => {
      const text = `${stock.symbol} ${stock.company} ${stock.isin}`.toLowerCase();
      return matchesFilter(stock) && text.includes(query);
    });
    results.replaceChildren();
    visible.slice(0, 250).forEach((stock, index) => {
      const button = document.createElement("button");
      button.className = "result";
      button.setAttribute("role", "option");
      button.innerHTML = `<strong>${stock.symbol}</strong><span class="pill">${stock.liquidity}</span><small>${stock.company}</small>`;
      button.addEventListener("click", () => select(index));
      results.appendChild(button);
    });
    if (visible.length) select(0);
  }

  function select(index) {
    if (!visible.length) return;
    current = (index + visible.length) % visible.length;
    const stock = visible[current];
    $("position").textContent = `${current + 1} / ${visible.length}`;
    $("symbol").textContent = stock.symbol;
    $("company").textContent = `${stock.company} · ${stock.isin} · ${(stock.coverage * 100).toFixed(1)}% coverage`;
    $("download").href = stock.image;
    $("download").download = `${stock.symbol}-${stock.isin}-anomaly-atlas.webp`;
    $("loading").hidden = false;
    image.classList.remove("ready");
    image.onload = () => { $("loading").hidden = true; image.classList.add("ready"); };
    image.src = `${stock.image}?v=${manifest.evaluation_end}-forecast-v1`;
    image.alt = `All 13 strategy equity curves for ${stock.symbol}`;
    history.replaceState(null, "", `#${stock.isin}`);
    [...results.children].forEach((item, itemIndex) => item.classList.toggle("active", itemIndex === current));
  }

  search.addEventListener("input", refreshResults);
  $("previous").addEventListener("click", () => select(current - 1));
  $("next").addEventListener("click", () => select(current + 1));
  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-filter]").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      filter = button.dataset.filter;
      refreshResults();
    });
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && document.activeElement !== search) { event.preventDefault(); search.focus(); }
    if (event.key === "ArrowLeft") select(current - 1);
    if (event.key === "ArrowRight") select(current + 1);
  });

  refreshResults();
  const requested = location.hash.slice(1);
  const requestedIndex = visible.findIndex((stock) => stock.isin === requested);
  if (requestedIndex >= 0) select(requestedIndex);
})();
