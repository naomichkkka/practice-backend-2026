# Список эндпоинтов API

Все эндпоинты под префиксом `/api/`. Требуется JWT в заголовке `Authorization: Bearer <access_token>`, кроме регистрации, логина и refresh.

## Авторизация

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/auth/register/` | Регистрация (username, email, password) |
| POST | `/api/auth/login/` | Вход, получение access + refresh токенов |
| POST | `/api/auth/refresh/` | Обновление access по refresh токену |

## Опросы

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/surveys/` | Список опросов (пагинация, фильтры: my, status; сортировка: date, responses_count) |
| POST | `/api/surveys/` | Создать опрос (автор = текущий пользователь) |
| GET | `/api/surveys/{id}/` | Детали опроса с вопросами и вариантами |
| PUT | `/api/surveys/{id}/` | Обновить опрос (только черновик, только автор) |
| PATCH | `/api/surveys/{id}/` | Частично обновить опрос |
| DELETE | `/api/surveys/{id}/` | Удалить опрос (только автор) |
| POST | `/api/surveys/{id}/publish/` | Опубликовать опрос (только автор, только из черновика) |
| POST | `/api/surveys/{id}/close/` | Закрыть опрос (только автор, только опубликованный) |

## Вопросы (в рамках опроса)

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/surveys/{survey_id}/questions/` | Список вопросов опроса |
| POST | `/api/surveys/{survey_id}/questions/` | Добавить вопрос (type: single_choice, multiple_choice, text; order) |
| GET | `/api/surveys/{survey_id}/questions/{qid}/` | Вопрос по id |
| PUT | `/api/surveys/{survey_id}/questions/{qid}/` | Изменить вопрос (только черновик) |
| PATCH | `/api/surveys/{survey_id}/questions/{qid}/` | Частично изменить |
| DELETE | `/api/surveys/{survey_id}/questions/{qid}/` | Удалить вопрос |

## Варианты ответов (для вопросов с выбором)

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/surveys/{survey_id}/questions/{qid}/choices/` | Варианты вопроса |
| POST | `/api/surveys/{survey_id}/questions/{qid}/choices/` | Добавить вариант (только для single_choice / multiple_choice) |
| PUT | `/api/surveys/{survey_id}/questions/{qid}/choices/{cid}/` | Изменить вариант |
| DELETE | `/api/surveys/{survey_id}/questions/{qid}/choices/{cid}/` | Удалить вариант |

## Прохождение опроса

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/surveys/{id}/take/` | Получить опрос для прохождения (только опубликованные, без ответов) |
| POST | `/api/surveys/{id}/submit/` | Отправить ответы (один раз на респондента; валидация по типу вопроса) |

## Аналитика и экспорт

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/surveys/{id}/analytics/` | Аналитика: кол-во респондентов, по вопросам с выбором — кол-во и %, текстовые ответы (только автор) |
| GET | `/api/surveys/{id}/export/` | Экспорт результатов в JSON (только автор) |

## Схема OpenAPI (Swagger)

- `GET /api/schema/swagger-ui/` — Swagger UI
- `GET /api/schema/redoc/` — ReDoc
- `GET /api/schema/` — OpenAPI schema (YAML/JSON)
