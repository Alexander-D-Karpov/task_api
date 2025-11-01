# Task Management API

REST API для системы управления задачами.

## Возможности

- Регистрация и аутентификация через JWT
- CRUD операции для задач
- Фильтрация и поиск задач
- Совместный доступ к задачам
- Email-уведомления о приближающихся дедлайнах

## Технологии

- Django 4.2
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- JWT аутентификация

## Установка

### Локальная установка
```bash
# Установка uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -e .

cp .env.template .env

python manage.py migrate

python manage.py runserver_plus
```

### Docker
```bash
docker-compose up --build
```

## API Эндпоинты

### Аутентификация

- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/login/` - Получение JWT токена
- `POST /api/auth/token/refresh/` - Обновление токена

### Задачи

- `GET /api/tasks/` - Список задач
- `POST /api/tasks/` - Создание задачи
- `GET /api/tasks/{id}/` - Детали задачи
- `PATCH /api/tasks/{id}/` - Обновление задачи
- `DELETE /api/tasks/{id}/` - Удаление задачи

### Расшаривание

- `POST /api/tasks/{id}/share/` - Поделиться задачей
- `GET /api/tasks/{id}/shares/` - Список пользователей с доступом
- `DELETE /api/tasks/shares/{id}/` - Удалить доступ

## Документация API

Swagger UI: http://localhost:8000/api/docs/

## Тестирование
```bash
uv run pytest

# С покрытием
uv run pytest --cov
```

## Celery
```bash
celery -A config.celery_app worker -l info

celery -A config.celery_app beat -l info

celery -A config.celery_app flower
```

## Mailhog

Для тестирования email в development окружении используется Mailhog.

Web интерфейс: http://localhost:8025

## Линтинг
```bash
# Проверка кода
uv run ruff check .

# Автоисправление
uv run ruff check --fix .

# Форматирование
uv run ruff format .
```
