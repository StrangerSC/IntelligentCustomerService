from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.db.base import engine


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db():
    """FastAPI 依赖注入用的异步数据库会话。"""

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
