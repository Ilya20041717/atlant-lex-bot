# Деплой бота на хостинг REG.RU

Пошаговая инструкция: как залить бота на VPS/хостинг REG.RU и запустить в фоне.

---

## Что нужно от REG.RU

Для бота нужен **доступ по SSH** (терминал на сервере). Обычно это:

- **VPS** (виртуальный выделенный сервер) — в панели REG.RU есть раздел «VPS» или «Виртуальные серверы». После заказа вам пришлют **IP-адрес**, **логин** и **пароль** (или ключ) для SSH.
- Если купили только **обычный хостинг для сайтов** (без SSH) — там нельзя запустить бота 24/7. Нужно заказать именно VPS/облачный сервер.

Дальше предполагаем, что у вас есть **IP**, **логин** и **пароль** для SSH.

---

## 1. Подключиться к серверу по SSH

На Mac в терминале (подставьте свой IP и логин):

```bash
ssh логин@IP_АДРЕС_СЕРВЕРА
```

Пример: `ssh root@123.45.67.89`. Введите пароль, когда попросит. Вы окажетесь в консоли сервера.

---

## 2. Установить Docker (рекомендуется)

На сервере выполните по очереди:

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
```

Проверка: `sudo docker run hello-world` — должно вывести приветствие и выйти.

---

## 3. Скачать проект с GitHub

На сервере:

```bash
cd ~
git clone https://github.com/Ilya20041717/atlant-lex-bot.git
cd atlant-lex-bot
```

Если `git` не установлен: `sudo apt install -y git`, затем снова команды выше.

---

## 4. Создать файл с переменными (.env)

На сервере в папке проекта:

```bash
nano .env
```

В открывшийся редактор вставьте (подставьте свой токен и при необходимости остальное):

```
BOT_TOKEN=ваш_токен_от_BotFather
ADMIN_TG_IDS=654078115
OPENAI_API_KEY=ваш_ключ_если_нужен
OPENAI_ASSISTANT_ID=asst_4KnF6O3l92sexVF0sW88kD5q
```

Сохранить: `Ctrl+O`, Enter, выйти: `Ctrl+X`.

---

## 5. Собрать образ и запустить бота в фоне

Всё ещё в папке `~/atlant-lex-bot`:

```bash
sudo docker build -t atlant-lex-bot .
sudo docker run -d --restart unless-stopped --name atlant-lex-bot -v $(pwd)/data:/app/data --env-file .env atlant-lex-bot
```

- `-d` — в фоне.
- `--restart unless-stopped` — перезапуск после перезагрузки сервера.
- Данные SQLite сохраняются в папке `./data` на сервере.

Проверка: `sudo docker ps` — в списке должна быть контейнер `atlant-lex-bot`. Логи: `sudo docker logs -f atlant-lex-bot` (выход — `Ctrl+C`).

После этого бот работает в фоне; можно отключиться от SSH — он продолжит работать.

---

## 6. Обновить бота после изменений в коде

На сервере в папке проекта:

```bash
cd ~/atlant-lex-bot
git pull
sudo docker build -t atlant-lex-bot .
sudo docker stop atlant-lex-bot
sudo docker rm atlant-lex-bot
sudo docker run -d --restart unless-stopped --name atlant-lex-bot -v $(pwd)/data:/app/data --env-file .env atlant-lex-bot
```

---

## Если на REG.RU нет Docker (только Python)

1. Установите Python 3.10+ и зависимости:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
cd ~
git clone https://github.com/Ilya20041717/atlant-lex-bot.git
cd atlant-lex-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Создайте `.env` (как в шаге 4 выше).

3. Запуск в фоне с автоперезапуском при падении:

```bash
nohup python3 -m app.main >> bot.log 2>&1 &
```

Или настройте systemd-сервис (бот будет подниматься после перезагрузки сервера) — могу расписать отдельно по запросу.

---

## Кратко

| Шаг | Действие |
|-----|----------|
| 1 | Подключиться по SSH: `ssh логин@IP` |
| 2 | Установить Docker (команды выше) |
| 3 | `git clone ...` и `cd atlant-lex-bot` |
| 4 | Создать `.env` с `BOT_TOKEN` и др. |
| 5 | `sudo docker build ...` и `sudo docker run ...` |

После этого бот доступен в Telegram 24/7, даже когда ваш компьютер выключен.
