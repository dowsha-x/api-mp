import os
import tempfile
from typing import List, Optional

from sqlalchemy import and_, false, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import text

from core.celery import celery_app
from core.config import settings
from core.logger import logger
from models.blogs import Blog
from schemas.blog import BlogCreate, BlogUpdate
from services.s3 import S3Client


async def create_blog(
        session: AsyncSession,
        blog_data: BlogCreate,
        author_id: int
) -> Blog:
    """
    Создает новый блог в базе данных.

    Проверяет уникальность слага, создает запись в БД,
    коммитит изменения и возвращает объект с загруженными связями
    (автор и категория).
    """
    stmt = select(Blog).where(Blog.slug == blog_data.slug)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        logger.info(
            f"Попытка создать блог с существующим слагом: {blog_data.slug}")
        raise ValueError(f"Слаг '{blog_data.slug}' уже существует.")

    blog = Blog(
        title=blog_data.title,
        text=blog_data.text,
        image=blog_data.image,
        slug=blog_data.slug,
        author_id=author_id,
        category_id=blog_data.category_id
    )
    session.add(blog)

    try:
        await session.commit()
    except Exception as e:
        logger.exception(f"Ошибка при коммите блога в БД {e}")
        raise

    await session.refresh(blog)

    stmt = select(Blog).options(
        selectinload(Blog.author),
        selectinload(Blog.category)
    ).where(Blog.id == blog.id)
    result = await session.execute(stmt)
    blog_with_relations = result.scalar_one()

    return blog_with_relations


async def get_blogs(
    session: AsyncSession,
    page_number: int = 1,
    page_size: int = 10,
    category_id: Optional[int] = None,
    search: Optional[str] = None
) -> List[Blog]:
    """
    Получение списка блогов с фильтрацией, поиском и пагинацией.

    Args:
        session: сессия SQLAlchemy.
        page_number: номер страницы.
        page_size: количество записей на странице.
        category_id: фильтр по категории.
        search: поисковая строка для заголовка и текста блога.

    Returns:
        Список объектов Blog с загруженными связями (автор и категория).
    """
    stmt = select(Blog).options(
        selectinload(Blog.category),
        selectinload(Blog.author)
    )

    filters = [Blog.is_deleted == false()]

    if category_id:
        filters.append(Blog.category_id == category_id)

    if search:
        filters.append(
            text(
                "to_tsvector('russian', blogs.title || ' ' || blogs.text) @@ plainto_tsquery('russian', :search)"
            ).bindparams(search=search)
        )

    if filters:
        stmt = stmt.where(and_(*filters))

    stmt = stmt.offset((page_number - 1) * page_size).limit(page_size)
    result = await session.execute(stmt)
    blogs = result.scalars().all()
    logger.info(f"Получено {len(blogs)} блогов)")
    return blogs


async def delete_blog(
        session: AsyncSession, blog_id: int, user_id: int) -> None:
    """
    Логическое удаление блога (is_deleted=True).

    Проверяет, существует ли блог и является текущий пользователь его автором.
    Если проверка не пройдена, вызывает ValueError или PermissionError.
    """
    stmt = select(Blog).where(Blog.id == blog_id)
    result = await session.execute(stmt)
    blog = result.scalar_one_or_none()

    if not blog:
        logger.info(
            f"Попытка удалить несуществующий блог: {blog_id}")
        raise ValueError("Пост не найден")

    if blog.author_id != user_id:
        logger.info(
            f"Попытка удалить чужой блог: {blog_id}")
        raise PermissionError("Вы не являетесь автором статьи")

    blog.is_deleted = True

    try:
        await session.commit()
    except Exception as e:
        logger.exception(f"Ошибка при коммите удаления из БД {e}")
        raise


async def update_blog(
    session: AsyncSession,
    blog_id: int,
    user_id: int,
    blog_data: BlogUpdate
) -> Blog:
    """
    Обновляет блог с проверкой прав пользователя.

    Проверяет существование записи, права автора, уникальность нового слага,
    обновляет поля и возвращает объект с подгруженными связями.
    """
    stmt = select(Blog).where(
        Blog.id == blog_id,
        Blog.is_deleted.is_(False)
    )
    result = await session.execute(stmt)
    blog = result.scalar_one_or_none()

    if not blog:
        logger.info(
            f"Попытка обновить несуществующий блог: {blog_id}")
        raise ValueError("Пост не найден")

    if blog.author_id != user_id:
        logger.info(
            f"Попытка обновить чужой блог: {blog.author_id}")
        raise PermissionError("Недостаточно прав")

    if blog.slug != blog_data.slug:
        existing_stmt = select(Blog).where(Blog.slug == blog_data.slug)
        existing_result = await session.execute(existing_stmt)
        existing_blog = existing_result.scalar_one_or_none()
        if existing_blog:
            logger.info(
                f"Попытка создать существующий слаг: {blog_data.slug}")
            raise ValueError("Слаг уже занят")

    blog.title = blog_data.title
    blog.text = blog_data.text
    blog.slug = blog_data.slug
    blog.category_id = blog_data.category_id

    if blog_data.image:
        blog.image = blog_data.image

    try:
        await session.commit()
    except Exception as e:
        logger.exception(f"Ошибка при коммите обновления в БД {e}")
        raise

    stmt = select(Blog).options(
        selectinload(Blog.author),
        selectinload(Blog.category)
    ).where(Blog.id == blog_id)
    result = await session.execute(stmt)
    blog_with_relations = result.scalar_one()

    return blog_with_relations


@celery_app.task
async def upload_to_s3_task(file_content: bytes, filename: str) -> str:
    """
    Фоновая загрузка файла в S3.

    Создает временный файл, загружает его в S3 и возвращает публичный URL.
    """
    try:
        s3 = S3Client(
            access_key=settings.ACCESS_KEY,
            secret_key=settings.SECRET_KEY_S,
            endpoint_url=settings.ENDPOINT_URL,
            bucket_name=settings.BUCKET_NAME,
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=filename
        ) as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name

        try:
            return await s3.upload_file(tmp_path, filename)
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        logger.error(f"S3 upload failed: {str(e)}")
        raise


@celery_app.task
async def create_blog_task(
    title: str,
    text: str,
    slug: str,
    category_id: int,
    image_url: str,
    author_id: int
) -> int:
    """
    Фоновая задача для создания блога.

    Создает блог в базе данных с переданными параметрами
    и возвращает ID нового блога.
    """
    from db.session import SessionLocal

    async with SessionLocal() as session:
        try:
            blog_data = BlogCreate(
                title=title,
                text=text,
                slug=slug,
                category_id=category_id,
                image=image_url
            )

            blog = await create_blog(session, blog_data, author_id=author_id)
            return blog.id

        except Exception as e:
            logger.error(f"Ошибка создания блога: {str(e)}")
            raise
