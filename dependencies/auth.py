from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import logger
from db.session import get_db
from services.user import get_user_by_id

get_db_dep = Depends(get_db)


async def get_current_user(
    request: Request,
    db: AsyncSession = get_db_dep
):
    """
    Получает текущего авторизованного пользователя из запроса.

    Логика:
    1. Извлекает user_id из request.state, установленного AuthMiddleware.
    2. Если user_id отсутствует, выбрасывает HTTP 401.
    3. Получает пользователя из базы данных по user_id.
    4. Если пользователь не найден, выбрасывает HTTP 401.

    Args:
        request (Request): объект запроса FastAPI,
        содержащий состояние middleware.
        db (AsyncSession, optional): асинхронная сессия SQLAlchemy.
        Подставляется через Depends.

    Raises:
        HTTPException: 401 Unauthorized, если пользователь
        не авторизован или не найден в БД.

    Returns:
        User: объект пользователя из базы данных.
    """
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        logger.debug("No user_id in request.state")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован"
        )

    user = await get_user_by_id(db, user_id)
    if not user:
        logger.debug(f"User with id={user_id} not found in DB")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован"
        )

    logger.debug(f"Authenticated user: id={user.id}, email={user.email}")
    return user
