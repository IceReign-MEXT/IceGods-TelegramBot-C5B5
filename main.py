import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import init_db, get_user, add_referral, set_vip
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
init_db()
bot = Bot(token=TOKEN)
dp = Dispatcher()

app = Flask('')
@app.route('/')
def home(): return "Ice Gods PRO: Online"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

async def fetch_alpha():
    url = "https://api.dexscreener.com/token-boosts/latest/v1"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                return data[:3]
        except: return []

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🦅 SCAN ALPHA GEMS", callback_data="alpha")],
        [InlineKeyboardButton(text="💰 BALANCE & REFER", callback_data="stats")],
        [InlineKeyboardButton(text="💎 BUY VIP ACCESS", callback_data="vip")]
    ])

@dp.message(CommandStart())
async def start(m: types.Message):
    args = m.text.split()
    if len(args) > 1 and args[1].isdigit():
        add_referral(m.from_user.id, int(args[1]), 0.5)

    msg = (
        f"👑 <b>ICE GODS MODERN BRAIN</b> 👑\n\n"
        f"Welcome, {m.from_user.first_name}.\n"
        "Earn USDT by referring and unlock elite 100x Alpha signals."
    )
    await m.answer(msg, parse_mode="HTML", reply_markup=main_kb())

@dp.callback_query(F.data == "alpha")
async def alpha_handler(c: types.CallbackQuery):
    await c.answer("Scanning Blockchain...")
    gems = await fetch_alpha()
    for g in gems:
        alert = (
            f"⚡️⚡️ <b>LARGE ALPHA DETECTED</b> ⚡️⚡️\n\n"
            f"💎 <b>TOKEN:</b> {g.get('header', 'Unknown').upper()}\n"
            f"📊 <b>SOURCE:</b> DexScreener\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 <a href='{g.get('url')}'>VIEW LIVE CHART</a>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💀 <b>POWERED BY ICE GODS</b>"
        )
        await c.message.answer(alert, parse_mode="HTML", disable_web_page_preview=True)

@dp.callback_query(F.data == "stats")
async def stats(c: types.CallbackQuery):
    bal, refs, _ = get_user(c.from_user.id)
    me = await bot.get_me()
    await c.message.answer(f"💵 <b>Balance:</b> {bal} USDT\n👥 <b>Referrals:</b> {refs}\n\n🔗 <code>https://t.me/{me.username}?start={c.from_user.id}</code>", parse_mode="HTML")

async def main():
    Thread(target=run_web).start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
