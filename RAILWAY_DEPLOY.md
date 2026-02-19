# Деплой бота на Railway (один раз)

Код уже на GitHub: **Ilya20041717/atlant-lex-bot**

## Шаги

1. Откройте **https://railway.app** и войдите через **GitHub**.
2. Нажмите **New Project** → **Deploy from GitHub repo**.
3. Выберите репозиторий **atlant-lex-bot**. Railway подхватит Dockerfile и начнёт сборку.
4. Откройте созданный сервис → вкладка **Variables** (или **Settings** → **Variables**).
5. Добавьте переменные (скопируйте **значения** из вашего локального `.env`):

| Переменная | Откуда взять |
|------------|--------------|
| `BOT_TOKEN` | Токен от @BotFather (в .env) |
| `OPENAI_API_KEY` | Ключ OpenAI (в .env) |
| `OPENAI_ASSISTANT_ID` | `asst_4KnF6O3l92sexVF0sW88kD5q` |
| `AI_PROVIDER` | `openai` |
| `START_IMAGE_FILE_ID` | Опционально: отправьте логотип боту в Telegram, получите file_id (через @userinfobot или логи), вставьте сюда. Иначе старт без картинки. |

Остальные переменные (AGENCY_NAME, OPENAI_MODEL и т.д.) — по желанию, можно не добавлять.

6. Сохраните. Деплой перезапустится автоматически.
7. Когда статус **Success** / **Active** — бот работает 24/7. Ссылка для клиентов: **t.me/имя_вашего_бота**.

## Обновление бота позже

На своём компьютере:
```bash
cd "/Users/ilabyckov/Downloads/Нужное/Business increase/АБФЛ"
git add -A && git commit -m "update" && git push
```
Railway сам пересоберёт и перезапустит бота.
