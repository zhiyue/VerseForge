from .base import CRUDBase
from .user import user, user_preference
from .novel import novel, chapter, character, event
from .agent import agent, task, interaction

# 导出所有CRUD操作实例
__all__ = [
    # 基类
    "CRUDBase",
    
    # 用户相关
    "user",
    "user_preference",
    
    # 小说相关
    "novel",
    "chapter",
    "character",
    "event",
    
    # Agent相关
    "agent",
    "task",
    "interaction",
]