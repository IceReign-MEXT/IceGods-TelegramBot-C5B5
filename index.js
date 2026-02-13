const TelegramBot = require('node-telegram-bot-api');
const { Connection, PublicKey } = require('@solana/web3.js');
const http = require('http');
require('dotenv').config();

// SINGLE BOT INSTANCE
const bot = new TelegramBot(process.env.TELEGRAM_TOKEN, { polling: true });
const connection = new Connection(process.env.RPC_URL, "confirmed");
const architectWallet = new PublicKey(process.env.ARCHITECT_WALLET);
const channelId = process.env.CHANNEL_ID;

// Health Server
http.createServer((req, res) => { res.end("Vanguard System Online"); }).listen(process.env.PORT || 7860);

console.log("🚀 VANGUARD UNIFIED CORE: ONLINE");

// 1. PAYMENT GUARD LOGIC (Integrated)
connection.onAccountChange(architectWallet, (info) => {
    console.log("💰 Payment detected in wallet!");
    // Logic to notify you or unlock users
}, "confirmed");

// 2. THE TEASER BAIT & ALPHA LOGIC
bot.on('message', (msg) => {
    if (!msg.text) return;
    
    const caMatch = msg.text.match(/[1-9A-HJ-NP-Za-km-z]{32,44}pump|[1-9A-HJ-NP-Za-km-z]{32,44}/);
    
    if (caMatch && !msg.text.startsWith('/')) {
        const ca = caMatch[0];
        const hiddenCA = ca.substring(0, 6) + "...." + ca.substring(ca.length - 4);
        
        // Post BAIT to the channel
        bot.sendMessage(channelId, `
🚨 **[ALPHA LEAK DETECTED]**
Token: **AUTHENTICATING...**
CA: \`${hiddenCA}\`

🔓 **FULL CA POSTED BELOW IN 30S**
Join for speed: @ICEGODSICEDEVIL
        `, { parse_mode: 'Markdown' });

        // Post FULL CA after delay
        setTimeout(() => {
            bot.sendMessage(channelId, `🎯 **FULL ALPHA UNLOCKED**\nCA: \`${ca}\`\n[🦅 DexScreener](https://dexscreener.com/solana/${ca})`, { parse_mode: 'Markdown' });
        }, 30000);
    }
});

// 3. COMMANDS
bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, "Welcome, Architect. System is autonomous.");
});
