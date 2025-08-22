# API_MP Backend

Бэкенд на FastAPI для управления блогом с аутентификацией, категориями и статьями.  
Проект запускается через Docker и использует PostgreSQL, RabbitMQ, Celery и MailHog.

---

## 🛠 Стек технологий

- Python 3.9.6
- FastAPI
- PostgreSQL
- RabbitMQ
- Celery
- Flower (мониторинг Celery)
- MailHog (тестирование почты)
- Docker & Docker Compose
- Alembic (миграции)
- JWT аутентификация (через cookie)
- S3 для хранения изображений
- Pytest для тестирования
- RUFF и Pydantic Settings для валидации

---

## 📦 Установка и запуск на новом компьютере

1. **Клонировать репозиторий**

```bash
git clone <ссылка-на-репозиторий>
cd <папка-проекта>
```
2. **Собрать Docker-образы**
```bash
docker-compose build
```
3. **Запустить контейнеры в фоне**
```bash
docker-compose up -d
```
4. **Создать базу данных**
```bash
docker-compose exec db psql -U alex -d postgres -c "CREATE DATABASE alex;"
```
5. **Применить миграции**
```bash
docker-compose run --rm backend alembic upgrade head
```
6. **Ссылки на сервисы**
- **Swagger UI:** http://0.0.0.0:8000/docs/
- **Flower (мониторинг Celery):** http://localhost:5555/
- **RabbitMQ Management:** http://localhost:15672/
- **MailHog (тестирование почты):** http://localhost:8025/

---

## 📦 Аутентификация
- **Регистрация:** POST /auth/register
После регистрации пользователю отправляется письмо через RabbitMQ и Celery воркер.

- **Логин:** POST /auth/login
При успешном входе выдаётся JWT токен в cookie.

- **Логаут:** POST /auth/logout

JWT проверяется через middleware на каждом запросе к системе.

---

## 📦 Эндпоинты для блогов
| Метод  | URL                | Описание                                                              |
| ------ | ------------------ | --------------------------------------------------------------------- |
| **GET**    | `/blogs`           | Список статей с пагинацией и фильтрацией                              |
| **POST**   | `/blogs`           | Создание новой статьи (текст, название, категория, изображение)       |
| **PUT**    | `/blogs/{blog_id}` | Редактирование статьи                                                 |
| **DELETE** | `/blogs/{blog_id}` | Фейковое удаление статьи (оставляется в БД, но исключается из выдачи) |

**Query-параметры для GET /blogs:**

**search** — полнотекстовый поиск по статьям (PostgreSQL)

**category_id** — фильтр по категории

**page_number** — номер страницы

**page_size** — количество элементов на странице (есть ограничение на max)

Особенности:

- При создании статьи автоматически проставляются даты создания и изменения.

- Изображения хряняться в S3.

---

## 📦 Эндпоинты для категорий
| Метод | URL           | Описание                 |
| ----- | ------------- | ------------------------ |
| **GET**   | `/categories` | Список категорий         |
| **POST**  | `/categories` | Создание новой категории |

---

## 📦 Тестирование
Тесты запускаются внутри контейнера backend:
```bash
docker compose exec backend pytest -v
```
Или без захода в контейнер:
```bash
docker compose run --rm backend pytest -v
```

---

## 📦 Особенности проекта

- Полнотекстовый поиск статей реализован через PostgreSQL.

- JWT проверяется через middleware на каждом запросе.

- Фейковое удаление статей — удалённые статьи остаются в БД, но исключаются из выдачи.

- Отправка писем через Celery и RabbitMQ, чтобы не блокировать основное выполнение.

- Изображения для статей хранятся в S3.

---

## 📦 Зависимости

- FastAPI, SQLAlchemy, asyncpg, alembic

- Celery, Flower, amqp

- python-jose, bcrypt, email-validator

- pytest, pytest-asyncio

- pydantic, pydantic-settings, ruff

- aiohttp, aiobotocore и др.