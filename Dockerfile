# Dockerfile - runs the Telegram bot
FROM python:3.11-slim

WORKDIR /app

# system deps (small)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# default: run the bot
CMD ["python", "bot.py"]
