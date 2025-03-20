from typing import List
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base

class NovelStatus(enum.Enum):
    """
    小说状态枚举
    """
    PLANNING = "planning"      # 规划中
    WRITING = "writing"       # 写作中
    REVIEWING = "reviewing"   # 审核中
    COMPLETED = "completed"   # 已完成
    PAUSED = "paused"        # 已暂停
    ABANDONED = "abandoned"   # 已废弃

class Novel(Base):
    """
    小说模型
    """
    # 标题
    title = Column(String(200), nullable=False, index=True)
    # 描述
    description = Column(Text, nullable=True)
    # 类型
    genre = Column(String(50), nullable=True)
    # 目标字数
    target_word_count = Column(Integer, nullable=False, default=50000)
    # 当前字数
    current_word_count = Column(Integer, nullable=False, default=0)
    # 状态
    status = Column(
        Enum(NovelStatus),
        nullable=False,
        default=NovelStatus.PLANNING
    )
    # 大纲
    outline = Column(Text, nullable=True)
    # 创建者ID（预留外键）
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=True)

    # 关联关系
    chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="novel", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="novel", cascade="all, delete-orphan")

class Chapter(Base):
    """
    章节模型
    """
    # 章节号
    chapter_number = Column(Integer, nullable=False)
    # 标题
    title = Column(String(200), nullable=True)
    # 内容
    content = Column(Text, nullable=True)
    # 字数
    word_count = Column(Integer, nullable=False, default=0)
    # 状态
    status = Column(
        String(20),
        nullable=False,
        default="draft"
    )
    # 所属小说ID
    novel_id = Column(Integer, ForeignKey("novel.id"), nullable=False)

    # 关联关系
    novel = relationship("Novel", back_populates="chapters")

class Character(Base):
    """
    人物模型
    """
    # 名称
    name = Column(String(100), nullable=False)
    # 描述
    description = Column(Text, nullable=True)
    # 角色类型（主角/配角等）
    role_type = Column(String(50), nullable=True)
    # 性格特征
    personality = Column(Text, nullable=True)
    # 背景故事
    background = Column(Text, nullable=True)
    # 所属小说ID
    novel_id = Column(Integer, ForeignKey("novel.id"), nullable=False)

    # 关联关系
    novel = relationship("Novel", back_populates="characters")
    events = relationship("Event", back_populates="characters")

class Event(Base):
    """
    事件模型
    """
    # 事件类型
    event_type = Column(String(50), nullable=False)
    # 事件描述
    description = Column(Text, nullable=False)
    # 发生章节
    chapter_number = Column(Integer, nullable=True)
    # 优先级
    priority = Column(Integer, nullable=False, default=0)
    # 状态
    status = Column(String(20), nullable=False, default="pending")
    # 所属小说ID
    novel_id = Column(Integer, ForeignKey("novel.id"), nullable=False)
    # 相关人物ID
    character_id = Column(Integer, ForeignKey("character.id"), nullable=True)

    # 关联关系
    novel = relationship("Novel", back_populates="events")
    characters = relationship("Character", back_populates="events")