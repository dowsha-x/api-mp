import pytest

from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_list_blogs(async_session):
    """
    Тест эндпоинта GET /blogs.

    Проверяет:
    1. Возвращается статус код 200 OK.
    2. Возвращается пустой список, так как таблица blogs существует,
    но данных ещё нет.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/blogs")
        assert response.status_code == 200
        assert response.json() == []
