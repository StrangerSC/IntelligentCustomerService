import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, computed_field, field_serializer

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
    is_enabled: bool
    view_count: int
    vector_id: Optional[str]
    embedding_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime, _info) -> str:
        """将时间格式化为 YYYY-MM-DD HH:MM:SS。"""
        return value.strftime("%Y-%m-%d %H:%M:%S")

    @computed_field
    @property
    def knowledge_type_name(self) -> str:
        """知识类型中文名，由 knowledge_type 自动派生。"""
        return self.knowledge_type.knowledge_type_name

class FAQListResponse(BaseModel):
    """FAQ 列表分页响应。"""

    items: List[FAQOut]
    total: int
    page: int
    page_size: int
