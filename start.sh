#!/bin/bash
set -e

cd /app 2>/dev/null || true

echo "Starting FastAPI backend on port ${PORT:-8000}..."
uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}" &

echo "Waiting for backend to start..."
sleep 5

echo "Starting Telegram bot..."
python backend/telegram_bot.py
