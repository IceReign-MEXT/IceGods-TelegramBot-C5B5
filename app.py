import os
import threading
import time
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.error import TelegramError

from handlers import handle_text_command, init_bot_objects
from db import init_db
from payments import run_payment_checks

# Load token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN not set!")

bot = Bot(token=TOKEN)
init_bot_objects(bot)

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        threading.Thread(target=handle_text_command, args=(bot, update)).start()
    except TelegramError as e:
        print("❌ Telegram API error:", e)
    except Exception as e:
        print("❌ General error:", e)
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return jsonify({"ok": True, "msg": "Bot running"}), 200

def background_payment_checker():
    while True:
        try:
            run_payment_checks()
        except Exception as e:
            print("❌ Payment checker error:", e)
        time.sleep(30)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=background_payment_checker, daemon=True).start()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
