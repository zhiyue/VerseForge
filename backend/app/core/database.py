from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from .config import settings

# 创建数据库引擎
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    echo=False,
)

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话的依赖函数
    用于FastAPI的Depends
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()