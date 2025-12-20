FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Set Port and run the script directly (NOT gunicorn)
ENV PORT=7860
EXPOSE 7860

# This is the fix: Running python main.py allows the bot to start!
CMD ["python", "main.py"]
