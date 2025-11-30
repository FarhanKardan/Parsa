# syntax=docker/dockerfile:1

FROM python:3.10-slim

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m botuser

WORKDIR /app

# Copy only requirements first
COPY requirements.txt .
RUN python -m venv /opt/venv \
 && . /opt/venv/bin/activate \
 && pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY . .

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Enable external overwrite of bot token
ENV BOT_TOKEN=${BOT_TOKEN}

USER botuser

CMD ["python", "bot.py"]
