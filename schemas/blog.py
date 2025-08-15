from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas.user import UserRead
from schemas.category import CategoryRead


class BlogCreate(BaseModel):
    title: str
    text: str
    slug: str
    category_id: int
    image: Optional[str] = None

    class Config:
        from_attributes = True


class BlogRead(BaseModel):
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
    title: str
    text: str
    image: Optional[str] = None
    category_id: Optional[int]
    slug: str

    class Config:
        from_attributes = True
