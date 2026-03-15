# Survey API

API сервиса опросов и голосований. Платформа для создания анкет с разными типами вопросов, сбора ответов и аналитики.

**Стек:** Django, Django REST Framework, JWT (Simple JWT), PostgreSQL / SQLite, drf-spectacular (OpenAPI).

## Возможности

- **Пользователи:** регистрация, авторизация по JWT; один пользователь может быть и автором опросов, и респондентом.
- **Опросы:** создание с заголовком и описанием, статусы «черновик» → «опубликован» → «закрыт».
- **Вопросы:** одиночный выбор, множественный выбор, текстовый ответ; порядок вопросов, варианты ответов для вопросов с выбором.
- **Прохождение:** респондент проходит опрос один раз; валидация ответов по типу вопроса.
- **Аналитика:** количество респондентов, статистика по вариантам (количество и %), текстовые ответы, экспорт в JSON.
- **Список опросов:** пагинация, фильтрация (мои / активные / завершённые), сортировка.

## Быстрый старт

### Локально (SQLite)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### С Docker (PostgreSQL)

```bash
docker-compose up --build
```

API: http://localhost:8000/api/  
Документация Swagger: http://localhost:8000/api/schema/swagger-ui/

## Переменные окружения (Docker)

- `DB_ENGINE=postgresql` — использовать PostgreSQL.
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` — параметры БД.
- `DB_HOST`, `DB_PORT` — хост и порт БД (по умолчанию `db:5432` в docker-compose).

## Основные эндпоинты

См. [API_ENDPOINTS.md](docs/API_ENDPOINTS.md) и Swagger UI.

- `POST /api/auth/register/` — регистрация.
- `POST /api/auth/login/` — получение JWT (access + refresh).
- `POST /api/auth/refresh/` — обновление access по refresh.
- `GET/POST /api/surveys/` — список опросов (с фильтрами/сортировкой) и создание.
- `GET/PUT/PATCH/DELETE /api/surveys/{id}/` — опрос по id.
- `POST /api/surveys/{id}/publish/`, `POST /api/surveys/{id}/close/` — смена статуса.
- Вопросы и варианты — вложенные в опрос или отдельные эндпоинты (см. Swagger).
- `GET /api/surveys/{id}/take/` — получить опрос для прохождения (только опубликованные).
- `POST /api/surveys/{id}/submit/` — отправить ответы респондента.
- `GET /api/surveys/{id}/analytics/` — аналитика для автора.
- `GET /api/surveys/{id}/export/` — экспорт результатов в JSON.

## ER-диаграмма

См. [docs/ER_DIAGRAM.md](docs/ER_DIAGRAM.md).

## Тесты

```bash
python manage.py test
```

## Лицензия

Учебный проект.
