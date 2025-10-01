import os, sqlite3, time
DB_PATH = os.getenv("DATABASE_PATH", "subscriptions.db")
conn = None

def init_db():
    global conn
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS subscriptions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      telegram_id TEXT, plan TEXT, start_ts INTEGER, expires_ts INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS payments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      telegram_id TEXT, tx_hash TEXT, chain TEXT, amount REAL,
      plan TEXT, status TEXT, ts INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS pending_payments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      telegram_id TEXT, plan TEXT, chain TEXT,
      expected_amount REAL, created_ts INTEGER, processed INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS user_wallets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      telegram_id TEXT, address TEXT, created_ts INTEGER)""")
    conn.commit()

def add_subscription(tg, plan, start, end):
    c = conn.cursor()
    c.execute("INSERT INTO subscriptions (telegram_id, plan, start_ts, expires_ts) VALUES (?,?,?,?)",
              (tg, plan, start, end))
    conn.commit()

def get_latest_subscription(tg):
    c = conn.cursor()
    c.execute("SELECT plan,start_ts,expires_ts FROM subscriptions WHERE telegram_id=? ORDER BY id DESC LIMIT 1",(tg,))
    row = c.fetchone()
    return None if not row else {"plan": row[0], "start_ts": row[1], "expires_ts": row[2]}

def add_payment_record(tg, tx, chain, amount, plan, status):
    c = conn.cursor()
    c.execute("INSERT INTO payments (telegram_id, tx_hash, chain, amount, plan, status, ts) VALUES (?,?,?,?,?,?,?)",
              (tg, tx, chain, amount, plan, status, int(time.time())))
    conn.commit()

def add_pending_payment_request(tg, plan, chain, amt):
    c = conn.cursor()
    c.execute("INSERT INTO pending_payments (telegram_id, plan, chain, expected_amount, created_ts) VALUES (?,?,?,?,?)",
              (tg, plan, chain, amt, int(time.time())))
    conn.commit()

def get_pending_payment_requests(chain=None):
    c = conn.cursor()
    if chain:
        c.execute("SELECT id,telegram_id,plan,chain,expected_amount FROM pending_payments WHERE processed=0 AND chain=?",(chain,))
    else:
        c.execute("SELECT id,telegram_id,plan,chain,expected_amount FROM pending_payments WHERE processed=0")
    return [{"id":r[0],"telegram_id":r[1],"plan":r[2],"chain":r[3],"expected_amount":r[4]} for r in c.fetchall()]

def mark_payment_processed(pid):
    c = conn.cursor()
    c.execute("UPDATE pending_payments SET processed=1 WHERE id=?", (pid,))
    conn.commit()