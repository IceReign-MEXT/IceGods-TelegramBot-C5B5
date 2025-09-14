# ==============================
# Dockerfile – used by Render to build your image
# ==============================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Expose port (Flask/Gunicorn will listen here)
EXPOSE 5000

# Default CMD (this will be overridden in Render’s Start Command)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]