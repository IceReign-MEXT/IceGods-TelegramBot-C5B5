import os
import sqlite3
import time
from datetime import datetime

DB_PATH = os.getenv("DATABASE_PATH", "subscriptions.db")
conn = None

def init_db():
    global conn
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    # subscriptions table
    c.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      telegram_id TEXT,
      plan TEXT,
      start_ts INTEGER,
      expires_ts INTEGER
    )
    """)
    # payments table: records confirmed payments
    c.execute("""
    CREATE TABLE IF NOT EXISTS payments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      telegram_id TEXT,
      tx_hash TEXT,
      chain TEXT,
      amount REAL,
      plan TEXT,
      status TEXT,
      ts INTEGER
    )
    """)
    # pending payment requests (expected amounts). We'll match incoming txs against these entries.
    c.execute("""
    CREATE TABLE IF NOT EXISTS pending_payments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      telegram_id TEXT,
      plan TEXT,
      chain TEXT,
      expected_amount REAL,
      created_ts INTEGER,
      processed INTEGER DEFAULT 0
    )
    """)
    # user wallets to monitor
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_wallets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      telegram_id TEXT,
      address TEXT,
      created_ts INTEGER
    )
    """)
    conn.commit()

def add_subscription(telegram_id, plan, start_ts, expires_ts):
    c = conn.cursor()
    c.execute("INSERT INTO subscriptions (telegram_id, plan, start_ts, expires_ts) VALUES (?, ?, ?, ?)",
              (telegram_id, plan, int(start_ts), int(expires_ts)))
    conn.commit()
    return c.lastrowid

def get_latest_subscription(telegram_id):
    c = conn.cursor()
    c.execute("SELECT id, plan, start_ts, expires_ts FROM subscriptions WHERE telegram_id=? ORDER BY id DESC LIMIT 1",
              (telegram_id,))
    row = c.fetchone()
    if not row:
        return None
    return {"id": row[0], "plan": row[1], "start_ts": row[2], "expires_ts": row[3]}

def add_payment_record(telegram_id, tx_hash, chain, amount, plan, status):
    c = conn.cursor()
    c.execute("INSERT INTO payments (telegram_id, tx_hash, chain, amount, plan, status, ts) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (telegram_id, tx_hash, chain, amount, plan, status, int(time.time())))
    conn.commit()
    return c.lastrowid

def add_pending_payment_request(telegram_id, plan, chain, expected_amount):
    c = conn.cursor()
    c.execute("INSERT INTO pending_payments (telegram_id, plan, chain, expected_amount, created_ts) VALUES (?, ?, ?, ?, ?)",
              (telegram_id, plan, chain, float(expected_amount), int(time.time())))
    conn.commit()
    return c.lastrowid

def get_pending_payment_requests(chain=None):
    c = conn.cursor()
    if chain:
        c.execute("SELECT id, telegram_id, plan, chain, expected_amount FROM pending_payments WHERE processed=0 AND chain=?",
                  (chain,))
    else:
        c.execute("SELECT id, telegram_id, plan, chain, expected_amount FROM pending_payments WHERE processed=0")
    rows = c.fetchall()
    return [{"id": r[0], "telegram_id": r[1], "plan": r[2], "chain": r[3], "expected_amount": r[4]} for r in rows]

def mark_payment_processed(pending_id):
    c = conn.cursor()
    c.execute("UPDATE pending_payments SET processed=1 WHERE id=?", (pending_id,))
    conn.commit()

def add_user_wallet(telegram_id, address):
    c = conn.cursor()
    c.execute("INSERT INTO user_wallets (telegram_id, address, created_ts) VALUES (?, ?, ?)",
              (telegram_id, address, int(time.time())))
    conn.commit()

def get_user_wallets(telegram_id):
    c = conn.cursor()
    c.execute("SELECT address FROM user_wallets WHERE telegram_id=?", (telegram_id,))
    return [r[0] for r in c.fetchall()]