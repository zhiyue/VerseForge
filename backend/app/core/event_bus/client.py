"""
事件总线客户端
用于连接到独立运行的事件总线服务
"""
import asyncio
import logging
from typing import Callable, Dict, List, Optional, Set
import json

from fastapi import FastAPI

from .event_bus import EventBus, Message, get_event_bus, init_event_bus
from ..config import settings

logger = logging.getLogger(__name__)


class EventBusClient:
    """
    事件总线客户端
    
    用于API服务和其他组件连接到事件总线服务
    """
    
    def __init__(self, app: FastAPI = None):
        """
        初始化事件总线客户端
        
        Args:
            app: FastAPI应用实例，用于注册启动和关闭事件
        """
        self.app = app
        self.event_bus = None
        self.callbacks: Dict[str, Set[Callable[[Message], None]]] = {}
        
        # 如果提供了FastAPI应用，注册事件处理
        if app:
            self.register_fastapi_events()
    
    def register_fastapi_events(self):
        """注册FastAPI应用的启动和关闭事件"""
        @self.app.on_event("startup")
        async def startup_event_bus_client():
            await self.connect()
        
        @self.app.on_event("shutdown")
        async def shutdown_event_bus_client():
            await self.disconnect()
    
    async def connect(self):
        """连接到事件总线服务"""
        # 使用与服务器相同的配置初始化事件总线
        implementation = settings.EVENT_BUS_IMPLEMENTATION
        
        try:
            if implementation == "kafka":
                self.event_bus = init_event_bus(
                    implementation="kafka",
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    client_id='verseforge-client',
                    group_id='verseforge-client-group'
                )
            elif implementation == "redis":
                self.event_bus = init_event_bus(
                    implementation="redis",
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB
                )
            else:
                self.event_bus = init_event_bus(
                    implementation="memory"
                )
            
            # 启动事件总线客户端
            await self.event_bus.start()
            
            # 重新订阅所有主题
            for topic, callbacks in self.callbacks.items():
                for callback in callbacks:
                    await self.event_bus.subscribe(topic, callback)
            
            logger.info(f"已连接到事件总线 (实现: {implementation})")
            
            # 如果是FastAPI应用，将事件总线保存到应用状态中
            if self.app:
                self.app.state.event_bus = self.event_bus
            
        except Exception as e:
            logger.error(f"连接到事件总线失败: {e}")
            raise
    
    async def disconnect(self):
        """断开与事件总线的连接"""
        if self.event_bus:
            # 取消所有订阅
            for topic, callbacks in self.callbacks.items():
                for callback in callbacks:
                    await self.event_bus.unsubscribe(topic, callback)
            
            # 停止事件总线
            await self.event_bus.stop()
            self.event_bus = None
            
            logger.info("已断开与事件总线的连接")
    
    async def publish(self, topic: str, payload: any, **kwargs):
        """
        发布消息到指定主题
        
        Args:
            topic: 主题名称
            payload: 消息内容
            **kwargs: 其他消息属性
        """
        if not self.event_bus:
            await self.connect()
        
        message = Message(topic=topic, payload=payload, **kwargs)
        await self.event_bus.publish(message)
    
    async def subscribe(self, topic: str, callback: Callable[[Message], None]):
        """
        订阅指定主题
        
        Args:
            topic: 主题名称
            callback: 当收到消息时调用的回调函数
        """
        if not self.event_bus:
            await self.connect()
        
        # 保存回调引用
        if topic not in self.callbacks:
            self.callbacks[topic] = set()
        self.callbacks[topic].add(callback)
        
        # 订阅主题
        await self.event_bus.subscribe(topic, callback)
    
    async def unsubscribe(self, topic: str, callback: Callable[[Message], None]):
        """
        取消订阅指定主题
        
        Args:
            topic: 主题名称
            callback: 要移除的回调函数
        """
        if self.event_bus and topic in self.callbacks and callback in self.callbacks[topic]:
            # 从集合中移除回调
            self.callbacks[topic].remove(callback)
            
            # 取消订阅
            await self.event_bus.unsubscribe(topic, callback)
            
            # 如果没有更多回调，清理字典
            if not self.callbacks[topic]:
                del self.callbacks[topic]
    

def setup_event_bus_client(app: FastAPI) -> EventBusClient:
    """
    为FastAPI应用设置事件总线客户端
    
    Args:
        app: FastAPI应用实例
        
    Returns:
        EventBusClient: 初始化的事件总线客户端
    """
    client = EventBusClient(app)
    
    # 通过依赖注入使事件总线可用
    @app.get("/api/v1/health/event-bus", tags=["health"])
    async def event_bus_health():
        """事件总线健康检查接口"""
        if not client.event_bus:
            return {"status": "disconnected"}
            
        try:
            # 简单的连接测试
            test_topic = "_health_check"
            await client.event_bus.create_topics([test_topic])
            return {"status": "connected", "implementation": settings.EVENT_BUS_IMPLEMENTATION}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    return client
