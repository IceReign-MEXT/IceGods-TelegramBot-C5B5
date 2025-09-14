# Dockerfile - run bot + web in one container using Honcho
FROM python:3.11-slim

WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# install python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy everything
COPY . .

# Honcho will read Procfile and run both processes
CMD ["honcho", "start", "--procfile", "Procfile"]