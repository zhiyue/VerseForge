from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.agent import Agent, AgentTask, AgentInteraction
from app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    TaskCreate,
    TaskUpdate,
    AgentInteractionCreate,
    AgentInteractionUpdate,
)

class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    """
    Agent CRUD操作
    """
    def get_by_type(
        self,
        db: Session,
        *,
        agent_type: str
    ) -> List[Agent]:
        """
        获取指定类型的所有Agent
        """
        return (
            db.query(Agent)
            .filter(Agent.agent_type == agent_type)
            .all()
        )

    def get_available(
        self,
        db: Session,
        *,
        agent_type: str
    ) -> Optional[Agent]:
        """
        获取指定类型的可用Agent
        """
        return (
            db.query(Agent)
            .filter(
                Agent.agent_type == agent_type,
                Agent.status == "idle"
            )
            .first()
        )

    def update_status(
        self,
        db: Session,
        *,
        agent_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> Agent:
        """
        更新Agent状态
        """
        db_obj = self.get(db, id=agent_id)
        if not db_obj:
            return None
            
        update_data = {"status": status}
        if error_message is not None:
            update_data["error_message"] = error_message
            
        return super().update(db, db_obj=db_obj, obj_in=update_data)

class CRUDTask(CRUDBase[AgentTask, TaskCreate, TaskUpdate]):
    """
    任务CRUD操作
    """
    def get_multi_by_novel(
        self,
        db: Session,
        *,
        novel_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentTask]:
        """
        获取指定小说的所有任务
        """
        return (
            db.query(AgentTask)
            .filter(AgentTask.novel_id == novel_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_agent(
        self,
        db: Session,
        *,
        agent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentTask]:
        """
        获取指定Agent的所有任务
        """
        return (
            db.query(AgentTask)
            .filter(AgentTask.agent_id == agent_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_status(
        self,
        db: Session,
        *,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentTask]:
        """
        获取指定状态的所有任务
        """
        return (
            db.query(AgentTask)
            .filter(AgentTask.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_creator(
        self,
        db: Session,
        *,
        creator_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        novel_id: Optional[int] = None
    ) -> List[AgentTask]:
        """
        获取指定创建者的所有任务
        """
        from app.models import Novel
        query = (
            db.query(AgentTask)
            .join(Novel)
            .filter(Novel.creator_id == creator_id)
        )
        
        if status:
            query = query.filter(AgentTask.status == status)
        if novel_id:
            query = query.filter(AgentTask.novel_id == novel_id)
            
        return query.offset(skip).limit(limit).all()

class CRUDAgentInteraction(CRUDBase[AgentInteraction, AgentInteractionCreate, AgentInteractionUpdate]):
    """
    Agent交互CRUD操作
    """
    def get_multi_by_novel(
        self,
        db: Session,
        *,
        novel_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentInteraction]:
        """
        获取指定小说的所有Agent交互
        """
        return (
            db.query(AgentInteraction)
            .filter(AgentInteraction.novel_id == novel_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_agent(
        self,
        db: Session,
        *,
        agent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentInteraction]:
        """
        获取指定Agent的所有交互记录
        """
        return (
            db.query(AgentInteraction)
            .filter(
                (AgentInteraction.sender_id == agent_id) |
                (AgentInteraction.receiver_id == agent_id)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

agent = CRUDAgent(Agent)
task = CRUDTask(AgentTask)
interaction = CRUDAgentInteraction(AgentInteraction)