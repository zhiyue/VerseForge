from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.models import Agent, AgentTask, AgentStatus
from app.core.config import settings
from app.core.celery_app import celery_app
from app.ai import model_manager
from app.crud import model_config as model_config_crud

class BaseAgent(ABC):
    """
    Agent基类
    支持可配置的AI模型
    """
    def __init__(
        self,
        db: Session,
        agent_model: Agent,
        parameters: Optional[Dict] = None
    ):
        self.db = db
        self.agent_model = agent_model
        self.parameters = parameters or {}
        
        # 获取模型配置
        self.model_config = model_config_crud.get_by_agent_id(
            db,
            agent_id=agent_model.id
        )
        
        # 根据配置初始化模型
        if self.model_config:
            self.setup_model()
        else:
            # 使用默认模型
            self.model = model_manager.get_model()

    def setup_model(self) -> None:
        """
        根据配置设置模型
        """
        config = self.model_config
        
        # 获取或创建模型实例
        model_key = f"{config.provider}_{config.model_name}"
        try:
            self.model = model_manager.get_model(model_key)
        except ValueError:
            # 如果模型不存在，创建新实例
            from app.ai import OpenAIAdapter  # 未来可以支持更多适配器
            
            if config.provider == "openai":
                model = OpenAIAdapter(
                    api_key=config.api_key,
                    model_name=config.model_name,
                    organization=config.organization_id
                )
                model_manager.register_model(model_key, model)
                self.model = model
            else:
                # 使用默认模型
                self.model = model_manager.get_model()

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        处理任务前检查使用限制
        """
        # 如果有模型配置，检查使用限制
        if self.model_config:
            # 估算所需token
            prompt = await self.prepare_prompt(task)
            tokens_required = self.model.get_token_count(prompt)
            
            # 检查限制
            check_result = model_config_crud.check_usage_limits(
                self.db,
                agent_id=self.agent_model.id,
                tokens_required=tokens_required
            )
            
            if not check_result["allowed"]:
                raise ValueError(f"使用限制检查失败: {check_result['reason']}")
        
        # 处理任务
        result = await self._process_task(task)
        
        # 更新使用统计
        if self.model_config and isinstance(result, dict):
            tokens_used = result.get("tokens_used", 0)
            cost = result.get("cost", 0.0)
            
            model_config_crud.update_usage_stats(
                self.db,
                agent_id=self.agent_model.id,
                tokens_used=tokens_used,
                cost=cost
            )
        
        return result

    @abstractmethod
    async def _process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        实际的任务处理逻辑
        由具体的Agent实现
        """
        pass

    @abstractmethod
    async def prepare_prompt(self, task: AgentTask) -> str:
        """
        准备提示文本
        由具体的Agent实现
        """
        pass

    @abstractmethod
    async def validate_task(self, task: AgentTask) -> bool:
        """
        验证任务的抽象方法
        由具体的Agent实现
        """
        pass

    async def update_status(self, status: AgentStatus) -> None:
        """
        更新Agent状态
        """
        self.agent_model.status = status
        self.db.add(self.agent_model)
        await self.db.commit()
        await self.db.refresh(self.agent_model)

    async def log_error(self, error_message: str) -> None:
        """
        记录错误信息
        """
        self.agent_model.error_message = error_message
        self.agent_model.status = AgentStatus.ERROR
        self.db.add(self.agent_model)
        await self.db.commit()
        await self.db.refresh(self.agent_model)

    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        发送事件
        """
        from app.core.events import emit_event
        emit_event(
            event_type=event_type,
            data={
                "agent_id": self.agent_model.id,
                "agent_type": self.agent_model.agent_type.value,
                **data
            }
        )