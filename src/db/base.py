from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from src.config.settings import settings


class Base(AsyncAttrs, DeclarativeBase):
    """SQLAlchemy 2.0 声明式基类，支持异步操作。"""
    pass


# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)
