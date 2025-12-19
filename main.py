import os
import asyncio
import aiohttp
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import init_db, get_user, add_referral, check_vip
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID"))
REF_BONUS = float(os.getenv("REFERRAL_BONUS_USDT", 0.5))
WALLET = os.getenv("TRON_PAYOUT_ADDRESS")
init_db()

bot = Bot(token=TOKEN)
dp = Dispatcher()

app = Flask('')
@app.route('/')
def home(): return "Ice Gods PRO Engine: Online"
@app.route('/health')
def health(): return "OK", 200

def run_web():
    # Hugging Face uses port 7860
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)

async def fetch_alpha_gems():
    url = "https://api.dexscreener.com/token-boosts/latest/v1"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []
        except: return []

def main_menu():
    kb = [
        [InlineKeyboardButton(text="🦅 SCAN ALPHA GEMS", callback_data="alpha")],
        [InlineKeyboardButton(text="💰 BALANCE & EARN", callback_data="stats")],
        [InlineKeyboardButton(text="💎 VIP SUBSCRIPTION", callback_data="vip")],
        [InlineKeyboardButton(text="📞 SUPPORT", url="https://t.me/MexRobert")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

@dp.message(CommandStart())
async def cmd_start(m: types.Message):
    user_id = m.from_user.id
    args = m.text.split()
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != user_id:
            add_referral(user_id, referrer_id, REF_BONUS)
            try: await bot.send_message(referrer_id, f"🎊 <b>Referral Bonus!</b> +{REF_BONUS} USDT", parse_mode="HTML")
            except: pass

    welcome = (
        f"👑 <b>ICE GODS MODERN BRAIN</b> 👑\n\n"
        f"Welcome <b>{m.from_user.first_name}</b>.\n"
        "Earn USDT by referring and unlock elite 100x Alpha signals."
    )
    await m.answer(welcome, parse_mode="HTML", reply_markup=main_menu())

@dp.callback_query(F.data == "alpha")
async def alpha_handler(c: types.CallbackQuery):
    balance, _, _ = get_user(c.from_user.id)
    if balance < 1.0 and not check_vip(c.from_user.id):
        await c.message.answer("❌ <b>ACCESS DENIED</b>\n\nYou need 1.0 USDT or VIP to see Alpha.", parse_mode="HTML")
        return

    await c.answer("Scanning Blockchain... 🦅")
    gems = await fetch_alpha_gems()
    for g in gems[:3]:
        alert = (
            f"⚡️⚡️ <b>ALPHA DETECTED</b> ⚡️⚡️\n\n"
            f"💎 <b>TOKEN:</b> {g.get('header', 'Unknown').upper()}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 <a href='{g.get('url')}'>VIEW LIVE CHART</a>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💀 <b>POWERED BY ICE GODS BRAIN</b>"
        )
        await c.message.answer(alert, parse_mode="HTML", disable_web_page_preview=True)

@dp.callback_query(F.data == "stats")
async def stats_handler(c: types.CallbackQuery):
    bal, refs, _ = get_user(c.from_user.id)
    me = await bot.get_me()
    msg = f"💵 <b>Balance:</b> {bal} USDT\n👥 <b>Referrals:</b> {refs}\n🔗 <code>https://t.me/{me.username}?start={c.from_user.id}</code>"
    await c.message.answer(msg, parse_mode="HTML")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    Thread(target=run_web).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
