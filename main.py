import os
import asyncio
import logging
import socket
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from threading import Thread
from database import init_db

# --- CONFIG ---
# Hugging Face Secrets will fill this
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
app = Flask(__name__)

# --- WEB SERVER (For Hugging Face Health) ---
@app.route('/')
def home(): return "Ice Gods Engine: Active"

@app.route('/health')
def health(): return "OK", 200

# --- BOT SETUP ---
bot = Bot(token=TOKEN) if TOKEN else None
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    # Professional Furniture Layout
    divider = "━━━━━━━━━━━━━━━━━━━━"
    welcome = (
        f"⚡️⚡️ <b>ICE GODS MODERN BRAIN</b> ⚡️⚡️\n"
        f"{divider}\n"
        f"👋 Welcome, <b>{message.from_user.first_name}</b>\n\n"
        f"👑 <b>STATUS:</b> 🟢 ONLINE & ACTIVE\n"
        f"🦅 <b>ENGINE:</b> Alpha Hunter v4.0\n\n"
        f"<i>The brain is fully synchronized with the new secure token. Digital Empire is LIVE.</i>\n"
        f"{divider}"
    )
    await message.answer(welcome, parse_mode="HTML")

async def run_bot():
    if not bot:
        logging.error("CRITICAL: NEW TELEGRAM_BOT_TOKEN NOT FOUND IN SECRETS!")
        return

    # --- THE INTERNET WAIT FIX ---
    logging.info("Checking network connectivity...")
    while True:
        try:
            # Check if we can resolve Telegram's address
            socket.create_connection(("api.telegram.org", 443), timeout=5)
            logging.info("✅ Internet detected! Bot waking up...")
            break
        except OSError:
            logging.error("⏳ DNS/Network not ready. Retrying in 5 seconds...")
            await asyncio.sleep(5)

    # Force delete old webhooks to clear any conflicts
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("SUCCESS: Bot is now listening to Telegram!")
    await dp.start_polling(bot)

def start_flask():
    # Hugging Face MUST have this running on 7860
    app.run(host='0.0.0.0', port=7860, debug=False, use_reloader=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()

    # 1. Start Flask in background
    flask_thread = Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # 2. Start Bot in Main Thread (with retry logic)
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
