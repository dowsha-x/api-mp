from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from models.user import User
from schemas.user import UserCreate
from core.security import hash_password, verify_password


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """Получение пользователя по EMAIL."""
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
    """Создание нового пользователя."""
    hashed_pwd = hash_password(user_data.password.get_secret_value())
    user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hashed_pwd,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


def check_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля пользователя."""
    return verify_password(plain_password, hashed_password)


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
