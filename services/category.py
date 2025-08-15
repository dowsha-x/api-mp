from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from models.category import Category
from schemas.category import CategoryCreate
from core.logger import logger


async def create_category(
        session: AsyncSession,
        category_data: CategoryCreate
) -> Category:
    """Создание категории."""
    stmt = select(Category).where(Category.slug == category_data.slug)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        logger.info(
            f"Попытка создать блог с существующей категорией: {category_data.slug}")
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
    """Получение всего списка категорий."""
    stmt = select(Category)
    result = await session.execute(stmt)
    categories = result.scalars().all()
    return categories
