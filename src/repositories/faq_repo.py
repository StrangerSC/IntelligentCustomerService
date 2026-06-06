import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.faq import FAQ, KnowledgeType


class FAQRepository:
    """FAQ 数据访问层，只负责数据库 CRUD，不包含业务逻辑。"""

    def __init__(self, db: AsyncSession) -> None:
        """初始化 Repository。

        Args:
            db: 异步数据库会话。
        """
        self.db = db

    async def find_by_id_repo(self, faq_id: uuid.UUID) -> FAQ | None:
        """根据 ID 查询单条 FAQ。"""
        result = await self.db.execute(
            select(FAQ).where(FAQ.id == faq_id, FAQ.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def find_all_repo(
        self,
        *,
        knowledge_type: KnowledgeType | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[FAQ], int]:
        """分页查询 FAQ 列表，支持按知识类型过滤。

        Args:
            knowledge_type: 知识类型过滤条件，None 表示不限。
            page: 页码，从 1 开始。
            page_size: 每页条数。

        Returns:
            (faq_list, total_count)
        """
        stmt = select(FAQ)
        count_stmt = select(func.count(FAQ.id))

        if knowledge_type is not None:
            stmt = stmt.where(FAQ.knowledge_type == knowledge_type)
            count_stmt = count_stmt.where(
                FAQ.knowledge_type == knowledge_type
            )

        offset = (page - 1) * page_size
        stmt = (
            stmt.offset(offset)
            .limit(page_size)
            .order_by(FAQ.updated_at.desc())
        )

        result = await self.db.execute(stmt.where(FAQ.is_deleted == False))
        count_result = await self.db.execute(count_stmt.where(FAQ.is_deleted == False))

        faqs = result.scalars().all()
        total = count_result.scalar_one()
        return list(faqs), total

    async def insert_repo(self, faq: FAQ) -> FAQ:
        """插入一条 FAQ 记录。

        Args:
            faq: 已构建好字段的 FAQ 实例。

        Returns:
            刷新后的 FAQ 实例（含数据库生成的字段）。
        """
        self.db.add(faq)
        await self.db.commit()
        await self.db.refresh(faq)
        return faq

    async def update_repo(self, faq: FAQ) -> FAQ:
        """更新一条 FAQ 记录。

        Args:
            faq: 已修改属性的 FAQ 实例。

        Returns:
            刷新后的 FAQ 实例。
        """
        await self.db.commit()
        await self.db.refresh(faq)
        return faq

    async def delete_by_id_repo(self, faq_id: uuid.UUID) -> bool:
        """根据 ID 删除一条 FAQ。

        Args:
            faq_id: FAQ 的唯一标识符。

        Returns:
            True 表示删除成功，False 表示记录不存在。
        """
        result = await self.db.execute(
            update(FAQ).where(FAQ.id == faq_id).values(is_deleted=True)
        )
        await self.db.commit()
        return result.rowcount > 0
