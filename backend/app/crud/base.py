from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD操作基类
    提供基本的数据库操作方法
    """
    def __init__(self, model: Type[ModelType]):
        """
        初始化
        :param model: SQLAlchemy模型类
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        通过ID获取记录
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        获取多条记录
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        创建新记录
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        更新记录
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        删除记录
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def exists(self, db: Session, *, id: int) -> bool:
        """
        检查记录是否存在
        """
        return db.query(self.model).filter(self.model.id == id).first() is not None

    def count(self, db: Session) -> int:
        """
        获取记录总数
        """
        return db.query(self.model).count()

    def get_multi_by_ids(
        self,
        db: Session,
        *,
        ids: List[int],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        通过ID列表获取多条记录
        """
        return (
            db.query(self.model)
            .filter(self.model.id.in_(ids))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_filter(
        self,
        db: Session,
        *,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        通过过滤条件获取多条记录
        """
        query = db.query(self.model)
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)
        return query.offset(skip).limit(limit).all()

    def bulk_create(
        self,
        db: Session,
        *,
        objs_in: List[CreateSchemaType]
    ) -> List[ModelType]:
        """
        批量创建记录
        """
        db_objs = []
        for obj_in in objs_in:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db_objs.append(db_obj)
            
        db.bulk_save_objects(db_objs)
        db.commit()
        return db_objs

    def bulk_update(
        self,
        db: Session,
        *,
        objs: List[Dict[str, Any]]
    ) -> List[ModelType]:
        """
        批量更新记录
        objs格式: [{"id": 1, "field": "value"}, ...]
        """
        db_objs = []
        for obj in objs:
            if "id" not in obj:
                continue
            db_obj = self.get(db, id=obj["id"])
            if not db_obj:
                continue
            for field, value in obj.items():
                if field != "id":
                    setattr(db_obj, field, value)
            db_objs.append(db_obj)
            
        db.bulk_save_objects(db_objs)
        db.commit()
        return db_objs