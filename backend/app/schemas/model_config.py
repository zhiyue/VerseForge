from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ModelProviderConfig(BaseModel):
    """
    AI模型供应商配置
    """
    provider: str = Field(..., description="供应商名称")
    model_name: str = Field(..., description="模型名称")
    api_key: str = Field(..., description="API密钥")
    organization_id: Optional[str] = Field(None, description="组织ID")
    base_url: Optional[str] = Field(None, description="API基础URL")
    extra_params: Optional[Dict[str, Any]] = Field(default={}, description="额外参数")

class AgentModelConfig(BaseModel):
    """
    Agent的模型配置
    """
    agent_id: int = Field(..., description="Agent ID")
    provider_config: ModelProviderConfig = Field(..., description="供应商配置")
    parameters: Dict[str, Any] = Field(
        default={
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        },
        description="模型参数"
    )
    usage_limits: Dict[str, Any] = Field(
        default={
            "max_requests_per_minute": 60,
            "max_tokens_per_request": 4096,
            "max_daily_tokens": 1000000
        },
        description="使用限制"
    )
    fallback_provider: Optional[str] = Field(None, description="备用供应商")

class ModelConfigUpdate(BaseModel):
    """
    模型配置更新请求
    """
    provider_config: Optional[ModelProviderConfig]
    parameters: Optional[Dict[str, Any]]
    usage_limits: Optional[Dict[str, Any]]
    fallback_provider: Optional[str]