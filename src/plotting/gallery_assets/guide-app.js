(() => {
  const data = window.RESEARCH_GUIDE
  const $ = (id) => document.getElementById(id)
  let category = "All"

  const title = (value) => value.replaceAll("_", " ").toUpperCase()
  const pct = (value) => `${(value * 100).toFixed(1)}%`
  const money = (value) => {
    const absolute = Math.abs(value)
    if (absolute >= 1e12) return `${value < 0 ? "-" : "+"}INR ${absolute.toExponential(2)}`
    return `${value < 0 ? "-" : "+"}INR ${absolute.toLocaleString(undefined, {maximumFractionDigits: 0})}`
  }

  $("windowBadge").textContent = `${data.window.label} study | ${data.window.start} to ${data.window.end}`
  $("sessionCount").textContent = data.window.sessions.toLocaleString()
  $("stockCount").textContent = data.window.stocks.toLocaleString()
  $("pairCount").textContent = data.window.pairs.toLocaleString()
  $("windowSwitch").href = data.window.other_url
  $("windowSwitch").textContent = data.window.sessions > 1000 ? "252 session guide →" : "10 year guide →"

  function setTab(tab) {
    const insights = tab === "insights"
    $("glossaryPanel").classList.toggle("active", !insights)
    $("insightsPanel").classList.toggle("active", insights)
    $("glossaryTab").classList.toggle("active", !insights)
    $("insightsTab").classList.toggle("active", insights)
    $("glossaryTab").setAttribute("aria-selected", String(!insights))
    $("insightsTab").setAttribute("aria-selected", String(insights))
    history.replaceState(null, "", `#${tab}`)
  }

  document.querySelectorAll("[data-tab]").forEach((button) => {
    button.addEventListener("click", () => setTab(button.dataset.tab))
  })

  const categories = ["All", ...new Set(data.glossary.map((item) => item.category))]
  categories.forEach((name) => {
    const button = document.createElement("button")
    button.textContent = name
    button.classList.toggle("active", name === category)
    button.addEventListener("click", () => {
      category = name
      document.querySelectorAll(".category-filters button").forEach((item) => item.classList.toggle("active", item.textContent === name))
      renderGlossary()
    })
    $("categoryFilters").appendChild(button)
  })

  function renderGlossary() {
    const query = $("glossarySearch").value.trim().toLowerCase()
    const terms = data.glossary.filter((item) => {
      const text = `${item.term} ${item.definition} ${item.category}`.toLowerCase()
      return (category === "All" || item.category === category) && text.includes(query)
    })
    $("glossaryCount").textContent = `${terms.length} of ${data.glossary.length} terms`
    $("glossaryGrid").replaceChildren()
    if (!terms.length) {
      const empty = document.createElement("p")
      empty.className = "empty"
      empty.textContent = "No matching term. Try a broader search."
      $("glossaryGrid").appendChild(empty)
      return
    }
    terms.forEach((item) => {
      const card = document.createElement("article")
      card.className = "term"
      card.innerHTML = `<span class="category">${item.category}</span><h3>${item.term}</h3><p>${item.definition}</p>`
      $("glossaryGrid").appendChild(card)
    })
  }

  $("glossarySearch").addEventListener("input", renderGlossary)

  $("insightIntro").textContent = data.window.sessions > 1000
    ? "My read is that gap fade deserves the most research attention across the full decade. The result is broad, but its largest compounded values are not realistic execution forecasts."
    : "My read is that the recent window points to the same three leaders as the decade study. That agreement is useful, but the shorter sample can still be dominated by the current market regime."

  data.collective_top.forEach((item) => {
    const card = document.createElement("article")
    card.dataset.rank = String(item.rank).padStart(2, "0")
    card.innerHTML = `<span>COLLECTIVE RANK ${String(item.rank).padStart(2, "0")}</span><h3>${title(item.strategy)}</h3><p>${item.score.toFixed(1)} / 100 | ${item.tier}</p>`
    $("topStrategies").appendChild(card)
  })

  const sameLeaders = data.windows.length === 2
  const insightCards = [
    {
      title: "The leaders repeat",
      text: sameLeaders
        ? "<strong>Gap fade 050, gap fade 100, and close to open lead both windows.</strong> That consistency makes them better research candidates than a strategy that appears in only one ranking."
        : "<strong>The top three strategies are the clearest research shortlist.</strong> A second window is needed before treating the order as stable."
    },
    {
      title: "Breadth matters more than a hero stock",
      text: `<strong>${title(data.broadest.strategy)} is profitable across ${pct(data.broadest.breadth)} of tested stocks.</strong> Broad participation is more informative than one extreme winner, although it still does not prove easy execution.`
    },
    {
      title: "Costs are the fastest reality check",
      text: `<strong>${title(data.severe_cost.strategy)} retains the strongest breadth at 30 bps per side, at ${pct(data.severe_cost.breadth)}.</strong> A result that disappears under severe costs should not lead the practical shortlist.`
    },
    {
      title: "Raw rank is not practical rank",
      text: `<strong>The raw leader is ${data.raw_leader.symbol} with ${title(data.raw_leader.strategy)}, labeled ${data.raw_leader.sample}.</strong> The comparable leader is ${data.comparable_leader.symbol} with ${title(data.comparable_leader.strategy)} across ${data.comparable_leader.trades.toLocaleString()} trades.`
    },
    {
      title: "The decade magnifies every assumption",
      text: "<strong>Thousands of compounded sessions can turn small data or execution errors into enormous ending values.</strong> Treat extreme figures as a prompt to inspect liquidity, circuits, short availability, and point in time tradability."
    },
    {
      title: "My action bias is validation",
      text: "<strong>Use the ranking to choose what to paper trade first.</strong> Keep the tested entry and exit fixed, log every skipped fill, and move to capital only after the operating gates pass."
    }
  ]
  insightCards.forEach((item, index) => {
    const card = document.createElement("article")
    card.className = "insight-card"
    card.innerHTML = `<span class="number">INSIGHT ${String(index + 1).padStart(2, "0")}</span><h3>${item.title}</h3><p>${item.text}</p>`
    $("insightGrid").appendChild(card)
  })

  function renderComparison() {
    if (data.windows.length < 2) {
      $("comparisonTable").innerHTML = "<p>Run both research windows to populate the comparison.</p>"
      return
    }
    const shortWindow = data.windows.find((item) => item.sessions < 1000)
    const decade = data.windows.find((item) => item.sessions > 1000)
    const strategies = ["gap_fade_050", "gap_fade_100", "close_to_open"]
    const rows = [
      `<div class="compare-row header"><strong>Strategy</strong><span>${shortWindow.label}</span><span>${decade.label}</span></div>`,
      ...strategies.map((strategy) => {
        const recent = shortWindow.metrics[strategy]
        const long = decade.metrics[strategy]
        return `<div class="compare-row"><strong>${title(strategy)}</strong><span>${money(recent.median_pnl)} median | ${pct(recent.breadth)} breadth</span><span>${money(long.median_pnl)} median | ${pct(long.breadth)} breadth</span></div>`
      })
    ]
    $("comparisonTable").innerHTML = rows.join("")
  }

  renderGlossary()
  renderComparison()
  setTab(location.hash === "#insights" ? "insights" : "glossary")
})()
