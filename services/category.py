from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import logger
from models.category import Category
from schemas.category import CategoryCreate


async def create_category(
        session: AsyncSession,
        category_data: CategoryCreate
) -> Category:
    """
    Создает новую категорию в базе данных.

    Проверяет уникальность slug категории, добавляет запись в БД,
    выполняет коммит и возвращает объект категории.

    Args:
        session: асинхронная сессия SQLAlchemy.
        category_data: данные для создания категории (name, slug).

    Raises:
        ValueError: если категория с таким slug уже существует.
        Exception: при ошибке коммита в БД.

    Returns:
        Category: объект созданной категории с заполненным ID.
    """
    stmt = select(Category).where(Category.slug == category_data.slug)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        logger.info(
            f"Попытка создать блог с "
            f"существующей категорией: {category_data.slug}")
        raise ValueError(f"Категория '{category_data.slug}' уже существует.")

    category = Category(
        name=category_data.name,
        slug=category_data.slug
    )
    session.add(category)

    try:
        await session.commit()
    except Exception as e:
        logger.exception(f"Ошибка при коммите категории в БД {e}")
        raise

    await session.refresh(category)
    return category


async def get_categories(session: AsyncSession) -> List[Category]:
    """
    Получает список всех категорий из базы данных.

    Args:
        session: асинхронная сессия SQLAlchemy.

    Returns:
        List[Category]: список объектов категорий.
    """
    stmt = select(Category)
    result = await session.execute(stmt)
    categories = result.scalars().all()
    return categories
