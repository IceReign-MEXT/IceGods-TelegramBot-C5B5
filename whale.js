const { Connection, PublicKey } = require('@solana/web3.js');
const TelegramBot = require('node-telegram-bot-api');
require('dotenv').config();

const connection = new Connection(process.env.RPC_URL);
const bot = new TelegramBot(process.env.TELEGRAM_TOKEN);
const PUMP_PROGRAM = new PublicKey("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P");

console.log("🐋 WHALE WATCHER: SCANNING PUMP.FUN...");

connection.onLogs(PUMP_PROGRAM, ({ logs, signature }) => {
    if (logs.some(log => log.includes("Buy"))) {
        // High-level logic: Post to channel when a signature hits
        bot.sendMessage(process.env.CHANNEL_ID, `🐋 **WHALE INJECTION DETECTED**\n\nSomeone is creating Green Candles. Check the ticker!\n\n[🔍 View Transaction](https://solscan.io/tx/${signature})`, { parse_mode: 'Markdown' });
    }
}, "confirmed");
