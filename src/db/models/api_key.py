import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class ApiKey(Base):
    """第三方 API 密钥表。"""

    __tablename__ = 'api_keys'
    __table_args__ = (
        Index('idx_api_key', 'api_key'),
        Index('idx_api_keys_is_deleted', 'is_deleted'),
        {'schema': 'auth'},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment='主键',
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment='备注名称（如"XXX平台"）',
    )
    api_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        comment='公开的 API Key',
    )
    secret: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment='API Secret（明文存储，仅创建时返回）',
    )
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment='是否启用',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.date_trunc('second', func.now()),
        nullable=False,
        comment='创建时间',
    )
    created_by: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment='创建人',
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment='是否删除',
    )
