from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.model_config import ModelConfig
from app.schemas.model_config import (
    AgentModelConfig,
    ModelConfigUpdate,
)

class CRUDModelConfig(CRUDBase[ModelConfig, AgentModelConfig, ModelConfigUpdate]):
    """
    ModelConfig的CRUD操作
    """
    def get_by_agent_id(
        self,
        db: Session,
        *,
        agent_id: int
    ) -> Optional[ModelConfig]:
        """
        通过Agent ID获取模型配置
        """
        return (
            db.query(ModelConfig)
            .filter(ModelConfig.agent_id == agent_id)
            .first()
        )

    def create_with_agent(
        self,
        db: Session,
        *,
        obj_in: AgentModelConfig,
        agent_id: int
    ) -> ModelConfig:
        """
        创建Agent的模型配置
        """
        provider_config = obj_in.provider_config
        db_obj = ModelConfig(
            agent_id=agent_id,
            provider=provider_config.provider,
            model_name=provider_config.model_name,
            api_key=provider_config.api_key,
            organization_id=provider_config.organization_id,
            base_url=provider_config.base_url,
            extra_params=provider_config.extra_params,
            parameters=obj_in.parameters,
            usage_limits=obj_in.usage_limits,
            fallback_provider=obj_in.fallback_provider
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_usage_stats(
        self,
        db: Session,
        *,
        agent_id: int,
        tokens_used: int,
        cost: float
    ) -> ModelConfig:
        """
        更新使用统计信息
        """
        config = self.get_by_agent_id(db, agent_id=agent_id)
        if not config:
            return None

        # 获取当前统计信息
        stats = config.usage_stats
        
        # 更新总计数据
        stats["total_requests"] += 1
        stats["total_tokens"] += tokens_used
        stats["total_cost"] += cost
        
        # 更新每日统计
        from datetime import date
        today = date.today().isoformat()
        daily_stats = stats.get("daily_stats", {})
        today_stats = daily_stats.get(today, {
            "requests": 0,
            "tokens": 0,
            "cost": 0.0
        })
        
        today_stats["requests"] += 1
        today_stats["tokens"] += tokens_used
        today_stats["cost"] += cost
        
        daily_stats[today] = today_stats
        stats["daily_stats"] = daily_stats
        
        # 更新数据库
        config.usage_stats = stats
        db.add(config)
        db.commit()
        db.refresh(config)
        
        return config

    def check_usage_limits(
        self,
        db: Session,
        *,
        agent_id: int,
        tokens_required: int
    ) -> Dict[str, Any]:
        """
        检查是否超过使用限制
        返回检查结果和剩余配额
        """
        config = self.get_by_agent_id(db, agent_id=agent_id)
        if not config:
            return {
                "allowed": False,
                "reason": "未找到模型配置"
            }
        
        limits = config.usage_limits
        stats = config.usage_stats
        
        # 检查每分钟请求限制
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        last_minute = (now - timedelta(minutes=1)).isoformat()
        
        recent_requests = sum(
            1 for timestamp in stats.get("request_timestamps", [])
            if timestamp > last_minute
        )
        
        if recent_requests >= limits["max_requests_per_minute"]:
            return {
                "allowed": False,
                "reason": "超过每分钟请求限制"
            }
        
        # 检查token数量限制
        if tokens_required > limits["max_tokens_per_request"]:
            return {
                "allowed": False,
                "reason": "超过单次token限制"
            }
        
        # 检查每日token限制
        today = datetime.now().date().isoformat()
        daily_stats = stats.get("daily_stats", {}).get(today, {})
        daily_tokens = daily_stats.get("tokens", 0)
        
        if daily_tokens + tokens_required > limits["max_daily_tokens"]:
            return {
                "allowed": False,
                "reason": "超过每日token限制"
            }
        
        return {
            "allowed": True,
            "remaining": {
                "requests_per_minute": limits["max_requests_per_minute"] - recent_requests,
                "daily_tokens": limits["max_daily_tokens"] - daily_tokens
            }
        }

model_config = CRUDModelConfig(ModelConfig)