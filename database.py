import asyncpg
import os
from decimal import Decimal

DATABASE_URL = os.getenv("DATABASE_URL")

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS mex_users (
            telegram_id TEXT PRIMARY KEY,
            public_key TEXT,
            private_key TEXT,
            balance DECIMAL DEFAULT 0.0,
            tier TEXT DEFAULT 'GUEST'
        )
    """)
    await conn.close()

async def get_user(user_id):
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        row = await conn.fetchrow("SELECT * FROM mex_users WHERE telegram_id=$1", str(user_id))
        await conn.close()
        return row
    except: return None

async def save_user(user_id, pub, priv):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("INSERT INTO mex_users (telegram_id, public_key, private_key) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING", str(user_id), pub, priv)
    await conn.close()
