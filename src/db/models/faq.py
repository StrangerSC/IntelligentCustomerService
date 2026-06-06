import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class KnowledgeType(str, Enum):
    """知识类型枚举。"""

    BC = '1'
    OC = '2'
    SC = '3'

    @property
    def knowledge_type_name(self) -> str:
        name_map = {
            '1': '业务类',
            '2': '操作类',
            '3': '技能类',
        }
        return name_map[self.value]


class EmbeddingStatus(str, Enum):
    """向量状态枚举。"""

    PENDING = 'pending'
    INDEXED = 'indexed'
    FAILED = 'failed'

    @property
    def embedding_status_name(self) -> str:
        name_map = {
            'pending': '待处理',
            'indexed': '已索引',
            'failed': '处理失败',
        }
        return name_map[self.value]


class FAQ(Base):
    """FAQ 知识问答表。

    存储结构化问答对，为 AI 客服提供知识库支撑。
    预留 vector_id 与 embedding_status 字段，供后续 RAG 向量检索接入。
    """

    __tablename__ = 'faq_records'
    __table_args__ = {"schema": "knowledge"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment='主键',
    )
    question: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        comment='问题文本',
    )
    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment='答案文本',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='创建时间',
    )
    created_by: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment='创建人',
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment='更新时间',
    )
    updated_by: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment='更新人',
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
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment='查看次数',
    )
    knowledge_type: Mapped[KnowledgeType] = mapped_column(
        SqlEnum(KnowledgeType, name='knowledge_type'),
        nullable=False,
        default=KnowledgeType.BC,
        comment='知识类型',
    )
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment='是否启用',
    )
    vector_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        unique=True,
        comment='向量库 Point ID',
    )
    embedding_status: Mapped[EmbeddingStatus] = mapped_column(
        SqlEnum(EmbeddingStatus, name='embedding_status'),
        nullable=False,
        default=EmbeddingStatus.PENDING,
        comment='向量状态: pending/indexed/failed',
    )
