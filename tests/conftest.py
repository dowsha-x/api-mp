import os
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Явно задаем URL для тестов, если .env не загрузился
TEST_DB_URL = os.getenv(
    'TEST_DATABASE_URL',
    'postgresql+asyncpg://test_user:test_api_mp_password@localhost:5432/test_api_mp_db'
)

@pytest.fixture(scope="session")
async def test_db_engine():
    """Фикстура асинхронного подключения к БД с проверкой URL"""
    assert TEST_DB_URL, "TEST_DATABASE_URL не задан"
    assert "asyncpg" in TEST_DB_URL, "Используйте asyncpg в TEST_DATABASE_URL"
    
    engine = create_async_engine(
        TEST_DB_URL,
        echo=True,
        pool_size=5,
        max_overflow=10
    )
    
    # Проверка подключения
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(test_db_engine):
    """Фикстура асинхронной сессии с автоматическим откатом"""
    async with test_db_engine.begin() as conn:
        Session = sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False
        )
        async with Session() as session:
            # Создаем тестовые таблицы
            await conn.run_sync(lambda sync_conn: sync_conn.execute(text(
                """CREATE TABLE IF NOT EXISTS test_users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL
                )"""
            )))
            
            yield session
            await session.rollback()