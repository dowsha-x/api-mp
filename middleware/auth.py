from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.security import decode_access_token
from services.user import get_user_by_id
from db.session import SessionLocal


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("access_token")
        request.state.user = None
        if token:
            try:
                payload = decode_access_token(token)
                user_id = int(payload.get("sub"))
                async with SessionLocal() as session:
                    user = await get_user_by_id(session, user_id)
                    request.state.user = user
            except Exception:
                pass
        response = await call_next(request)
        return response
