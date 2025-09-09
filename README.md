# IceGods Minimal

This repo contains a minimal Telegram bot (`bot.py`) and a small subscription API (`app.py`).
- `bot.py` — Telegram bot (polling) with /start and /ping
- `app.py` — simple Flask endpoints to create/check subscriptions
- `.env` — keep your secrets here (NOT in git)

Deploy options:
- Render: create a Web Service (for `app.py`) and a Background Worker (for `bot.py`), set environment variables.
- Docker: build and run the container, it runs `bot.py`.
