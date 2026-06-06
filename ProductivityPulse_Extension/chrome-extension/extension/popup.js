// popup.js — ProductivityPulse popup logic

function fmt(seconds) {
  if (seconds < 60) return `${seconds}s`;
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

function scoreColor(score) {
  if (score >= 70) return '#4ade80';
  if (score >= 40) return '#fbbf24';
  return '#f87171';
}

function scoreLabel(score) {
  if (score >= 80) return '🚀 Excellent!';
  if (score >= 60) return '💪 Good Work';
  if (score >= 40) return '⚡ Getting There';
  if (score >= 20) return '😐 Room to Improve';
  return '😴 Needs Focus';
}

// ── Render score ring ─────────────────────────────────────────
function renderRing(score) {
  const circ = 201;
  const offset = circ - (circ * score / 100);
  const fill = document.getElementById('ringFill');
  fill.style.strokeDashoffset = offset;
  fill.style.stroke = scoreColor(score);
  document.getElementById('ringScore').textContent = score;
  document.getElementById('scoreTitle').textContent = scoreLabel(score);
}

// ── Render today's site list ──────────────────────────────────
function renderSites(usage) {
  const list = document.getElementById('sitesList');
  const empty = document.getElementById('sitesEmpty');
  list.innerHTML = '';

  const entries = Object.entries(usage)
    .sort((a, b) => b[1].seconds - a[1].seconds)
    .slice(0, 10);

  if (entries.length === 0) { empty.style.display = 'block'; return; }
  empty.style.display = 'none';

  const maxSec = entries[0][1].seconds;

  entries.forEach(([hostname, data]) => {
    const row = document.createElement('div');
    row.className = 'site-row';

    const badgeClass = data.category === 'productive' ? 'badge-p' : data.category === 'unproductive' ? 'badge-u' : 'badge-n';
    const barColor = data.category === 'productive' ? '#4ade80' : data.category === 'unproductive' ? '#f87171' : '#60a5fa';
    const pct = Math.round((data.seconds / maxSec) * 100);

    row.innerHTML = `
      <img class="site-favicon" src="${data.favicon}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
      <div class="site-favicon-fallback" style="display:none">🌐</div>
      <div class="site-info">
        <div class="site-name">${hostname}</div>
        <div class="site-bar-wrap"><div class="site-bar" style="width:${pct}%;background:${barColor}"></div></div>
      </div>
      <div class="site-time">${fmt(data.seconds)}</div>
      <span class="badge ${badgeClass}">${data.category === 'productive' ? 'Pro' : data.category === 'unproductive' ? 'Unpro' : 'Neutral'}</span>
    `;
    list.appendChild(row);
  });
}

// ── Render week chart ─────────────────────────────────────────
function renderWeek(weekData) {
  const container = document.getElementById('weekBars');
  container.innerHTML = '';

  const days = Object.entries(weekData);
  const maxTotal = Math.max(...days.map(([, v]) => v.productive + v.unproductive + v.neutral), 1);

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  days.forEach(([date, vals]) => {
    const total = vals.productive + vals.unproductive + vals.neutral;
    const pPct = (vals.productive / maxTotal) * 88;
    const uPct = (vals.unproductive / maxTotal) * 88;
    const nPct = (vals.neutral / maxTotal) * 88;
    const d = new Date(date + 'T00:00:00');
    const dayName = dayNames[d.getDay()];
    const isToday = date === new Date().toISOString().split('T')[0];

    const group = document.createElement('div');
    group.className = 'week-bar-group';
    group.innerHTML = `
      <div class="week-bar-stack">
        <div class="week-bar-seg" style="height:${pPct}px;background:#4ade80;margin-bottom:1px"></div>
        <div class="week-bar-seg" style="height:${uPct}px;background:#f87171;margin-bottom:1px"></div>
        <div class="week-bar-seg" style="height:${nPct}px;background:#374151"></div>
      </div>
      <div class="week-day" style="color:${isToday ? '#60a5fa' : '#64748b'};font-weight:${isToday ? 700 : 400}">${dayName}</div>
    `;
    container.appendChild(group);
  });
}

// ── Render insights ───────────────────────────────────────────
function renderInsights(usage) {
  const container = document.getElementById('insightCards');
  container.innerHTML = '';

  const entries = Object.entries(usage);
  let topSite = null, topWaste = null, productive = 0, unproductive = 0;
  entries.forEach(([h, v]) => {
    if (v.category === 'productive') productive += v.seconds;
    if (v.category === 'unproductive') unproductive += v.seconds;
    if (!topSite || v.seconds > topSite.sec) topSite = { host: h, sec: v.seconds };
    if (v.category === 'unproductive' && (!topWaste || v.seconds > topWaste.sec)) topWaste = { host: h, sec: v.seconds };
  });

  const cards = [];

  if (topSite) {
    cards.push({ title: '🏆 Most Visited', text: `You spent the most time on <b>${topSite.host}</b> today (${fmt(topSite.sec)}).` });
  }
  if (topWaste) {
    cards.push({ title: '⚠️ Biggest Time Sink', text: `<b>${topWaste.host}</b> consumed ${fmt(topWaste.sec)} of unproductive time.` });
  }
  if (productive > 0 && unproductive > 0) {
    const ratio = (productive / unproductive).toFixed(1);
    cards.push({ title: '📊 Productivity Ratio', text: `For every minute wasted, you spent ${ratio} minutes productively.` });
  }
  if (productive > 3600) {
    cards.push({ title: '🎯 Deep Work', text: `You've clocked over ${fmt(productive)} of focused, productive browsing today. Great!` });
  }
  if (entries.length === 0) {
    cards.push({ title: '👋 Getting Started', text: 'Browse a few sites and come back — your insights will appear here.' });
  }

  cards.forEach(c => {
    const card = document.createElement('div');
    card.className = 'insight-card';
    card.innerHTML = `<div class="insight-title">${c.title}</div><div class="insight-text">${c.text}</div>`;
    container.appendChild(card);
  });
}

// ── Load settings ─────────────────────────────────────────────
async function loadSettings() {
  const result = await chrome.storage.local.get('settings');
  const settings = result.settings || { focusMode: false };
  document.getElementById('focusToggle').checked = settings.focusMode;
}

// ── Main init ─────────────────────────────────────────────────
async function init() {
  // Today's data
  const todayResp = await chrome.runtime.sendMessage({ type: 'GET_TODAY' });
  const usage = todayResp.usage || {};

  let productive = 0, unproductive = 0, total = 0;
  Object.values(usage).forEach(v => {
    total += v.seconds;
    if (v.category === 'productive') productive += v.seconds;
    else if (v.category === 'unproductive') unproductive += v.seconds;
  });

  const score = total > 0 ? Math.round((productive / (productive + unproductive + 1)) * 100) : 0;
  renderRing(score);

  document.getElementById('statProductive').textContent = fmt(productive);
  document.getElementById('statUnproductive').textContent = fmt(unproductive);
  document.getElementById('statTotal').textContent = fmt(total);
  document.getElementById('scoreSub').textContent = total > 0
    ? `${Math.round(total / 60)} min browsed today`
    : 'No data yet — start browsing!';

  renderSites(usage);
  renderInsights(usage);

  // Week data
  const weekResp = await chrome.runtime.sendMessage({ type: 'GET_WEEK' });
  renderWeek(weekResp.data || {});

  await loadSettings();
}

// ── Tab switching ─────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('panel-' + tab.dataset.tab).classList.add('active');
  });
});

// ── Focus mode toggle ─────────────────────────────────────────
document.getElementById('focusToggle').addEventListener('change', async (e) => {
  const result = await chrome.storage.local.get('settings');
  const settings = result.settings || {};
  settings.focusMode = e.target.checked;
  await chrome.storage.local.set({ settings });
});

// ── Buttons ───────────────────────────────────────────────────
document.getElementById('clearBtn').addEventListener('click', async () => {
  if (confirm('Reset today\'s data?')) {
    await chrome.runtime.sendMessage({ type: 'CLEAR_TODAY' });
    init();
  }
});

document.getElementById('settingsBtn').addEventListener('click', () => {
  chrome.runtime.openOptionsPage();
});

document.getElementById('reportBtn').addEventListener('click', () => {
  chrome.tabs.create({ url: chrome.runtime.getURL('report.html') });
});

init();
