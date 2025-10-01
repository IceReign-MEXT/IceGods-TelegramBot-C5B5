from telegram import Update
from db import get_latest_subscription, add_pending_payment_request
import os

bot_instance = None

def init_bot_objects(bot):
    global bot_instance
    bot_instance = bot

def handle_text_command(bot, update: Update):
    if not update.message:
        return

    message = update.message.text.strip().lower()
    chat_id = update.message.chat_id

    if message == "/start":
        bot.send_message(chat_id, "👋 Welcome! Use /subscribe to view plans.")

    elif message == "/subscribe":
        bot.send_message(chat_id,
            "💳 Subscription Plans:\n"
            "- Weekly: $5\n"
            "- Monthly: $15\n"
            "- Yearly: $100\n\n"
            "Pay to:\n"
            f"ETH: {os.getenv('ETH_MAIN_WALLET')}\n"
            f"SOL: {os.getenv('SOL_MAIN_WALLET')}\n\n"
            "Then reply with: /plan weekly|monthly|yearly ETH|SOL"
        )

    elif message.startswith("/plan"):
        try:
            _, plan, chain = message.split()
            prices = {"weekly": 5, "monthly": 15, "yearly": 100}
            amount = prices.get(plan.lower())
            if not amount:
                bot.send_message(chat_id, "❌ Invalid plan.")
                return
            add_pending_payment_request(str(chat_id), plan, chain.upper(), amount)
            bot.send_message(chat_id, f"✅ Send {amount} USD in {chain.upper()} to confirm.")
        except Exception:
            bot.send_message(chat_id, "Usage: /plan weekly|monthly|yearly ETH|SOL")

    elif message == "/status":
        sub = get_latest_subscription(str(chat_id))
        if not sub:
            bot.send_message(chat_id, "❌ No active subscription.")
        else:
            bot.send_message(chat_id,
                f"📅 Plan: {sub['plan']}\n"
                f"Start: {sub['start_ts']}\n"
                f"Expires: {sub['expires_ts']}"
            )
    else:
        bot.send_message(chat_id, "❓ Unknown command. Try /subscribe")