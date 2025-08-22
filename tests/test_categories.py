import pytest
from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_list_categories(async_session):
    """
    Интеграционный тест эндпоинтов POST /categories и GET /categories.

    Шаги:
    1. Отправляет POST-запрос для создания категории (с name и slug).
    2. Проверяет, что возвращается статус 201 Created
    и объект с id, name, slug.
    3. Проверяет, что GET /categories возвращает
    список с добавленной категорией.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        new_category = {"name": "test_category", "slug": "test_category"}
        response = await ac.post("/categories", json=new_category)
        assert response.status_code == 201
        created = response.json()

        assert created["id"] == 1
        assert created["name"] == "test_category"
        assert created["slug"] == "test_category"

        response = await ac.get("/categories")
        assert response.status_code == 200
        categories = response.json()
        assert len(categories) == 1
        assert categories[0] == created
