import os
import json
import threading
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from telegram import Bot, Update
from bot_handlers import handle_text_command, init_bot_objects
from background_checker import start_background_checker
from db import init_db

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN missing from environment")

app = Flask(__name__)

# Initialize DB, bot objects, and background checker
init_db()  # ensures tables exist
bot = Bot(token=TELEGRAM_BOT_TOKEN)
# initialize shared objects in handlers (bot, env, db)
init_bot_objects(bot)

# Start background checker in a separate thread (checks blockchain for payments)
# It will run every CHECK_INTERVAL seconds (default 60s)
start_background_checker()

@app.route("/")
def index():
    return jsonify({"ok": True, "note": "StakerBot service running"})

# Telegram webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update_json = request.get_json(force=True)
        # Build Update object (so helper functions can use it if needed)
        update = Update.de_json(update_json, bot)
        # Very simple dispatcher: parse message text and call handler
        # Our handle_text_command will accept bot and update
        threading.Thread(target=handle_text_command, args=(bot, update)).start()
        return "ok", 200
    except Exception as e:
        app.logger.exception("Webhook processing error")
        return jsonify({"error": str(e)}), 500

# Endpoint to view subscription status (optional, handy for testing)
@app.route("/status/<telegram_id>", methods=["GET"])
def status(telegram_id):
    from db import get_latest_subscription
    sub = get_latest_subscription(str(telegram_id))
    if not sub:
        return jsonify({"active": False})
    active = sub["expires_ts"] > int(__import__("time").time())
    return jsonify({"active": active, **sub})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
