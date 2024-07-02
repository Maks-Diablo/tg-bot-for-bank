# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /tg-bot-for-bank

# Устанавливаем зависимости для psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем poetry
RUN pip install poetry

# Копируем файлы с зависимостями
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Копируем все остальные файлы в контейнер
COPY . .

# Устанавливаем переменную окружения для логов на стандартный вывод
ENV PYTHONUNBUFFERED=1

# Устанавливаем PYTHONPATH для поиска модулей
ENV PYTHONPATH=/app

# Указываем команду для запуска вашего бота
CMD ["poetry", "run", "python", "tg_bot_for_bank/bot.py"]
