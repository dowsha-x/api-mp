from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from middleware.auth import AuthMiddleware
from routers import auth, blog, category
from core.logger import logger


app = FastAPI()
app.add_middleware(AuthMiddleware)
app.include_router(auth.router)
app.include_router(blog.router)
app.include_router(category.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        f"Глобальная ошибка на {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
