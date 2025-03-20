from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import decode_token
from app.models.user import User

# OAuth2 配置
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_db() -> Generator:
    """
    数据库会话依赖
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前认证用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception
            
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
            
    except (JWTError, ValidationError):
        raise credentials_exception
        
    # 从数据库获取用户
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账号未激活"
        )
        
    return user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前超级用户
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return current_user

def get_agent_manager(db: Session = Depends(get_db)):
    """
    获取Agent管理器实例
    """
    from app.agents import AgentManager
    return AgentManager(db)

def check_novel_access(
    novel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> bool:
    """
    检查用户是否有权限访问指定小说
    """
    from app.models import Novel
    
    novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="小说不存在"
        )
        
    # 超级用户可以访问所有小说
    if current_user.is_superuser:
        return True
        
    # 检查是否是小说的创建者
    if novel.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有访问权限"
        )
        
    return True

def check_resource_limit(
    resource_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> bool:
    """
    检查资源使用限制
    """
    from app.agents.constants import SYSTEM_LIMITS
    from app.models import Novel
    
    if resource_type == "novel":
        # 检查用户的小说数量是否达到上限
        novel_count = db.query(Novel).filter(
            Novel.creator_id == current_user.id
        ).count()
        
        if novel_count >= SYSTEM_LIMITS["max_concurrent_novels"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已达到最大小说数量限制"
            )
            
    return True