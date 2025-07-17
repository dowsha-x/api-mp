from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from core.config import settings


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
ALGORITHM = 'HS256'


def hash_password(password: str) -> str:
    """Шифрование пароля пользователя."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Сравнение пароля для верификации."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    """Создание JWT-токена."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Декодирует JWT-токен и возвращает полезные данные."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None
