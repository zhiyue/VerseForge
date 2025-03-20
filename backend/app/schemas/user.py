from typing import Optional
from pydantic import BaseModel, EmailStr, constr

class UserBase(BaseModel):
    """
    用户基础模型
    """
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    username: Optional[str] = None

class UserCreate(UserBase):
    """
    创建用户请求模型
    """
    email: EmailStr
    username: constr(min_length=4, max_length=32)  # 用户名长度限制
    password: constr(min_length=8, max_length=32)  # 密码长度限制

class UserUpdate(UserBase):
    """
    更新用户请求模型
    """
    password: Optional[constr(min_length=8, max_length=32)] = None

class UserInDBBase(UserBase):
    """
    数据库用户基础模型
    """
    id: int
    
    class Config:
        from_attributes = True

class User(UserInDBBase):
    """
    用户响应模型
    不包含敏感信息
    """
    pass

class UserInDB(UserInDBBase):
    """
    数据库用户完整模型
    包含敏感信息
    """
    hashed_password: str

class UserPreferenceBase(BaseModel):
    """
    用户偏好设置基础模型
    """
    theme: Optional[str] = "light"
    language: Optional[str] = "zh-CN"
    items_per_page: Optional[int] = 20
    notification_settings: Optional[str] = "all"

class UserPreferenceCreate(UserPreferenceBase):
    """
    创建用户偏好设置请求模型
    """
    user_id: int

class UserPreferenceUpdate(UserPreferenceBase):
    """
    更新用户偏好设置请求模型
    """
    pass

class UserPreference(UserPreferenceBase):
    """
    用户偏好设置响应模型
    """
    id: int
    user_id: int

    class Config:
        from_attributes = True