class AgentError(Exception):
    """
    Agent基础异常类
    """
    pass

class AgentInitializationError(AgentError):
    """
    Agent初始化失败异常
    """
    pass

class AgentValidationError(AgentError):
    """
    Agent验证失败异常
    """
    pass

class AgentTaskError(AgentError):
    """
    Agent任务处理异常
    """
    pass

class AgentNotFoundError(AgentError):
    """
    Agent不存在异常
    """
    pass

class AgentBusyError(AgentError):
    """
    Agent忙碌异常
    """
    pass

class TaskValidationError(AgentError):
    """
    任务验证失败异常
    """
    pass

class TaskExecutionError(AgentError):
    """
    任务执行失败异常
    """
    pass

class TaskNotFoundError(AgentError):
    """
    任务不存在异常
    """
    pass

class InvalidTaskTypeError(AgentError):
    """
    无效的任务类型异常
    """
    pass

class NoAvailableAgentError(AgentError):
    """
    没有可用Agent异常
    """
    pass

class AgentStateError(AgentError):
    """
    Agent状态异常
    """
    pass

class ModelAPIError(AgentError):
    """
    AI模型API调用异常
    """
    pass

class ResourceExhaustedError(AgentError):
    """
    资源耗尽异常
    """
    pass

class CommunicationError(AgentError):
    """
    Agent间通信异常
    """
    pass