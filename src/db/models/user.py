import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base

class User(Base):
    """用户表"""

    __tablename__ = "user"
    __table_args__ = (
        Index('idx_id', 'id'),
        Index('idx_is_deleted', 'is_deleted'),
        Index('idx_account', 'account'),
        Index('idx_phone_number', 'phone_number'),
        {"schema": "auth"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment='主键',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.date_trunc('second', func.now()),
        nullable=False,
        comment='创建时间',
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.date_trunc('second', func.now()),
        onupdate=func.date_trunc('second', func.now()),
        nullable=False,
        comment='更新时间',
    )
    ver: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment='版本号',
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment='是否删除',
    )
    account: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment='账号',
    )
    phone_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment='手机号',
        unique=True,
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment='密码',
    )
    is_frozen: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment='是否冻结',
    )
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment='是否启用',
    )
