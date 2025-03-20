from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.model_config import (
    AgentModelConfig,
    ModelConfigUpdate,
    ModelProviderConfig,
)
from app.models.user import User as UserModel
from app import crud

router = APIRouter()

@router.get("", response_model=List[AgentModelConfig])
async def read_model_configs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    获取所有模型配置列表（仅管理员）
    """
    configs = crud.model_config.get_multi(db, skip=skip, limit=limit)
    return configs

@router.post("", response_model=AgentModelConfig)
async def create_model_config(
    *,
    db: Session = Depends(deps.get_db),
    config_in: AgentModelConfig,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    创建新的模型配置（仅管理员）
    """
    # 检查Agent是否存在
    agent = crud.agent.get(db, id=config_in.agent_id)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent不存在"
        )
        
    # 检查是否已存在配置
    existing_config = crud.model_config.get_by_agent_id(
        db,
        agent_id=config_in.agent_id
    )
    if existing_config:
        raise HTTPException(
            status_code=400,
            detail="该Agent已有模型配置"
        )
    
    config = crud.model_config.create_with_agent(
        db,
        obj_in=config_in,
        agent_id=config_in.agent_id
    )
    return config

@router.get("/{agent_id}", response_model=AgentModelConfig)
async def read_model_config(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    获取指定Agent的模型配置
    """
    config = crud.model_config.get_by_agent_id(db, agent_id=agent_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail="未找到模型配置"
        )
        
    # 检查权限
    if not current_user.is_superuser:
        # 检查是否是该Agent相关小说的创建者
        agent = crud.agent.get(db, id=agent_id)
        if agent and agent.novel:
            if agent.novel.creator_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="无权访问此配置"
                )
    
    return config

@router.put("/{agent_id}", response_model=AgentModelConfig)
async def update_model_config(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    config_in: ModelConfigUpdate,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    更新模型配置（仅管理员）
    """
    config = crud.model_config.get_by_agent_id(db, agent_id=agent_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail="未找到模型配置"
        )
        
    config = crud.model_config.update(db, db_obj=config, obj_in=config_in)
    return config

@router.delete("/{agent_id}", response_model=AgentModelConfig)
async def delete_model_config(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    删除模型配置（仅管理员）
    """
    config = crud.model_config.get_by_agent_id(db, agent_id=agent_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail="未找到模型配置"
        )
        
    config = crud.model_config.remove(db, id=config.id)
    return config

@router.get("/{agent_id}/usage", response_model=dict)
async def read_usage_stats(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    获取模型使用统计信息
    """
    config = crud.model_config.get_by_agent_id(db, agent_id=agent_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail="未找到模型配置"
        )
        
    # 检查权限
    if not current_user.is_superuser:
        agent = crud.agent.get(db, id=agent_id)
        if agent and agent.novel:
            if agent.novel.creator_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="无权访问此信息"
                )
    
    return config.usage_stats

@router.get("/{agent_id}/limits", response_model=dict)
async def check_usage_limits(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    tokens_required: int,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    检查使用限制
    """
    result = crud.model_config.check_usage_limits(
        db,
        agent_id=agent_id,
        tokens_required=tokens_required
    )
    return result