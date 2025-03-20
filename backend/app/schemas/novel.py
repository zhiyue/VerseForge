from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class NovelBase(BaseModel):
    """
    小说基础模型
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    genre: Optional[str] = None
    target_word_count: int = Field(default=50000, ge=1000)

class NovelCreate(NovelBase):
    """
    创建小说请求模型
    """
    pass

class NovelUpdate(NovelBase):
    """
    更新小说请求模型
    """
    status: Optional[str] = None
    current_word_count: Optional[int] = None
    outline: Optional[Dict[str, Any]] = None

class Novel(NovelBase):
    """
    小说响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    creator_id: Optional[int] = None
    status: str
    current_word_count: int
    outline: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ChapterBase(BaseModel):
    """
    章节基础模型
    """
    chapter_number: int = Field(..., ge=1)
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None

class ChapterCreate(ChapterBase):
    """
    创建章节请求模型
    """
    novel_id: int

class ChapterUpdate(ChapterBase):
    """
    更新章节请求模型
    """
    status: Optional[str] = None
    word_count: Optional[int] = None

class Chapter(ChapterBase):
    """
    章节响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    novel_id: int
    status: str
    word_count: int

    class Config:
        from_attributes = True

class CharacterBase(BaseModel):
    """
    人物基础模型
    """
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    role_type: Optional[str] = None
    personality: Optional[Dict[str, Any]] = None
    background: Optional[str] = None

class CharacterCreate(CharacterBase):
    """
    创建人物请求模型
    """
    novel_id: int

class CharacterUpdate(CharacterBase):
    """
    更新人物请求模型
    """
    pass

class Character(CharacterBase):
    """
    人物响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    novel_id: int

    class Config:
        from_attributes = True

class EventBase(BaseModel):
    """
    事件基础模型
    """
    event_type: str
    description: str
    chapter_number: Optional[int] = None
    priority: int = Field(default=0, ge=0, le=100)

class EventCreate(EventBase):
    """
    创建事件请求模型
    """
    novel_id: int
    character_id: Optional[int] = None

class EventUpdate(EventBase):
    """
    更新事件请求模型
    """
    status: Optional[str] = None

class Event(EventBase):
    """
    事件响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    novel_id: int
    character_id: Optional[int] = None
    status: str

    class Config:
        from_attributes = True

# 嵌套响应模型
class NovelDetail(Novel):
    """
    小说详细信息响应模型
    """
    chapters: List[Chapter] = []
    characters: List[Character] = []
    events: List[Event] = []