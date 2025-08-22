from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.logger import logger
from middleware.auth import AuthMiddleware
from routers import auth, blog, category

app = FastAPI()
app.add_middleware(AuthMiddleware)
app.include_router(auth.router)
app.include_router(blog.router)
app.include_router(category.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Глобальный обработчик всех необработанных исключений.

    Логирует ошибку с методом запроса и путём, после чего возвращает
    стандартный ответ с кодом 500 и сообщением "Internal Server Error".

    Args:
        request (Request): Объект запроса FastAPI.
        exc (Exception): Исключение, которое было поднято.

    Returns:
        JSONResponse: Ответ с кодом 500 и сообщением об ошибке.
    """
    logger.exception(
        f"Глобальная ошибка на {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
