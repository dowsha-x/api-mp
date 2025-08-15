from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from models.user import User
from models.category import Category

if TYPE_CHECKING:
    from models.user import User
    from models.category import Category


class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), index=True)
    text: Mapped[str] = mapped_column(Text)
    image: Mapped[Optional[str]] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True)
    author: Mapped["User"] = relationship(back_populates="blogs")
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False, index=True)
    category: Mapped["Category"] = relationship(back_populates="blogs")
