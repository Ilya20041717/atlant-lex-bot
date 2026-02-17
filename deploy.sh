#!/usr/bin/env bash
# Делает коммит, push (если настроен remote) и подсказывает шаги деплоя.
set -e
cd "$(dirname "$0")"

echo "→ Добавляю изменения..."
git add -A
if git diff --staged --quiet; then
  echo "  Нет изменений для коммита."
else
  git commit -m "deploy: update"
  echo "  Коммит создан."
fi

if git remote get-url origin &>/dev/null; then
  echo "→ Отправляю на GitHub..."
  git push origin main 2>/dev/null || git push origin master 2>/dev/null || true
  echo ""
  echo "Готово. Дальше:"
  echo "  • Railway: https://railway.app → New Project → Deploy from GitHub → выберите репо → Variables → BOT_TOKEN."
  echo "  • Vercel:  https://vercel.com → Import repo → добавьте BOT_TOKEN и DB_URL (Neon, postgresql+asyncpg://...) → после деплоя выполните setWebhook (см. DEPLOY.md)."
else
  echo ""
  echo "Remote не настроен. Создайте репо на GitHub и выполните:"
  echo "  git remote add origin https://github.com/ВАШ_ЛОГИН/ИМЯ_РЕПО.git"
  echo "  git push -u origin main"
  echo "После этого снова запустите: ./deploy.sh"
fi
