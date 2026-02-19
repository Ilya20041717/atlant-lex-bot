# Хостинг бота за 5 минут (Railway)

Код уже в GitHub: **Ilya20041717/atlant-lex-bot**. Дальше — только Railway.

## Шаги

1. **Зайдите на [railway.app](https://railway.app)** → войдите через GitHub.

2. **New Project** → **Deploy from GitHub repo** → выберите репозиторий **atlant-lex-bot**.

3. Railway сам найдёт `Dockerfile` и начнёт сборку. Дождитесь **Deployed**.

4. Откройте сервис → вкладка **Variables** → **Add Variable**:
   - `BOT_TOKEN` = токен от @BotFather (обязательно)

   По желанию добавьте из вашего `.env`:
   - `START_IMAGE_FILE_ID` — чтобы на старте показывалась картинка
   - `ADMIN_TG_IDS` — ваш Telegram ID для уведомлений о заявках (например `654078115`)
   - `OPENAI_API_KEY`, `OPENAI_ASSISTANT_ID` — если используете ИИ-ответы

5. Сохраните. Railway перезапустит бота с новыми переменными.

6. Готово. Бот работает 24/7. Ссылка для клиентов: **t.me/ИМЯ_ВАШЕГО_БОТА**.

---

**Обновление бота в будущем:** в папке проекта выполните:
```bash
git add -A && git commit -m "update" && git push
```
Railway автоматически пересоберёт и перезапустит бота.
