import os
import asyncio
import logging
from datetime import datetime, timedelta
from collections import defaultdict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

from web3 import Web3
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey

# Environment
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ETH_MAIN_WALLET = os.environ.get("ETH_MAIN_WALLET")
SOL_MAIN_WALLET = os.environ.get("SOL_MAIN_WALLET")
ALCHEMY_ETH_RPC = os.environ.get("ALCHEMY_ETH_RPC")
ALCHEMY_SOL_RPC = os.environ.get("ALCHEMY_SOL_RPC", "https://api.mainnet-beta.solana.com")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Subscription Plans ---
SUBSCRIPTION_TIERS = {
    "12h": 20,
    "24h": 35,
    "3 days": 50,
    "weekly": 120,
    "monthly": 250,
    "quarterly": 700,
    "yearly": 1800
}

# --- Blockchain Clients ---
w3 = Web3(Web3.HTTPProvider(ALCHEMY_ETH_RPC))
sol_client = AsyncClient(ALCHEMY_SOL_RPC)

# --- In-memory user subscriptions (replace with DB for production) ---
user_subscriptions = {}  # chat_id -> {"expires": datetime, "crypto": "ETH/SOL", "amount": float}
user_paid_addresses = defaultdict(lambda: ETH_MAIN_WALLET)  # simulate unique addresses

# --- Helper Functions ---
async def check_payment(chat_id: int):
    sub = user_subscriptions.get(chat_id)
    if not sub:
        return False
    crypto, amount = sub["crypto"], sub["amount"]
    if crypto.lower() == "eth":
        balance = w3.eth.get_balance(user_paid_addresses[chat_id]) / 1e18
        return balance >= amount
    elif crypto.lower() == "sol":
        resp = await sol_client.get_balance(PublicKey(user_paid_addresses[chat_id]))
        balance = resp['result']['value'] / 1e9
        return balance >= amount
    return False

async def activate_subscription(chat_id: int, duration_hours: int):
    expires = datetime.utcnow() + timedelta(hours=duration_hours)
    user_subscriptions[chat_id] = {"expires": expires, "crypto": None, "amount": 0}
    return expires

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Subscription Plans", callback_data="plans")],
        [InlineKeyboardButton("📊 Check Status", callback_data="status")]
    ]
    await update.message.reply_text(
        "👋 Welcome to IceGods Bot! Monitor wallets and subscribe for automated sweeping.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "💰 *Subscription Plans:*\n"
    for tier, price in SUBSCRIPTION_TIERS.items():
        msg += f"{tier} → ${price}\n"
    msg += "\nAfter selecting a plan, send /pay <crypto> <plan> to generate payment instructions."
    await update.message.reply_text(msg)

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /pay <crypto> <plan>")
        return

    crypto, plan = context.args
    plan = plan.lower()
    if plan not in SUBSCRIPTION_TIERS:
        await update.message.reply_text("❌ Invalid plan. Use /plans to see options.")
        return

    amount = SUBSCRIPTION_TIERS[plan]
    user_subscriptions[chat_id] = {"expires": None, "crypto": crypto.upper(), "amount": amount}
    address = user_paid_addresses[chat_id]  # could be unique wallet per user
    await update.message.reply_text(
        f"Send {amount} {crypto.upper()} to address:\n{address}\n"
        "Once received, the bot will automatically activate your subscription."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sub = user_subscriptions.get(chat_id)
    if not sub or not sub.get("expires"):
        await update.message.reply_text("❌ No active subscription.")
    else:
        expires = sub["expires"].strftime("%Y-%m-%d %H:%M UTC")
        await update.message.reply_text(f"✅ Subscription active until {expires}.")

# --- Background task to check payments ---
async def payment_watcher(app):
    while True:
        for chat_id, sub in user_subscriptions.items():
            if sub["expires"] is None and sub["crypto"]:
                if await check_payment(chat_id):
                    duration = 24 if sub["crypto"].lower() == "eth" else 24  # Example: 24h for all
                    expires = await activate_subscription(chat_id, duration)
                    try:
                        await app.bot.send_message(chat_id, f"✅ Payment detected! Subscription active until {expires}.")
                    except Exception as e:
                        logger.error(f"Failed to notify {chat_id}: {e}")
        await asyncio.sleep(30)  # check every 30 seconds

# --- Callback Buttons ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "plans":
        await plans(update, context)
    elif query.data == "status":
        await status(update, context)

# --- Main ---
async def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plans", plans))
    app.add_handler(CommandHandler("pay", pay))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(button_handler))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    asyncio.create_task(payment_watcher(app))  # background watcher
    await asyncio.Event().wait()  # keep running

if __name__ == "__main__":
    asyncio.run(main())
