import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_blog(auth_client, test_user):
    """
    Тест: создание блога авторизованным пользователем.

    Шаги:
    1. Создать категорию.
    2. Создать блог, связанный с категорией.
    3. Проверить, что блог корректно возвращается через GET /blogs.
    """
    client: AsyncClient = auth_client

    category_data = {
        "name": f"Update Category {uuid.uuid4().hex[:6]}",
        "slug": f"update-category-{uuid.uuid4().hex[:6]}"
    }
    category_resp = await client.post("/categories", json=category_data)
    assert category_resp.status_code == 201
    category = category_resp.json()

    new_blog = {
        "title": "Test Blog",
        "text": "This is a test blog",
        "slug": "test-blog",
        "category_id": category["id"]
    }

    files = {
        "image": ("test_image.jpg", b"fake image content", "image/jpeg")
    }
    blog_resp = await client.post("/blogs", data=new_blog, files=files)
    assert blog_resp.status_code == 201
    created_blog = blog_resp.json()

    assert created_blog["title"] == new_blog["title"]
    assert created_blog["category"]["id"] == category["id"]
    assert created_blog["author"]["email"] == test_user["email"]

    get_resp = await client.get("/blogs")
    assert get_resp.status_code == 200
    blogs = get_resp.json()
    assert any(b["id"] == created_blog["id"] for b in blogs)


@pytest.mark.asyncio
async def test_create_blog_unauthorized(client):
    """
    Тест: попытка создать блог без авторизации.

    Ожидаемый результат:
    - Статус 401 Unauthorized
    """
    blog = {
        "title": "unauth_blog",
        "text": "some text",
        "slug": "unauth_slug",
        "category_id": 1,
        "image": "fake.png"
    }
    resp = await client.post("/blogs", json=blog)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_blog(auth_client):
    """
    Тест: обновление блога авторизованным пользователем.

    Шаги:
    1. Создать категорию и блог.
    2. Обновить данные блога через PUT /blogs/{id}.
    3. Проверить, что данные обновились.
    """
    client = auth_client

    category_resp = await client.post("/categories", json={
        "name": f"Cat {uuid.uuid4().hex[:4]}",
        "slug": f"cat-{uuid.uuid4().hex[:4]}"
    })
    assert category_resp.status_code == 201
    category = category_resp.json()

    new_blog = {
        "title": "Blog to update",
        "text": "original text",
        "slug": f"blog-{uuid.uuid4().hex[:4]}",
        "category_id": category["id"]
    }
    files = {"image": ("test_image.jpg", b"fake image content", "image/jpeg")}
    blog_resp = await client.post("/blogs", data=new_blog, files=files)
    assert blog_resp.status_code == 201
    blog = blog_resp.json()

    update_data = {
        "title": "Updated Title",
        "text": "updated text",
        "slug": f"new_slug_{uuid.uuid4().hex[:4]}",
        "category_id": category["id"]
    }
    update_files = {
        "image": ("test_image.jpg", b"fake image content", "image/jpeg")}
    resp = await client.put(
        f"/blogs/{blog['id']}", data=update_data, files=update_files)
    assert resp.status_code == 200
    updated_blog = resp.json()
    assert updated_blog["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_blog(auth_client, test_user):
    """
    Тест: удаление блога авторизованным пользователем.

    Шаги:
    1. Создать категорию и блог.
    2. Удалить блог через DELETE /blogs/{id}.
    3. Проверить, что блог больше не возвращается через GET /blogs.
    """
    client = auth_client

    category_resp = await client.post("/categories", json={
        "name": f"Cat {uuid.uuid4().hex[:4]}",
        "slug": f"cat-{uuid.uuid4().hex[:4]}"
    })
    assert category_resp.status_code == 201
    category = category_resp.json()

    new_blog = {
        "title": "Blog to delete",
        "text": "delete me",
        "slug": f"blog-{uuid.uuid4().hex[:4]}",
        "category_id": category["id"]
    }
    files = {"image": ("test_image.jpg", b"fake image content", "image/jpeg")}
    blog_resp = await client.post("/blogs", data=new_blog, files=files)
    assert blog_resp.status_code == 201
    blog = blog_resp.json()

    delete_resp = await client.delete(f"/blogs/{blog['id']}")
    assert delete_resp.status_code == 200

    get_resp = await client.get("/blogs")
    blogs = get_resp.json()
    assert all(b["id"] != blog["id"] for b in blogs)


@pytest.mark.asyncio
async def test_delete_blog_unauthorized(client):
    """
    Тест: неавторизованный пользователь не может удалить блог.

    Ожидаемый результат:
    - Статус 401 Unauthorized
    """
    resp = await client.delete("/blogs/1")
    assert resp.status_code == 401
