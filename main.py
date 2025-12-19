import os
import asyncio
import aiohttp
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import init_db, get_user, add_referral, check_vip
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

# --- WEB SERVER (For Hugging Face / 7860) ---
app = Flask('')
@app.route('/')
def home(): return "Ice Gods PRO Engine: Online"
@app.route('/health')
def health(): return "OK", 200

def run_web():
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)

# --- THE "FURNITURE" (Aesthetics & Formatters) ---
DIVIDER = "━━━━━━━━━━━━━━━━━━━━"

async def fetch_alpha_gems():
    url = "https://api.dexscreener.com/token-boosts/latest/v1"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []
        except: return []

# --- KEYBOARDS (Professional Icons) ---
def main_menu():
    kb = [
        [InlineKeyboardButton(text="🦅 SCAN ALPHA GEMS", callback_data="alpha")],
        [InlineKeyboardButton(text="💰 BALANCE & EARN", callback_data="stats")],
        [InlineKeyboardButton(text="💎 VIP SUBSCRIPTION", callback_data="vip")],
        [InlineKeyboardButton(text="📞 SUPPORT / CONTACT", url="https://t.me/MexRobert")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# --- HANDLERS ---
@dp.message(CommandStart())
async def cmd_start(m: types.Message):
    user_id = m.from_user.id
    args = m.text.split()
    if len(args) > 1 and args[1].isdigit():
        add_referral(user_id, int(args[1]), REF_BONUS)

    # WELCOME FURNITURE
    welcome = (
        f"⚡️⚡️ <b>ICE GODS MODERN BRAIN</b> ⚡️⚡️\n"
        f"{DIVIDER}\n"
        f"👋 Welcome, <b>{m.from_user.first_name}</b>\n\n"
        f"👑 <b>STATUS:</b> User Console\n"
        f"💵 <b>REWARD:</b> {REF_BONUS} USDT per Invite\n"
        f"🦅 <b>ENGINE:</b> High-Speed Alpha v4.0\n\n"
        f"<i>Unlock the most professional Solana/ETH hunter in the market. Earn or Buy access below.</i>\n"
        f"{DIVIDER}"
    )
    await message_with_photo(m, welcome, main_menu())

async def message_with_photo(m, text, kb):
    # Optional: Add your banner URL here for even better "Furniture"
    banner_url = "https://your-image-url.com/ice-banner.jpg"
    try:
        await m.answer(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        await m.answer(text, parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data == "alpha")
async def alpha_handler(c: types.CallbackQuery):
    balance, _, _ = get_user(c.from_user.id)
    if balance < 1.0 and not check_vip(c.from_user.id):
        await c.message.answer(
            f"❌ <b>ACCESS DENIED</b>\n"
            f"{DIVIDER}\n"
            f"Your current balance is insufficient to unlock the <b>Live Alpha Feed</b>.\n\n"
            f"🎁 <b>FREE OPTION:</b> Invite 3 friends\n"
            f"💎 <b>VIP OPTION:</b> Upgrade to PRO\n"
            f"{DIVIDER}", parse_mode="HTML")
        return

    await c.answer("Scanning Multi-Chain Alpha... 🦅")
    gems = await fetch_alpha_gems()
    for g in gems[:3]:
        # THE "LARGE FORMAT" ALERT FURNITURE
        alert = (
            f"⚡️⚡️ <b>ALPHA DETECTED</b> ⚡️⚡️\n"
            f"<b>MODE:</b> Smart-Money Tracker\n"
            f"{DIVIDER}\n"
            f"💎 <b>TOKEN:</b> {g.get('header', 'Unknown').upper()}\n"
            f"📊 <b>SOURCE:</b> DexScreener Pro\n"
            f"🕒 <b>TIME:</b> {datetime.now().strftime('%H:%M:%S')}\n"
            f"{DIVIDER}\n\n"
            f"🔗 <a href='{g.get('url')}'><b>[ OPEN LIVE ALPHA CHART ]</b></a>\n\n"
            f"💀 <b>POWERED BY ICE GODS MODERN BRAIN</b>"
        )
        await c.message.answer(alert, parse_mode="HTML", disable_web_page_preview=True)

@dp.callback_query(F.data == "stats")
async def stats_handler(c: types.CallbackQuery):
    bal, refs, _ = get_user(c.from_user.id)
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start={c.from_user.id}"

    msg = (
        f"💵 <b>ACCOUNT LEDGER</b>\n"
        f"{DIVIDER}\n"
        f"👤 <b>USER:</b> {c.from_user.first_name}\n"
        f"💰 <b>BALANCE:</b> {bal} USDT\n"
        f"👥 <b>REFERRALS:</b> {refs}\n"
        f"{DIVIDER}\n\n"
        f"🎁 <b>YOUR INVITE LINK:</b>\n"
        f"<code>{link}</code>"
    )
    await c.message.answer(msg, parse_mode="HTML")

@dp.callback_query(F.data == "vip")
async def vip_handler(c: types.CallbackQuery):
    msg = (
        f"💎 <b>VIP ELITE UPGRADE</b>\n"
        f"{DIVIDER}\n"
        f"• Unrestricted Alpha Gems\n"
        f"• Direct Whale Wallet Alerts\n"
        f"• Priority Support 24/7\n"
        f"{DIVIDER}\n\n"
        f"💰 <b>COST:</b> 10 USDT / Month\n"
        f"💳 <b>WALLET (TRC20):</b>\n"
        f"<code>{WALLET}</code>"
    )
    await c.message.answer(msg, parse_mode="HTML")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    Thread(target=run_web).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
