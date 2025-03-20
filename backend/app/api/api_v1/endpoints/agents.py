from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.agent import (
    Agent,
    AgentCreate,
    AgentUpdate,
    Task,
    TaskCreate,
    AgentStatus,
    AgentSystemStatus
)
from app.models.user import User as UserModel
from app import crud

router = APIRouter()

@router.get("", response_model=List[Agent])
async def read_agents(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    获取Agent列表（仅管理员）
    """
    agents = crud.agent.get_multi(db, skip=skip, limit=limit)
    return agents

@router.post("", response_model=Agent)
async def create_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_in: AgentCreate,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    创建新Agent（仅管理员）
    """
    agent = crud.agent.create(db, obj_in=agent_in)
    return agent

@router.get("/system-status", response_model=AgentSystemStatus)
async def get_system_status(
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    获取Agent系统状态
    """
    agent_manager = deps.get_agent_manager(db)
    status = await agent_manager.get_system_status()
    return status

@router.get("/{agent_id}", response_model=Agent)
async def read_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    获取Agent详情（仅管理员）
    """
    agent = crud.agent.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent不存在"
        )
    return agent

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    agent_in: AgentUpdate,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    更新Agent配置（仅管理员）
    """
    agent = crud.agent.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent不存在"
        )
    agent = crud.agent.update(db, db_obj=agent, obj_in=agent_in)
    return agent

@router.get("/{agent_id}/status", response_model=AgentStatus)
async def get_agent_status(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    获取Agent状态
    """
    agent_manager = deps.get_agent_manager(db)
    status = await agent_manager.get_agent_status(agent_id)
    return status

@router.post("/{agent_id}/reset", response_model=Agent)
async def reset_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    重置Agent状态（仅管理员）
    """
    agent_manager = deps.get_agent_manager(db)
    await agent_manager.reset_agent(agent_id)
    
    agent = crud.agent.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent不存在"
        )
    return agent

@router.post("/{agent_id}/tasks", response_model=Task)
async def create_agent_task(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    task_in: TaskCreate,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    为Agent创建新任务
    """
    agent = crud.agent.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent不存在"
        )
    
    # 检查小说访问权限
    deps.check_novel_access(task_in.novel_id, current_user=current_user, db=db)
    
    agent_manager = deps.get_agent_manager(db)
    task = await agent_manager.create_task(
        agent_type=agent.agent_type.value,
        task_type=task_in.task_type,
        task_data=task_in.task_data,
        novel_id=task_in.novel_id,
        priority=task_in.priority
    )
    return task