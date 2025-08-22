from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from .blogs import Blog


class User(Base):
    """
    Модель пользователя.

    Атрибуты:
        id: Уникальный идентификатор пользователя.
        email: Электронная почта (уникальная).
        name: Имя пользователя.
        phone: Телефонный номер (уникальный).
        hashed_password: Захэшированный пароль.
        is_superuser: Флаг суперпользователя.
        blogs: Список блогов, созданных пользователем.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    phone: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    blogs: Mapped[list["Blog"]] = relationship(back_populates="author")
