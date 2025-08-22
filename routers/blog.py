from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.logger import logger
from db.session import get_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.blog import BlogCreate, BlogRead, BlogUpdate
from services.blog import create_blog, delete_blog, get_blogs, update_blog
from services.s3 import S3Client

router = APIRouter(prefix="/blogs", tags=["blogs"])
get_db_dep = Depends(get_db)
get_current_user_dep = Depends(get_current_user)
title_form = Form(...)
text_form = Form(...)
slug_form = Form(...)
category_id_form = Form(...)
image_file = File(...)


@router.get(
    "",
    summary="Получение всех постов",
    description="Получение всех постов блога с использованием пагинации",
    response_model=List[BlogRead],
    status_code=status.HTTP_200_OK
)
async def list_blogs(
    page: int = Query(1, gt=0, description="Номер страницы, начиная с 1"),
    size: int = Query(
        10,
        gt=0,
        le=100,
        description="Количество элементов на странице (макс. 100)"),
    category_id: Optional[int] = Query(
        None, description="Фильтр по категории"),
    search: Optional[str] = Query(None, description="Поисковый запрос"),
    session: AsyncSession = get_db_dep
):
    """
    Получение списка блогов с опциональной фильтрацией
    по категории и поисковым запросам.
    Поддерживается пагинация.
    """
    return await get_blogs(
        session,
        page_number=page,
        page_size=size,
        category_id=category_id,
        search=search
    )


@router.post(
    "",
    summary="Создание поста",
    description="Создание поста блога",
    response_model=BlogRead,
    status_code=status.HTTP_201_CREATED
)
async def create_blogs(
    title: str = title_form,
    text: str = text_form,
    slug: str = slug_form,
    category_id: int = category_id_form,
    image: UploadFile = image_file,
    session: AsyncSession = get_db_dep,
    current_user: User = get_current_user_dep
):
    """
    Создание нового блога:
        - Загрузка изображения в S3.
        - Создание записи в базе с указанием автора.
    """
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
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при создании блога: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error"
        ) from e


@router.delete(
    "/{blog_id}",
    summary="Удаление поста",
    description="Удаление поста определенного пользователя",
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_blog(
    blog_id: int,
    session: AsyncSession = get_db_dep,
    current_user: User = get_current_user_dep
):
    """
    Удаление блога по ID:
        - Проверка прав пользователя.
        - Удаление записи из базы.
    """
    try:
        logger.info(f"Удаление блога пользователем {current_user.id}")
        await delete_blog(session, blog_id, user_id=current_user.id)
        return JSONResponse(
            status_code=200,
            content={"message": f"Пост #{blog_id} удалён"}
        )
    except ValueError as v:
        logger.exception(f"Статья отсутствует в БД {v}")
        raise HTTPException(status_code=404, detail="Статья не найдена") from v
    except PermissionError as p:
        logger.exception(f"Недостаточно прав {p}")
        raise HTTPException(status_code=403, detail="Недостаточно прав") from p


@router.put(
    "/{blog_id}",
    summary="Изменение записи",
    description="Изменение определенной записи блога",
    status_code=status.HTTP_200_OK,
    response_model=BlogRead
)
async def update_blog_view(
    blog_id: int,
    title: str = title_form,
    text: str = text_form,
    slug: str = slug_form,
    category_id: int = category_id_form,
    image: UploadFile = image_file,
    session: AsyncSession = get_db_dep,
    current_user: User = get_current_user_dep
):
    """
    Обновление блога:
        - Загрузка нового изображения (если есть) в S3.
        - Обновление данных блога в базе.
        - Проверка прав пользователя.
    """
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
            session, blog_id, current_user.id, blog_data)
        return BlogRead.from_orm(updated_blog)
    except ValueError as v:
        logger.exception(f"Статья отсутствует в БД {v}")
        raise HTTPException(status_code=404, detail="Статья не найдена") from v
    except PermissionError as p:
        logger.exception(f"Недостаточно прав {p}")
        raise HTTPException(status_code=403, detail="Недостаточно прав") from p
