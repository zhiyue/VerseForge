from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class AgentBase(BaseModel):
    """
    Agent基础模型
    """
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class AgentCreate(AgentBase):
    """
    创建Agent请求模型
    """
    agent_type: str

class AgentUpdate(AgentBase):
    """
    更新Agent请求模型
    """
    status: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None

class Agent(AgentBase):
    """
    Agent响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    agent_type: str
    status: str
    stats: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    """
    任务基础模型
    """
    task_type: str
    task_data: Dict[str, Any]
    priority: int = Field(default=0, ge=0, le=100)

class TaskCreate(TaskBase):
    """
    创建任务请求模型
    """
    agent_id: int
    novel_id: int

class TaskUpdate(BaseModel):
    """
    更新任务请求模型
    """
    status: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class Task(TaskBase):
    """
    任务响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    agent_id: int
    novel_id: int
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class AgentInteractionBase(BaseModel):
    """
    Agent交互基础模型
    """
    interaction_type: str
    interaction_data: Dict[str, Any]

class AgentInteractionCreate(AgentInteractionBase):
    """
    创建Agent交互请求模型
    """
    sender_id: int
    receiver_id: int
    novel_id: int

class AgentInteractionUpdate(BaseModel):
    """
    更新Agent交互请求模型
    """
    status: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class AgentInteraction(AgentInteractionBase):
    """
    Agent交互响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    sender_id: int
    receiver_id: int
    novel_id: int
    status: str
    result: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class AgentMetrics(BaseModel):
    """
    Agent指标模型
    """
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_processing_time: float = 0.0
    success_rate: float = 0.0

class AgentStatus(BaseModel):
    """
    Agent状态详情模型
    """
    id: int
    name: str
    agent_type: str
    status: str
    current_task: Optional[Task] = None
    metrics: AgentMetrics
    stats: Dict[str, Any]
    last_error: Optional[str] = None
    uptime: float  # 运行时间（秒）
    memory_usage: float  # 内存使用（MB）

class AgentSystemStatus(BaseModel):
    """
    Agent系统状态模型
    """
    total_agents: int
    active_agents: int
    idle_agents: int
    error_agents: int
    total_tasks_pending: int
    total_tasks_processing: int
    system_metrics: Dict[str, Any]
    agents: List[AgentStatus]