"""
基于Redis的事件总线实现
"""
import asyncio
import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Set

import redis
from redis import Redis

from .event_bus import EventBus, Message

logger = logging.getLogger(__name__)


class RedisEventBus(EventBus):
    """
    基于Redis的事件总线实现
    使用Redis的发布/订阅功能实现事件总线
    """
    
    def __init__(
        self,
        host: str = "redis",
        port: int = 6379,
        db: int = 0,
        password: str = None,
        **kwargs
    ):
        """
        初始化Redis事件总线
        
        Args:
            host: Redis服务器地址
            port: Redis服务器端口
            db: Redis数据库索引
            password: Redis密码
            **kwargs: 其他Redis参数
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.redis_kwargs = kwargs
        
        # Redis客户端将在start方法中初始化
        self.redis_client = None
        self.pubsub = None
        
        # 存储主题和回调的映射
        self.callbacks: Dict[str, Set[Callable[[Message], None]]] = {}
        
        # 存储主题和订阅线程的映射
        self.subscription_threads: Dict[str, threading.Thread] = {}
        self.running = False
        
        # 用于存储主题列表的Redis键
        self.topics_key = "verseforge:event_bus:topics"
    
    async def start(self) -> None:
        """启动Redis事件总线"""
        if self.running:
            return
        
        try:
            # 初始化Redis客户端
            self.redis_client = Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
                **self.redis_kwargs
            )
            
            # 检查Redis连接
            self.redis_client.ping()
            
            # 初始化PubSub对象
            self.pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)
            
            self.running = True
            logger.info("Redis事件总线已启动")
            
        except Exception as e:
            logger.error(f"启动Redis事件总线失败: {e}")
            raise
    
    async def stop(self) -> None:
        """停止Redis事件总线"""
        if not self.running:
            return
        
        self.running = False
        
        # 停止所有订阅线程
        for topic, thread in self.subscription_threads.items():
            logger.info(f"正在停止主题 '{topic}' 的订阅线程")
            thread.join(timeout=5.0)
        
        # 关闭PubSub连接
        if self.pubsub:
            self.pubsub.close()
            self.pubsub = None
        
        # 关闭Redis客户端
        if self.redis_client:
            self.redis_client.close()
            self.redis_client = None
        
        logger.info("Redis事件总线已停止")
    
    async def publish(self, message: Message) -> None:
        """
        发布消息到Redis主题
        
        Args:
            message: 要发布的消息
        """
        if not self.running or not self.redis_client:
            raise RuntimeError("Redis事件总线尚未启动")
        
        try:
            # 将消息转换为JSON字符串
            message_json = message.to_json()
            
            # 发布消息
            self.redis_client.publish(message.topic, message_json)
            logger.debug(f"消息已发布到主题 '{message.topic}' (ID: {message.message_id})")
            
        except Exception as e:
            logger.error(f"发布消息到主题 '{message.topic}' 失败: {e}")
            raise
    
    async def subscribe(self, topic: str, callback: Callable[[Message], None]) -> None:
        """
        订阅Redis主题
        
        Args:
            topic: 主题名称
            callback: 收到消息时调用的回调函数
        """
        if not self.running or not self.redis_client:
            raise RuntimeError("Redis事件总线尚未启动")
        
        # 将回调添加到主题的回调集合中
        if topic not in self.callbacks:
            self.callbacks[topic] = set()
            
            # 为新主题创建订阅线程
            self._start_subscription_thread(topic)
        
        self.callbacks[topic].add(callback)
        logger.info(f"已订阅主题 '{topic}'")
    
    async def unsubscribe(self, topic: str, callback: Callable[[Message], None]) -> None:
        """
        取消订阅Redis主题
        
        Args:
            topic: 主题名称
            callback: 要移除的回调函数
        """
        if topic in self.callbacks and callback in self.callbacks[topic]:
            self.callbacks[topic].remove(callback)
            logger.info(f"已取消订阅主题 '{topic}'")
            
            # 如果没有更多的回调，停止订阅线程
            if not self.callbacks[topic] and topic in self.subscription_threads:
                # 取消订阅
                self.pubsub.unsubscribe(topic)
                
                # 停止线程
                thread = self.subscription_threads.pop(topic)
                thread.join(timeout=5.0)
                logger.info(f"已停止主题 '{topic}' 的订阅线程")
    
    async def create_topics(self, topics: List[str]) -> None:
        """
        创建Redis主题（在Redis中，不需要预先创建主题，但我们会记录主题列表）
        
        Args:
            topics: 主题名称列表
        """
        if not self.running or not self.redis_client:
            raise RuntimeError("Redis事件总线尚未启动")
        
        try:
            # 添加主题到集合中
            for topic in topics:
                self.redis_client.sadd(self.topics_key, topic)
            
            logger.info(f"已记录主题列表: {topics}")
                
        except Exception as e:
            logger.error(f"记录Redis主题列表失败: {e}")
            raise
    
    def _start_subscription_thread(self, topic: str) -> None:
        """
        为指定主题启动订阅线程
        
        Args:
            topic: 主题名称
        """
        def subscription_worker(topic):
            try:
                # 创建新的PubSub对象，因为PubSub对象不是线程安全的
                local_pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)
                local_pubsub.subscribe(topic)
                
                logger.info(f"已启动主题 '{topic}' 的订阅线程")
                
                # 持续监听消息，直到事件总线停止
                while self.running:
                    # 获取消息，超时时间为1秒
                    message = local_pubsub.get_message(timeout=1.0)
                    
                    if message and message["type"] == "message":
                        try:
                            # 将JSON解析为Message对象
                            message_obj = Message.from_json(message["data"])
                            
                            # 调用所有注册的回调
                            if topic in self.callbacks:
                                for callback in self.callbacks[topic]:
                                    try:
                                        callback(message_obj)
                                    except Exception as e:
                                        logger.error(f"处理主题 '{topic}' 的消息时回调出错: {e}")
                        except Exception as e:
                            logger.error(f"解析主题 '{topic}' 的消息失败: {e}")
                
                # 取消订阅并关闭连接
                local_pubsub.unsubscribe(topic)
                local_pubsub.close()
                logger.info(f"已关闭主题 '{topic}' 的订阅")
                
            except Exception as e:
                logger.error(f"主题 '{topic}' 的订阅线程出错: {e}")
        
        # 创建并启动线程
        thread = threading.Thread(
            target=subscription_worker,
            args=(topic,),
            daemon=True,
            name=f"redis-subscriber-{topic}"
        )
        thread.start()
        
        # 保存线程引用
        self.subscription_threads[topic] = thread
