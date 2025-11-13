# Auth Service

Сервис авторизации на FastAPI с JWT токенами

## Быстрый старт

```bash

# 1. Установить зависимости
pip install -r requirements.txt

# 2. Запустить сервер
python -m main
```

## Документация API
http://localhost:8000/docs

## Реализованные роуты
- POST /api/v1/auth/registration
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- PATCH /api/v1/account/change-password
- PATCH /api/v1/account/change-login
- GET /api/v1/account/user-info
- GET /api/v1/account/auth-history
