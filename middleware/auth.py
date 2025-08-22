from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from core.logger import logger
from core.security import decode_access_token


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware для проверки авторизации пользователя по JWT токену в cookie.

    Логика:
    1. Читает токен из cookie 'access_token'.
    2. Декодирует токен и получает user_id.
    3. Сохраняет user_id в request.state.user_id
    для использования в эндпоинтах.
    """
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("access_token")
        request.state.user_id = None

        if token:
            safe_token_preview = f"{token[:5]}...{token[-5:]}"
            logger.debug(f"Middleware token (preview): {safe_token_preview}")

            try:
                payload = decode_access_token(token)
                user_id = payload.get("sub")
                if user_id:
                    request.state.user_id = int(user_id)
                    logger.debug(f"Decoded user_id from token: {user_id}")
            except Exception as e:
                logger.warning(f"AuthMiddleware exception: {e}")

        response = await call_next(request)
        return response
