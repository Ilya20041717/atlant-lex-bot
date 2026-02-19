# Хостинг бота без иностранной карты (работа в фоне)

Нужно, чтобы бот работал в фоне 24/7, а иностранной карты нет. Ниже варианты по возрастанию надёжности.

---

## 1. Render.com (без карты)

- Обычно **не просят карту** на бесплатном плане.
- [render.com](https://render.com) → войти через GitHub → **New +** → **Background Worker** → репо **atlant-lex-bot**.
- **Build:** `pip install -r requirements.txt`, **Start:** `python -m app.main`.
- В **Environment** добавить **BOT_TOKEN** (и при желании остальные из `.env`).
- Минус: на Free воркер может «засыпать» после 15 мин без трафика; первое сообщение может прийти с задержкой 30–60 сек.

Подробно: **RENDER_DEPLOY.md**.

---

## 2. Российский VPS (оплата российской картой / Qiwi / СБП)

Бот крутится в фоне без «засыпания». Оплата: карта РФ, Qiwi, СБП и т.п.

**Провайдеры (ориентир 200–400 ₽/мес):**

| Провайдер | Сайт | Оплата |
|-----------|------|--------|
| **Timeweb** | [timeweb.com](https://timeweb.com) | Карта РФ, СБП |
| **Selectel** | [selectel.ru](https://selectel.ru) | Карта РФ, юрлица |
| **REG.RU** | [reg.ru](https://www.reg.ru) | Карта РФ, Qiwi |
| **Beget** | [beget.com](https://beget.com) | Карта РФ |
| **VDSina** | [vdsina.ru](https://vdsina.ru) | Карта РФ, от ~200 ₽/мес |

**Что сделать на VPS (Ubuntu):**

1. Арендовать VPS (минимальный тариф, Ubuntu 22.04).
2. Подключиться по SSH, установить Docker:
   ```bash
   sudo apt update && sudo apt install -y docker.io
   sudo systemctl enable docker && sudo systemctl start docker
   ```
3. Скопировать проект на сервер (Git или архив):
   ```bash
   git clone https://github.com/Ilya20041717/atlant-lex-bot.git
   cd atlant-lex-bot
   ```
4. Создать на сервере файл `.env` с переменными (минимум `BOT_TOKEN`). Можно скопировать с компьютера или набрать вручную:
   ```bash
   nano .env
   # BOT_TOKEN=...
   # ADMIN_TG_IDS=654078115
   # и т.д.
   ```
5. Запустить бота в фоне:
   ```bash
   sudo docker build -t atlant-lex-bot .
   sudo docker run -d --restart unless-stopped --name atlant-lex-bot -v $(pwd)/data:/app/data --env-file .env atlant-lex-bot
   ```
6. Логи: `sudo docker logs -f atlant-lex-bot`.

После этого бот работает в фоне даже когда ваш компьютер выключен.

---

## 3. Домашний компьютер или Raspberry Pi (бесплатно)

Если есть ПК или Raspberry Pi, который может быть включён постоянно:

1. На нём установите Python 3.10+ и склонируйте репо (или скопируйте папку проекта).
2. Создайте `.env` с `BOT_TOKEN` и остальным.
3. Запустите в фоне через **systemd** (Linux) или **nohup**:
   ```bash
   cd /путь/к/АБФЛ
   nohup python3 -m app.main > bot.log 2>&1 &
   ```
   Или настройте systemd-сервис с `Restart=always` — тогда после перезагрузки ПК бот поднимется сам.

Минус: пока компьютер выключен или без интернета, бот не отвечает.

---

## 4. Oracle Cloud Always Free (попробовать без списаний)

Oracle даёт бесплатные VPS без списаний. При регистрации могут попросить карту только для верификации (иногда списывают и возвращают 1$). Не у всех российских карт проходит.

- [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)
- Создать Always Free VM (Ubuntu), подключиться по SSH.
- Дальше как в пункте 2 (установка Docker или Python, клонирование репо, `.env`, запуск контейнера или `python -m app.main` в фоне).

---

## Кратко

| Вариант              | Карта      | В фоне 24/7      | Сложность   |
|----------------------|------------|------------------|-------------|
| Render               | Не нужна   | Может засыпать   | Легко       |
| Российский VPS       | РФ / Qiwi  | Да               | Средне      |
| Домашний ПК / RPi     | Не нужна   | Пока ПК включён | Легко       |
| Oracle Cloud Free    | Могут спросить | Да         | Средне      |

Для стабильной работы в фоне без иностранной карты оптимально: **Render** (если устраивает возможная задержка после простоя) или **российский VPS** (Timeweb, REG.RU и т.п.) за 200–400 ₽/мес.
