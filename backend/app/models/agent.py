from sqlalchemy import Column, String, Text, Integer, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base

class AgentType(enum.Enum):
    """
    Agent类型枚举
    """
    PLOT = "plot"              # 故事大纲规划
    CHARACTER = "character"    # 人物塑造
    SCENE = "scene"           # 剧情生成
    WRITING = "writing"       # 文字描写
    QA = "qa"                 # 质量审核
    COHERENCE = "coherence"   # 连贯性维护

class AgentStatus(enum.Enum):
    """
    Agent状态枚举
    """
    IDLE = "idle"           # 空闲
    WORKING = "working"     # 工作中
    PAUSED = "paused"      # 已暂停
    ERROR = "error"        # 错误状态

class Agent(Base):
    """
    Agent模型
    """
    # Agent类型
    agent_type = Column(Enum(AgentType), nullable=False)
    # 名称
    name = Column(String(100), nullable=False)
    # 描述
    description = Column(Text, nullable=True)
    # 状态
    status = Column(
        Enum(AgentStatus),
        nullable=False,
        default=AgentStatus.IDLE
    )
    # 配置参数
    parameters = Column(JSON, nullable=True)
    # 统计信息
    stats = Column(JSON, nullable=True)
    # 错误信息
    error_message = Column(Text, nullable=True)

    # 关联关系
    tasks = relationship("AgentTask", back_populates="agent", cascade="all, delete-orphan")

class AgentTask(Base):
    """
    Agent任务模型
    """
    # 任务类型
    task_type = Column(String(50), nullable=False)
    # 任务数据
    task_data = Column(JSON, nullable=False)
    # 优先级
    priority = Column(Integer, nullable=False, default=0)
    # 状态
    status = Column(String(20), nullable=False, default="pending")
    # 结果
    result = Column(JSON, nullable=True)
    # 错误信息
    error_message = Column(Text, nullable=True)
    # 重试次数
    retry_count = Column(Integer, nullable=False, default=0)
    # 所属AgentID
    agent_id = Column(Integer, ForeignKey("agent.id"), nullable=False)
    # 所属小说ID
    novel_id = Column(Integer, ForeignKey("novel.id"), nullable=False)

    # 关联关系
    agent = relationship("Agent", back_populates="tasks")
    novel = relationship("Novel")

class AgentInteraction(Base):
    """
    Agent交互记录模型
    """
    # 发送者Agent ID
    sender_id = Column(Integer, ForeignKey("agent.id"), nullable=False)
    # 接收者Agent ID
    receiver_id = Column(Integer, ForeignKey("agent.id"), nullable=False)
    # 交互类型
    interaction_type = Column(String(50), nullable=False)
    # 交互数据
    interaction_data = Column(JSON, nullable=False)
    # 状态
    status = Column(String(20), nullable=False, default="pending")
    # 结果
    result = Column(JSON, nullable=True)
    # 所属小说ID
    novel_id = Column(Integer, ForeignKey("novel.id"), nullable=False)

    # 关联关系
    sender = relationship("Agent", foreign_keys=[sender_id])
    receiver = relationship("Agent", foreign_keys=[receiver_id])
    novel = relationship("Novel")