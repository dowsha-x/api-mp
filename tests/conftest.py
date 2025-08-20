import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.base import Base
from db.session import get_db


@pytest.fixture(scope="module")
async def async_session():
    """
    Фикстура для создания асинхронной сессии SQLAlchemy с in-memory SQLite.

    Особенности:
    - Используется SQLite в памяти (sqlite+aiosqlite:///:memory:),
    чтобы не трогать реальную базу.
    - Таблицы создаются автоматически перед тестами через
    Base.metadata.create_all.
    - Патчит зависимость FastAPI `get_db`,
    чтобы эндпоинты использовали тестовую сессию.
    - После завершения всех тестов соединение закрывается (engine.dispose).

    Возвращает:
        sessionmaker для создания AsyncSession внутри тестов.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def _get_session():
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = _get_session

    yield async_session_maker

    await engine.dispose()
