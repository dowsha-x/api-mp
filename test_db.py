import pytest
from sqlalchemy import text

@pytest.mark.asyncio
async def test_db_connection(db_session):
    """Тест подключения к БД"""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

@pytest.mark.asyncio
async def test_table_operations(db_session):
    """Тест операций с таблицами"""
    # Вставка тестовых данных
    await db_session.execute(
        text("INSERT INTO test_users (email) VALUES (:email)"),
        [{"email": "test1@example.com"}, {"email": "test2@example.com"}]
    )
    
    # Проверка количества записей
    result = await db_session.execute(
        text("SELECT COUNT(*) FROM test_users")
    )
    assert result.scalar() == 2