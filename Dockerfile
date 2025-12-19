FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for high-speed libraries)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your professional bot files
COPY . .

# Hugging Face Spaces default port is 7860
ENV PORT=7860
EXPOSE 7860

# Start the Modern Brain engine
CMD ["python", "main.py"]



