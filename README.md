# maintenance-api

Система мониторинга и обслуживания промышленного оборудования (FastAPI + SQLAlchemy 2.0 + PostgreSQL 15).

## Быстрый старт

```bash
cp .env.example .env                 # обязательно поменяйте SECRET_KEY
docker compose up -d                 # PostgreSQL 15 (:5432) + pgAdmin 4 (:5050)

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

alembic upgrade head                 # создать таблицы
python seed.py                       # тестовые данные (идемпотентно)
uvicorn app.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (логин/пароль из `.env`; хост БД внутри compose — `db`)

## Тестовые пользователи

| Роль       | Логин        | Пароль          |
|------------|--------------|-----------------|
| ADMIN      | admin        | admin123        |
| DISPATCHER | dispatcher   | dispatcher123   |
| TECHNICIAN | technician   | technician123   |
| WORKER     | worker       | worker123       |

QR-коды станков: `EQ-0001` … `EQ-0004`.

## Права доступа

| Действие                          | Роли                              |
|-----------------------------------|-----------------------------------|
| Создание оборудования             | ADMIN, DISPATCHER                 |
| Создание/список пользователей     | ADMIN / ADMIN, DISPATCHER         |
| Смена статуса заявки              | ADMIN, DISPATCHER, TECHNICIAN     |
| Остальные эндпоинты               | любой авторизованный              |

WORKER видит в `GET /requests` только свои заявки.

## Логика обходов

Булевы пункты чек-листа сформулированы так, что «Да» = норма, поэтому `boolean_value == false` — аномалия.
Числовые пункты — аномалия при выходе за `min_value..max_value`. При наличии хотя бы одной аномалии
автоматически создаётся заявка `NEW` / `HIGH`, привязанная к обходу (`inspection_id`).
В обходе должны быть ответы на все пункты чек-листа типа оборудования.
