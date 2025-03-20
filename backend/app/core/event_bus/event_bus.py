"""
事件总线抽象接口和工厂实现
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import json
import uuid
import logging
import time

logger = logging.getLogger(__name__)

@dataclass
class Message:
    """事件消息数据类"""
    topic: str
    payload: Any
    message_id: str = None
    timestamp: float = None
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()
    
    def to_json(self) -> str:
        """将消息转换为JSON字符串"""
        return json.dumps({
            "message_id": self.message_id,
            "topic": self.topic,
            "payload": self.payload,
            "timestamp": self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """从JSON字符串创建消息对象"""
        data = json.loads(json_str)
        return cls(
            topic=data["topic"],
            payload=data["payload"],
            message_id=data["message_id"],
            timestamp=data["timestamp"]
        )


class EventBus(ABC):
    """
    事件总线抽象基类
    
    定义了事件总线的基本接口，包括发布和订阅事件的方法。
    具体实现类需要继承此类并实现所有抽象方法。
    """
    
    @abstractmethod
    async def publish(self, message: Message) -> None:
        """
        发布消息到指定主题
        
        Args:
            message: 要发布的消息对象
        """
        ...
    
    @abstractmethod
    async def subscribe(self, topic: str, callback: Callable[[Message], None]) -> None:
        """
        订阅指定主题的消息
        
        Args:
            topic: 主题名称
            callback: 当收到消息时要调用的回调函数
        """
        ...
    
    @abstractmethod
    async def unsubscribe(self, topic: str, callback: Callable[[Message], None]) -> None:
        """
        取消订阅指定主题
        
        Args:
            topic: 主题名称
            callback: 之前注册的回调函数
        """
        ...
    
    @abstractmethod
    async def create_topics(self, topics: List[str]) -> None:
        """
        创建主题（如果尚不存在）
        
        Args:
            topics: 主题名称列表
        """
        ...
    
    @abstractmethod
    async def start(self) -> None:
        """启动事件总线"""
        ...
    
    @abstractmethod
    async def stop(self) -> None:
        """停止事件总线"""
        ...


# 全局事件总线实例
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """
    获取全局事件总线实例
    
    Returns:
        EventBus: 当前配置的事件总线实例
    
    Raises:
        RuntimeError: 如果事件总线尚未初始化
    """
    if _event_bus is None:
        raise RuntimeError("事件总线尚未初始化，请先调用 init_event_bus")
    return _event_bus


def init_event_bus(implementation: str = "kafka", **kwargs) -> EventBus:
    """
    初始化事件总线
    
    Args:
        implementation: 事件总线实现，可选值: "kafka", "redis", "memory"
        **kwargs: 传递给具体实现的参数
    
    Returns:
        EventBus: 初始化后的事件总线实例
    
    Raises:
        ValueError: 如果指定的实现不存在
    """
    global _event_bus
    
    if implementation == "kafka":
        from .kafka_event_bus import KafkaEventBus
        _event_bus = KafkaEventBus(**kwargs)
    elif implementation == "redis":
        from .redis_event_bus import RedisEventBus
        _event_bus = RedisEventBus(**kwargs)
    elif implementation == "memory":
        from .memory_event_bus import MemoryEventBus
        _event_bus = MemoryEventBus(**kwargs)
    else:
        raise ValueError(f"不支持的事件总线实现: {implementation}")
    
    # 返回事件总线实例
    return _event_bus
