import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyCreateRequest(BaseModel):
    """创建 API Key 请求体。"""

    name: str = Field(..., min_length=1, max_length=100, description='备注名称')


class ApiKeyCreateResponse(BaseModel):
    """创建 API Key 响应体（Secret 仅此一次返回）。"""

    id: uuid.UUID
    name: str
    api_key: str
    secret: str  # ⚠️ 仅创建时返回，之后不可查询


class ApiKeyOut(BaseModel):
    """API Key 列表响应体（不含 Secret）。"""

    id: uuid.UUID
    name: str
    api_key: str
    is_enabled: bool
    created_at: datetime
    created_by: str

    class Config:
        from_attributes = True


class ApiKeyListResponse(BaseModel):
    """API Key 分页列表。"""

    items: list[ApiKeyOut]
    total: int
    page: int
    page_size: int
