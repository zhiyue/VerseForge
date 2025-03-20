from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app.models import Novel, Chapter, Character, AgentTask, AgentType, Event
from .base import BaseAgent

class SceneAgent(BaseAgent):
    """
    剧情生成Agent
    负责规划和生成具体场景，包括环境描写、氛围营造和情节推进
    """
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        处理场景相关任务
        """
        task_type = task.task_type
        task_data = task.task_data
        
        if task_type == "generate_scene":
            return await self._generate_scene(task_data)
        elif task_type == "update_scene":
            return await self._update_scene(task_data)
        elif task_type == "check_scene_coherence":
            return await self._check_scene_coherence(task_data)
        elif task_type == "generate_transition":
            return await self._generate_transition(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def validate_task(self, task: AgentTask) -> bool:
        """
        验证任务参数是否合法
        """
        required_fields = {
            "generate_scene": ["chapter_id", "scene_type", "characters"],
            "update_scene": ["chapter_id", "scene_id", "changes"],
            "check_scene_coherence": ["chapter_id", "scene_range"],
            "generate_transition": ["from_scene_id", "to_scene_id"],
        }
        
        if task.task_type not in required_fields:
            return False
            
        required = required_fields[task.task_type]
        return all(field in task.task_data for field in required)

    async def _generate_scene(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成场景
        创建完整的场景描写，包括环境、氛围和人物互动
        """
        chapter_id = data["chapter_id"]
        scene_type = data["scene_type"]
        character_ids = data["characters"]

        chapter = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        characters = self.db.query(Character).filter(
            Character.id.in_(character_ids)
        ).all()

        # TODO: 调用AI模型生成场景
        scene = {
            "setting": {
                "location": "场景地点",
                "time": "时间",
                "weather": "天气",
                "atmosphere": "氛围描写"
            },
            "description": "环境描写...",
            "character_positions": [
                {"character_id": id, "position": "位置描述"}
                for id in character_ids
            ],
            "events": [
                {"type": "事件类型", "description": "事件描写"}
            ],
            "sensory_details": {
                "visual": ["视觉细节1", "视觉细节2"],
                "auditory": ["听觉细节1", "听觉细节2"],
                "other": ["其他感官细节"]
            }
        }

        # 创建场景事件
        event = Event(
            novel_id=chapter.novel_id,
            event_type="scene",
            description=scene["description"],
            chapter_number=chapter.chapter_number,
            status="active"
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        # 发送场景生成事件
        self.emit_event(
            "scene_generated",
            {
                "chapter_id": chapter_id,
                "scene": scene,
                "event_id": event.id
            }
        )

        return scene

    async def _update_scene(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新场景
        根据情节发展调整场景内容
        """
        chapter_id = data["chapter_id"]
        scene_id = data["scene_id"]
        changes = data["changes"]

        event = self.db.query(Event).filter(Event.id == scene_id).first()
        if not event:
            raise ValueError(f"Scene event {scene_id} not found")

        # TODO: 调用AI模型更新场景
        update = {
            "modified_elements": ["元素1", "元素2"],
            "new_content": "更新后的内容...",
            "impact_analysis": {
                "plot_impact": "对情节的影响",
                "character_impact": "对人物的影响",
                "atmosphere_change": "氛围变化"
            }
        }

        # 更新场景事件
        event.description = update["new_content"]
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        # 发送场景更新事件
        self.emit_event(
            "scene_updated",
            {
                "chapter_id": chapter_id,
                "scene_id": scene_id,
                "changes": changes,
                "update": update
            }
        )

        return update

    async def _check_scene_coherence(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查场景连贯性
        确保场景之间的过渡自然，整体流畅
        """
        chapter_id = data["chapter_id"]
        scene_range = data["scene_range"]

        events = self.db.query(Event).filter(
            Event.chapter_number == chapter_id,
            Event.event_type == "scene"
        ).all()

        # TODO: 调用AI模型检查场景连贯性
        coherence_check = {
            "is_coherent": True,
            "transitions": [
                {"from_scene": "场景1", "to_scene": "场景2", "quality": "自然"}
            ],
            "pacing": {
                "rating": 8,
                "issues": [],
                "suggestions": []
            },
            "atmosphere_consistency": {
                "rating": 9,
                "variations": []
            }
        }

        # 发送连贯性检查事件
        self.emit_event(
            "scene_coherence_checked",
            {
                "chapter_id": chapter_id,
                "scene_range": scene_range,
                "result": coherence_check
            }
        )

        return coherence_check

    async def _generate_transition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成场景转换
        创建自然流畅的场景转换描写
        """
        from_scene_id = data["from_scene_id"]
        to_scene_id = data["to_scene_id"]

        from_scene = self.db.query(Event).filter(Event.id == from_scene_id).first()
        to_scene = self.db.query(Event).filter(Event.id == to_scene_id).first()

        if not from_scene or not to_scene:
            raise ValueError("Scene not found")

        # TODO: 调用AI模型生成场景转换
        transition = {
            "content": "转场描写...",
            "type": "转场类型",
            "duration": "时间跨度",
            "connecting_elements": ["连接元素1", "连接元素2"],
            "mood_transition": {
                "from_mood": "起始氛围",
                "to_mood": "目标氛围",
                "transition_style": "过渡方式"
            }
        }

        # 发送场景转换事件
        self.emit_event(
            "scene_transition_generated",
            {
                "from_scene_id": from_scene_id,
                "to_scene_id": to_scene_id,
                "transition": transition
            }
        )

        return transition

    @staticmethod
    def get_agent_type() -> AgentType:
        """
        获取Agent类型
        """
        return AgentType.SCENE