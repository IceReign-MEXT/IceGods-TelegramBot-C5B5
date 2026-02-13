const { Connection, PublicKey } = require('@solana/web3.js');
const TelegramBot = require('node-telegram-bot-api');
require('dotenv').config();

const connection = new Connection(process.env.RPC_URL, "finalized");
const bot = new TelegramBot(process.env.TELEGRAM_TOKEN);
const architectWallet = new PublicKey(process.env.ARCHITECT_WALLET);

console.log("🛡️ GUARD SYSTEM: SCANNING LEDGER...");

// Scan every new block for payments to YOUR wallet
connection.onLogs(architectWallet, async (logs) => {
    try {
        const tx = await connection.getParsedTransaction(logs.signature, { maxSupportedTransactionVersion: 0 });
        const amount = tx.meta.postBalances[1] - tx.meta.preBalances[1];
        
        if (amount >= 100000000) { // 0.1 SOL in Lamports
            const sender = tx.transaction.message.accountKeys[0].pubkey.toString();
            console.log(`💰 Verified Payment from: ${sender}`);
            // Logic to unlock user based on their wallet link would go here
        }
    } catch (e) { /* Ignore non-transfer logs */ }
}, "confirmed");
