"""
基于内存的事件总线实现
适用于开发和测试环境
"""
import asyncio
import logging
from typing import Any, Callable, Dict, List, Set

from .event_bus import EventBus, Message

logger = logging.getLogger(__name__)


class MemoryEventBus(EventBus):
    """
    基于内存的事件总线实现
    
    这是一个轻量级的事件总线实现，完全在内存中工作，不需要外部依赖。
    主要用于开发和测试环境。
    """
    
    def __init__(self, **kwargs):
        """初始化内存事件总线"""
        # 存储主题和回调的映射
        self.callbacks: Dict[str, Set[Callable[[Message], None]]] = {}
        
        # 存储已创建的主题
        self.topics: Set[str] = set()
        
        # 运行状态
        self.running = False
        
        # 用于异步处理的事件循环
        self._loop = None
    
    async def start(self) -> None:
        """启动内存事件总线"""
        if self.running:
            return
        
        # 获取当前事件循环
        self._loop = asyncio.get_event_loop()
        self.running = True
        logger.info("内存事件总线已启动")
    
    async def stop(self) -> None:
        """停止内存事件总线"""
        if not self.running:
            return
        
        self.running = False
        self._loop = None
        logger.info("内存事件总线已停止")
    
    async def publish(self, message: Message) -> None:
        """
        发布消息到指定主题
        
        Args:
            message: 要发布的消息
        """
        if not self.running:
            raise RuntimeError("内存事件总线尚未启动")
        
        topic = message.topic
        
        # 检查主题是否存在
        if topic not in self.topics:
            logger.warning(f"发布到未创建的主题 '{topic}'")
            return
        
        # 获取该主题的所有回调
        callbacks = self.callbacks.get(topic, set())
        
        # 没有订阅者，记录日志并返回
        if not callbacks:
            logger.debug(f"主题 '{topic}' 没有订阅者，消息将被丢弃")
            return
        
        # 异步调用所有回调
        for callback in callbacks:
            try:
                # 使用事件循环创建任务来执行回调
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(message))
                else:
                    self._loop.run_in_executor(None, callback, message)
                
            except Exception as e:
                logger.error(f"调用主题 '{topic}' 的回调时出错: {e}")
        
        logger.debug(f"消息已发布到主题 '{topic}' (ID: {message.message_id})")
    
    async def subscribe(self, topic: str, callback: Callable[[Message], None]) -> None:
        """
        订阅指定主题
        
        Args:
            topic: 主题名称
            callback: 收到消息时调用的回调函数
        """
        if not self.running:
            raise RuntimeError("内存事件总线尚未启动")
        
        # 如果主题不存在，自动创建
        if topic not in self.topics:
            await self.create_topics([topic])
        
        # 初始化主题的回调集合（如果不存在）
        if topic not in self.callbacks:
            self.callbacks[topic] = set()
        
        # 添加回调到集合
        self.callbacks[topic].add(callback)
        logger.info(f"已订阅主题 '{topic}'")
    
    async def unsubscribe(self, topic: str, callback: Callable[[Message], None]) -> None:
        """
        取消订阅指定主题
        
        Args:
            topic: 主题名称
            callback: 之前注册的回调函数
        """
        if topic in self.callbacks and callback in self.callbacks[topic]:
            # 从回调集合中移除
            self.callbacks[topic].remove(callback)
            logger.info(f"已取消订阅主题 '{topic}'")
            
            # 如果没有更多回调，清理回调字典
            if not self.callbacks[topic]:
                del self.callbacks[topic]
                logger.debug(f"主题 '{topic}' 已没有订阅者")
    
    async def create_topics(self, topics: List[str]) -> None:
        """
        创建主题
        
        Args:
            topics: 主题名称列表
        """
        if not self.running:
            raise RuntimeError("内存事件总线尚未启动")
        
        # 添加所有主题到集合
        for topic in topics:
            self.topics.add(topic)
        
        logger.info(f"已创建主题: {topics}")
