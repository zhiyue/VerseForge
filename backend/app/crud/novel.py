from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.novel import Novel, Chapter, Character, Event
from app.schemas.novel import (
    NovelCreate,
    NovelUpdate,
    ChapterCreate,
    ChapterUpdate,
    CharacterCreate,
    CharacterUpdate,
    EventCreate,
    EventUpdate,
)

class CRUDNovel(CRUDBase[Novel, NovelCreate, NovelUpdate]):
    """
    小说CRUD操作
    """
    def create_with_creator(
        self,
        db: Session,
        *,
        obj_in: NovelCreate,
        creator_id: int
    ) -> Novel:
        """
        创建新小说（带创建者ID）
        """
        obj_in_data = obj_in.dict()
        db_obj = Novel(**obj_in_data, creator_id=creator_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_creator(
        self,
        db: Session,
        *,
        creator_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Novel]:
        """
        获取指定创建者的所有小说
        """
        return (
            db.query(Novel)
            .filter(Novel.creator_id == creator_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_generation_status(
        self,
        db: Session,
        *,
        novel_id: int
    ) -> Dict[str, Any]:
        """
        获取小说生成状态
        """
        novel = self.get(db, id=novel_id)
        if not novel:
            return None

        from app.models import AgentTask
        # 获取相关任务状态
        tasks = (
            db.query(AgentTask)
            .filter(AgentTask.novel_id == novel_id)
            .order_by(AgentTask.created_at.desc())
            .all()
        )

        return {
            "novel_status": novel.status,
            "current_word_count": novel.current_word_count,
            "target_word_count": novel.target_word_count,
            "progress": (novel.current_word_count / novel.target_word_count)
            if novel.target_word_count > 0 else 0,
            "tasks": [
                {
                    "id": task.id,
                    "type": task.task_type,
                    "status": task.status,
                    "created_at": task.created_at,
                    "updated_at": task.updated_at,
                }
                for task in tasks
            ]
        }

class CRUDChapter(CRUDBase[Chapter, ChapterCreate, ChapterUpdate]):
    """
    章节CRUD操作
    """
    def get_multi_by_novel(
        self,
        db: Session,
        *,
        novel_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Chapter]:
        """
        获取指定小说的所有章节
        """
        return (
            db.query(Chapter)
            .filter(Chapter.novel_id == novel_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_chapter_number(
        self,
        db: Session,
        *,
        novel_id: int,
        chapter_number: int
    ) -> Optional[Chapter]:
        """
        通过章节号获取章节
        """
        return (
            db.query(Chapter)
            .filter(
                Chapter.novel_id == novel_id,
                Chapter.chapter_number == chapter_number
            )
            .first()
        )

class CRUDCharacter(CRUDBase[Character, CharacterCreate, CharacterUpdate]):
    """
    人物CRUD操作
    """
    def get_multi_by_novel(
        self,
        db: Session,
        *,
        novel_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Character]:
        """
        获取指定小说的所有人物
        """
        return (
            db.query(Character)
            .filter(Character.novel_id == novel_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

class CRUDEvent(CRUDBase[Event, EventCreate, EventUpdate]):
    """
    事件CRUD操作
    """
    def get_multi_by_novel(
        self,
        db: Session,
        *,
        novel_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """
        获取指定小说的所有事件
        """
        return (
            db.query(Event)
            .filter(Event.novel_id == novel_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_character(
        self,
        db: Session,
        *,
        character_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """
        获取指定人物的所有事件
        """
        return (
            db.query(Event)
            .filter(Event.character_id == character_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

novel = CRUDNovel(Novel)
chapter = CRUDChapter(Chapter)
character = CRUDCharacter(Character)
event = CRUDEvent(Event)