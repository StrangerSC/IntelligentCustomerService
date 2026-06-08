import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User


class UserRepository:
    """用户数据访问层，只负责数据库 CRUD，不包含业务逻辑。"""

    def __init__(self, db: AsyncSession) -> None:
        """初始化 Repository。

        Args:
            db: 异步数据库会话。
        """
        self.db = db

    async def find_by_id(self, user_id: uuid.UUID) -> User | None:
        """根据 ID 查找用户。"""
        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.is_deleted == False,  # noqa: E712
                User.is_enabled == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def find_by_account(self, account: str) -> User | None:
        """根据账号查找用户。"""
        result = await self.db.execute(
            select(User).where(
                User.account == account,
                User.is_deleted == False,  # noqa: E712
                User.is_enabled == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def find_by_phone(self, phone_number: str) -> User | None:
        """根据手机号查找用户。"""
        result = await self.db.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

    async def insert(self, user: User) -> User:
        """插入一条用户记录。"""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
