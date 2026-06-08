from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.api_key import ApiKey


class ApiKeyRepository:
    """API Key 数据访问层。"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def find_by_key(self, api_key: str) -> ApiKey | None:
        """根据 API Key 查找记录。"""
        result = await self.db.execute(
            select(ApiKey).where(
                ApiKey.api_key == api_key,
                ApiKey.is_deleted == False,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def find_all(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ApiKey], int]:
        """分页查询 API Key 列表。"""
        stmt = (
            select(ApiKey)
            .where(ApiKey.is_deleted == False)  # noqa: E712
            .offset((page - 1) * page_size)
            .limit(page_size)
            .order_by(ApiKey.created_at.desc())
        )
        count_stmt = select(func.count(ApiKey.id)).where(
            ApiKey.is_deleted == False  # noqa: E712
        )

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        return list(result.scalars().all()), count_result.scalar_one()

    async def insert(self, api_key: ApiKey) -> ApiKey:
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        return api_key

    async def soft_delete(self, ak_id: UUID) -> bool:
        result = await self.db.execute(
            select(ApiKey).where(
                ApiKey.id == ak_id,
                ApiKey.is_deleted == False,  # noqa: E712
            )
        )
        ak = result.scalar_one_or_none()
        if ak is None:
            return False
        ak.is_deleted = True
        await self.db.commit()
        return True
