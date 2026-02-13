const TelegramBot = require('node-telegram-bot-api');
const { Connection, PublicKey } = require('@solana/web3.js');
const cron = require('node-cron');
const http = require('http');
require('dotenv').config();

// CONFIG
const token = process.env.TELEGRAM_TOKEN;
const channelId = '-1003844332949'; // Your Vanguard Channel
const architectWallet = new PublicKey("3KJZZxQ7yYNLqNzsxN33x1V3pav2nRybtXXrBpNm1Zqf");
const connection = new Connection("https://api.mainnet-beta.solana.com", "confirmed");

const bot = new TelegramBot(token, { polling: true });

// 1. WEB SERVER (For Render 24/7 Hosting)
http.createServer((req, res) => { res.writeHead(200); res.end("Sentinel Active"); }).listen(process.env.PORT || 10000);

console.log("🧊 ICEGODS SENTINEL v4.0: ENGAGED");

// 2. THE CHANNEL AUTOPILOT (Keeping it active)
const transmissions = [
    "📡 LORE: The Great Freeze of 2026 has begun. Are you building the bypass?",
    "🧊 STATUS: Treasury verified. The Architect is observing the grid.",
    "🔓 ACCESS: 10 Vanguard slots open. Use the bot to verify your entry."
];

cron.schedule('0 */2 * * *', async () => {
    const balance = await connection.getBalance(architectWallet);
    const text = transmissions[Math.floor(Math.random() * transmissions.length)];
    bot.sendMessage(channelId, `📡 **[SYSTEM SIGNAL]**\n\n"${text}"\n\nTreasury: ${(balance/1e9).toFixed(4)} SOL\n[FORGE](https://ice-alpha-2040-underground.vercel.app)`);
});

// 3. THE VERIFICATION GATEKEEPER
bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, `🛰️ **ICEGODS VERIFICATION**\n\nAccess the Underground School tools.\n\n**Fee:** 0.05 SOL\n**Target:** \`3KJZZxQ7yYNLqNzsxN33x1V3pav2nRybtXXrBpNm1Zqf\`\n\nSend the SOL, then paste your **Transaction Signature** here.`, { parse_mode: 'Markdown' });
});

bot.on('message', async (msg) => {
    const text = msg.text;
    if (text && text.length > 60 && !text.startsWith('/')) {
        bot.sendMessage(msg.chat.id, "🔍 Checking the Blockchain...");
        try {
            const tx = await connection.getTransaction(text, { maxSupportedTransactionVersion: 0 });
            if (tx) {
                const received = tx.transaction.message.staticAccountKeys.some(key => key.equals(architectWallet));
                if (received) {
                    bot.sendMessage(msg.chat.id, "✅ **ACCESS GRANTED.**\n\nWelcome Initiate. You have unlocked the Bypass Tools.\n\n🔗 [SECRET TOOL LINK HERE]");
                } else {
                    bot.sendMessage(msg.chat.id, "❌ Signature found, but funds went to the wrong address.");
                }
            } else {
                bot.sendMessage(msg.chat.id, "❌ Transaction not confirmed. Wait 10 seconds.");
            }
        } catch (e) {
            bot.sendMessage(msg.chat.id, "⚠️ Solana RPC Error. Try again.");
        }
    }
});
