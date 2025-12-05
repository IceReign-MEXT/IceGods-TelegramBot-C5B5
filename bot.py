import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from db import init_db, create_user, update_balance, get_balance, set_wallet
from payments import automate_payout

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = int(os.getenv('TELEGRAM_ADMIN_ID', 0))
REFERRAL_BONUS = float(os.getenv('REFERRAL_BONUS_USDT', 0.5))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    create_user(user.id, user.username)
    keyboard = [['/balance', '/refer'], ['/tasks', '/withdraw']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"🚀 Welcome to EarningsBot, {user.first_name}!\n\n"
        "Earn USDT by referring friends & completing tasks.\n"
        "Min payout: $5 | Instant via Tron.\n\n"
        "Use /setwallet TYourAddress to add wallet.",
        reply_markup=reply_markup
    )

async def balance(update: Update, context: CallbackContext):
    bal = get_balance(update.effective_user.id)
    await update.message.reply_text(f"💰 Your balance: ${bal:.2f} USDT")

async def refer(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    ref_link = f"https://t.me/{context.bot.username}?start={user_id}"
    await update.message.reply_text(
        f"👥 Invite friends!\nYour link: {ref_link}\n"
        f"Get ${REFERRAL_BONUS} per referral.\n\n"
        "They join via your link → you earn instantly."
    )

async def handle_referral(update: Update, context: CallbackContext):
    if context.args:
        ref_id = int(context.args[0])
        if ref_id != update.effective_user.id:
            update_balance(ref_id, REFERRAL_BONUS)
            await context.bot.send_message(ref_id, "🎉 New referral! +${REFERRAL_BONUS} credited.")

async def tasks(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📋 Quick tasks (earn $0.10–$1 each):\n"
        "1. Join our channel: /joinchannel\n"
        "2. Watch ad: Earn $0.50 (simulated—add real API later).\n"
        "Reply 'done1' or 'done2' to claim."
    )

async def withdraw(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    bal = get_balance(user_id)
    if bal < 5:
        await update.message.reply_text("❌ Need $5+ to withdraw.")
        return
    # For simplicity, assume wallet set; in prod, query if needed
    wallet = "TTestWallet123"  # Replace with DB fetch: from db.get_user(user_id)[3]
    result = automate_payout(wallet, bal, user_id)
    if result['success']:
        await update.message.reply_text(
            f"✅ Paid ${result['payout_amount']:.2f} USDT!\n"
            f"Fee: ${result['fee']:.2f}\n"
            f"Proof: {result['link']}\n\n"
            "Check your TronLink wallet!"
        )
    else:
        await update.message.reply_text(f"❌ Error: {result['error']}")

async def set_wallet_cmd(update: Update, context: CallbackContext):
    if context.args:
        set_wallet(update.effective_user.id, context.args[0])
        await update.message.reply_text("✅ Wallet updated!")

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if 'done1' in text:
        update_balance(update.effective_user.id, 0.50)
        await update.message.reply_text("✅ Task 1 done! +$0.50")
    elif 'done2' in text:
        update_balance(update.effective_user.id, 1.00)
        await update.message.reply_text("✅ Task 2 done! +$1.00")

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("refer", refer))
    app.add_handler(CommandHandler("tasks", tasks))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("setwallet", set_wallet_cmd))
    app.add_handler(MessageHandler(filters.Regex(r'^done\d'), handle_message))
    app.add_handler(CommandHandler("start", handle_referral))  # For referrals
    app.run_polling()

if __name__ == '__main__':
    main()
