FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install poetry

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock* /app/

# Установка зависимостей
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Копирование проекта
COPY . /app/
