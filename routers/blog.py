from typing import List, Optional

from fastapi import (
    APIRouter, Depends, Query, HTTPException, UploadFile, Form, File
)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from schemas.blog import BlogRead, BlogCreate, BlogUpdate
from services.blog import get_blogs, create_blog, delete_blog, update_blog
from dependencies.auth import get_current_user
from models.user import User
from services.s3 import S3Client
from core.config import settings
from core.logger import logger

router = APIRouter(prefix="/blogs", tags=["blogs"])


@router.get("", response_model=List[BlogRead])
async def list_blogs(
    page: int = Query(
        1, gt=0, description="Номер страницы, начиная с 1"
    ),
    size: int = Query(
        10, gt=0,
        le=100,
        description="Количество элементов на странице (макс. 100)"
    ),
    category_id: Optional[int] = Query(
        None,
        description="Фильтр по категории"
    ),
    search: Optional[str] = Query(None, description="Поисковый запрос"),
    session: AsyncSession = Depends(get_db)
):
    return await get_blogs(
        session,
        page_number=page,
        page_size=size,
        category_id=category_id,
        search=search
    )


@router.post("", response_model=BlogRead)
async def create_blogs(
    title: str = Form(...),
    text: str = Form(...),
    slug: str = Form(...),
    category_id: int = Form(...),
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Создание блога пользователем {current_user.id}")
        s3 = S3Client(
            access_key=settings.ACCESS_KEY,
            secret_key=settings.SECRET_KEY_S,
            endpoint_url=settings.ENDPOINT_URL,
            bucket_name=settings.BUCKET_NAME,
        )
        image_url = await s3.upload_file(image)

        blog_data = BlogCreate(
            title=title,
            text=text,
            slug=slug,
            category_id=category_id,
        )
        blog_data.image = image_url

        blog = await create_blog(session, blog_data, author_id=current_user.id)
        return blog

    except ValueError as ve:
        logger.warning(f"Ошибка при создании блога: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при создании блога: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{blog_id}", status_code=204)
async def remove_blog(
    blog_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Удаление блога пользователем {current_user.id}")
        await delete_blog(session, blog_id, user_id=current_user.id)
        return JSONResponse(
            status_code=200,
            content={"message": f"Пост #{blog_id} удалён"}
        )
    except ValueError as v:
        logger.exception(f"Статья отсутствует в БД {v}")
        raise HTTPException(status_code=404, detail="Статья не найдена")
    except PermissionError as p:
        logger.exception(f"Недостаточно прав {p}")
        raise HTTPException(status_code=403, detail="Недостаточно прав")


@router.put("/{blog_id}", response_model=BlogRead)
async def update_blog_view(
    blog_id: int,
    title: str = Form(...),
    text: str = Form(...),
    slug: str = Form(...),
    category_id: int = Form(...),
    image: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    image_url = None

    if image:
        s3 = S3Client(
            access_key=settings.ACCESS_KEY,
            secret_key=settings.SECRET_KEY_S,
            endpoint_url=settings.ENDPOINT_URL,
            bucket_name=settings.BUCKET_NAME,
        )
        image_url = await s3.upload_file(image)

    blog_data = BlogUpdate(
        title=title,
        text=text,
        slug=slug,
        category_id=category_id,
        image=image_url,
    )

    try:
        logger.info(f"Обновление блога пользователем {current_user.id}")
        updated_blog = await update_blog(
            session, blog_id, current_user.id, blog_data
        )
        return BlogRead.from_orm(updated_blog)
    except ValueError as v:
        logger.exception(f"Статья отсутствует в БД {v}")
        raise HTTPException(status_code=404, detail="Статья не найдена")
    except PermissionError as p:
        logger.exception(f"Недостаточно прав {p}")
        raise HTTPException(status_code=403, detail="Недостаточно прав")
