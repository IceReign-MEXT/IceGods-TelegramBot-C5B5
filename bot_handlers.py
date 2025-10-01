from telegram import Update, Bot
from telegram.ext import CallbackContext
from db import add_subscription, get_latest_subscription, add_pending_payment_request

bot_ref = None

def init_bot_objects(bot: Bot):
    global bot_ref
    bot_ref = bot

def handle_text_command(bot: Bot, update: Update):
    message = update.message
    chat_id = message.chat_id
    text = message.text.strip().lower()

    if text == "/start":
        bot.send_message(chat_id, "👋 Welcome! Use /subscribe to buy a plan.")
    elif text == "/subscribe":
        # Example subscription prompt
        bot.send_message(chat_id, "💳 Choose a plan:\n1. Basic - $10\n2. Pro - $20\n\nSend the plan number.")
    elif text == "1":
        add_pending_payment_request(chat_id, "Basic", "ETH", 10)
        bot.send_message(chat_id, "✅ Please send 10 USDT (ERC20) to the main ETH wallet.")
    elif text == "2":
        add_pending_payment_request(chat_id, "Pro", "ETH", 20)
        bot.send_message(chat_id, "✅ Please send 20 USDT (ERC20) to the main ETH wallet.")
    else:
        bot.send_message(chat_id, "❓ Unknown command.")