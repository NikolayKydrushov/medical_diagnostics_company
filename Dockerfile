FROM python:3.13-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install poetry==1.8.5

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock* /app/

# Установка зависимостей
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Копирование проекта
COPY . /app/

# Команда для запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
