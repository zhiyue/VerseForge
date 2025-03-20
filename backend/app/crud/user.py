from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User, UserPreference
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.user import UserPreferenceCreate, UserPreferenceUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    用户CRUD操作
    """
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        通过邮箱获取用户
        """
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        通过用户名获取用户
        """
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        创建新用户
        """
        create_data = obj_in.dict()
        create_data.pop("password")
        db_obj = User(
            **create_data,
            hashed_password=get_password_hash(obj_in.password)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        更新用户信息
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
            
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self,
        db: Session,
        *,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        验证用户
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """
        检查用户是否激活
        """
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """
        检查是否是超级用户
        """
        return user.is_superuser

    def update_password(
        self,
        db: Session,
        *,
        db_obj: User,
        new_password: str
    ) -> User:
        """
        更新用户密码
        """
        hashed_password = get_password_hash(new_password)
        db_obj.hashed_password = hashed_password
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

class CRUDUserPreference(CRUDBase[UserPreference, UserPreferenceCreate, UserPreferenceUpdate]):
    """
    用户偏好设置CRUD操作
    """
    def get_by_user_id(
        self,
        db: Session,
        *,
        user_id: int
    ) -> Optional[UserPreference]:
        """
        通过用户ID获取偏好设置
        """
        return (
            db.query(UserPreference)
            .filter(UserPreference.user_id == user_id)
            .first()
        )

    def create_or_update(
        self,
        db: Session,
        *,
        user_id: int,
        obj_in: Union[UserPreferenceCreate, UserPreferenceUpdate]
    ) -> UserPreference:
        """
        创建或更新用户偏好设置
        """
        db_obj = self.get_by_user_id(db, user_id=user_id)
        if db_obj:
            return self.update(db, db_obj=db_obj, obj_in=obj_in)
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        return self.create(db, obj_in=UserPreferenceCreate(**obj_in_data))

user = CRUDUser(User)
user_preference = CRUDUserPreference(UserPreference)