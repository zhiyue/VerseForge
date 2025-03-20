from typing import Any, Dict
from sqlalchemy.orm import Session

from app.models import Novel, Chapter, AgentTask, AgentType
from .base import BaseAgent

class PlotAgent(BaseAgent):
    """
    故事大纲规划Agent
    负责生成和管理小说的整体故事架构、主要情节线和故事发展规划
    """
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        处理故事大纲相关任务
        """
        task_type = task.task_type
        task_data = task.task_data
        
        if task_type == "generate_outline":
            return await self._generate_outline(task_data)
        elif task_type == "update_plot_thread":
            return await self._update_plot_thread(task_data)
        elif task_type == "check_plot_consistency":
            return await self._check_plot_consistency(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def validate_task(self, task: AgentTask) -> bool:
        """
        验证任务参数是否合法
        """
        required_fields = {
            "generate_outline": ["novel_id", "genre", "target_length"],
            "update_plot_thread": ["novel_id", "chapter_id", "changes"],
            "check_plot_consistency": ["novel_id", "chapter_range"],
        }
        
        if task.task_type not in required_fields:
            return False
            
        required = required_fields[task.task_type]
        return all(field in task.task_data for field in required)

    async def _generate_outline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成故事大纲
        包括：主要情节线、转折点、高潮和结局
        """
        novel_id = data["novel_id"]
        novel = self.db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            raise ValueError(f"Novel {novel_id} not found")

        # TODO: 调用AI模型生成大纲
        outline = {
            "main_plot": "主要情节线...",
            "subplots": [
                {"name": "支线1", "description": "..."},
                {"name": "支线2", "description": "..."}
            ],
            "turning_points": [
                {"chapter": 1, "event": "事件1"},
                {"chapter": 2, "event": "事件2"}
            ],
            "climax": {"chapter": 10, "description": "高潮..."},
            "ending": {"type": "结局类型", "description": "结局描述..."}
        }

        # 更新小说大纲
        novel.outline = outline
        self.db.add(novel)
        await self.db.commit()
        await self.db.refresh(novel)

        # 发送大纲生成事件
        self.emit_event(
            "outline_generated",
            {
                "novel_id": novel_id,
                "outline": outline
            }
        )

        return outline

    async def _update_plot_thread(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新情节线
        在故事发展过程中动态调整和优化情节发展
        """
        novel_id = data["novel_id"]
        chapter_id = data["chapter_id"]
        changes = data["changes"]

        chapter = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        # TODO: 调用AI模型分析变更对情节的影响并生成调整建议
        analysis = {
            "impact": "变更影响分析...",
            "suggestions": ["建议1", "建议2"],
            "risk_level": "low"
        }

        # 发送情节更新事件
        self.emit_event(
            "plot_thread_updated",
            {
                "novel_id": novel_id,
                "chapter_id": chapter_id,
                "changes": changes,
                "analysis": analysis
            }
        )

        return analysis

    async def _check_plot_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查情节一致性
        确保故事发展的连贯性和合理性
        """
        novel_id = data["novel_id"]
        chapter_range = data["chapter_range"]

        # 获取指定范围的章节
        chapters = self.db.query(Chapter).filter(
            Chapter.novel_id == novel_id,
            Chapter.chapter_number.between(chapter_range[0], chapter_range[1])
        ).all()

        # TODO: 调用AI模型检查情节一致性
        consistency_check = {
            "is_consistent": True,
            "issues": [],
            "suggestions": []
        }

        # 发送一致性检查事件
        self.emit_event(
            "plot_consistency_checked",
            {
                "novel_id": novel_id,
                "chapter_range": chapter_range,
                "result": consistency_check
            }
        )

        return consistency_check

    @staticmethod
    def get_agent_type() -> AgentType:
        """
        获取Agent类型
        """
        return AgentType.PLOT