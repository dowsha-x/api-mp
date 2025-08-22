from pydantic import BaseModel


class CategoryCreate(BaseModel):
    """
    Схема для создания новой категории блога.
    Поля:
    - name: название категории
    - slug: уникальный идентификатор категории
    """
    name: str
    slug: str


class CategoryRead(BaseModel):
    """
    Схема для чтения категории блога.
    Поля:
    - id: идентификатор категории
    - name: название категории
    - slug: уникальный идентификатор категории
    """
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True
