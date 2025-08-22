from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas.category import CategoryRead
from schemas.user import UserRead


class BlogCreate(BaseModel):
    """
    Схема для создания нового поста блога.
    Поля:
    - title: заголовок поста
    - text: содержание поста
    - slug: уникальный URL-идентификатор
    - category_id: ID категории
    - image: URL изображения (необязательно)
    """
    title: str
    text: str
    slug: str
    category_id: int
    image: Optional[str] = None

    class Config:
        from_attributes = True


class BlogRead(BaseModel):
    """
    Схема для чтения поста блога.
    Поля:
    - id: идентификатор поста
    - title: заголовок
    - text: содержание
    - image: URL изображения
    - slug: уникальный URL
    - created_at: дата создания
    - updated_at: дата обновления
    - author: данные автора (UserRead)
    - category: данные категории (CategoryRead)
    """
    id: int
    title: str
    text: str
    image: str
    slug: str
    created_at: datetime
    updated_at: datetime
    author: UserRead
    category: CategoryRead

    class Config:
        from_attributes = True


class BlogUpdate(BaseModel):
    """
    Схема для обновления поста блога.
    Поля:
    - title: заголовок
    - text: содержание
    - image: URL изображения (необязательно)
    - category_id: ID категории (необязательно)
    - slug: уникальный URL
    """
    title: str
    text: str
    image: Optional[str] = None
    category_id: Optional[int]
    slug: str

    class Config:
        from_attributes = True
