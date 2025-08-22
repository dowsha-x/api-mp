from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.engine import engine

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db() -> AsyncSession:
    """Асинхронный генератор сессий базы данных для Dependency Injection."""
    async with SessionLocal() as session:
        yield session
