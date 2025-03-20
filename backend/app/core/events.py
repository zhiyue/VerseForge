from typing import Callable
from fastapi import FastAPI
from redis import Redis
from pymilvus import connections, utility
import logging

from .config import settings
from .event_bus import init_event_bus, get_event_bus

logger = logging.getLogger(__name__)

def create_milvus_collections() -> None:
    """
    创建Milvus集合
    """
    try:
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT
        )
        
        collections = {
            "plot_vectors": 768,  # BERT embedding 维度
            "character_vectors": 768,
            "scene_vectors": 768,
        }
        
        for name, dim in collections.items():
            if not utility.exists_collection(name):
                from pymilvus import Collection, FieldSchema, CollectionSchema, DataType
                
                fields = [
                    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
                    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim)
                ]
                schema = CollectionSchema(fields=fields, description=f"Collection for {name}")
                Collection(name=name, schema=schema)
                logger.info(f"Created Milvus collection: {name}")
                
    except Exception as e:
        logger.error(f"Error creating Milvus collections: {e}")
    finally:
        connections.disconnect("default")

def create_start_app_handler(app: FastAPI) -> Callable:
    """
    应用启动时的处理函数
    """
    async def start_app() -> None:
        # 初始化Redis连接
        app.state.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        
        # 初始化事件总线
        event_bus_implementation = settings.EVENT_BUS_IMPLEMENTATION
        if event_bus_implementation == "kafka":
            init_event_bus(
                app,
                implementation="kafka",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id='verseforge-client',
                group_id='verseforge-consumer-group'
            )
        elif event_bus_implementation == "redis":
            init_event_bus(
                app,
                implementation="redis",
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB
            )
        else:  # 默认使用内存实现
            init_event_bus(app, implementation="memory")
        
        # 创建事件主题
        topics = [
            "plot_events",
            "character_events",
            "scene_events",
            "writing_events",
            "qa_events",
            "coherence_events",
        ]
        await get_event_bus().create_topics(topics)
        
        # 创建Milvus集合
        create_milvus_collections()
        
        logger.info("Application startup complete")

    return start_app

def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    应用关闭时的处理函数
    """
    async def stop_app() -> None:
        # 关闭Redis连接
        await app.state.redis.close()
        
        # 事件总线会在FastAPI的shutdown事件中自动关闭
        
        logger.info("Application shutdown complete")

    return stop_app