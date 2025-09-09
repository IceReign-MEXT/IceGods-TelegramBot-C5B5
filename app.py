# app.py - simple Flask subscription API (demo)
import os
import sqlite3
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

DB_PATH = os.getenv("DATABASE_PATH", "subscriptions.db")

# init DB
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS subscriptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  telegram_id TEXT,
  plan TEXT,
  start_ts INTEGER,
  expires_ts INTEGER
)
""")
conn.commit()

app = Flask(__name__)

PLAN_SECONDS = {
    "1h": 3600,
    "1d": 86400,
    "1w": 604800,
    "1m": 2592000
}

@app.route("/")
def index():
    return jsonify({"ok": True, "note": "Subscription API running"})

@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.json or {}
    tg = data.get("telegram_id")
    plan = data.get("plan")
    if not tg or plan not in PLAN_SECONDS:
        return jsonify({"error": "telegram_id and valid plan required"}), 400
    now = int(datetime.utcnow().timestamp())
    expires = now + PLAN_SECONDS[plan]
    c.execute("INSERT INTO subscriptions (telegram_id, plan, start_ts, expires_ts) VALUES (?, ?, ?, ?)",
              (str(tg), plan, now, expires))
    conn.commit()
    return jsonify({"ok": True, "telegram_id": tg, "plan": plan, "expires": expires})

@app.route("/status/<telegram_id>", methods=["GET"])
def status(telegram_id):
    c.execute("SELECT plan, start_ts, expires_ts FROM subscriptions WHERE telegram_id=? ORDER BY id DESC LIMIT 1", (telegram_id,))
    row = c.fetchone()
    if not row:
        return jsonify({"active": False})
    plan, start_ts, expires_ts = row
    active = int(datetime.utcnow().timestamp()) < expires_ts
    return jsonify({"active": active, "plan": plan, "expires_ts": expires_ts})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
