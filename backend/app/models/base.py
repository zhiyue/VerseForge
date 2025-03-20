from typing import Any
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    """
    SQLAlchemy 模型基类
    """
    id: Any
    created_at: datetime
    updated_at: datetime
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True)
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # 更新时间
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """
        生成表名
        将驼峰命名转换为下划线命名
        例如: UserModel -> user_model
        """
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    def dict(self) -> dict:
        """
        将模型转换为字典
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def update(self, **kwargs: Any) -> None:
        """
        更新模型属性
        """
        for key, value in kwargs.items():
            setattr(self, key, value)