import os
import time
import json
import requests
from datetime import datetime
from payments import get_prices_usd, record_payment_check_request, PAYMENT_TOLERANCE
from db import add_subscription, add_payment_record, get_latest_subscription, add_user_wallet, get_user_wallets
from telegram import Bot, Update

BOT = None

PLANS_USD = {
    "weekly": 16,
    "monthly": 60,
    "yearly": 600
}

def init_bot_objects(bot: Bot):
    global BOT
    BOT = bot

def _send(chat_id, text, parse_mode=None):
    try:
        BOT.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
    except Exception as e:
        print("Failed to send message:", e)

def handle_text_command(bot: Bot, update: Update):
    """Simple dispatcher for messages — runs in a separate thread for webhook."""
    if not update.message:
        return
    chat_id = update.effective_chat.id
    text = update.message.text or ""
    parts = text.strip().split()
    cmd = parts[0].lower()

    if cmd == "/start":
        _cmd_start(chat_id)
    elif cmd == "/pricing":
        _cmd_pricing(chat_id)
    elif cmd == "/payment":
        arg = parts[1] if len(parts) > 1 else None
        _cmd_payment(chat_id, arg)
    elif cmd == "/addwallet":
        addr = parts[1] if len(parts) > 1 else None
        _cmd_addwallet(chat_id, addr)
    elif cmd == "/status":
        _cmd_status(chat_id)
    elif cmd == "/support":
        _cmd_support(chat_id)
    elif cmd == "/whitepaper":
        _cmd_whitepaper(chat_id)
    else:
        _send(chat_id, "I didn't understand that. Use /start to see commands.")

def _cmd_start(chat_id):
    text = (
        "👋 Welcome to YieldForge (IceGods)\n\n"
        "Commands:\n"
        "/pricing - View subscription plans\n"
        "/payment <weekly|monthly|yearly> - Get payment address & amount\n"
        "/addwallet <address> - Add wallet to monitor (after subscription)\n"
        "/status - Check your subscription status\n"
        "/support - Contact admin\n"
        "/whitepaper - Platform docs\n"
    )
    _send(chat_id, text)

def _cmd_pricing(chat_id):
    try:
        prices = get_prices_usd()
        eth_price = prices["ETH"]
        sol_price = prices["SOL"]
    except Exception as e:
        print("price fetch error", e)
        _send(chat_id, "Unable to fetch prices right now. Try again in a minute.")
        return

    text = "💰 Subscription Plans (equivalents in ETH / SOL):\n\n"
    for name, usd in PLANS_USD.items():
        eth_amt = usd / eth_price
        sol_amt = usd / sol_price
        text += f"{name.capitalize()}: ${usd} → {eth_amt:.6f} ETH / {sol_amt:.6f} SOL\n"
    _send(chat_id, text)

def _cmd_payment(chat_id, plan_arg):
    if not plan_arg:
        _send(chat_id, "Usage: /payment <weekly|monthly|yearly>")
        return
    plan = plan_arg.lower()
    if plan not in PLANS_USD:
        _send(chat_id, "Invalid plan. Choose weekly, monthly or yearly.")
        return
    usd = PLANS_USD[plan]
    try:
        prices = get_prices_usd()
        eth_price = prices["ETH"]
        sol_price = prices["SOL"]
    except Exception as e:
        print("price error", e)
        _send(chat_id, "Price fetch failed. Try again later.")
        return

    eth_amt = usd / eth_price
    sol_amt = usd / sol_price

    eth_addr = os.getenv("ETH_MAIN_WALLET")
    sol_addr = os.getenv("SOL_MAIN_WALLET")

    # Save a pending payment check request (so background checker knows expected amounts)
    record_payment_check_request(str(chat_id), plan, "ETH", eth_amt)
    record_payment_check_request(str(chat_id), plan, "SOL", sol_amt)

    text = (
        f"🔒 To activate your *{plan.capitalize()}* plan (${usd}):\n\n"
        f"Send *{eth_amt:.6f} ETH* to:\n`{eth_addr}`\n\n"
        f"OR\n\n"
        f"Send *{sol_amt:.6f} SOL* to:\n`{sol_addr}`\n\n"
        "After the chain confirms payment (1 confirmation), your subscription will be activated automatically.\n"
        "⚠️ Allow a few minutes for confirmation checks."
    )
    _send(chat_id, text, parse_mode="Markdown")

def _cmd_addwallet(chat_id, addr):
    if not addr:
        _send(chat_id, "Usage: /addwallet <address>")
        return
    # check subscription active
    sub = get_latest_subscription(str(chat_id))
    now_ts = int(time.time())
    if not sub or sub["expires_ts"] < now_ts:
        _send(chat_id, "You must have an active subscription to add wallets. Use /payment to subscribe.")
        return
    add_user_wallet(str(chat_id), addr)
    _send(chat_id, f"✅ Wallet {addr} added for monitoring.")

def _cmd_status(chat_id):
    sub = get_latest_subscription(str(chat_id))
    if not sub:
        _send(chat_id, "You have no active subscription.")
        return
    active = sub["expires_ts"] > int(time.time())
    exp = datetime.utcfromtimestamp(sub["expires_ts"]).strftime("%Y-%m-%d %H:%M:%S UTC")
    _send(chat_id, f"Subscription: {sub['plan']} | Active: {active}\nExpires: {exp}")

def _cmd_support(chat_id):
    admin = os.getenv("TELEGRAM_ADMIN_ID")
    _send(chat_id, "Support: your message has been forwarded to admin.")
    if admin:
        _send(admin, f"Support request from {chat_id}. Use /status to view their subscription.")
    
def _cmd_whitepaper(chat_id):
    # link or short text — tweak as you like
    _send(chat_id, "Whitepaper: https://example.com/whitepaper.pdf")