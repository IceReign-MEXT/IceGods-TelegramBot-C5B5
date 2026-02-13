const TelegramBot = require('node-telegram-bot-api');
const { Connection, PublicKey } = require('@solana/web3.js');
const cron = require('node-cron');
const http = require('http');
require('dotenv').config();

const bot = new TelegramBot(process.env.TELEGRAM_TOKEN, { polling: true });
const connection = new Connection(process.env.RPC_URL, "confirmed");
const channelId = process.env.CHANNEL_ID;

// Mock Database (In production, use MongoDB or a JSON file)
let users = {}; 

// 1. HEALTH CHECK
http.createServer((req, res) => { res.end("Sentinel Autonomous"); }).listen(process.env.PORT || 7860);

// 2. THE TEASER BAIT (Posts to other channels/Your channel)
function sendTeaserAlpha(ca) {
    const hiddenCA = ca.substring(0, 6) + "...." + ca.substring(ca.length - 4);
    const teaser = `
🚨 **[ALPHA LEAK DETECTED]**
---
Token: **HIDDEN UNTIL VERIFIED**
CA: \`${hiddenCA}\`
Whale Entry: **0.4 SOL**

🔓 **UNLOCK FULL CA:**
Join: @ICEGODSICEDEVIL
Or use the bot: @IceGodMatrix_Bot
    `;
    // Post to your channel as bait
    bot.sendMessage(channelId, teaser);
}

// 3. AUTO-RECOGNITION ON START
bot.onText(/\/start (.+)/, (msg, match) => {
    const referrer = match[1].replace('ref_', '');
    const newUser = msg.from.id;

    if (!users[newUser]) {
        users[newUser] = { invitedBy: referrer, paid: false, referrals: 0 };
        if (users[referrer]) {
            users[referrer].referrals += 1;
            bot.sendMessage(referrer, `👤 **New Recruit!** You now have ${users[referrer].referrals}/5 referrals.`);
        }
    }
});

// 4. AUTOMATIC CA DETECTION (Posts Teaser then Full)
bot.on('message', (msg) => {
    const caMatch = msg.text?.match(/[1-9A-HJ-NP-Za-km-z]{32,44}pump|[1-9A-HJ-NP-Za-km-z]{32,44}/);
    if (caMatch && msg.chat.id.toString() !== channelId) {
        sendTeaserAlpha(caMatch[0]); // Create the Bait
        // Wait 30 seconds then post full CA to your private group/channel
        setTimeout(() => {
            bot.sendMessage(channelId, `🎯 **FULL ALPHA UNLOCKED**\nCA: \`${caMatch[0]}\``);
        }, 30000);
    }
});

console.log("🚀 AUTONOMOUS SENTINEL v7.0 LIVE");
