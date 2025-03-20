from typing import Any
from datetime import timedelta
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.core.config import settings
from app.api import deps
from app.schemas.token import Token
from app.schemas.user import User, UserCreate
from app.models.user import User as UserModel
from app import crud

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 兼容的令牌登录，获取访问令牌
    """
    # 验证用户
    user = crud.user.authenticate(
        db,
        email=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400,
            detail="邮箱或密码错误"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="用户未激活"
        )

    # 创建访问令牌
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        user.id,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/signup", response_model=User)
async def signup(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate
) -> Any:
    """
    用户注册
    """
    # 检查用户是否已存在
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已注册"
        )
    
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="该用户名已被使用"
        )

    # 创建新用户
    user = crud.user.create(db, obj_in=user_in)
    
    return user

@router.post("/test-token", response_model=User)
async def test_token(
    current_user: UserModel = Depends(deps.get_current_user)
) -> Any:
    """
    测试访问令牌
    """
    return current_user

@router.post("/reset-password", response_model=User)
async def reset_password(
    *,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user),
    new_password: str = Body(...),
) -> Any:
    """
    重置密码
    """
    # 更新密码
    user = crud.user.update_password(
        db,
        db_obj=current_user,
        new_password=new_password
    )
    
    return user