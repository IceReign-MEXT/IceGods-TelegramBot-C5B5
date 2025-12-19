import os
import asyncio
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

# --- CONFIG FROM YOUR .ENV ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID"))
REF_BONUS = float(os.getenv("REFERRAL_BONUS_USDT", 0.5))
MIN_WD = float(os.getenv("MIN_WITHDRAWAL", 5.0))
WALLET = os.getenv("TRON_PAYOUT_ADDRESS")

init_db()
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- WEB SERVER (For Hugging Face) ---
app = Flask('')
@app.route('/')
def home(): return "Ice Gods PRO: Online"
@app.route('/health')
def health(): return "OK", 200

def run_web():
    # Hugging Face Spaces port
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)

# --- KEYBOARDS ---
def main_menu():
    kb = [
        [InlineKeyboardButton(text="🦅 SCAN ALPHA GEMS", callback_data="alpha")],
        [InlineKeyboardButton(text="💰 BALANCE & EARN", callback_data="stats")],
        [InlineKeyboardButton(text="💳 WITHDRAW USDT", callback_data="withdraw")],
        [InlineKeyboardButton(text="📞 SUPPORT", url="https://t.me/MexRobert")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# --- HANDLERS ---
@dp.message(CommandStart())
async def cmd_start(m: types.Message):
    user_id = m.from_user.id
    args = m.text.split()
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != user_id:
            add_referral(user_id, referrer_id, REF_BONUS)
            try: await bot.send_message(referrer_id, f"🎊 <b>Referral Bonus!</b>\nYour account was credited with {REF_BONUS} USDT.", parse_mode="HTML")
            except: pass

    welcome = (
        f"👑 <b>ICE GODS MODERN BRAIN</b> 👑\n\n"
        f"Welcome <b>{m.from_user.first_name}</b>.\n"
        f"Earn <b>{REF_BONUS} USDT</b> for every friend you invite. Use your balance to unlock elite Alpha signals.\n\n"
        f"🚀 <b>Min. Withdrawal:</b> {MIN_WD} USDT"
    )
    await m.answer(welcome, parse_mode="HTML", reply_markup=main_menu())

@dp.callback_query(F.data == "stats")
async def stats(c: types.CallbackQuery):
    bal, refs, _ = get_user(c.from_user.id)
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start={c.from_user.id}"
    msg = (
        f"💵 <b>YOUR ACCOUNT STATS</b>\n\n"
        f"<b>Balance:</b> {bal} USDT\n"
        f"<b>Total Referrals:</b> {refs}\n\n"
        f"🔗 <b>Invite Link:</b>\n<code>{link}</code>"
    )
    await c.message.answer(msg, parse_mode="HTML")

@dp.callback_query(F.data == "withdraw")
async def withdraw(c: types.CallbackQuery):
    bal, _, _ = get_user(c.from_user.id)
    if bal < MIN_WD:
        await c.answer(f"❌ Minimum withdrawal is {MIN_WD} USDT.", show_alert=True)
    else:
        await c.message.answer(f"✅ <b>Withdrawal Request</b>\n\nSend your TRC20 address to @MexRobert to process your <b>{bal} USDT</b> payout.", parse_mode="HTML")

@dp.callback_query(F.data == "alpha")
async def alpha_handler(c: types.CallbackQuery):
    # (DexScreener API logic from previous message)
    await c.answer("Scanning Blockchain... 🦅")
    await c.message.answer("🔥 <b>LATEST ALPHA GEMS:</b>\n\n[Displaying Trending Tokens...]")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    Thread(target=run_web).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
