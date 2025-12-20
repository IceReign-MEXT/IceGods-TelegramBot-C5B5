FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Bind to 0.0.0.0:7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "main:app"]

