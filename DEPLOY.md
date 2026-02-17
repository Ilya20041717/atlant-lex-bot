# Пошаговый деплой бота BINC LEXA (бесплатно)

Чтобы бот работал 24/7 без вашего компьютера и его можно было отправлять клиентам (`t.me/ВашБот`), сделайте по шагам один из вариантов ниже.

---

## Общий шаг: залить проект в GitHub

Если репозитория ещё нет:

1. В корне проекта (папка `АБФЛ`) выполните:
   ```bash
   cd "/Users/ilabyckov/Downloads/Нужное/Business increase/АБФЛ"
   git init
   git add .
   git commit -m "BINC LEXA bot: deploy config"
   ```
2. На [github.com](https://github.com) нажмите **New repository**, создайте репо (например, `binc-lexa-bot`), **не** добавляйте README (у вас уже есть файлы).
3. Подключите репо и запушьте (подставьте свой логин и имя репо):
   ```bash
   git remote add origin https://github.com/ВАШ_ЛОГИН/binc-lexa-bot.git
   git branch -M main
   git push -u origin main
   ```

Дальше выберите **один** способ: **Railway** (проще всего), **Vercel** (бесплатно, нужна БД Neon) или Fly.io.

**Одной командой:** из корня проекта запустите `./deploy.sh` — скрипт сделает коммит, push (если настроен remote) и подскажет следующие шаги.

---

## Вариант A: Railway (проще всего, как раньше)

1. Зайдите на [railway.app](https://railway.app) и войдите через GitHub.
2. **New Project** → **Deploy from GitHub repo**.
3. Выберите репозиторий с ботом (например, `binc-lexa-bot`). Railway сам найдёт `Dockerfile` в корне и соберёт образ.
4. Откройте созданный сервис → вкладка **Variables**.
5. Добавьте переменные (минимум обязательно):
   - `BOT_TOKEN` = токен от @BotFather  
   Остальное по желанию (скопируйте из вашего `.env`): `START_IMAGE_FILE_ID`, `AGENCY_NAME`, `DB_URL`, ключи ИИ, ПАУ и т.д.
6. Сохраните. Деплой запустится сам. Дождитесь статуса **Success** / **Active**.
7. Готово. Бот уже работает. Ссылка для клиентов: `https://t.me/ИМЯ_ВАШЕГО_БОТА`.

**Обновление бота:** сделайте `git add` → `git commit` → `git push` в этот же репо — Railway пересоберёт и перезапустит бота автоматически.

---

## Вариант B: Fly.io

1. Установите [flyctl](https://fly.io/docs/hands-on/install-flyctl/) (на Mac: `brew install flyctl`).
2. Войдите: `fly auth login` (откроется браузер).
3. В корне проекта:
   ```bash
   cd "/Users/ilabyckov/Downloads/Нужное/Business increase/АБФЛ"
   fly launch
   ```
   - Имя приложения можно оставить `binc-lexa` или ввести своё.
   - Регион выберите ближайший (например, `ams` — Амстердам).
   - На вопрос про PostgreSQL нажмите **No**.
   - На вопрос **Would you like to set up a volume?** можно ответить **No** — том для SQLite уже описан в `fly.toml`; его нужно создать отдельно (шаг 5).
4. Создайте том для базы (подставьте имя приложения и регион, если меняли):
   ```bash
   fly volumes create binc_lexa_data --region ams --size 1
   ```
5. Задайте секреты (токен и при необходимости остальное из `.env`):
   ```bash
   fly secrets set BOT_TOKEN="ВАШ_ТОКЕН_ОТ_BOTFATHER"
   ```
   Опционально несколько переменных сразу:
   ```bash
   fly secrets set BOT_TOKEN="..." START_IMAGE_FILE_ID="..." AGENCY_NAME="Агентство по банкротству"
   ```
6. Деплой:
   ```bash
   fly deploy
   ```
7. Проверка логов: `fly logs`. Бот работает по `t.me/ИМЯ_ВАШЕГО_БОТА`.

**Обновление:** после изменений в коде — `git push`, затем в папке проекта: `fly deploy`.

---

## Вариант C: Vercel (бесплатно, webhook)

На Vercel бот работает по **webhook**: Telegram шлёт обновления на ваш URL. Нужна внешняя БД (SQLite на Vercel не сохраняется) — бесплатно подойдёт **Neon** (Postgres).

1. **БД:** зайдите на [neon.tech](https://neon.tech), создайте аккаунт и проект. Скопируйте connection string (вид `postgresql://user:pass@host/dbname`). В переменных Vercel он должен быть как **postgresql+asyncpg://...** (замените в начале `postgresql://` на `postgresql+asyncpg://`).
2. **Деплой:** на [vercel.com](https://vercel.com) → **Add New** → **Project** → импортируйте репозиторий с ботом. Root Directory оставьте корнем. Deploy.
3. **Переменные:** в настройках проекта → **Environment Variables** добавьте:
   - `BOT_TOKEN` — токен от @BotFather
   - `DB_URL` — строка Neon в формате `postgresql+asyncpg://user:pass@host/dbname?sslmode=require`  
   При желании добавьте остальное из `.env` (START_IMAGE_FILE_ID, AGENCY_NAME и т.д.).
4. **Webhook:** после деплоя узнайте URL проекта (например `https://binc-lexa-xxx.vercel.app`). Один раз выполните (подставьте токен и URL):
   ```bash
   curl "https://api.telegram.org/bot<ВАШ_BOT_TOKEN>/setWebhook?url=https://ВАШ-ПРОЕКТ.vercel.app/api/webhook"
   ```
   В ответ должно быть `"ok":true`. Готово: бот отвечает по `t.me/ВашБот`.

**Ограничение:** FSM (состояние диалога) хранится в памяти серверной функции — при «холодном» старте может сброситься. Для стабильных длинных сценариев лучше Railway или Fly.io.

---

## Стартовая картинка на хостинге

На сервере нет вашего локального файла. Используйте **START_IMAGE_FILE_ID**:

1. Отправьте нужную картинку боту в Telegram (в личку бота).
2. Узнайте `file_id`: либо из логов бота при старте, либо через бота [@userinfobot](https://t.me/userinfobot) (Forward ему сообщение с фото — покажет file_id).
3. В Railway (Variables) или Fly (`fly secrets set START_IMAGE_FILE_ID="AgACAgIAAxkB..."`) укажите этот `file_id`.

После деплоя бот будет работать постоянно, даже когда компьютер выключен. Ссылку `t.me/ВашБот` можно отправлять клиентам.
