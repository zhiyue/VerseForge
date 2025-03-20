from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from app.models import Agent, AgentTask, Novel, AgentType, AgentStatus
from .base import BaseAgent
from . import get_agent_class, validate_task_type

class AgentManager:
    """
    Agent管理器
    负责创建、管理和协调各个Agent的工作
    """

    def __init__(self, db: Session):
        self.db = db
        self._agents: Dict[str, BaseAgent] = {}

    async def initialize_agents(self) -> None:
        """
        初始化所有Agent
        """
        # 获取数据库中的所有Agent记录
        db_agents = self.db.query(Agent).all()
        
        # 为每种类型确保至少有一个Agent实例
        for agent_type in AgentType:
            existing = next(
                (a for a in db_agents if a.agent_type == agent_type),
                None
            )
            
            if not existing:
                # 创建新的Agent记录
                agent = Agent(
                    agent_type=agent_type,
                    name=f"{agent_type.value}_agent",
                    status=AgentStatus.IDLE,
                    parameters={},
                    stats={"tasks_completed": 0}
                )
                self.db.add(agent)
                db_agents.append(agent)

        await self.db.commit()
        
        # 初始化Agent实例
        for db_agent in db_agents:
            agent_class = get_agent_class(db_agent.agent_type.value)
            self._agents[db_agent.id] = agent_class(
                self.db,
                db_agent,
                db_agent.parameters
            )

    async def create_task(
        self,
        agent_type: str,
        task_type: str,
        task_data: Dict[str, Any],
        novel_id: int,
        priority: int = 0
    ) -> AgentTask:
        """
        创建新任务
        """
        # 验证任务类型
        if not validate_task_type(agent_type, task_type):
            raise ValueError(f"Invalid task type {task_type} for agent {agent_type}")

        # 获取空闲的Agent
        agent = await self._get_available_agent(agent_type)
        if not agent:
            raise RuntimeError(f"No available {agent_type} agent")

        # 创建任务
        task = AgentTask(
            agent_id=agent.agent_model.id,
            novel_id=novel_id,
            task_type=task_type,
            task_data=task_data,
            priority=priority,
            status="pending"
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        # 发送任务创建事件
        agent.emit_event(
            "task_created",
            {
                "task_id": task.id,
                "task_type": task_type,
                "novel_id": novel_id
            }
        )

        return task

    async def execute_task(self, task_id: int) -> Dict[str, Any]:
        """
        执行任务
        """
        task = self.db.query(AgentTask).filter(AgentTask.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        agent = self._agents.get(task.agent_id)
        if not agent:
            raise ValueError(f"Agent {task.agent_id} not found")

        try:
            # 更新Agent状态
            await agent.update_status(AgentStatus.WORKING)

            # 验证任务
            if not await agent.validate_task(task):
                raise ValueError("Task validation failed")

            # 处理任务
            result = await agent.process_task(task)

            # 更新任务状态
            task.status = "completed"
            task.result = result
            
            # 更新Agent状态和统计信息
            await agent.update_status(AgentStatus.IDLE)
            await agent.update_stats({
                "tasks_completed": agent.agent_model.stats.get("tasks_completed", 0) + 1
            })

            await self.db.commit()
            return result

        except Exception as e:
            # 错误处理
            task.status = "failed"
            task.error_message = str(e)
            await agent.update_status(AgentStatus.ERROR)
            await agent.log_error(str(e))
            await self.db.commit()
            raise

    async def _get_available_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """
        获取可用的Agent实例
        """
        for agent in self._agents.values():
            if (
                agent.agent_model.agent_type.value == agent_type
                and agent.agent_model.status == AgentStatus.IDLE
            ):
                return agent
        return None

    async def get_agent_status(self, agent_id: int) -> Dict[str, Any]:
        """
        获取Agent状态信息
        """
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        return {
            "id": agent.agent_model.id,
            "type": agent.agent_model.agent_type.value,
            "status": agent.agent_model.status.value,
            "stats": agent.agent_model.stats,
            "error": agent.agent_model.error_message
        }

    async def reset_agent(self, agent_id: int) -> None:
        """
        重置Agent状态
        """
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        await agent.update_status(AgentStatus.IDLE)
        agent.agent_model.error_message = None
        await self.db.commit()