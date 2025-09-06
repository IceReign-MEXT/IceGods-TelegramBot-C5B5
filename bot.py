import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # must be a string

# Async function to send a test message
async def send_start_message(app: Application):
    chat_id = int(TELEGRAM_CHAT_ID)
    await app.bot.send_message(chat_id=chat_id, text="✅ Bot has started!")

async def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    print("Bot is starting...")
    await app.initialize()
    await app.start()

    # Send a start message
    await send_start_message(app)

    # Start polling
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
