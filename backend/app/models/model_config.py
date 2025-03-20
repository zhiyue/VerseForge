from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base

class ModelConfig(Base):
    """
    Agent的模型配置数据模型
    """
    # 关联的Agent ID
    agent_id = Column(Integer, ForeignKey("agent.id"), nullable=False, unique=True)
    
    # 供应商配置
    provider = Column(String(50), nullable=False)  # 供应商名称
    model_name = Column(String(50), nullable=False)  # 模型名称
    api_key = Column(String(255), nullable=False)  # API密钥
    organization_id = Column(String(255), nullable=True)  # 组织ID
    base_url = Column(String(255), nullable=True)  # API基础URL
    extra_params = Column(JSON, nullable=True)  # 额外参数
    
    # 模型参数
    parameters = Column(
        JSON,
        nullable=False,
        default={
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
    )
    
    # 使用限制
    usage_limits = Column(
        JSON,
        nullable=False,
        default={
            "max_requests_per_minute": 60,
            "max_tokens_per_request": 4096,
            "max_daily_tokens": 1000000
        }
    )
    
    # 备用供应商
    fallback_provider = Column(String(50), nullable=True)
    
    # 使用统计
    usage_stats = Column(
        JSON,
        nullable=False,
        default={
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "daily_stats": {}
        }
    )
    
    # 关联关系
    agent = relationship("Agent", back_populates="model_config")