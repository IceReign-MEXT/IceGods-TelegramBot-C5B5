import os
import time
import asyncio
import threading
import sqlite3
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from telegram.ext import Application, CommandHandler

# --- Load environment ---
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- Flask app ---
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ IceGods Bot + API running!"

# --- Database ---
conn = sqlite3.connect('chainpilot.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT UNIQUE,
    subscription TEXT,
    start_time INTEGER
)
''')
conn.commit()

# --- Subscription logic ---
def is_subscription_active(start_time, plan):
    now = int(time.time())
    durations = {
        "1_hour": 3600,
        "4_hours": 14400,
        "8_hours": 28800,
        "12_hours": 43200,
        "24_hours": 86400,
        "1_week": 604800,
        "1_month": 2592000,
        "1_year": 31536000
    }
    duration = durations.get(plan, 0)
    return now - start_time < duration

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})

@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.json
    telegram_id = data.get("telegram_id")
    plan = data.get("plan")
    start_time = int(time.time())

    cursor.execute("INSERT OR REPLACE INTO users (telegram_id, subscription, start_time) VALUES (?, ?, ?)",
                   (telegram_id, plan, start_time))
    conn.commit()

    send_telegram_message(telegram_id, f"✅ Subscription activated for {plan}")
    return jsonify({"status": "success", "plan": plan})

@app.route("/check_subscription/<telegram_id>")
def check_subscription(telegram_id):
    cursor.execute("SELECT subscription, start_time FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    if not result:
        return jsonify({"active": False})
    plan, start_time = result
    active = is_subscription_active(start_time, plan)
    return jsonify({"active": active, "plan": plan})

# --- Flask background runner ---
def run_flask():
    app.run(host="0.0.0.0", port=5000)

# --- Telegram bot ---
async def run_bot():
    bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    async def start(update, context):
        cursor.execute("SELECT subscription, start_time FROM users WHERE telegram_id = ?", (str(update.effective_chat.id),))
        result = cursor.fetchone()
        if not result:
            await update.message.reply_text("👋 Welcome! You don’t have a subscription yet. Use /plans to see options.")
        else:
            plan, start_time = result
            if is_subscription_active(start_time, plan):
                await update.message.reply_text(f"✅ Active subscription: {plan}")
            else:
                await update.message.reply_text("⚠️ Your subscription has expired. Please renew.")

    async def plans(update, context):
        msg = (
            "💰 *Subscription Plans:*\n"
            "1_hour → $1\n"
            "4_hours → $3\n"
            "8_hours → $5\n"
            "12_hours → $7\n"
            "24_hours → $10\n"
            "1_week → $50\n"
            "1_month → $100\n"
            "1_year → $1000\n\n"
            "To subscribe, call API: /subscribe"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("plans", plans))

    await bot_app.initialize()
    await bot_app.start()
    await bot_app.run_polling()

# --- Main entry ---
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    asyncio.run(run_bot())
