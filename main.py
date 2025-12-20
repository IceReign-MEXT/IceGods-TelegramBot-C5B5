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

# Web Server Routes for Hugging Face
@app.route('/')
def home(): return "Ice Gods Engine: Online"

@app.route('/health')
def health(): return "OK", 200

# Bot Setup
bot = Bot(token=TOKEN) if TOKEN else None
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    # Professional furniture layout
    div = "━━━━━━━━━━━━━━━━━━━━"
    welcome = (
        f"⚡️⚡️ <b>ICE GODS MODERN BRAIN</b> ⚡️⚡️\n"
        f"{div}\n"
        f"👋 Welcome, <b>{message.from_user.first_name}</b>\n\n"
        f"👑 <b>STATUS:</b> 🟢 ONLINE & ACTIVE\n"
        f"🦅 <b>ENGINE:</b> Alpha Hunter v4.0\n\n"
        f"<i>The brain is fully synchronized with the cloud. Your Digital Empire is ready.</i>\n"
        f"{div}"
    )
    await message.answer(welcome, parse_mode="HTML")

async def start_bot():
    if not bot:
        logging.error("TELEGRAM_BOT_TOKEN is missing in Secrets!")
        return

    # Fix the 'Conflict' error by deleting old webhooks
    logging.info("Cleaning old connections...")
    await bot.delete_webhook(drop_pending_updates=True)

    logging.info("Bot is now listening to Telegram...")
    await dp.start_polling(bot)

def run_flask():
    # Hugging Face MUST have port 7860
    app.run(host='0.0.0.0', port=7860, debug=False, use_reloader=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()

    # 1. Start Web Server in a background thread
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    # 2. Run Bot in the main thread (This is the fix)
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
