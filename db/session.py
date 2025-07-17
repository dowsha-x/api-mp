from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from db.engine import engine


SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)
