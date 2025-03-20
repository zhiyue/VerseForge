from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.user import (
    User,
    UserCreate,
    UserUpdate,
    UserPreference,
    UserPreferenceCreate,
    UserPreferenceUpdate,
)
from app.models.user import User as UserModel
from app import crud

router = APIRouter()

@router.get("/me", response_model=User)
async def read_current_user(
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    获取当前登录用户信息
    """
    return current_user

@router.put("/me", response_model=User)
async def update_current_user(
    *,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user),
    user_in: UserUpdate
) -> Any:
    """
    更新当前登录用户信息
    """
    user = crud.user.update(
        db,
        db_obj=current_user,
        obj_in=user_in
    )
    return user

@router.get("/me/preferences", response_model=UserPreference)
async def read_user_preferences(
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    获取用户偏好设置
    """
    preferences = crud.user_preference.get_by_user_id(
        db,
        user_id=current_user.id
    )
    if not preferences:
        raise HTTPException(
            status_code=404,
            detail="未找到用户偏好设置"
        )
    return preferences

@router.put("/me/preferences", response_model=UserPreference)
async def update_user_preferences(
    *,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user),
    preferences_in: UserPreferenceUpdate
) -> Any:
    """
    更新用户偏好设置
    """
    preferences = crud.user_preference.get_by_user_id(
        db,
        user_id=current_user.id
    )
    if not preferences:
        preferences_in_data = jsonable_encoder(preferences_in)
        preferences_create = UserPreferenceCreate(
            **preferences_in_data,
            user_id=current_user.id
        )
        preferences = crud.user_preference.create(
            db,
            obj_in=preferences_create
        )
    else:
        preferences = crud.user_preference.update(
            db,
            db_obj=preferences,
            obj_in=preferences_in
        )
    return preferences

@router.get("", response_model=List[User])
async def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    获取用户列表（仅超级管理员）
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("", response_model=User)
async def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    创建新用户（仅超级管理员）
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已注册"
        )
    user = crud.user.create(db, obj_in=user_in)
    return user

@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int,
    current_user: UserModel = Depends(deps.get_current_active_superuser),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    通过ID获取用户信息（仅超级管理员）
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    更新用户信息（仅超级管理员）
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=User)
async def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    删除用户（仅超级管理员）
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    user = crud.user.remove(db, id=user_id)
    return user