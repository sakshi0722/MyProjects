// ============================================================
// ProductivityPulse — Background Service Worker
// Tracks time per domain, classifies sites, syncs to backend
// ============================================================

const PRODUCTIVE_SITES = [
  'github.com','stackoverflow.com','docs.google.com','notion.so',
  'leetcode.com','kaggle.com','medium.com','dev.to','coursera.org',
  'udemy.com','linkedin.com','figma.com','codepen.io','replit.com',
  'developer.mozilla.org','w3schools.com','npmjs.com','pypi.org',
  'arxiv.org','research.google.com','openai.com','anthropic.com'
];

const UNPRODUCTIVE_SITES = [
  'youtube.com','facebook.com','instagram.com','twitter.com','x.com',
  'reddit.com','tiktok.com','snapchat.com','twitch.tv','netflix.com',
  'amazon.com','flipkart.com','9gag.com','buzzfeed.com','tumblr.com'
];

const BACKEND_URL = 'http://localhost:8000';

let activeTabId = null;
let activeTabUrl = null;
let activeStart = null;

// ── Classify a hostname ──────────────────────────────────────
function classifySite(hostname) {
  const h = hostname.replace(/^www\./, '');
  if (PRODUCTIVE_SITES.some(s => h === s || h.endsWith('.' + s))) return 'productive';
  if (UNPRODUCTIVE_SITES.some(s => h === s || h.endsWith('.' + s))) return 'unproductive';
  return 'neutral';
}

function getHostname(url) {
  try { return new URL(url).hostname; }
  catch { return null; }
}

// ── Save a time segment ───────────────────────────────────────
async function saveSegment(url, seconds) {
  if (!url || seconds < 1) return;
  const hostname = getHostname(url);
  if (!hostname) return;

  const today = new Date().toISOString().split('T')[0];
  const key = `usage_${today}`;

  const result = await chrome.storage.local.get([key, 'totalTime', 'settings']);
  const usage = result[key] || {};
  const settings = result.settings || { dailyGoalMinutes: 240, focusMode: false, blockedSites: [] };

  // Focus mode — block unproductive sites
  if (settings.focusMode) {
    const cat = classifySite(hostname);
    if (cat === 'unproductive') {
      chrome.tabs.query({ active: true }, tabs => {
        if (tabs[0]) chrome.tabs.update(tabs[0].id, { url: chrome.runtime.getURL('blocked.html') });
      });
      return;
    }
  }

  const category = classifySite(hostname);
  if (!usage[hostname]) {
    usage[hostname] = { seconds: 0, category, favicon: `https://www.google.com/s2/favicons?domain=${hostname}&sz=32` };
  }
  usage[hostname].seconds += seconds;
  usage[hostname].category = category;

  const totalTime = (result.totalTime || 0) + seconds;
  await chrome.storage.local.set({ [key]: usage, totalTime });

  // Sync to backend (fire-and-forget)
  fetch(`${BACKEND_URL}/api/track`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hostname, seconds, category, date: today })
  }).catch(() => {}); // Backend optional
}

// ── Tab / window tracking ─────────────────────────────────────
async function onTabChange(tabId, url) {
  const now = Date.now();
  if (activeTabUrl && activeStart) {
    const elapsed = Math.round((now - activeStart) / 1000);
    await saveSegment(activeTabUrl, elapsed);
  }
  activeTabId = tabId;
  activeTabUrl = url;
  activeStart = now;
}

chrome.tabs.onActivated.addListener(async ({ tabId }) => {
  const tab = await chrome.tabs.get(tabId);
  await onTabChange(tabId, tab.url);
});

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.active) {
    await onTabChange(tabId, tab.url);
  }
});

chrome.windows.onFocusChanged.addListener(async (windowId) => {
  if (windowId === chrome.windows.WINDOW_ID_NONE) {
    if (activeTabUrl && activeStart) {
      const elapsed = Math.round((Date.now() - activeStart) / 1000);
      await saveSegment(activeTabUrl, elapsed);
      activeStart = null;
      activeTabUrl = null;
    }
  } else {
    const [tab] = await chrome.tabs.query({ active: true, windowId });
    if (tab) await onTabChange(tab.id, tab.url);
  }
});

// ── Periodic save every 30s (handles long sessions) ──────────
chrome.alarms.create('periodicSave', { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'periodicSave' && activeTabUrl && activeStart) {
    const now = Date.now();
    const elapsed = Math.round((now - activeStart) / 1000);
    await saveSegment(activeTabUrl, elapsed);
    activeStart = now; // Reset so we don't double count
  }

  if (alarm.name === 'dailyReport') {
    sendDailyNotification();
  }
});

// ── Daily 9 PM summary notification ──────────────────────────
chrome.alarms.create('dailyReport', { when: getNext9PM(), periodInMinutes: 1440 });

function getNext9PM() {
  const now = new Date();
  const next = new Date();
  next.setHours(21, 0, 0, 0);
  if (next <= now) next.setDate(next.getDate() + 1);
  return next.getTime();
}

async function sendDailyNotification() {
  const today = new Date().toISOString().split('T')[0];
  const result = await chrome.storage.local.get(`usage_${today}`);
  const usage = result[`usage_${today}`] || {};
  let productive = 0, unproductive = 0;
  Object.values(usage).forEach(v => {
    if (v.category === 'productive') productive += v.seconds;
    else if (v.category === 'unproductive') unproductive += v.seconds;
  });
  const pMin = Math.round(productive / 60);
  const uMin = Math.round(unproductive / 60);
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon128.png',
    title: '📊 ProductivityPulse Daily Report',
    message: `Today: ${pMin}m productive, ${uMin}m unproductive. Keep it up!`
  });
}

// ── Message API for popup/options ────────────────────────────
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'GET_TODAY') {
    const today = new Date().toISOString().split('T')[0];
    chrome.storage.local.get(`usage_${today}`).then(r => {
      sendResponse({ usage: r[`usage_${today}`] || {} });
    });
    return true;
  }
  if (msg.type === 'GET_WEEK') {
    getWeekData().then(data => sendResponse({ data }));
    return true;
  }
  if (msg.type === 'CLEAR_TODAY') {
    const today = new Date().toISOString().split('T')[0];
    chrome.storage.local.remove(`usage_${today}`).then(() => sendResponse({ ok: true }));
    return true;
  }
});

async function getWeekData() {
  const result = {};
  for (let i = 6; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const key = `usage_${d.toISOString().split('T')[0]}`;
    const r = await chrome.storage.local.get(key);
    const usage = r[key] || {};
    let productive = 0, unproductive = 0, neutral = 0;
    Object.values(usage).forEach(v => {
      if (v.category === 'productive') productive += v.seconds;
      else if (v.category === 'unproductive') unproductive += v.seconds;
      else neutral += v.seconds;
    });
    result[d.toISOString().split('T')[0]] = { productive, unproductive, neutral };
  }
  return result;
}
