# Базовий образ з Python
FROM python:3.12

# Встановлюємо змінну середовища для коректного виводу в Docker
ENV PYTHONUNBUFFERED 1

# Робоча директорія в контейнері
WORKDIR /app

# Встановлюємо залежності
COPY requirements.txt /app
RUN pip install -r requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо всі файли проєкту в контейнер
COPY project_1444 /app

# Запускаємо сервер Django
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project_1444.wsgi:application"]
CMD ["bash", "-c", "./run.sh"]
