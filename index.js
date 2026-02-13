const TelegramBot = require('node-telegram-bot-api');
const { Connection, PublicKey } = require('@solana/web3.js');
const cron = require('node-cron');
const http = require('http');
require('dotenv').config();

// Load New Config
const token = process.env.TELEGRAM_TOKEN;
const channelId = process.env.CHANNEL_ID; 
const adminId = process.env.TELEGRAM_ADMIN_ID;
const architectWallet = new PublicKey(process.env.ARCHITECT_WALLET);
const connection = new Connection(process.env.RPC_URL, "confirmed");

const bot = new TelegramBot(token, { polling: true });

// Health Check for Render
http.createServer((req, res) => { res.writeHead(200); res.end("Matrix Sentinel Active"); }).listen(process.env.PORT || 10000);

console.log("🧊 MATRIX CONTROLLER v5.2: ONLINE");

// --- 1. CHANNEL AUTO-TRANSMISSION ---
cron.schedule('0 */2 * * *', async () => {
    const text = "📡 **[MATRIX SIGNAL]**\n\nThe grid is active. Vanguard tools are ready for deployment.";
    bot.sendMessage(channelId, text, { parse_mode: 'Markdown' });
});

// --- 2. THE ALPHA PANEL (Now using Admin ID for Alerts) ---
function sendAlphaPanel(chatId, ca) {
    const ref = process.env.REFERRAL_ID;
    const message = `🛰️ **VANGUARD ALPHA DETECTED**\n\n**CA:** \`${ca}\`\n\n[🦅 DexScreener](https://dexscreener.com/solana/${ca})`;

    const keyboard = {
        inline_keyboard: [
            [{ text: "🛒 Buy (Trojan)", url: `https://t.me/solana_trojanbot?start=r-${ref}-${ca}` }],
            [{ text: "🛡️ RugCheck", url: `https://rugcheck.xyz/tokens/${ca}` }]
        ]
    };
    bot.sendMessage(chatId, message, { parse_mode: 'Markdown', reply_markup: keyboard });
}

// --- 3. COMMANDS ---
bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, "Welcome to the Matrix, Mex Robert. System standing by.");
});

bot.on('message', (msg) => {
    if (msg.text && msg.text.length > 32 && !msg.text.startsWith('/')) {
        const caMatch = msg.text.match(/[1-9A-HJ-NP-Za-km-z]{32,44}pump|[1-9A-HJ-NP-Za-km-z]{32,44}/);
        if (caMatch) sendAlphaPanel(channelId, caMatch[0]);
    }
});
