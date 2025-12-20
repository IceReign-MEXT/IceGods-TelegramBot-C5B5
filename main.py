import os
import asyncio
import logging
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from threading import Thread
from database import init_db

# --- CONFIG ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
app = Flask(__name__)

@app.route('/')
def home(): return "Ice Gods Engine: Online"

@app.route('/health')
def health(): return "OK", 200

# Bot Setup
bot = Bot(token=TOKEN) if TOKEN else None
dp = Dispatcher()

@dp.message(CommandStart())
async def start(m: types.Message):
    div = "━━━━━━━━━━━━━━━━━━━━"
    welcome = (
        f"⚡️⚡️ <b>ICE GODS MODERN BRAIN</b> ⚡️⚡️\n"
        f"{div}\n"
        f"👋 Welcome, <b>{m.from_user.first_name}</b>\n\n"
        f"👑 <b>STATUS:</b> 🟢 ONLINE & ACTIVE\n"
        f"🦅 <b>ENGINE:</b> Alpha Hunter v4.0\n\n"
        f"<i>The brain is fully synchronized. Your Digital Empire is ready.</i>\n"
        f"{div}"
    )
    await m.answer(welcome, parse_mode="HTML")

async def run_bot():
    if not bot:
        logging.error("CRITICAL: TELEGRAM_BOT_TOKEN NOT FOUND")
        return
    # Fix conflict
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Bot is now listening to Telegram...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    # Start bot in background thread
    Thread(target=lambda: asyncio.run(run_bot())).start()
    # Flask on main thread for Hugging Face port 7860
    app.run(host='0.0.0.0', port=7860)
