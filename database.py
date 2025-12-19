import sqlite3
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('ice_gods.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  balance REAL DEFAULT 0.0,
                  referrals INTEGER DEFAULT 0,
                  vip_expiry TEXT)''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('ice_gods.db')
    c = conn.cursor()
    c.execute("SELECT balance, referrals, vip_expiry FROM users WHERE user_id = ?", (user_id,))
    res = c.fetchone()
    conn.close()
    return res if res else (0.0, 0, None)

def add_referral(user_id, ref_id, bonus):
    conn = sqlite3.connect('ice_gods.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    if c.rowcount > 0 and ref_id:
        c.execute("UPDATE users SET balance = balance + ?, referrals = referrals + 1 WHERE user_id = ?", (bonus, ref_id))
    conn.commit()
    conn.close()

def set_vip(user_id, hours=24):
    conn = sqlite3.connect('ice_gods.db')
    c = conn.cursor()
    expiry = (datetime.now() + timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
    c.execute("UPDATE users SET vip_expiry = ? WHERE user_id = ?", (expiry, user_id))
    conn.commit()
    conn.close()
