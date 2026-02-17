## Telegram-бот сопровождения клиентов

Система сопровождения клиентов агентства по банкротству физических лиц.  
Логика строго процессная и информационная, без юридических выводов.

### Запуск (MVP)

1. Создайте виртуальное окружение и установите зависимости:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Скопируйте `.env.example` в `.env` и укажите `BOT_TOKEN`.
3. Запустите бота:
   - `python -m app.main`

### Примечания

- По умолчанию используется SQLite (`./data/app.db`). Для PostgreSQL задайте `DB_URL`.
- Секции с пометкой `[ЗАГЛУШКА]` обозначены в коде комментариями.
- Для клиентского кабинета данные клиента должны быть внесены в БД.

---

## Хостинг 24/7 (чтобы бот работал без вашего компьютера)

Чтобы бот работал постоянно и его можно было отправлять клиентам, его нужно запустить на сервере в интернете. Ниже — несколько рабочих вариантов.

### Бесплатный хостинг (как мы уже делали)

Эти варианты позволяют держать бота онлайн без оплаты (или с бесплатным лимитом):

| Сервис | Что даёт | Ограничения |
|--------|----------|--------------|
| **Railway** | [railway.app](https://railway.app) — деплой из GitHub, ~\$5 бесплатного кредита в месяц | Часто хватает на один бот 24/7; после расхода кредита сервис останавливается до следующего месяца |
| **Fly.io** | [fly.io](https://fly.io) — маленькая VM 24/7 по бесплатной квоте | Нужно зарегистрироваться, привязать карту (списаний нет в рамках free tier); есть лимиты по ресурсам |
| **Oracle Cloud Always Free** | [oracle.com/cloud/free](https://www.oracle.com/cloud/free/) — всегда бесплатный VPS | Нужна регистрация и создание VM (Ubuntu), затем установка Docker и запуск бота как на обычном VPS |

**Пошаговый деплой (Railway и Fly.io)** — в файле [DEPLOY.md](DEPLOY.md): команды для GitHub, настройка Variables/секретов и запуск бота 24/7.

---

### Вариант 1: VPS (сервер по подписке)

Подходит, если нужен полный контроль и стабильная работа. Арендуете маленький Linux-сервер и запускаете бота там.

**Примеры провайдеров (РФ и мир):**

- **Timeweb** — [timeweb.com](https://timeweb.com) (есть тарифы от ~200 ₽/мес)
- **Selectel** — [selectel.ru](https://selectel.ru) (облако/VPS)
- **REG.RU** — [reg.ru](https://www.reg.ru) (VPS)
- **DigitalOcean** — [digitalocean.com](https://www.digitalocean.com) (от $4/мес)
- **Beget** — [beget.com](https://beget.com) (VPS)

**Шаги на VPS (Ubuntu/Debian):**

1. Подключитесь по SSH, установите Docker:
   ```bash
   sudo apt update && sudo apt install -y docker.io
   sudo systemctl enable docker && sudo systemctl start docker
   ```
2. Скопируйте на сервер папку проекта (через `scp`, Git или архив).
3. На сервере в папке проекта создайте файл `.env` с теми же переменными, что и локально (обязательно `BOT_TOKEN`). Для стартовой картинки на хостинге лучше использовать `START_IMAGE_FILE_ID` (загрузите картинку боту в Telegram, получите file_id через @userinfobot или логи).
4. Запустите контейнер (данные SQLite сохранятся в `./data`):
   ```bash
   docker build -t binc-lexa .
   docker run -d --restart unless-stopped --name binc-lexa -v $(pwd)/data:/app/data --env-file .env binc-lexa
   ```
5. Проверьте логи: `docker logs -f binc-lexa`.

Перезапуск после обновления кода: `docker build -t binc-lexa . && docker stop binc-lexa && docker rm binc-lexa && docker run -d --restart unless-stopped --name binc-lexa -v $(pwd)/data:/app/data --env-file .env binc-lexa`.

**Без Docker (только Python):** создайте виртуальное окружение, установите зависимости из `requirements.txt`, настройте `.env` и запускайте через systemd (unit-файл можно сделать по аналогии с LaunchAgent: `ExecStart=/путь/к/.venv/bin/python -m app.main`, `Restart=always`).

---

### Вариант 2: Railway

Удобно, если проект уже в Git: деплой по push, переменные задаются в веб-интерфейсе.

1. Зарегистрируйтесь на [railway.app](https://railway.app).
2. Создайте проект → Deploy from GitHub (привяжите репозиторий с этим ботом).
3. В настройках сервиса добавьте переменные окружения из `.env.example` (минимум `BOT_TOKEN`).
4. В Build задайте: Root Directory — папка, где лежит `Dockerfile` (корень репо); при наличии `Dockerfile` Railway соберёт образ и запустит контейнер.
5. Деплой запустится автоматически. Бот будет работать 24/7 (на бесплатном плане есть лимиты по времени работы/трафику; для постоянной работы обычно берут платный план).

---

### Вариант 3: Render

Похоже на Railway: деплой из Git, переменные в панели.

1. [render.com](https://render.com) → New → Background Worker.
2. Подключите репозиторий, укажите корень проекта.
3. Build: `docker build -t binc-lexa .` (или оставьте Docker), Start: `python -m app.main` (если без Docker — укажите команду и `pip install -r requirements.txt` в Build).
4. В разделе Environment добавьте переменные из `.env` (обязательно `BOT_TOKEN`).
5. После деплоя воркер будет работать постоянно (на бесплатном плане возможны ограничения по времени работы).

---

### Что учесть при хостинге

- **Стартовая картинка:** на сервере нет вашего локального файла. Заполните `START_IMAGE_FILE_ID` в `.env`: отправьте картинку боту в Telegram, получите file_id (например, через логи бота или бота @userinfobot) и вставьте в переменную.
- **База данных:** по умолчанию SQLite в `./data/app.db`. На Docker том `-v $(pwd)/data:/app/data` сохраняет базу между перезапусками. Для высокой нагрузки можно перейти на PostgreSQL (`DB_URL=postgresql+asyncpg://...` и добавить драйвер в `requirements.txt`).
- **Ссылка для клиентов:** после деплоя бот доступен по тому же имени в Telegram (например, `@YourBotName`). Ссылку вида `t.me/YourBotName` можно отправлять клиентам — бот будет отвечать, пока запущен на сервере.

---

## Первый бот (ATLANT LEX / NareBot)

В папке `Наре проект/NareBot` — бот на pyTelegramBotAPI с интеграцией Bitrix24: личный кабинет по телефону, заявки, вопросы, FAQ, загрузка документов.

**Локальный запуск (чтобы показать клиенту):**

```bash
./run_nare_bot.sh
```

При первом запуске скрипт создаст `.env` из `.env.example`; укажите в `.env` токен бота (`BOT_TOKEN`) и при необходимости `BITRIX_WEBHOOK`. Подробно — в `Наре проект/NareBot/README.md`.
