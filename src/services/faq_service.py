import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.faq import FAQ, EmbeddingStatus, KnowledgeType
from src.repositories.faq_repo import FAQRepository
from src.schemas.faq import FAQCreate, FAQUpdate


async def create_faq_service(db: AsyncSession, data: FAQCreate) -> FAQ:
    """新建 FAQ，默认 embedding_status 为 pending。"""
    repo = FAQRepository(db)
    faq = FAQ(
        question=data.question,
        answer=data.answer,
        knowledge_type=data.knowledge_type,
        is_enabled=data.is_enabled,
        embedding_status=EmbeddingStatus.PENDING,
    )
    return await repo.insert_repo(faq)


async def get_faq_service(db: AsyncSession, faq_id: uuid.UUID) -> Optional[FAQ]:
    """根据 ID 查询单条 FAQ。"""
    repo = FAQRepository(db)
    return await repo.find_by_id_repo(faq_id)


async def list_faqs_service(
    db: AsyncSession,
    *,
    knowledge_type: Optional[KnowledgeType] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[FAQ], int]:
    """分页查询 FAQ 列表，支持按知识类型过滤。

    Returns:
        (faq_list, total_count)
    """
    repo = FAQRepository(db)
    return await repo.find_all_repo(
        knowledge_type=knowledge_type,
        page=page,
        page_size=page_size,
    )


async def update_faq_service(
    db: AsyncSession, faq_id: uuid.UUID, data: FAQUpdate
) -> Optional[FAQ]:
    """更新 FAQ。内容变更后自动将 embedding_status 重置为 pending。"""
    repo = FAQRepository(db)
    faq = await repo.find_by_id_repo(faq_id)
    if not faq:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(faq, field, value)

    # 内容变更后需要重新向量化
    faq.embedding_status = EmbeddingStatus.PENDING

    return await repo.update_repo(faq)


async def delete_faq_service(db: AsyncSession, faq_id: uuid.UUID) -> bool:
    """删除 FAQ。"""
    repo = FAQRepository(db)
    return await repo.delete_by_id_repo(faq_id)
