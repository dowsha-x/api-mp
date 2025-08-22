from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import logger
from db.session import get_db
from schemas.category import CategoryCreate, CategoryRead
from services.category import create_category, get_categories

router = APIRouter(prefix="/categories", tags=["categories"])
get_db_dep = Depends(get_db)


@router.get(
    "",
    summary="Получение всех категорий",
    description="Получение всех категорий блога",
    status_code=status.HTTP_200_OK,
    response_model=List[CategoryRead]
)
async def list_categories(session: AsyncSession = get_db_dep):
    """
    Получение списка всех категорий блога.
    Возвращает список объектов CategoryRead.
    """
    try:
        categories = await get_categories(session)
        logger.info(f"Получено {len(categories)} категорий")
        return categories
    except Exception as e:
        logger.exception(f"Ошибка при получении категорий: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить категории"
        ) from e


@router.post(
    "",
    summary="Создание категории",
    description="Создание категории блога",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryRead
)
async def create_categories(
    category_data: CategoryCreate,
    session: AsyncSession = get_db_dep
):
    """
    Создание новой категории блога.
    - category_data: данные категории для создания.
    Возвращает объект созданной категории.
    """
    try:
        category = await create_category(session, category_data)
        logger.info(f"Создана категория: {category.name} (id={category.id})")
        return category
    except ValueError as ve:
        logger.warning(f"Ошибка при создании категории: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve)
        ) from ve
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при создании категории: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать категорию"
        ) from e
