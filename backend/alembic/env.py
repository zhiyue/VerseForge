import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from app.core.config import settings
from app.models import Base

# Alembic配置对象
config = context.config

# 如果存在alembic.ini中的logger配置则使用它
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 添加模型的元数据
target_metadata = Base.metadata

def get_url():
    """获取数据库URL"""
    return str(settings.SQLALCHEMY_DATABASE_URI)

def run_migrations_offline() -> None:
    """
    在"离线"模式下运行迁移
    不需要实际的数据库连接，只生成SQL语句
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    在"在线"模式下运行迁移
    需要实际的数据库连接
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # compare_type比较列类型
            compare_type=True,
            # compare_server_default比较默认值
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()