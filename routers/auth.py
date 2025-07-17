from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from db.session import SessionLocal
from schemas.user import UserCreate, UserRead, UserLogin
from services.user import create_user, get_user_by_email, check_password
from core.security import create_access_token
from core.config import settings


async def get_db():
    """Зависимость для получения сессии."""
    async with SessionLocal() as session:
        yield session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Регистрация пользователя:
     - проверка пользователя на существование в БД (existing)
     - регистрация пользователя (user)
    """
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=400, detail="Пользователь уже существует!"
        )
    user = await create_user(db, user_in)
    return user


@router.post("/login")
async def login(
    response: Response,
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Логин пользователя:
     - проверка пользователя на существование в БД (user)
     - создание токена (token)
    """
    user = await get_user_by_email(db, user_in.email)
    if not user or not check_password(
        user_in.password.get_secret_value(), user.hashed_password
    ):
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


@router.post("/logout")
def logout(
    response: Response,
    access_token: Optional[str] = Cookie(default=None)
):
    """Разлогинивание пользователя."""
    if not access_token:
        raise HTTPException(
            status_code=400,
            detail="Пользователь не авторизован"
        )
    response.delete_cookie("access_token")
    return {"message": "Вы вышли"}
