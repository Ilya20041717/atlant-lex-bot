# Бот BINC LEXA — образ для хостинга 24/7
FROM python:3.12-slim

WORKDIR /app

# Зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код приложения
COPY app/ ./app/
COPY .env.example .env.example

# Папка для SQLite (если используется)
RUN mkdir -p /app/data

# Переменные окружения задаются при запуске (BOT_TOKEN и др.)
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "app.main"]
