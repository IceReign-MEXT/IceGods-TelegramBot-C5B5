import os
import asyncio
import logging
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from threading import Thread

# Config
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
app = Flask(__name__)

@app.route('/')
def home(): return "Ice Gods PRO: Online"

@app.route('/health')
def health(): return "OK", 200

# Bot Setup
bot = Bot(token=TOKEN) if TOKEN else None
dp = Dispatcher()

@dp.message(CommandStart())
async def start(m: types.Message):
    await m.answer(f"👑 <b>ICE GODS MODERN BRAIN</b>\n\nWelcome {m.from_user.first_name}.", parse_mode="HTML")

async def run_bot():
    if bot:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Bot in background
    Thread(target=lambda: asyncio.run(run_bot())).start()
    # Flask in foreground on port 7860
    app.run(host='0.0.0.0', port=7860)
