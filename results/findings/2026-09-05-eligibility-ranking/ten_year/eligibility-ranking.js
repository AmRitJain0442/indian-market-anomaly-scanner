(() => {
  'use strict'
  const data = window.ELIGIBILITY_DATA
  const $ = id => document.getElementById(id)
  if (!data) { $('windowInfo').textContent = 'Ranking data unavailable. Regenerate this report.'; return }
  const meta = data.metadata
  const rows = data.rows.map(values => {
    const row = Object.fromEntries(data.columns.map((column, index) => [column, values[index]]))
    return {...row, historical_initial_investment: meta.historical_initial_investment,
      historical_ending_value: meta.historical_initial_investment + row.net_pnl,
      historical_return_percent: row.net_pnl / meta.historical_initial_investment * 100,
      searchText: `${row.symbol} ${row.current_symbol || ''} ${row.company_name} ${row.isin}`.toLowerCase()}
  })
  const money = value => value == null ? 'Unavailable' : `INR ${Number(value).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`
  const number = value => Number(value).toLocaleString('en-IN')
  const percent = value => value == null ? 'Unavailable' : `${Number(value).toLocaleString('en-IN', {maximumFractionDigits: 2})}%`
  const esc = value => String(value ?? '').replace(/[&<>"']/g, character => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[character]))
  let view = 'practical', page = 0, filtered = [], expanded = null
  const pageSize = 50
  $('budget').textContent = money(meta.budget)
  $('cap').textContent = money(meta.notional_cap)
  $('riskLimit').textContent = `Planned-risk illustration: ${money(meta.risk_budget)}`
  $('eqCount').textContent = number(meta.eq_pairs)
  $('practicalCount').textContent = `${number(meta.practical_pairs)} / ${number(meta.practical_stocks)}`
  $('windowInfo').textContent = `${meta.window === 'ten_year' ? '10-year' : '1-year'} study: ${meta.evaluation_start} to ${meta.evaluation_end}. NSE and broker snapshot: ${meta.snapshot_date}.`
  $(meta.window === 'ten_year' ? 'tenYearLink' : 'oneYearLink').setAttribute('aria-current', 'page')
  if (meta.window === 'ten_year') $('atlasLink').href = '../../../ten_year/stock_gallery/index.html'
  $('referenceNote').textContent = `Historical reference account: ${money(meta.historical_initial_investment)}. Historical returns and profits are not performance of your ${money(meta.budget)} account.`
  $('footer').textContent = `Zerodha list updated ${meta.broker_updated}. ${number(meta.total_pairs)} pairs audited. No leverage assumed. No live strategy validated.`
  for (const name of [...new Set(rows.map(row => row.strategy))].sort()) {
    const option = document.createElement('option')
    option.value = name; option.textContent = name.replaceAll('_', ' '); $('strategy').append(option)
  }
  const descriptions = {
    practical: 'Passes the EQ-history, budget, liquidity, sample and published MIS-list checks. A candidate for execution testing, not a recommendation to trade.',
    eq: 'Every historical trade has EQ on both legs and the latest NSE record is EQ. Budget and broker checks may still fail.',
    excluded: 'Rejected from the EQ-only rank. Open Checks to see current-series, historical-series or missing-data reasons.',
    all: 'All original stock-strategy pairs with their audit results. Excluded pairs have no new rank or score.'
  }
  function applyFilters() {
    const query = $('search').value.trim().toLowerCase()
    const strategy = $('strategy').value
    const broker = $('broker').value
    filtered = rows.filter(row =>
      (view === 'all' || (view === 'practical' && row.worklist_pass) || (view === 'eq' && row.eq_screen_pass) || (view === 'excluded' && !row.eq_screen_pass)) &&
      (!query || row.searchText.includes(query)) && (strategy === 'all' || row.strategy === strategy) &&
      (broker === 'all' || (broker === 'listed' && row.broker_listed) || (broker === 'not-listed' && !row.broker_listed)))
    const order = $('sort').value
    const rank = row => row.eq_rank ?? Infinity
    filtered.sort((a, b) => {
      if (order === 'price') return (a.snapshot_price ?? Infinity) - (b.snapshot_price ?? Infinity) || rank(a) - rank(b)
      if (order === 'liquidity') return (b.recent_median_value ?? -1) - (a.recent_median_value ?? -1) || rank(a) - rank(b)
      if (order === 'return') return (b.eq_screen_pass ? b.historical_return_percent : -Infinity) - (a.eq_screen_pass ? a.historical_return_percent : -Infinity) || rank(a) - rank(b)
      return rank(a) - rank(b) || a.symbol.localeCompare(b.symbol) || a.strategy.localeCompare(b.strategy)
    })
    page = 0; expanded = null; render()
  }
  function detail(row) {
    const tr = document.createElement('tr'); tr.className = 'detail-row'
    const reason = row.worklist_pass ? 'Passes the dated practical research screen. Current order permission and execution still need validation.' : row.worklist_reasons
    tr.innerHTML = `<td colspan="9"><dl class="detail-grid">
      <div><dt>Current series / historical BE or BZ trades</dt><dd>${esc(row.current_series || 'Missing')} / ${number(row.restricted_trades)}</dd></div>
      <div><dt>Missing historical leg series</dt><dd>${number(row.unknown_series_trades)}</dd></div>
      <div><dt>Recent median daily turnover</dt><dd>${row.recent_median_value == null ? 'Unavailable' : money(row.recent_median_value / 10000000) + ' crore'}</dd></div>
      <div><dt>Historical initial investment</dt><dd>${money(row.historical_initial_investment)}</dd></div>
      <div><dt>Original modeled profit / ending value</dt><dd>${money(row.net_pnl)} / ${money(row.historical_ending_value)}</dd></div>
      <div><dt>Drawdown with initial capital included</dt><dd>${percent(Math.abs(row.max_drawdown) * 100)}</dd></div>
      <div><dt>Historical coverage / short trades</dt><dd>${percent(row.coverage_ratio * 100)} / ${number(row.short_trades)}</dd></div>
      <div><dt>Original profit at 30 bps per side</dt><dd>${money(row.pnl_30bps)} on ${money(row.historical_initial_investment)}</dd></div>
      <div><dt>Broker snapshot</dt><dd>${row.broker_listed ? 'Listed' : 'Not listed'} in Zerodha MIS table dated ${esc(meta.broker_updated)}</dd></div>
      <div><dt>Illustrative planned loss / limit</dt><dd>${money(row.illustrative_planned_loss)} / ${money(row.risk_budget)}</dd></div>
      </dl><p class="detail-reason">${esc(reason)}</p><p class="detail-warning">Original theoretical profits are not a corrected executable backtest. Risk shares are a separate current-price illustration using a 1% stop, not a newly tested strategy. Historical broker permissions, live fills and Dhan access are unverified.</p></td>`
    return tr
  }
  function render() {
    const pages = Math.max(1, Math.ceil(filtered.length / pageSize))
    page = Math.min(page, pages - 1)
    $('viewDescription').textContent = descriptions[view]
    $('rankHeading').textContent = view === 'practical' ? 'Practical rank' : 'EQ rank'
    $('matches').textContent = `${number(filtered.length)} matching pairs`
    $('pageLabel').textContent = `Page ${page + 1} of ${pages}`
    $('previous').disabled = page === 0; $('next').disabled = page + 1 >= pages
    $('emptyState').hidden = filtered.length !== 0
    const body = $('rankingBody'); body.replaceChildren()
    for (const row of filtered.slice(page * pageSize, (page + 1) * pageSize)) {
      const key = `${row.isin}:${row.strategy}`
      const tr = document.createElement('tr')
      const rankValue = view === 'practical' ? row.worklist_rank : row.eq_rank
      tr.innerHTML = `<td class="rank">${rankValue == null ? 'Excluded' : number(rankValue)}</td>
        <td><span class="pair-name">${esc(row.current_symbol || row.symbol)}</span><span class="strategy-name">${esc(row.strategy.replaceAll('_', ' '))}</span><small>${esc(row.company_name)}</small></td>
        <td class="number">${money(row.snapshot_price)}<small>${esc(meta.snapshot_date)}</small></td>
        <td>${row.illustrative_risk_shares == null ? 'Not evaluated' : number(row.illustrative_risk_shares)}<small>1% stop risk limit</small><small>Cash-cap maximum: ${number(row.cash_cap_shares)}</small></td>
        <td class="${row.broker_listed ? 'listed' : 'not-listed'}">${row.broker_listed ? 'Listed' : 'Not listed'}<small>Zerodha MIS</small></td>
        <td>${row.research_score == null ? 'Not ranked' : row.research_score.toFixed(1)}</td>
        <td class="${row.net_pnl < 0 ? 'negative' : ''}">${row.eq_screen_pass ? percent(row.historical_return_percent) : 'Not ranked'}</td>
        <td>${number(row.number_of_trades)}</td>
        <td><button class="check-button" aria-expanded="${expanded === key}" aria-label="Checks for ${esc(row.current_symbol || row.symbol)} ${esc(row.strategy)}">${expanded === key ? 'Close' : 'Checks'}</button></td>`
      tr.querySelector('button').addEventListener('click', () => { expanded = expanded === key ? null : key; render() })
      body.append(tr)
      if (expanded === key) body.append(detail(row))
    }
  }
  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => {
    view = button.dataset.view
    document.querySelectorAll('[data-view]').forEach(item => item.setAttribute('aria-pressed', String(item === button)))
    applyFilters()
  }))
  for (const id of ['search', 'strategy', 'broker', 'sort']) $(id).addEventListener(id === 'search' ? 'input' : 'change', applyFilters)
  $('previous').addEventListener('click', () => { page--; expanded = null; render() })
  $('next').addEventListener('click', () => { page++; expanded = null; render() })
  $('searchAll').addEventListener('click', () => document.querySelector('[data-view="all"]').click())
  applyFilters()
})()
