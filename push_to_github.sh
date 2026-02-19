#!/usr/bin/env bash
# Подключение к GitHub и пуш. Запуск: ./push_to_github.sh ВАШ_ЛОГИН_GITHUB
set -e
cd "$(dirname "$0")"
if [ -z "$1" ]; then
  echo "Укажите логин GitHub: ./push_to_github.sh ВАШ_ЛОГИН"
  echo "Сначала создайте репо: https://github.com/new?name=atlant-lex-bot (кнопка Create repository, без README)"
  exit 1
fi
USER="$1"
REPO="atlant-lex-bot"
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/${USER}/${REPO}.git"
git push -u origin main
echo ""
echo "Готово. Дальше: railway.app → New Project → Deploy from GitHub → выберите ${REPO} → Variables → добавьте BOT_TOKEN, OPENAI_API_KEY, OPENAI_ASSISTANT_ID, AI_PROVIDER=openai"
