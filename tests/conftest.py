import uuid
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.base import Base
from db.session import get_db
from main import app


@pytest.fixture(scope="function", autouse=True)
def celery_mock():
    """
    Мок для Celery задач, чтобы при тестах не отправлялись реальные письма.

    Используется автоматически для всех тестов.
    """
    with patch("routers.auth.send_registration_email.delay") as mock_task:
        mock_task.return_value = None
        yield mock_task


@pytest.fixture(scope="function")
async def async_session():
    """
    Фикстура для асинхронной сессии SQLAlchemy на SQLite in-memory.

    Используется для тестирования работы с базой без влияния на реальную БД.
    Перекрывает зависимость get_db в FastAPI приложении.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def _get_db():
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db

    yield async_session_maker

    await engine.dispose()


@pytest.fixture(scope="function")
async def client(async_session):
    """
    Асинхронный HTTP клиент для тестирования FastAPI эндпоинтов.

    Использует AsyncClient из httpx с базовым URL http://test.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def test_user(client):
    """
    Создаёт тестового пользователя через эндпоинт регистрации.

    Возвращает словарь с данными пользователя.
    """
    unique_id = uuid.uuid4().int % 1000000
    user_data = {
        "name": "Test User",
        "email": f"user_{unique_id}@example.com",
        "phone": f"+7922{unique_id:07d}",
        "password": "StrongPass123!",
        "is_superuser": False,
    }
    resp = await client.post("/auth/register", json=user_data)
    assert resp.status_code == 201
    return user_data


@pytest.fixture(scope="function")
async def auth_client(client: AsyncClient, test_user: dict):
    """
    Возвращает авторизованный HTTP клиент с установленной cookie access_token.

    Используется для тестирования защищённых эндпоинтов.
    """
    await client.post(
        "/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )

    token_cookie = client.cookies.get("access_token")
    assert token_cookie, "Токен не установлен в cookie!"

    client.headers.update({"Authorization": f"Bearer {token_cookie}"})
    return client
