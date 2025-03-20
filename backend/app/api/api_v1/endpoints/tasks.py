from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.agent import Task, TaskCreate, TaskUpdate
from app.models.user import User as UserModel
from app import crud

router = APIRouter()

@router.get("", response_model=List[Task])
async def read_tasks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    novel_id: int = None,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    获取任务列表
    可以根据状态和小说ID筛选
    """
    if current_user.is_superuser:
        tasks = crud.task.get_multi(
            db,
            skip=skip,
            limit=limit,
            status=status,
            novel_id=novel_id
        )
    else:
        # 普通用户只能看到自己小说相关的任务
        tasks = crud.task.get_multi_by_creator(
            db,
            creator_id=current_user.id,
            skip=skip,
            limit=limit,
            status=status,
            novel_id=novel_id
        )
    return tasks

@router.post("", response_model=Task)
async def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    创建新任务
    """
    # 检查小说访问权限
    deps.check_novel_access(task_in.novel_id, current_user=current_user, db=db)
    
    # 获取Agent管理器
    agent_manager = deps.get_agent_manager(db)
    
    # 创建任务
    task = await agent_manager.create_task(
        agent_type=task_in.agent_type,
        task_type=task_in.task_type,
        task_data=task_in.task_data,
        novel_id=task_in.novel_id,
        priority=task_in.priority
    )
    
    # 在后台执行任务
    background_tasks.add_task(
        agent_manager.execute_task,
        task.id
    )
    
    return task

@router.get("/{task_id}", response_model=Task)
async def read_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    获取任务详情
    """
    task = crud.task.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="任务不存在"
        )
        
    # 检查访问权限
    if not current_user.is_superuser:
        deps.check_novel_access(task.novel_id, current_user=current_user, db=db)
        
    return task

@router.put("/{task_id}", response_model=Task)
async def update_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    task_in: TaskUpdate,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    更新任务状态（仅管理员）
    """
    task = crud.task.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="任务不存在"
        )
    
    task = crud.task.update(db, db_obj=task, obj_in=task_in)
    return task

@router.delete("/{task_id}", response_model=Task)
async def cancel_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    取消任务
    """
    task = crud.task.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="任务不存在"
        )
        
    # 检查访问权限
    if not current_user.is_superuser:
        deps.check_novel_access(task.novel_id, current_user=current_user, db=db)
    
    # 获取Agent管理器
    agent_manager = deps.get_agent_manager(db)
    
    # 更新任务状态为已取消
    task_in = TaskUpdate(status="cancelled")
    task = crud.task.update(db, db_obj=task, obj_in=task_in)
    
    return task

@router.post("/{task_id}/retry", response_model=Task)
async def retry_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    重试失败的任务
    """
    task = crud.task.get(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="任务不存在"
        )
        
    # 检查访问权限
    if not current_user.is_superuser:
        deps.check_novel_access(task.novel_id, current_user=current_user, db=db)
    
    # 检查任务状态
    if task.status != "failed":
        raise HTTPException(
            status_code=400,
            detail="只能重试失败的任务"
        )
    
    # 获取Agent管理器
    agent_manager = deps.get_agent_manager(db)
    
    # 重置任务状态
    task_in = TaskUpdate(status="pending", error_message=None)
    task = crud.task.update(db, db_obj=task, obj_in=task_in)
    
    # 在后台重新执行任务
    background_tasks.add_task(
        agent_manager.execute_task,
        task.id
    )
    
    return task