import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.error import TelegramError

from bot_handlers import handle_text_command, init_bot_objects

TOKEN = os.getenv("BOT_TOKEN")  # make sure this is set in Render
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN not set in environment!")

bot = Bot(token=TOKEN)
init_bot_objects(bot)  # give handlers access to bot object

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
