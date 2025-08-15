from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from schemas.category import CategoryRead, CategoryCreate
from services.category import get_categories, create_category


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[CategoryRead])
async def list_categories(session: AsyncSession = Depends(get_db)):
    return await get_categories(session)


@router.post("", response_model=CategoryRead)
async def create_categories(
    category_data: CategoryCreate,
    session: AsyncSession = Depends(get_db)
):
    category = await create_category(session, category_data)
    return category
