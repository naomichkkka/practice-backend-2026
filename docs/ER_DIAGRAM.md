# ER-диаграмма (Survey API)

## Сущности

- **User** (django.contrib.auth) — пользователь (автор и/или респондент).
- **Survey** — опрос: title, description, status (draft | published | closed), author_id → User.
- **Question** — вопрос: survey_id → Survey, text, type (single_choice | multiple_choice | text), order.
- **Choice** — вариант ответа: question_id → Question, text. Только у вопросов с типом single_choice / multiple_choice.
- **Response** — прохождение опроса: survey_id → Survey, respondent_id → User. Уникальная пара (survey, respondent).
- **Answer** — ответ на один вопрос в рамках одного прохождения: response_id → Response, question_id → Question; text_answer (для текстовых), selected_choices M2M → Choice (для выбора).

## Связи

```
User 1───* Survey (author)
User 1───* Response (respondent)

Survey 1───* Question
Question 1───* Choice

Survey 1───* Response
Response 1───* Answer
Question 1───* Answer

Answer *───* Choice (selected_choices)
```

## Ограничения

- Уникальность: (Response.survey, Response.respondent).
- Валидация на уровне приложения: у текстового вопроса нет Choice; у Answer для single_choice — ровно один selected_choice, для multiple_choice — один и более, для text — только text_answer.

## Диаграмма (текстовый вид)

```
┌─────────┐       ┌─────────┐       ┌──────────┐
│  User   │───*───│ Survey  │───*───│ Question │
└────┬────┘       └────┬────┘       └────┬─────┘
     │                 │                  │
     │                 │                  └───*───┌───────┐
     │                 │                          │ Choice│
     │                 │                          └───────┘
     │                 │
     │                 └───*───┌──────────┐
     │                         │ Response │
     └─────────────────────────┼──────────┤
                               └────┬─────┘
                                    │
                                    └───*───┌───────┐
                                            │ Answer│─── text_answer
                                            └───┬───┘
                                                │
                                                └───*─── Choice (M2M)
```

Для визуальной ER-диаграммы можно использовать [dbdiagram.io](https://dbdiagram.io) или аналог.
