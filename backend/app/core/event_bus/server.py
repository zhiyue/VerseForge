"""
事件总线服务器
作为独立服务运行的事件总线
"""
import asyncio
import logging
import signal
import sys
import os
import json
from typing import Dict, List, Optional

from .event_bus import init_event_bus, get_event_bus, EventBus
from ..config import settings

logger = logging.getLogger(__name__)

class EventBusServer:
    """
    事件总线服务器
    
    作为一个独立的服务运行，不依赖于API服务
    """
    
    def __init__(
        self,
        implementation: str = None,
        config_kwargs: Dict = None,
        topics: List[str] = None
    ):
        """
        初始化事件总线服务器
        
        Args:
            implementation: 事件总线实现类型，默认从配置文件读取
            config_kwargs: 传递给事件总线实现的配置参数
            topics: 要创建的主题列表
        """
        self.implementation = implementation or settings.EVENT_BUS_IMPLEMENTATION
        self.config_kwargs = config_kwargs or {}
        self.topics = topics or [
            "plot_events",
            "character_events",
            "scene_events",
            "writing_events",
            "qa_events",
            "coherence_events",
        ]
        self.event_bus: Optional[EventBus] = None
        self.running = False
        
    async def start(self):
        """启动事件总线服务器"""
        logger.info(f"正在启动事件总线服务器 (实现: {self.implementation})")
        
        # 初始化事件总线
        if self.implementation == "kafka":
            self.event_bus = init_event_bus(
                implementation="kafka",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id='verseforge-server',
                group_id='verseforge-server-group',
                **self.config_kwargs
            )
        elif self.implementation == "redis":
            self.event_bus = init_event_bus(
                implementation="redis",
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                **self.config_kwargs
            )
        else:
            self.event_bus = init_event_bus(
                implementation="memory",
                **self.config_kwargs
            )
        
        # 启动事件总线
        await self.event_bus.start()
        
        # 创建主题
        await self.event_bus.create_topics(self.topics)
        
        self.running = True
        logger.info("事件总线服务器已启动")
        
        # 设置信号处理器以便优雅关闭
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop = asyncio.get_running_loop()
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
            except (NotImplementedError, RuntimeError):
                # Windows不支持add_signal_handler，使用signal.signal作为回退
                signal.signal(sig, lambda s, f: asyncio.create_task(self.stop()))
    
    async def stop(self):
        """停止事件总线服务器"""
        if not self.running:
            return
        
        logger.info("正在停止事件总线服务器...")
        self.running = False
        
        if self.event_bus:
            await self.event_bus.stop()
            self.event_bus = None
        
        logger.info("事件总线服务器已停止")
        
        # 停止事件循环
        loop = asyncio.get_running_loop()
        loop.stop()
    
    async def run_forever(self):
        """运行事件总线服务器，直到收到停止信号"""
        await self.start()
        
        # 保持服务器运行
        while self.running:
            await asyncio.sleep(1)
        
        await self.stop()


async def main():
    """事件总线服务器主入口点"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # 解析命令行参数
    implementation = os.environ.get("EVENT_BUS_IMPLEMENTATION", settings.EVENT_BUS_IMPLEMENTATION)
    
    # 启动服务器
    server = EventBusServer(implementation=implementation)
    await server.run_forever()


if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
