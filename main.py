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
def home(): return "Ice Gods Engine: Active"

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
        f"<i>Connection established successfully via Hugging Face.</i>\n"
        f"{div}"
    )
    await m.answer(welcome, parse_mode="HTML")

async def run_bot():
    if not bot:
        logging.error("CRITICAL: TELEGRAM_BOT_TOKEN NOT FOUND")
        return

    # --- RETRY LOGIC FOR DNS ERRORS ---
    retry_count = 0
    while retry_count < 10:
        try:
            logging.info(f"Attempting to connect to Telegram (Attempt {retry_count + 1})...")
            await bot.delete_webhook(drop_pending_updates=True)
            logging.info("✅ SUCCESS: Bot is now listening to Telegram!")
            await dp.start_polling(bot)
            break # Exit loop if successful
        except Exception as e:
            retry_count += 1
            logging.error(f"❌ Network not ready. Retrying in 5 seconds... ({e})")
            await asyncio.sleep(5)

    if retry_count == 10:
        logging.error("FATAL: Could not connect to Telegram after 10 attempts.")

def start_flask():
    # Hugging Face MUST have this running on 7860
    app.run(host='0.0.0.0', port=7860, debug=False, use_reloader=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()

    # 1. Start Flask in background thread
    flask_thread = Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # 2. Start Bot in Main Thread (with retry logic)
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
