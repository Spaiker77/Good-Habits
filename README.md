# GoodHabits — бэкенд трекера привычек (Django + DRF + Celery + Redis + Telegram)

Учебный проект по книге Джеймса Клира «Атомные привычки».  
Реализует учёт полезных/приятных привычек, напоминания в Telegram, JWT-авторизацию, CORS, пагинацию, документацию и тесты.

---

## Стек

- **Python 3.12**
- **Django 5**, **Django REST Framework**
- **JWT**: `djangorestframework-simplejwt`
- **Документация**: `drf-spectacular` (Swagger UI)
- **Celery + Redis** (напоминания)
- **PostgreSQL**
- **CORS**: `django-cors-headers`
- **Тесты**: `pytest`, `pytest-django`, `model-bakery`, `pytest-cov`
- **Линтинг**: `flake8`

---

## Быстрый старт (Windows / PowerShell)

```powershell
# 0) Redis & PostgreSQL (локально)
# - Установи Redis (порт 6379) и запусти redis-server
# - Создай БД PostgreSQL (см. ниже)

# 1) Клонирование
git clone <repo-url> GoodHabits
cd GoodHabits

# 2) Виртуальное окружение
py -m venv .venv
. .venv\Scripts\activate

# 3) Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# 4) Настройка переменных окружения
copy .env.example .env
# отредактируй .env (SECRET_KEY, доступы к БД, TELEGRAM_BOT_TOKEN и т.п.)

# 5) Миграции и суперпользователь
python manage.py migrate
python manage.py createsuperuser

# 6) Запуск
python manage.py runserver
```

### Создание БД (пример для psql)

```sql
CREATE DATABASE habits_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE habits_db TO postgres;
```

---

## Переменные окружения (`.env`)

```ini
DEBUG=True
SECRET_KEY=dev-secret
ALLOWED_HOSTS=127.0.0.1,localhost

# Postgres
DB_NAME=habits_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432

# CORS (фронтенд)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# JWT
ACCESS_LIFETIME_MIN=60
REFRESH_LIFETIME_DAYS=7

# Redis / Celery
REDIS_URL=redis://127.0.0.1:6379/0

# Telegram (обязателен для напоминаний)
TELEGRAM_BOT_TOKEN=123456789:ABC...
DEFAULT_TELEGRAM_CHAT_ID=000000000   # временно; лучше хранить per-user
```

`.env.sample` можно хранить в репозитории, `.env` — нет.

---

## Архитектура/структура

```
GoodHabits/
  habits_backend/
    __init__.py            # включает celery_app
    settings.py            # окружение, DRF, JWT, CORS, Celery
    urls.py                # swagger, jwt, api
    celery.py              # Celery конфиг
    wsgi.py / asgi.py
  habits/
    models.py              # Habit + валидаторы в save/clean
    validators.py
    serializers.py
    permissions.py
    pagination.py
    views.py
    urls.py
    admin.py
    tests/
      ...
  accounts/
    serializers.py         # регистрация
    views.py
    urls.py
  telegram_bot/
    bot.py                 # отправка HTTP в Telegram
    tasks.py               # Celery-задача напоминаний
    tests/
      ...
  requirements.txt
  pytest.ini
  setup.cfg                # flake8
  .env
  .env.example
  manage.py
  README.md   ← (этот файл)
```

---

## Миграции/данные

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata fixtures/*.json  # опционально
```

---

## Запуск Celery (Windows)

Открой 2 отдельные консоли **внутри** виртуального окружения:

```powershell
# Консоль 1 — worker
celery -A habits_backend worker -l INFO -P solo

# Консоль 2 — beat (планировщик)
celery -A habits_backend beat -l INFO
```

> В проекте настроена периодическая задача `habit-reminders` раз в 60 секунд: ищет привычки «на текущее время» и шлёт уведомления в Telegram.

---

## Документация API

- **Swagger UI**: `GET /api/docs/`
- **OpenAPI**: `GET /api/schema/`

---

## Аутентификация

- Регистрация: `POST /api/register/`
  
  ```json
  {
    "username": "newuser",
    "password": "StrongPass123!",
    "email": "new@example.com"
  }
  ```

- Получение токена: `POST /api/token/obtain/`
  
  ```json
  {
    "username": "newuser",
    "password": "StrongPass123!"
  }
  ```

  Ответ: `{ "access": "...", "refresh": "..." }`

- Обновление токена: `POST /api/token/refresh/` с `{"refresh":"..."}`

**Заголовки для защищённых эндпоинтов**:  
`Authorization: Bearer <access-token>`

---

## Модель Habit (ключевые поля)

- `user` — владелец
- `place` — место выполнения
- `time` — время (HH:MM)
- `action` — действие
- `is_pleasant` — признак «приятной привычки»
- `linked_habit` — ссылка на **приятную** привычку (только для полезных)
- `periodicity_days` — частота (1..7), по умолчанию 1 (ежедневно)
- `reward` — награда (строка)
- `duration_seconds` — предполагаемая длительность (≤ 120)
- `is_public` — публичность

### Валидаторы/правила

- Нельзя одновременно `reward` и `linked_habit`.
- `linked_habit` должна быть `is_pleasant=True`.
- У `is_pleasant=True` нельзя иметь `reward` или `linked_habit`.
- `duration_seconds ≤ 120`.
- `periodicity_days ∈ [1..7]`.

---

## Эндпоинты

| Метод | Путь                       | Описание                                  | Доступ |
|------:|----------------------------|-------------------------------------------|:------:|
| POST  | `/api/register/`          | Регистрация                               | Public |
| POST  | `/api/token/obtain/`      | JWT получить пары                         | Public |
| POST  | `/api/token/refresh/`     | JWT обновить                               | Public |
| GET   | `/api/habits/`            | Список **моих** привычек, пагинация 5/стр | Auth   |
| POST  | `/api/habits/`            | Создать свою привычку                      | Auth   |
| GET   | `/api/habits/{id}/`       | Получить свою                              | Auth   |
| PATCH | `/api/habits/{id}/`       | Обновить свою                              | Auth   |
| DELETE| `/api/habits/{id}/`       | Удалить свою                               | Auth   |
| GET   | `/api/public-habits/`     | Публичные привычки (без редактирования)    | Public |
| GET   | `/api/docs/`              | Swagger UI                                 | Public |

**Пагинация** (только в `/api/habits/`): `?page=1`

---

## Напоминания в Telegram

1. В `.env` задайте `TELEGRAM_BOT_TOKEN` (создать у @BotFather).
2. Временно укажете `DEFAULT_TELEGRAM_CHAT_ID` — свой chat_id (узнать через @userinfobot).
3. Запустите Celery worker и Celery beat.
4. Создайте привычку с `time` равным ближайшей минуте, Celery отправит сообщение в указанное время.

> На проде лучше сохранять `telegram_chat_id` у пользователя (через команду `/start` и webhook/long polling). Для курса достаточно `DEFAULT_TELEGRAM_CHAT_ID`.

---

## Тесты и покрытие

```powershell
pytest -q --cov=habits --cov=telegram_bot --cov-report=term-missing
```

- Покрываются: валидаторы, CRUD, права, пагинация, публичные, JWT, Celery-напоминания.
- Цель: **≥80%**.

---

## Линтинг

```powershell
flake8
```

`setup.cfg`:
```ini
[flake8]
max-line-length = 100
exclude = .venv,*/migrations/*,__pycache__
extend-ignore = E203,W503
```

---

## CORS

В `settings.py` используется `django-cors-headers`. Разрешённые источники из `.env`:

```ini
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

## Типовые проблемы и решения

- **400 при регистрации** — проверь пароль (валидаторы) и валидный email.
- **401 на защищённых ручках** — не передан/протух `Authorization: Bearer <token>`.
- **Напоминания не приходят**:
  - запущены **оба** процесса: `celery worker` и `celery beat`;
  - `REDIS_URL` доступен;
  - `TELEGRAM_BOT_TOKEN` и `DEFAULT_TELEGRAM_CHAT_ID` заданы;
  - время привычки совпадает с текущей минутой сервера (секунды/TZ).
- **psycopg2 ошибка подключения** — проверь `DB_HOST/PORT/USER/PASSWORD/NAME`, запущен ли PostgreSQL.
- **CORS ошибки на фронте** — добавь origin фронта в `CORS_ORIGINS`.

---

## Prod/деплой (кратко)

- `DEBUG=False`, корректные `ALLOWED_HOSTS`.
- Секреты/токены через `.env` или менеджер секретов.
- Supervisor/systemd для `gunicorn`/`uvicorn`, `celery worker`, `celery beat`.
- Reverse proxy (Nginx).
- Отдельный Redis/DB.

---

## Лицензия

Учебный проект. Используйте свободно для обучения и pet-проектов.
