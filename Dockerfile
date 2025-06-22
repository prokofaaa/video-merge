# 1. Базовый образ
FROM python:3.10-slim

# 2. Установка ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# 3. Копируем зависимости и ставим их
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем код приложения
COPY . /app

# 5. Открываем порт 8000 (по умолчанию Railway его определяет)
EXPOSE 8000

# 6. Команда запуска
CMD ["python", "app.py"]
