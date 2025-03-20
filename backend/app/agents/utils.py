from typing import Dict, Any, List
import json
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

def format_agent_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化Agent的响应数据
    """
    return {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "data": response
    }

def validate_task_data(task_data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    验证任务数据是否包含所需字段
    """
    return all(field in task_data for field in required_fields)

def calculate_task_priority(
    task_type: str,
    novel_progress: float,
    task_data: Dict[str, Any]
) -> int:
    """
    计算任务优先级
    基于任务类型、小说进度和任务数据计算优先级
    """
    base_priority = {
        "plot": 100,
        "character": 80,
        "scene": 60,
        "writing": 40,
        "qa": 20,
        "coherence": 10
    }.get(task_type, 0)

    # 根据小说进度调整优先级
    progress_factor = 1 + (novel_progress * 0.5)
    
    # 根据任务数据中的紧急程度调整
    urgency = task_data.get("urgency", 1)
    
    return int(base_priority * progress_factor * urgency)

def chunk_text(text: str, chunk_size: int = 2000) -> List[str]:
    """
    将长文本分割成小块以适应模型输入限制
    """
    if not text:
        return []
        
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in text.split():
        word_size = len(word)
        if current_size + word_size + 1 > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size + 1
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def merge_agent_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    合并多个Agent的处理结果
    """
    merged = {
        "content": "",
        "metadata": {
            "sources": [],
            "timestamps": [],
            "metrics": {}
        }
    }
    
    for result in results:
        # 合并内容
        if "content" in result:
            merged["content"] += result["content"] + "\n"
            
        # 合并元数据
        if "metadata" in result:
            merged["metadata"]["sources"].extend(
                result["metadata"].get("sources", [])
            )
            merged["metadata"]["timestamps"].append(
                result["metadata"].get("timestamp", datetime.utcnow().isoformat())
            )
            
            # 合并指标
            for metric, value in result["metadata"].get("metrics", {}).items():
                if metric in merged["metadata"]["metrics"]:
                    if isinstance(value, (int, float)):
                        # 数值类型取平均值
                        merged["metadata"]["metrics"][metric] = (
                            merged["metadata"]["metrics"][metric] + value
                        ) / 2
                    else:
                        # 其他类型保留最新值
                        merged["metadata"]["metrics"][metric] = value
                else:
                    merged["metadata"]["metrics"][metric] = value
                    
    return merged

def sanitize_agent_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    清理和验证Agent输入数据
    """
    sanitized = {}
    
    for key, value in data.items():
        # 移除空值
        if value is None:
            continue
            
        # 转换特殊类型
        if isinstance(value, datetime):
            sanitized[key] = value.isoformat()
        elif isinstance(value, (list, dict)):
            sanitized[key] = json.dumps(value)
        else:
            sanitized[key] = str(value)
            
    return sanitized

def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    格式化错误响应
    """
    return {
        "status": "error",
        "timestamp": datetime.utcnow().isoformat(),
        "error": {
            "type": error.__class__.__name__,
            "message": str(error),
            "details": getattr(error, "details", None)
        }
    }

def log_agent_activity(
    agent_type: str,
    action: str,
    status: str,
    details: Dict[str, Any]
) -> None:
    """
    记录Agent活动日志
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent_type": agent_type,
        "action": action,
        "status": status,
        "details": details
    }
    
    logger.info(f"Agent activity: {json.dumps(log_entry)}")