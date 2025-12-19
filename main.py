import os
import asyncio
import aiohttp
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import init_db, get_user, add_referral, check_vip, set_vip
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID"))
REF_BONUS = float(os.getenv("REFERRAL_BONUS_USDT", 0.5))
WALLET = os.getenv("TRON_PAYOUT_ADDRESS")
init_db()

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- WEB SERVER (RAILWAY HEALTH CHECK) ---
app = Flask('')
@app.route('/')
def home(): return "Ice Gods PRO Engine: Online"
@app.route('/health')
def health(): return "OK", 200

def run_web():
    # Railway provides the PORT environment variable automatically
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- ALPHA CONTENT ENGINE ---
async def fetch_alpha_gems():
    """Fetches trending tokens with professional formatting data"""
    url = "https://api.dexscreener.com/token-boosts/latest/v1"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []
        except: return []

# --- KEYBOARDS ---
def main_menu():
    kb = [
        [InlineKeyboardButton(text="🦅 SCAN ALPHA GEMS", callback_data="alpha")],
        [InlineKeyboardButton(text="💰 BALANCE & EARN", callback_data="stats")],
        [InlineKeyboardButton(text="💎 VIP SUBSCRIPTION", callback_data="vip")],
        [InlineKeyboardButton(text="📞 SUPPORT", url="https://t.me/MexRobert")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# --- HANDLERS ---
@dp.message(CommandStart())
async def cmd_start(m: types.Message):
    user_id = m.from_user.id
    args = m.text.split()

    # Handle Referral System
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != user_id:
            add_referral(user_id, referrer_id, REF_BONUS)
            try:
                await bot.send_message(referrer_id, f"🎊 <b>New Referral!</b>\nYour balance increased by <b>{REF_BONUS} USDT</b>.", parse_mode="HTML")
            except: pass

    welcome = (
        f"👑 <b>ICE GODS MODERN BRAIN</b> 👑\n\n"
        f"Welcome <b>{m.from_user.first_name}</b>.\n"
        "We use advanced AI to find 100x Gems on Solana & ETH.\n\n"
        "💵 <b>PROMO:</b> Get 0.5 USDT for every friend you invite!"
    )
    await m.answer(welcome, parse_mode="HTML", reply_markup=main_menu())

@dp.callback_query(F.data == "alpha")
async def alpha_handler(c: types.CallbackQuery):
    # Check if user has balance or VIP
    balance, _, expiry = get_user(c.from_user.id)
    if balance < 1.0 and not check_vip(c.from_user.id):
        await c.message.answer("❌ <b>ACCESS DENIED</b>\n\nYou need at least <b>1.0 USDT</b> in your balance or an active <b>VIP Plan</b> to see live Alpha.", parse_mode="HTML")
        return

    await c.answer("Scanning Blockchain... 🦅")
    gems = await fetch_alpha_gems()

    for g in gems[:3]:
        # THE LARGE FORMAT PROFESSIONAL ALERT
        alert = (
            f"⚡️⚡️ <b>ALPHA DETECTED</b> ⚡️⚡️\n\n"
            f"💎 <b>TOKEN:</b> {g.get('header', 'Unknown').upper()}\n"
            f"📊 <b>SOURCE:</b> DexScreener Pro\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 <a href='{g.get('url')}'>VIEW LIVE CHART & ALPHA</a>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💀 <b>POWERED BY ICE GODS BRAIN</b>"
        )
        await c.message.answer(alert, parse_mode="HTML", disable_web_page_preview=True)

@dp.callback_query(F.data == "stats")
async def stats_handler(c: types.CallbackQuery):
    bal, refs, _ = get_user(c.from_user.id)
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start={c.from_user.id}"

    msg = (
        f"💵 <b>YOUR ACCOUNT STATS</b>\n\n"
        f"<b>Balance:</b> {bal} USDT\n"
        f"<b>Referrals:</b> {refs}\n\n"
        f"🎁 <b>Invite Link:</b>\n<code>{link}</code>\n\n"
        "<i>Share your link to earn USDT for VIP content!</i>"
    )
    await c.message.answer(msg, parse_mode="HTML")

@dp.callback_query(F.data == "vip")
async def vip_handler(c: types.CallbackQuery):
    msg = (
        "💎 <b>VIP ALPHA SUBSCRIPTION</b>\n\n"
        "• Unrestricted Alpha Gems\n"
        "• Whale Tracking Alerts\n"
        "• Anti-Rug Security Access\n\n"
        "💰 <b>Cost:</b> 10 USDT / Month\n"
        f"💳 <b>Wallet (TRC20):</b>\n<code>{WALLET}</code>"
    )
    await c.message.answer(msg, parse_mode="HTML")

# --- STARTUP ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    Thread(target=run_web).start()
    logging.info("Modern Brain Started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
