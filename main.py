from fastapi import FastAPI

from middleware.auth import AuthMiddleware
from routers import auth


app = FastAPI()
app.add_middleware(AuthMiddleware)
app.include_router(auth.router)
