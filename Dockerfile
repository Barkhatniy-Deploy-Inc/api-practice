# Этап 1: Сборка зависимостей
FROM python:3.10-slim as builder

WORKDIR /app

# Установка системных зависимостей для сборки некоторых библиотек
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Этап 2: Финальный образ
FROM python:3.10-slim

WORKDIR /app

# Копируем виртуальное окружение из этапа сборки
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копируем код приложения
COPY . .

# Создаем папку для логов и БД, если их нет
RUN mkdir -p logs

# Переменные окружения по умолчанию
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Порт, который будет слушать FastAPI
EXPOSE 8000

# Запуск приложения через uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
