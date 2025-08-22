from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Category(Base):
    """
    Модель категории блога.

    Атрибуты:
        id: Уникальный идентификатор категории.
        name: Название категории.
        slug: Уникальный URL-идентификатор категории.
        blogs: Список блогов, относящихся к категории.
    """
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    blogs = relationship("Blog", back_populates="category")
