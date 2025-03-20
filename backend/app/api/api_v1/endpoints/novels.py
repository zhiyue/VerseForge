from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.novel import (
    Novel,
    NovelCreate,
    NovelUpdate,
    NovelDetail,
    Chapter,
    ChapterCreate,
)
from app.models.user import User as UserModel
from app import crud

router = APIRouter()

@router.get("", response_model=List[Novel])
async def read_novels(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    获取小说列表
    """
    if current_user.is_superuser:
        novels = crud.novel.get_multi(db, skip=skip, limit=limit)
    else:
        novels = crud.novel.get_multi_by_creator(
            db,
            creator_id=current_user.id,
            skip=skip,
            limit=limit
        )
    return novels

@router.post("", response_model=Novel)
async def create_novel(
    *,
    db: Session = Depends(deps.get_db),
    novel_in: NovelCreate,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    创建新小说
    """
    # 检查资源限制
    deps.check_resource_limit("novel", current_user=current_user, db=db)
    
    novel = crud.novel.create_with_creator(
        db,
        obj_in=novel_in,
        creator_id=current_user.id
    )
    return novel

@router.get("/{novel_id}", response_model=NovelDetail)
async def read_novel(
    *,
    db: Session = Depends(deps.get_db),
    novel_id: int,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    获取小说详细信息
    """
    novel = crud.novel.get(db, id=novel_id)
    if not novel:
        raise HTTPException(
            status_code=404,
            detail="小说不存在"
        )
        
    # 检查访问权限
    deps.check_novel_access(novel_id, current_user=current_user, db=db)
    
    return novel

@router.put("/{novel_id}", response_model=Novel)
async def update_novel(
    *,
    db: Session = Depends(deps.get_db),
    novel_id: int,
    novel_in: NovelUpdate,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    更新小说信息
    """
    novel = crud.novel.get(db, id=novel_id)
    if not novel:
        raise HTTPException(
            status_code=404,
            detail="小说不存在"
        )
        
    # 检查访问权限
    deps.check_novel_access(novel_id, current_user=current_user, db=db)
    
    novel = crud.novel.update(
        db,
        db_obj=novel,
        obj_in=novel_in
    )
    return novel

@router.delete("/{novel_id}", response_model=Novel)
async def delete_novel(
    *,
    db: Session = Depends(deps.get_db),
    novel_id: int,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    删除小说
    """
    novel = crud.novel.get(db, id=novel_id)
    if not novel:
        raise HTTPException(
            status_code=404,
            detail="小说不存在"
        )
        
    # 检查访问权限
    deps.check_novel_access(novel_id, current_user=current_user, db=db)
    
    novel = crud.novel.remove(db, id=novel_id)
    return novel

@router.get("/{novel_id}/generate", response_model=Any)
async def generate_content(
    *,
    db: Session = Depends(deps.get_db),
    novel_id: int,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    启动小说内容生成
    """
    novel = crud.novel.get(db, id=novel_id)
    if not novel:
        raise HTTPException(
            status_code=404,
            detail="小说不存在"
        )
        
    # 检查访问权限
    deps.check_novel_access(novel_id, current_user=current_user, db=db)
    
    # 获取Agent管理器
    agent_manager = deps.get_agent_manager(db)
    
    # 创建并启动生成任务
    task = await agent_manager.create_task(
        agent_type="plot",
        task_type="generate_outline",
        task_data={"novel_id": novel_id},
        novel_id=novel_id
    )
    
    return {"task_id": task.id}

@router.get("/{novel_id}/status", response_model=Any)
async def get_generation_status(
    *,
    db: Session = Depends(deps.get_db),
    novel_id: int,
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    获取小说生成状态
    """
    novel = crud.novel.get(db, id=novel_id)
    if not novel:
        raise HTTPException(
            status_code=404,
            detail="小说不存在"
        )
        
    # 检查访问权限
    deps.check_novel_access(novel_id, current_user=current_user, db=db)
    
    # 获取小说生成状态
    status = crud.novel.get_generation_status(db, novel_id=novel_id)
    return status