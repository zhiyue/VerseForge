from .base import BaseAgent
from .plot_agent import PlotAgent
from .character_agent import CharacterAgent
from .scene_agent import SceneAgent
from .writing_agent import WritingAgent
from .qa_agent import QAAgent
from .coherence_agent import CoherenceAgent
from .manager import AgentManager
from .exceptions import (
    AgentError,
    AgentInitializationError,
    AgentValidationError,
    AgentTaskError,
    AgentNotFoundError,
    AgentBusyError,
    TaskValidationError,
    TaskExecutionError,
    TaskNotFoundError,
    InvalidTaskTypeError,
    NoAvailableAgentError,
    AgentStateError,
    ModelAPIError,
    ResourceExhaustedError,
    CommunicationError,
)
from .utils import (
    format_agent_response,
    validate_task_data,
    calculate_task_priority,
    chunk_text,
    merge_agent_results,
    sanitize_agent_input,
    format_error_response,
    log_agent_activity,
)
from .constants import (
    AGENT_STATUS,
    AGENT_TYPES,
    TASK_STATUS,
    PRIORITY_RANGES,
    DEFAULT_AGENT_CONFIG,
    MODEL_PARAMS,
    TEXT_GENERATION_PARAMS,
    QUALITY_THRESHOLDS,
    EVENT_TYPES,
    ERROR_CODES,
    SYSTEM_LIMITS,
)

# 导出所有Agent类
__all__ = [
    # Agent类
    "BaseAgent",
    "PlotAgent",
    "CharacterAgent",
    "SceneAgent",
    "WritingAgent",
    "QAAgent",
    "CoherenceAgent",
    # 管理器
    "AgentManager",
    # 异常类
    "AgentError",
    "AgentInitializationError",
    "AgentValidationError",
    "AgentTaskError",
    "AgentNotFoundError",
    "AgentBusyError",
    "TaskValidationError",
    "TaskExecutionError",
    "TaskNotFoundError",
    "InvalidTaskTypeError",
    "NoAvailableAgentError",
    "AgentStateError",
    "ModelAPIError",
    "ResourceExhaustedError",
    "CommunicationError",
    # 工具函数
    "format_agent_response",
    "validate_task_data",
    "calculate_task_priority",
    "chunk_text",
    "merge_agent_results",
    "sanitize_agent_input",
    "format_error_response",
    "log_agent_activity",
    # 常量
    "AGENT_STATUS",
    "AGENT_TYPES",
    "TASK_STATUS",
    "PRIORITY_RANGES",
    "DEFAULT_AGENT_CONFIG",
    "MODEL_PARAMS",
    "TEXT_GENERATION_PARAMS",
    "QUALITY_THRESHOLDS",
    "EVENT_TYPES",
    "ERROR_CODES",
    "SYSTEM_LIMITS",
]

# Agent类型到具体Agent类的映射
AGENT_TYPE_MAP = {
    "plot": PlotAgent,
    "character": CharacterAgent,
    "scene": SceneAgent,
    "writing": WritingAgent,
    "qa": QAAgent,
    "coherence": CoherenceAgent,
}

def get_agent_class(agent_type: str) -> type:
    """
    根据Agent类型获取对应的Agent类
    """
    if agent_type not in AGENT_TYPE_MAP:
        raise InvalidTaskTypeError(f"Unknown agent type: {agent_type}")
    return AGENT_TYPE_MAP[agent_type]

def validate_task_type(agent_type: str, task_type: str) -> bool:
    """
    验证任务类型是否合法
    """
    valid_tasks = EVENT_TYPES.get(f"{agent_type.upper()}_EVENTS", {}).values()
    return task_type in valid_tasks