const TelegramBot = require('node-telegram-bot-api');
const { Connection, PublicKey } = require('@solana/web3.js');
const cron = require('node-cron');
const http = require('http');
require('dotenv').config();

// CONFIG FROM .ENV
const token = process.env.TELEGRAM_TOKEN;
const channelId = process.env.CHANNEL_ID;
const adminId = process.env.TELEGRAM_ADMIN_ID;
const architectWalletStr = process.env.ARCHITECT_WALLET || "3KJZZxQ7yYNLqNzsxN33x1V3pav2nRybtXXrBpNm1Zqf";
const architectWallet = new PublicKey(architectWalletStr);
const connection = new Connection(process.env.RPC_URL || "https://api.mainnet-beta.solana.com", "confirmed");
const referralId = process.env.REFERRAL_ID || "matrixice";

const bot = new TelegramBot(token, { polling: true });

// 1. HEALTH CHECK SERVER (For Render/Uptime Robot)
http.createServer((req, res) => {
    res.writeHead(200);
    res.end("Matrix Sentinel Status: 🟢 ACTIVE");
}).listen(process.env.PORT || 7860);

console.log("🧊 MATRIX CONTROLLER v5.5: CORE ENGAGED");

// 2. THE ALPHA PANEL (Revenue Engine)
function sendAlphaPanel(chatId, ca) {
    const message = `
🛰️ **[VANGUARD ALPHA SIGNAL]**
---
**Contract:** \`${ca}\`
**Status:** Analyzing Liquidity...
**Security:** [🛡️ RugCheck](https://rugcheck.xyz/tokens/${ca})
---
⚡ *Buy instantly via referral to support the Forge:*`;

    const keyboard = {
        inline_keyboard: [
            [
                { text: "🛒 Buy (Trojan)", url: `https://t.me/solana_trojanbot?start=r-${referralId}-${ca}` },
                { text: "🛒 Buy (BonkBot)", url: `https://t.me/bonkbot_bot?start=ref_${referralId}_${ca}` }
            ],
            [
                { text: "🦅 DexScreener", url: `https://dexscreener.com/solana/${ca}` },
                { text: "📊 Birdeye", url: `https://birdeye.so/token/${ca}?chain=solana` }
            ],
            [
                { text: "💎 Unlock Snipe Mode (0.1 SOL)", callback_data: 'vanguard_locked' }
            ]
        ]
    };

    bot.sendMessage(chatId, message, { parse_mode: 'Markdown', reply_markup: keyboard });
}

// 3. PAYMENT VERIFICATION (The Gatekeeper)
async function verifySolPayment(signature) {
    try {
        const tx = await connection.getTransaction(signature, {
            commitment: 'confirmed',
            maxSupportedTransactionVersion: 0
        });

        if (!tx || tx.meta.err) return false;

        // Check if the Architect Wallet is a recipient
        const accountKeys = tx.transaction.message.staticAccountKeys || tx.transaction.message.accountKeys;
        return accountKeys.some(key => key.equals(architectWallet));
    } catch (e) {
        console.error("RPC Error:", e);
        return false;
    }
}

// 4. COMMAND HANDLERS
bot.onText(/\/start/, (msg) => {
    const welcome = `🧊 **MATRIX CONTROLLER v5.5**\n\nWelcome, **Mex Robert**. The system is monitoring for Alpha.\n\n**Commands:**\n/status - Check System Vitals\n/boost - Request Volume Boost (0.5 SOL/hr)\n\nPaste a **Solana CA** to generate a trade panel.`;
    bot.sendMessage(msg.chat.id, welcome, { parse_mode: 'Markdown' });
});

bot.onText(/\/status/, async (msg) => {
    const balance = await connection.getBalance(architectWallet);
    const sol = (balance / 1e9).toFixed(4);
    bot.sendMessage(msg.chat.id, `🛰️ **SYSTEM STATUS**\n---\n**Sentinel:** Online 🟢\n**Treasury:** ${sol} SOL\n**Channel:** Connected\n**Uptime Robot:** Active 🔋`, { parse_mode: 'Markdown' });
});

// 5. MESSAGE LISTENER (Detects CAs and Transaction Signatures)
bot.on('message', async (msg) => {
    const text = msg.text;
    if (!text) return;

    // Detect Solana Address (CA)
    const caMatch = text.match(/[1-9A-HJ-NP-Za-km-z]{32,44}pump|[1-9A-HJ-NP-Za-km-z]{32,44}/);
    if (caMatch && !text.startsWith('/')) {
        sendAlphaPanel(channelId, caMatch[0]);
    }

    // Detect Transaction Signature (Payment attempt)
    if (text.length > 64 && !text.includes(' ') && !text.startsWith('/')) {
        bot.sendMessage(msg.chat.id, "🔍 *Verifying payment on Ledger...*", { parse_mode: 'Markdown' });
        const success = await verifySolPayment(text);
        if (success) {
            bot.sendMessage(msg.chat.id, "✅ **PAYMENT VERIFIED.** Access granted to the Vanguard private group.");
        } else {
            bot.sendMessage(msg.chat.id, "❌ **VERIFICATION FAILED.** Ensure you sent the SOL to the Architect Wallet.");
        }
    }
});

// 6. CALLBACK QUERY (Buttons)
bot.on('callback_query', (query) => {
    if (query.data === 'vanguard_locked') {
        bot.answerCallbackQuery(query.id, {
            text: "❌ ACCESS DENIED. Send 0.1 SOL to the Architect Wallet and paste the Signature here to unlock.",
            show_alert: true
        });
    }
});

// 7. AUTOPILOT (Every 2 hours)
cron.schedule('0 */2 * * *', () => {
    bot.sendMessage(channelId, "📡 **[MATRIX TRANSMISSION]**\n\nThe market is shifting. Stay locked. 🧊");
});

