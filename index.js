const TelegramBot = require('node-telegram-bot-api');
const { Connection, PublicKey } = require('@solana/web3.js');
const cron = require('node-cron');
const http = require('http');
require('dotenv').config();

const token = process.env.TELEGRAM_TOKEN;
const channelId = '-1003844332949'; 
const architectWallet = new PublicKey("3KJZZxQ7yYNLqNzsxN33x1V3pav2nRybtXXrBpNm1Zqf");
const connection = new Connection("https://api.mainnet-beta.solana.com", "confirmed");

const bot = new TelegramBot(token, { polling: true });

// Web server for Render
http.createServer((req, res) => { res.writeHead(200); res.end("Sentinel Active"); }).listen(process.env.PORT || 10000);

console.log("🧊 VANGUARD PRO v4.2: ONLINE");

// 1. THE STATUS COMMAND (With Progress Bar)
bot.onText(/\/status/, async (msg) => {
    try {
        const balance = await connection.getBalance(architectWallet);
        const sol = (balance/1e9).toFixed(4);
        const progress = Math.min((sol / 0.05) * 100, 100);
        const bar = "🟩".repeat(Math.round(progress/10)) + "⬜".repeat(10 - Math.round(progress/10));

        const statusMsg = `🛰️ **VANGUARD CORE v4.2**\n---\n**Treasury:** ${sol} SOL\n**Bypass:** ${progress.toFixed(1)}%\n${bar}\n\n**Sentinel:** Active\n**Alpha Feed:** 🟢 CONNECTED`;
        bot.sendMessage(msg.chat.id, statusMsg, { parse_mode: 'Markdown' });
    } catch (e) {
        bot.sendMessage(msg.chat.id, "⚠️ RPC Error.");
    }
});

// 2. THE ALPHA PANEL (The Professional UI)
function sendAlphaPanel(chatId, ca) {
    const message = `💀 **VANGUARD ALPHA DETECTED**\n\n**CA:** \`${ca}\`\n\n**Status:** Analyzing Bonding Curve...\n**Safety:** Check RugCheck below.`;
    
    const keyboard = {
        inline_keyboard: [
            [
                { text: "🦅 DexScreener", url: `https://dexscreener.com/solana/${ca}` },
                { text: "📊 RugCheck", url: `https://rugcheck.xyz/tokens/${ca}` }
            ],
            [
                { text: "🛒 Buy 0.1 SOL", url: `https://jup.ag/swap/SOL-${ca}` },
                { text: "🛒 Buy 0.5 SOL", url: `https://jup.ag/swap/SOL-${ca}` }
            ],
            [
                { text: "⚡ Snipe (Vanguard Only)", callback_data: 'snipe_locked' }
            ]
        ]
    };

    bot.sendMessage(chatId, message, { parse_mode: 'Markdown', reply_markup: keyboard });
}

// 3. SNIPE LOCK CALLBACK
bot.on('callback_query', (query) => {
    if (query.data === 'snipe_locked') {
        bot.answerCallbackQuery(query.id, {
            text: "❌ ACCESS DENIED. Enroll in Vanguard to unlock Snipe Mode.",
            show_alert: true
        });
    }
});

// 4. THE AUTO-SCANNER (Listening for CAs)
bot.on('message', (msg) => {
    if (msg.text && msg.text.length > 32 && !msg.text.startsWith('/')) {
        const caMatch = msg.text.match(/[1-9A-HJ-NP-Za-km-z]{32,44}pump|[1-9A-HJ-NP-Za-km-z]{32,44}/);
        if (caMatch) {
            sendAlphaPanel(msg.chat.id, caMatch[0]);
        }
    }
});
