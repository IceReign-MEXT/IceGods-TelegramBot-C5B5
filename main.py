import os
import asyncio
import logging
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from threading import Thread
from database import init_db

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIG ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Hugging Face MUST have a web server on port 7860
app = Flask(__name__)

@app.route('/')
def home():
    return "Ice Gods PRO: Online"

@app.route('/health')
def health():
    return "OK", 200

# --- BOT SETUP ---
bot = Bot(token=TOKEN) if TOKEN else None
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(m: types.Message):
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

async def start_bot_polling():
    if not bot:
        logger.error("CRITICAL: TELEGRAM_BOT_TOKEN is missing in Secrets!")
        return

    try:
        # Step 1: Force delete any old webhooks (Fixes 'Conflict' error)
        logger.info("CLEANING OLD CONNECTIONS...")
        await bot.delete_webhook(drop_pending_updates=True)

        # Step 2: Start listening to messages
        logger.info("ICE GODS BOT IS NOW LISTENING...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Polling Error: {e}")

def run_web_server():
    # Hugging Face uses port 7860
    logger.info("STARTING WEB SERVER ON PORT 7860...")
    app.run(host='0.0.0.0', port=7860, debug=False, use_reloader=False)

if __name__ == "__main__":
    init_db()

    # 1. Start the web server in a background thread
    web_thread = Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()

    # 2. Run the bot in the main thread (This prevents it from dying)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot_polling())
