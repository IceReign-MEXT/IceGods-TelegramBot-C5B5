import os
import time
import threading
from flask import Flask, request
from telegram import Bot, Update
from telegram.error import TelegramError
from bot_handlers import handle_text_command, init_bot_objects
from db import init_db
from payments import run_payment_checks

# ✅ Load bot token from environment
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN not set in environment!")

bot = Bot(token=TOKEN)
init_bot_objects(bot)

# ✅ Initialize database
init_db()

# ✅ Background loop for checking payments
def background_loop():
    while True:
        run_payment_checks()
        time.sleep(60)  # check every 60 seconds

threading.Thread(target=background_loop, daemon=True).start()

# ✅ Flask app
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        handle_text_command(bot, update)
    except TelegramError as e:
        print("❌ Telegram API error:", e)
    except Exception as e:
        print("❌ General error in webhook:", e)
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return "🤖 Telegram Bot Running!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
