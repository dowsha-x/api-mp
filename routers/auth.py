from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.logger import logger
from core.security import create_access_token
from db.session import get_db
from schemas.user import UserCreate, UserLogin, UserRead
from services.user import (
    check_password,
    create_user,
    get_user_by_email,
    get_user_by_phone,
)
from tasks.email import send_registration_email

router = APIRouter(prefix="/auth", tags=["auth"])
get_db_dep = Depends(get_db)


@router.post(
    "/register",
    summary="Регистрация пользователей",
    description="Регистрация новых пользователей в системе.",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
async def register(user_in: UserCreate, db: AsyncSession = get_db_dep):
    """
    Регистрация пользователя:
        - Проверка существования пользователя по email и телефону.
        - Создание нового пользователя в базе.
        - Отправка email с подтверждением регистрации.
    """
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        logger.info(f"Пользователь уже существует: {user_in.email}")
        raise HTTPException(
            status_code=400, detail="Пользователь уже существует!"
        )
    existing_phone = await get_user_by_phone(db, user_in.phone)
    if existing_phone:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким телефоном уже существует!"
        )
    user = await create_user(db, user_in)
    send_registration_email.delay(user.email, user.name)
    return user


@router.post(
    "/login",
    summary="Логин пользователей",
    description="Логин пользователей в системе.",
    status_code=status.HTTP_200_OK
)
async def login(
    response: Response,
    user_in: UserLogin,
    db: AsyncSession = get_db_dep
):
    """
    Аутентификация пользователя:
        - Проверка существования пользователя и правильности пароля.
        - Создание JWT-токена и установка его в cookie.
    """
    user = await get_user_by_email(db, user_in.email)
    if not user or not check_password(
        user_in.password.get_secret_value(), user.hashed_password
    ):
        logger.info(f"Пользователь не найден: {user_in.email}")
        raise HTTPException(
            status_code=401, detail="Неверные email или пароль!"
        )
    token = create_access_token({"sub": str(user.id)})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False
    )
    return {"message": "Вы успешно вошли в систему!"}


@router.post(
    "/logout",
    summary="Логаут пользователей",
    description="Логаут пользователей из системы.",
    status_code=status.HTTP_200_OK
)
def logout(
    response: Response,
    access_token: Optional[str] = Cookie(default=None)
):
    """
    Разлогинивание пользователя:
        - Проверка наличия токена.
        - Удаление токена из cookie.
    """
    if not access_token:
        logger.info("Пользователь не авторизован")
        raise HTTPException(
            status_code=400,
            detail="Пользователь не авторизован"
        )
    response.delete_cookie("access_token")
    return {"message": "Вы вышли"}
