from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from models.category import Category
from models.user import User

if TYPE_CHECKING:
    from models.category import Category
    from models.user import User


class Blog(Base):
    """
    Модель блога.

    Атрибуты:
        id: Уникальный идентификатор блога.
        title: Заголовок блога.
        text: Содержимое блога.
        image: Ссылка на изображение (необязательно).
        slug: Уникальный URL-идентификатор.
        created_at: Дата и время создания.
        updated_at: Дата и время последнего обновления.
        is_deleted: Флаг мягкого удаления.
        author_id: ID автора (связь с User).
        author: Объект автора.
        category_id: ID категории (связь с Category).
        category: Объект категории.
    """
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True)
    author: Mapped["User"] = relationship("User", back_populates="blogs")
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False, index=True)
    category: Mapped["Category"] = relationship(back_populates="blogs")
