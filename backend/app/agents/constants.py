from typing import Dict, Any

# Agent状态常量
AGENT_STATUS = {
    "IDLE": "idle",
    "WORKING": "working",
    "PAUSED": "paused",
    "ERROR": "error"
}

# Agent类型常量
AGENT_TYPES = {
    "PLOT": "plot",
    "CHARACTER": "character",
    "SCENE": "scene",
    "WRITING": "writing",
    "QA": "qa",
    "COHERENCE": "coherence"
}

# 任务状态常量
TASK_STATUS = {
    "PENDING": "pending",
    "PROCESSING": "processing",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "CANCELLED": "cancelled"
}

# 任务优先级范围
PRIORITY_RANGES = {
    "LOW": (0, 30),
    "MEDIUM": (31, 70),
    "HIGH": (71, 100)
}

# Agent默认配置
DEFAULT_AGENT_CONFIG: Dict[str, Any] = {
    "max_retries": 3,
    "timeout": 300,  # 5分钟
    "batch_size": 1000,
    "concurrent_tasks": 5
}

# AI模型参数配置
MODEL_PARAMS = {
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

# 文本生成参数
TEXT_GENERATION_PARAMS = {
    "min_words_per_chapter": 1000,
    "max_words_per_chapter": 5000,
    "target_chapter_count": 50
}

# 质量控制阈值
QUALITY_THRESHOLDS = {
    "min_coherence_score": 0.7,
    "min_engagement_score": 0.6,
    "min_grammar_score": 0.8,
    "min_plot_consistency": 0.75
}

# 事件类型
EVENT_TYPES = {
    # 故事进度事件
    "PLOT_PROGRESS": {
        "OUTLINE_GENERATED": "outline_generated",
        "PLOT_UPDATED": "plot_updated",
        "MILESTONE_REACHED": "milestone_reached"
    },
    # 人物事件
    "CHARACTER_EVENTS": {
        "CHARACTER_CREATED": "character_created",
        "CHARACTER_EVOLVED": "character_evolved",
        "INTERACTION_GENERATED": "interaction_generated"
    },
    # 场景事件
    "SCENE_EVENTS": {
        "SCENE_GENERATED": "scene_generated",
        "SCENE_UPDATED": "scene_updated",
        "TRANSITION_CREATED": "transition_created"
    },
    # 写作事件
    "WRITING_EVENTS": {
        "CONTENT_GENERATED": "content_generated",
        "TEXT_POLISHED": "text_polished",
        "STYLE_ADJUSTED": "style_adjusted"
    },
    # 质量控制事件
    "QA_EVENTS": {
        "QUALITY_CHECKED": "quality_checked",
        "CONSISTENCY_VERIFIED": "consistency_verified",
        "REVIEW_COMPLETED": "review_completed"
    },
    # 连贯性事件
    "COHERENCE_EVENTS": {
        "COHERENCE_ANALYZED": "coherence_analyzed",
        "ELEMENTS_TRACKED": "elements_tracked",
        "ADJUSTMENT_SUGGESTED": "adjustment_suggested"
    }
}

# 错误代码
ERROR_CODES = {
    "AGENT_ERROR": {
        "INITIALIZATION_FAILED": "AE001",
        "VALIDATION_FAILED": "AE002",
        "TASK_FAILED": "AE003",
        "NOT_FOUND": "AE004",
        "BUSY": "AE005"
    },
    "TASK_ERROR": {
        "VALIDATION_FAILED": "TE001",
        "EXECUTION_FAILED": "TE002",
        "NOT_FOUND": "TE003",
        "INVALID_TYPE": "TE004"
    },
    "SYSTEM_ERROR": {
        "DATABASE_ERROR": "SE001",
        "API_ERROR": "SE002",
        "RESOURCE_EXHAUSTED": "SE003",
        "COMMUNICATION_ERROR": "SE004"
    }
}

# 系统限制
SYSTEM_LIMITS = {
    "max_concurrent_novels": 5,
    "max_chapters_per_novel": 1000,
    "max_words_per_chapter": 5000,
    "max_characters_per_novel": 100,
    "max_events_per_chapter": 50
}