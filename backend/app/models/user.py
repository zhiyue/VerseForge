from sqlalchemy import Boolean, Column, String, Integer
from sqlalchemy.orm import relationship

from .base import Base

class User(Base):
    """
    用户模型
    """
    # 用户名
    username = Column(String(32), unique=True, nullable=False, index=True)
    # 电子邮件
    email = Column(String(255), unique=True, nullable=False, index=True)
    # 密码哈希
    hashed_password = Column(String(255), nullable=False)
    # 是否激活
    is_active = Column(Boolean(), default=True)
    # 是否是超级用户
    is_superuser = Column(Boolean(), default=False)
    # 是否是工作人员
    is_staff = Column(Boolean(), default=False)
    # 姓名
    full_name = Column(String(100), nullable=True)
    # 角色
    role = Column(String(20), nullable=False, default="user")
    
    # 关联关系
    novels = relationship("Novel", backref="creator")

    def __repr__(self):
        return f"<User {self.username}>"

class UserPreference(Base):
    """
    用户偏好设置模型
    """
    # 用户ID
    user_id = Column(Integer, nullable=False, unique=True)
    # 界面主题
    theme = Column(String(20), nullable=False, default="light")
    # 语言设置
    language = Column(String(10), nullable=False, default="zh-CN")
    # 每页显示数量
    items_per_page = Column(Integer, nullable=False, default=20)
    # 提醒设置
    notification_settings = Column(String(255), nullable=False, default="all")
    
    def __repr__(self):
        return f"<UserPreference {self.user_id}>"

class UserActivity(Base):
    """
    用户活动记录模型
    """
    # 用户ID
    user_id = Column(Integer, nullable=False)
    # 活动类型
    activity_type = Column(String(50), nullable=False)
    # 活动描述
    description = Column(String(255), nullable=False)
    # IP地址
    ip_address = Column(String(50), nullable=True)
    # 用户代理
    user_agent = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<UserActivity {self.user_id} - {self.activity_type}>"