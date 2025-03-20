"""
基于Kafka的事件总线实现
"""
import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Set

from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic

from .event_bus import EventBus, Message

logger = logging.getLogger(__name__)


class KafkaEventBus(EventBus):
    """
    基于Kafka的事件总线实现
    """
    
    def __init__(
        self,
        bootstrap_servers: str = "kafka:29092",
        client_id: str = "verseforge-client",
        group_id: str = "verseforge-consumer-group",
        **kwargs
    ):
        """
        初始化Kafka事件总线
        
        Args:
            bootstrap_servers: Kafka服务器地址
            client_id: 客户端ID
            group_id: 消费者组ID
            **kwargs: 其他Kafka参数
        """
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self.group_id = group_id
        self.kafka_kwargs = kwargs
        
        # 生产者和管理客户端将在start方法中初始化
        self.producer = None
        self.admin_client = None
        
        # 存储主题和回调的映射
        self.callbacks: Dict[str, Set[Callable[[Message], None]]] = {}
        
        # 消费者线程和停止标志
        self.consumer_threads: Dict[str, threading.Thread] = {}
        self.running = False
    
    async def start(self) -> None:
        """启动Kafka事件总线"""
        if self.running:
            return
        
        try:
            # 初始化生产者
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                acks='all',
                retries=3,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                **self.kafka_kwargs
            )
            
            # 初始化管理客户端
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id=f"{self.client_id}-admin"
            )
            
            self.running = True
            logger.info("Kafka事件总线已启动")
            
        except Exception as e:
            logger.error(f"启动Kafka事件总线失败: {e}")
            raise
    
    async def stop(self) -> None:
        """停止Kafka事件总线"""
        if not self.running:
            return
        
        self.running = False
        
        # 停止所有消费者线程
        for topic, thread in self.consumer_threads.items():
            logger.info(f"正在停止主题 '{topic}' 的消费者线程")
            thread.join(timeout=5.0)
        
        # 关闭生产者
        if self.producer:
            self.producer.close()
            self.producer = None
        
        # 关闭管理客户端
        if self.admin_client:
            self.admin_client.close()
            self.admin_client = None
        
        logger.info("Kafka事件总线已停止")
    
    async def publish(self, message: Message) -> None:
        """
        发布消息到Kafka主题
        
        Args:
            message: 要发布的消息
        """
        if not self.running or not self.producer:
            raise RuntimeError("Kafka事件总线尚未启动")
        
        try:
            # 将消息转换为字典
            message_dict = {
                "message_id": message.message_id,
                "topic": message.topic,
                "payload": message.payload,
                "timestamp": message.timestamp
            }
            
            # 发送消息
            future = self.producer.send(
                topic=message.topic,
                value=message_dict
            )
            
            # 等待发送完成
            future.get(timeout=10)
            logger.debug(f"消息已发布到主题 '{message.topic}' (ID: {message.message_id})")
            
        except Exception as e:
            logger.error(f"发布消息到主题 '{message.topic}' 失败: {e}")
            raise
    
    async def subscribe(self, topic: str, callback: Callable[[Message], None]) -> None:
        """
        订阅Kafka主题
        
        Args:
            topic: 主题名称
            callback: 收到消息时调用的回调函数
        """
        if not self.running:
            raise RuntimeError("Kafka事件总线尚未启动")
        
        # 将回调添加到主题的回调集合中
        if topic not in self.callbacks:
            self.callbacks[topic] = set()
            
            # 为新主题创建消费者线程
            self._start_consumer_thread(topic)
        
        self.callbacks[topic].add(callback)
        logger.info(f"已订阅主题 '{topic}'")
    
    async def unsubscribe(self, topic: str, callback: Callable[[Message], None]) -> None:
        """
        取消订阅Kafka主题
        
        Args:
            topic: 主题名称
            callback: 要移除的回调函数
        """
        if topic in self.callbacks and callback in self.callbacks[topic]:
            self.callbacks[topic].remove(callback)
            logger.info(f"已取消订阅主题 '{topic}'")
            
            # 如果没有更多的回调，停止消费者线程
            if not self.callbacks[topic] and topic in self.consumer_threads:
                thread = self.consumer_threads.pop(topic)
                thread.join(timeout=5.0)
                logger.info(f"已停止主题 '{topic}' 的消费者线程")
    
    async def create_topics(self, topics: List[str]) -> None:
        """
        创建Kafka主题（如果尚不存在）
        
        Args:
            topics: 主题名称列表
        """
        if not self.running or not self.admin_client:
            raise RuntimeError("Kafka事件总线尚未启动")
        
        try:
            # 获取现有主题
            existing_topics = self.admin_client.list_topics()
            
            # 找出需要创建的主题
            new_topics = [
                NewTopic(name=topic, num_partitions=3, replication_factor=1)
                for topic in topics
                if topic not in existing_topics
            ]
            
            # 创建新主题
            if new_topics:
                self.admin_client.create_topics(new_topics)
                logger.info(f"已创建Kafka主题: {[t.name for t in new_topics]}")
            else:
                logger.info("所有请求的主题已存在")
                
        except Exception as e:
            logger.error(f"创建Kafka主题失败: {e}")
            raise
    
    def _start_consumer_thread(self, topic: str) -> None:
        """
        为指定主题启动消费者线程
        
        Args:
            topic: 主题名称
        """
        def consumer_worker(topic):
            try:
                # 创建消费者
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=self.group_id,
                    auto_offset_reset='latest',
                    enable_auto_commit=True,
                    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                )
                
                logger.info(f"已启动主题 '{topic}' 的消费者线程")
                
                # 持续消费消息，直到事件总线停止
                while self.running:
                    # 轮询消息，超时时间为1秒
                    records = consumer.poll(timeout_ms=1000)
                    
                    for partition_records in records.values():
                        for record in partition_records:
                            # 将消息转换为Message对象
                            message_dict = record.value
                            message = Message(
                                topic=message_dict["topic"],
                                payload=message_dict["payload"],
                                message_id=message_dict["message_id"],
                                timestamp=message_dict["timestamp"]
                            )
                            
                            # 调用所有注册的回调
                            if topic in self.callbacks:
                                for callback in self.callbacks[topic]:
                                    try:
                                        callback(message)
                                    except Exception as e:
                                        logger.error(f"处理主题 '{topic}' 的消息时回调出错: {e}")
                
                # 关闭消费者
                consumer.close()
                logger.info(f"已关闭主题 '{topic}' 的消费者")
                
            except Exception as e:
                logger.error(f"主题 '{topic}' 的消费者线程出错: {e}")
        
        # 创建并启动线程
        thread = threading.Thread(
            target=consumer_worker,
            args=(topic,),
            daemon=True,
            name=f"kafka-consumer-{topic}"
        )
        thread.start()
        
        # 保存线程引用
        self.consumer_threads[topic] = thread
