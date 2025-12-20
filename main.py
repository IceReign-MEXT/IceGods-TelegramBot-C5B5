import os
import asyncio
import logging
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from threading import Thread

# --- CONFIG ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# We use Flask to keep Hugging Face happy on Port 7860
app = Flask(__name__)

@app.route('/')
def home():
    return "Ice Gods Engine: Active"

@app.route('/health')
def health():
    return "OK", 200

# --- BOT SETUP ---
bot = Bot(token=TOKEN) if TOKEN else None
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    divider = "━━━━━━━━━━━━━━━━━━━━"
    welcome = (
        f"⚡️⚡️ <b>ICE GODS MODERN BRAIN</b> ⚡️⚡️\n"
        f"{divider}\n"
        f"👋 Welcome, <b>{message.from_user.first_name}</b>\n\n"
        f"👑 <b>STATUS:</b> 🟢 ONLINE & PROTECTED\n"
        f"🦅 <b>HOSTING:</b> Hugging Face Dedicated\n\n"
        f"<i>The brain is now fully synchronized. Your Digital Empire is ready.</i>\n"
        f"{divider}"
    )
    await message.answer(welcome, parse_mode="HTML")

async def run_bot():
    if not bot:
        logging.error("CRITICAL: TELEGRAM_BOT_TOKEN IS MISSING IN SECRETS!")
        return

    # --- THIS IS THE FIX ---
    logging.info("CLEANING OLD CONNECTIONS...")
    await bot.delete_webhook(drop_pending_updates=True)
    # This removes any old "Webhook" block so Polling can start

    logging.info("ICE GODS BOT IS NOW LISTENING...")
    await dp.start_polling(bot)

def start_flask():
    # Hugging Face MUST have this running on 7860
    app.run(host='0.0.0.0', port=7860, debug=False, use_reloader=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 1. Start Web Server in background
    flask_thread = Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # 2. Run Bot in Main Thread
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_bot())
    except Exception as e:
        logging.error(f"Bot Error: {e}")
