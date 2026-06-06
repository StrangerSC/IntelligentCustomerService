from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from sqlalchemy.engine import Connection

from alembic import context

# 导入项目配置和模型基类
from src.config.settings import settings
from src.db.base import Base


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 模型的 MetaData，用于 autogenerate
target_metadata = Base.metadata

# Alembic 运行迁移需要同步引擎，将 asyncpg 替换为同步驱动
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("+asyncpg", "")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=SYNC_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(SYNC_DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
