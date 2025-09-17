# YieldForge / IceGods Staker Bot (Crypto Subscriptions)

This repo provides a Flask web app + Telegram webhook bot that accepts crypto payments (ETH + SOL) and activates subscriptions once payments confirm.

## Files
- `app.py` - Flask app & webhook entrypoint
- `bot_handlers.py` - bot command handlers
- `payments.py` - price fetch + on-chain checks
- `db.py` - sqlite DB helpers
- `background_checker.py` - background thread for payment polling
- `requirements.txt`, `Procfile`, `Dockerfile`

## Deploy (Render)
1. Push repo to GitHub.
2. Create a **Web Service** on Render or connect repository.
3. Set environment variables in Render dashboard:
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_ADMIN_ID
   - ETH_MAIN_WALLET, SOL_MAIN_WALLET
   - CMC_API_KEY, ETHERSCAN_API_KEY, INFURA_API_KEY
   - DATABASE_PATH (optional)
4. Deploy. After the service is live, set Telegram webhook:
