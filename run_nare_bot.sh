#!/bin/bash
# Запуск первого бота (ATLANT LEX / NareBot) из корня проекта АБФЛ
cd "$(dirname "$0")/Наре проект/NareBot" || exit 1
if [ ! -f .env ]; then
  cp .env.example .env 2>/dev/null || true
  echo "Создан .env. Укажите в нём BOT_TOKEN (токен от @BotFather) и при необходимости BITRIX_WEBHOOK."
  echo "Затем запустите снова: ./run_nare_bot.sh"
  exit 1
fi
if ! grep -q '^BOT_TOKEN=[0-9]\{5,}:' .env 2>/dev/null; then
  echo "В .env задайте BOT_TOKEN (токен от @BotFather, формат 123456789:ABC...)."
  exit 1
fi
if [ ! -d .venv ]; then
  echo "Создаю .venv и устанавливаю зависимости..."
  python3 -m venv .venv
  ./.venv/bin/pip install -r requirements.txt
fi
exec ./.venv/bin/python bot.py
