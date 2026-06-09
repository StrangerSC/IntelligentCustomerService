import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_current_user
from src.db.models.faq import KnowledgeType
from src.db.models.user import User
from src.db.session import get_db
from src.schemas.faq import FAQCreate, FAQUpdate, FAQOut, FAQListResponse
from src.services import faq_service
from src.core.response import UnifiedResponse

router = APIRouter(prefix='/kb', tags=['knowledgebase'])


@router.get('/faqs', response_model=FAQListResponse)
async def list_faqs(
    knowledge_type: Optional[KnowledgeType] = Query(
        None, description='按知识类型过滤'
    ),
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(20, ge=1, le=100, description='每页条数'),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页查询 FAQ 列表。"""
    faqs, total = await faq_service.list_faqs_service(
        db, knowledge_type=knowledge_type, page=page, page_size=page_size
    )
    return FAQListResponse(
        items=faqs,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post('/faqs', response_model=FAQOut)
async def create_faq(
    data: FAQCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """新建 FAQ（需登录）。"""
    faq = await faq_service.create_faq_service(db, data)
    return faq


@router.get('/faqs/{faq_id}', response_model=FAQOut)
async def get_faq(
    faq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """根据 ID 查询单条 FAQ。"""
    faq = await faq_service.get_faq_service(db, faq_id)
    if not faq:
        return UnifiedResponse.error(
            message='FAQ 不存在', code=404, status_code=404
        )
    return faq


@router.put('/faqs/{faq_id}', response_model=FAQOut)
async def update_faq(
    faq_id: uuid.UUID,
    data: FAQUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新 FAQ（需登录）。"""
    faq = await faq_service.update_faq_service(db, faq_id, data)
    if not faq:
        return UnifiedResponse.error(
            message='FAQ 不存在', code=404, status_code=404
        )
    return faq


@router.delete('/faqs/{faq_id}')
async def delete_faq(
    faq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除 FAQ（需登录）。"""
    deleted = await faq_service.delete_faq_service(db, faq_id)
    if not deleted:
        return UnifiedResponse.error(
            message='FAQ 不存在', code=404, status_code=404
        )
    return UnifiedResponse.success(data={'deleted': True})
