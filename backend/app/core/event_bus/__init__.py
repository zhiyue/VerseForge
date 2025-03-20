"""
事件总线模块初始化文件
"""

from .event_bus import EventBus, Message, get_event_bus

__all__ = ["EventBus", "Message", "get_event_bus"]
