import os
import asyncio
import logging
from flask import Flask
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from threading import Thread
from database import init_db, get_user, add_referral, check_vip

# --- CONFIG ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", 0))
app = Flask(__name__)

# --- WEB SERVER (For Hugging Face Health) ---
@app.route('/')
def home(): return "Ice Gods Engine: Online"

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
        f"👑 <b>STATUS:</b> Online & Active\n"
        f"🦅 <b>ENGINE:</b> Alpha Hunter v4.0\n\n"
        f"<i>The brain is now synchronized with Hugging Face. Use the menu to hunt gems or earn USDT.</i>\n"
        f"{divider}"
    )
    # Using simple text for speed and stability
    await message.answer(welcome, parse_mode="HTML")

async def run_bot():
    if not bot:
        logging.error("CRITICAL: BOT TOKEN MISSING!")
        return

    # Force delete old webhooks to fix 'Conflict' error
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Bot starting in Polling mode...")
    await dp.start_polling(bot)

# --- EXECUTION ENGINE ---
def run_flask():
    # Hugging Face MUST have a web server on port 7860
    app.run(host='0.0.0.0', port=7860, debug=False, use_reloader=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()

    # 1. Start Flask in background thread
    server = Thread(target=run_flask)
    server.daemon = True
    server.start()

    # 2. Run Bot in Main Loop (Priority)
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
