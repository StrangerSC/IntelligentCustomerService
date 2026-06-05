import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer

from src.db.models.faq import KnowledgeType


class FAQBase(BaseModel):
    """FAQ 基础字段。"""

    question: str = Field(..., max_length=1024, description="问题文本")
    answer: str = Field(..., description="答案文本")
    knowledge_type: KnowledgeType = Field(..., description="知识类型：1业务类 2操作类 3技能类")
    is_enabled: bool = Field(..., description="是否启用")


class FAQCreate(FAQBase):
    """创建 FAQ 请求体。"""

    pass


class FAQUpdate(BaseModel):
    """更新 FAQ 请求体（全部可选）。"""

    question: Optional[str] = Field(None, max_length=1024)
    answer: Optional[str] = Field(None)
    knowledge_type: Optional[KnowledgeType] = Field(None)
    is_enabled: Optional[bool] = Field(None)


class FAQOut(BaseModel):
    """FAQ 响应模型。"""

    id: uuid.UUID
    question: str
    answer: str
    knowledge_type: KnowledgeType
    knowledge_type_name: Optional[str] = None  # 自动中文
    is_enabled: bool
    view_count: int
    vector_id: Optional[str]
    embedding_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    # 自动返回中文类型
    @field_serializer("knowledge_type_name")
    def get_kt_name(self, *_):
        return self.knowledge_type.knowledge_type_name

class FAQListResponse(BaseModel):
    """FAQ 列表分页响应。"""

    items: List[FAQOut]
    total: int
    page: int
    page_size: int
