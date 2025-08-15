import pytest
from httpx import AsyncClient
from main import app

@pytest.fixture
async def async_client():
    """Фикстура асинхронного HTTP-клиента"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_successful_registration(async_client, mock_celery):
    """Тест успешной регистрации"""
    response = await async_client.post("/auth/register", json={
        "name": "Test User",
        "email": "newuser@example.com",
        "phone": "+79123456789",
        "password": "SecurePass123!"
    })
    
    assert response.status_code == 201
    assert "email" in response.json()
    mock_celery.delay.assert_called_once()