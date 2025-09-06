import os
import asyncio
from flask import Flask
import threading

# Import your Telegram bot main function
from bot import main as telegram_main  

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ IceGods Bot is alive and running!"

def run_telegram_bot():
    """Run the Telegram bot inside its own asyncio loop."""
    asyncio.run(telegram_main())

if __name__ == "__main__":
    # Start Telegram bot in background thread
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()

    # Run Flask server (required for Render)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
