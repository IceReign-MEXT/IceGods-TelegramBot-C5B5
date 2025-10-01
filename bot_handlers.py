import os
import time
from datetime import datetime
from telegram import Bot, Update

# Import your DB + payments helpers (assume already working in your repo)
from payments import get_prices_usd, record_payment_check_request
from db import (
    get_latest_subscription,
    add_user_wallet,
)

BOT = None
PLANS_USD = {"weekly": 16, "monthly": 60, "yearly": 600}

def init_bot_objects(bot: Bot):
    global BOT
    BOT = bot

def _send(chat_id, text, parse_mode=None):
    try:
        BOT.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
    except Exception as e:
        print("❌ Send error:", e)

def handle_text_command(bot: Bot, update: Update):
    if not update.message:
        return
    chat_id = update.effective_chat.id
    text = update.message.text or ""
    parts = text.strip().split()
    cmd = parts[0].lower()

    if cmd == "/start":
        _cmd_start(chat_id)
    elif cmd == "/ping":
        _send(chat_id, "🏓 Pong!")
    elif cmd == "/pricing":
        _cmd_pricing(chat_id)
    elif cmd == "/payment":
        _cmd_payment(chat_id, parts[1] if len(parts) > 1 else None)
    elif cmd == "/addwallet":
        _cmd_addwallet(chat_id, parts[1] if len(parts) > 1 else None)
    elif cmd == "/status":
        _cmd_status(chat_id)
    elif cmd == "/support":
        _cmd_support(chat_id)
    elif cmd == "/whitepaper":
        _cmd_whitepaper(chat_id)
    else:
        _send(chat_id, "Unknown command. Use /start to see options.")

def _cmd_start(chat_id):
    _send(chat_id,
        "👋 Welcome!\n\n"
        "/ping - Test bot\n"
        "/pricing - Plans\n"
        "/payment <plan>\n"
        "/addwallet <address>\n"
        "/status - Subscription info\n"
        "/support - Contact admin\n"
        "/whitepaper - Docs"
    )

def _cmd_pricing(chat_id):
    try:
        prices = get_prices_usd()
        eth_price, sol_price = prices["ETH"], prices["SOL"]
    except:
        _send(chat_id, "⚠️ Could not fetch prices.")
        return
    msg = "💰 Plans:\n\n"
    for plan, usd in PLANS_USD.items():
        msg += f"{plan.capitalize()}: ${usd} → {usd/eth_price:.6f} ETH / {usd/sol_price:.6f} SOL\n"
    _send(chat_id, msg)

def _cmd_payment(chat_id, plan):
    if not plan or plan not in PLANS_USD:
        _send(chat_id, "Usage: /payment <weekly|monthly|yearly>")
        return
    usd = PLANS_USD[plan]
    try:
        prices = get_prices_usd()
        eth_price, sol_price = prices["ETH"], prices["SOL"]
    except:
        _send(chat_id, "⚠️ Price fetch failed.")
        return
    eth_amt, sol_amt = usd/eth_price, usd/sol_price
    eth_addr, sol_addr = os.getenv("ETH_MAIN_WALLET"), os.getenv("SOL_MAIN_WALLET")
    record_payment_check_request(str(chat_id), plan, "ETH", eth_amt)
    record_payment_check_request(str(chat_id), plan, "SOL", sol_amt)
    _send(chat_id,
        f"🔒 {plan.capitalize()} (${usd})\n\n"
        f"Pay {eth_amt:.6f} ETH → `{eth_addr}`\n"
        f"or {sol_amt:.6f} SOL → `{sol_addr}`\n\n"
        "✅ Activated after 1 confirmation."
    , parse_mode="Markdown")

def _cmd_addwallet(chat_id, addr):
    if not addr:
        _send(chat_id, "Usage: /addwallet <address>")
        return
    sub = get_latest_subscription(str(chat_id))
    if not sub or sub["expires_ts"] < int(time.time()):
        _send(chat_id, "❌ No active subscription. Use /payment.")
        return
    add_user_wallet(str(chat_id), addr)
    _send(chat_id, f"✅ Wallet {addr} added.")

def _cmd_status(chat_id):
    sub = get_latest_subscription(str(chat_id))
    if not sub:
        _send(chat_id, "❌ No active subscription.")
        return
    exp = datetime.utcfromtimestamp(sub["expires_ts"]).strftime("%Y-%m-%d %H:%M:%S UTC")
    _send(chat_id, f"📊 Plan: {sub['plan']} | Expires: {exp}")

def _cmd_support(chat_id):
    admin = os.getenv("TELEGRAM_ADMIN_ID")
    _send(chat_id, "📨 Your message has been forwarded.")
    if admin:
        _send(admin, f"📩 Support from {chat_id}")

def _cmd_whitepaper(chat_id):
    _send(chat_id, "📄 Whitepaper: https://example.com/whitepaper.pdf")