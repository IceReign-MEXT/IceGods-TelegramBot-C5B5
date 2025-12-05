import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv('DATABASE_PATH', 'bot.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        wallet TEXT,
        balance REAL DEFAULT 0,
        referrals INTEGER DEFAULT 0,
        joined_date TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        wallet TEXT,
        txid TEXT,
        status TEXT DEFAULT 'pending',
        date TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(user_id, username, wallet=''):
    if not get_user(user_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (user_id, username, wallet) VALUES (?, ?, ?)", (user_id, username, wallet))
        conn.commit()
        conn.close()

def update_balance(user_id, amount):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def get_balance(user_id):
    user = get_user(user_id)
    return user[3] if user else 0

def deduct_balance(user_id, amount):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def set_wallet(user_id, wallet):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET wallet = ? WHERE user_id=?", (wallet, user_id))
    conn.commit()
    conn.close()

def add_withdrawal(user_id, amount, wallet, txid=''):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO withdrawals (user_id, amount, wallet, txid) VALUES (?, ?, ?, ?)", (user_id, amount, wallet, txid))
    conn.commit()
    conn.close()
