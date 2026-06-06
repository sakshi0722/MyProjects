"""
ProductivityPulse — FastAPI Backend
Stores usage data in SQLite, exposes REST API for analytics
Run: uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from typing import Optional
import sqlite3
import os

# ── App setup ────────────────────────────────────────────────
app = FastAPI(title="ProductivityPulse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Chrome extension origin
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "productivity.db"

# ── DB init ───────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hostname TEXT NOT NULL,
            seconds INTEGER NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('productive','unproductive','neutral')),
            date TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON usage(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hostname ON usage(hostname)")
    conn.commit()
    conn.close()

init_db()

# ── Models ────────────────────────────────────────────────────
class TrackRequest(BaseModel):
    hostname: str
    seconds: int
    category: str
    date: str

class DailyGoal(BaseModel):
    goal_minutes: int
    date: Optional[str] = None

# ── Routes ────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "service": "ProductivityPulse API"}

@app.post("/api/track")
def track_usage(req: TrackRequest):
    """Receive a time tracking segment from the extension."""
    if req.seconds < 1:
        raise HTTPException(400, "seconds must be >= 1")
    if req.category not in ("productive", "unproductive", "neutral"):
        raise HTTPException(400, "invalid category")

    conn = get_db()
    # Upsert: add to existing row if same hostname+date exists
    existing = conn.execute(
        "SELECT id, seconds FROM usage WHERE hostname=? AND date=?",
        (req.hostname, req.date)
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE usage SET seconds=? WHERE id=?",
            (existing["seconds"] + req.seconds, existing["id"])
        )
    else:
        conn.execute(
            "INSERT INTO usage (hostname, seconds, category, date) VALUES (?,?,?,?)",
            (req.hostname, req.seconds, req.category, req.date)
        )
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/today")
def get_today():
    """Get today's aggregated usage."""
    today = str(date.today())
    conn = get_db()
    rows = conn.execute(
        "SELECT hostname, seconds, category FROM usage WHERE date=? ORDER BY seconds DESC",
        (today,)
    ).fetchall()
    conn.close()
    return {
        "date": today,
        "sites": [dict(r) for r in rows],
        "summary": _summarize(rows)
    }

@app.get("/api/week")
def get_week():
    """Get last 7 days grouped by date."""
    result = {}
    conn = get_db()
    for i in range(6, -1, -1):
        d = str(date.today() - timedelta(days=i))
        rows = conn.execute(
            "SELECT category, SUM(seconds) as total FROM usage WHERE date=? GROUP BY category",
            (d,)
        ).fetchall()
        result[d] = {"productive": 0, "unproductive": 0, "neutral": 0}
        for r in rows:
            result[d][r["category"]] = r["total"]
    conn.close()
    return result

@app.get("/api/stats")
def get_stats():
    """Overall stats."""
    conn = get_db()
    total_days = conn.execute("SELECT COUNT(DISTINCT date) as c FROM usage").fetchone()["c"]
    top_sites = conn.execute("""
        SELECT hostname, category, SUM(seconds) as total
        FROM usage GROUP BY hostname ORDER BY total DESC LIMIT 10
    """).fetchall()
    weekly_avg = conn.execute("""
        SELECT category, AVG(daily) as avg FROM (
            SELECT date, category, SUM(seconds) as daily
            FROM usage GROUP BY date, category
        ) GROUP BY category
    """).fetchall()
    conn.close()
    return {
        "total_days_tracked": total_days,
        "top_sites": [dict(r) for r in top_sites],
        "weekly_avg": {r["category"]: round(r["avg"]) for r in weekly_avg}
    }

@app.delete("/api/today")
def clear_today():
    """Clear today's data."""
    today = str(date.today())
    conn = get_db()
    conn.execute("DELETE FROM usage WHERE date=?", (today,))
    conn.commit()
    conn.close()
    return {"ok": True, "cleared": today}

@app.get("/api/export")
def export_csv():
    """Export all data as CSV text."""
    conn = get_db()
    rows = conn.execute("SELECT date, hostname, category, seconds FROM usage ORDER BY date DESC, seconds DESC").fetchall()
    conn.close()
    lines = ["date,hostname,category,seconds"]
    lines += [f"{r['date']},{r['hostname']},{r['category']},{r['seconds']}" for r in rows]
    return "\n".join(lines)

# ── Helper ────────────────────────────────────────────────────
def _summarize(rows):
    summary = {"productive": 0, "unproductive": 0, "neutral": 0, "total": 0}
    for r in rows:
        summary[r["category"]] = summary.get(r["category"], 0) + r["seconds"]
        summary["total"] += r["seconds"]
    p, u = summary["productive"], summary["unproductive"]
    summary["score"] = round((p / (p + u + 1)) * 100)
    return summary
