# ⚡ ProductivityPulse — Chrome Extension

> An advanced full-stack productivity tracker built with Chrome Extension (MV3) + FastAPI + SQLite.

---

## 📁 Project Structure

```
chrome-extension/
├── extension/              ← Chrome Extension (load this in Chrome)
│   ├── manifest.json
│   ├── background.js       ← Service worker: tracks time, classifies sites
│   ├── content.js          ← Detects user activity / idle state
│   ├── popup.html/js       ← Main popup UI (380px)
│   ├── report.html         ← Full analytics page
│   ├── options.html        ← Settings page
│   └── blocked.html        ← Focus mode block page
└── backend/                ← FastAPI REST API (optional, for persistent storage)
    ├── main.py
    └── requirements.txt
```

---

## 🚀 How to Load the Extension in Chrome

1. Open Chrome → go to `chrome://extensions/`
2. Enable **Developer Mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the `extension/` folder
5. Pin the extension from the toolbar — you're live! ✅

> **Note:** The extension works fully without the backend. The backend adds persistent server-side storage and export features.

---

## 🔧 Backend Setup (Optional)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

API runs at `http://localhost:8000`

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/track` | Receive tracking data from extension |
| GET | `/api/today` | Today's usage summary |
| GET | `/api/week` | Last 7 days breakdown |
| GET | `/api/stats` | All-time stats & top sites |
| DELETE | `/api/today` | Clear today's data |
| GET | `/api/export` | Export all data as CSV |

---

## ✨ Features

### Extension
- ✅ **Real-time tracking** — logs time spent per domain
- ✅ **Smart classification** — auto-labels sites as Productive / Unproductive / Neutral
- ✅ **Productivity Score** — animated ring showing your daily score (0–100)
- ✅ **Focus Mode** — one-click toggle to block unproductive sites
- ✅ **Weekly bar chart** — see your 7-day productivity trend
- ✅ **AI Insights** — personalized tips based on your browsing patterns
- ✅ **Daily notification** — 9 PM summary of your day
- ✅ **Full Report page** — detailed analytics in a full browser tab
- ✅ **Settings page** — custom block lists, daily goals, notification prefs

### Backend
- ✅ **FastAPI REST API** — fast, async, auto-documented at `/docs`
- ✅ **SQLite storage** — lightweight, zero-config database
- ✅ **CSV export** — download all your data
- ✅ **CORS enabled** — works with the extension out of the box

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Extension | Chrome MV3, Vanilla JS, Chrome Storage API |
| Background | Service Worker, Chrome Alarms API |
| Backend | Python, FastAPI, Uvicorn |
| Database | SQLite (via Python sqlite3) |
| Styling | Pure CSS (dark theme, no frameworks) |

---

## 📸 Pages

- **Popup** — Score ring, stats, top sites list, weekly chart, focus mode toggle
- **Full Report** — Donut chart, weekly bar chart, full site table with usage bars
- **Settings** — Daily goal, focus mode, custom blocked sites, notification toggle
- **Blocked Page** — Shown when focus mode blocks a site

---

## 💡 How to Add More Productive/Unproductive Sites

Edit `background.js`:

```js
const PRODUCTIVE_SITES = [
  'github.com', 'stackoverflow.com', // add more here
];

const UNPRODUCTIVE_SITES = [
  'youtube.com', 'reddit.com', // add more here
];
```

Or add custom blocked sites via the Settings page in the extension.

---

Built with ❤️ — Perfect for your resume as a full-stack Chrome Extension project!
