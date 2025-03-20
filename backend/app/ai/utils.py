from typing import List, Dict, Any, Optional
import json
import tiktoken
from app.core.config import settings

def load_prompt_template(template: str, **kwargs: Any) -> str:
    """
    加载并格式化提示模板
    """
    return template.format(**kwargs)

def parse_json_response(response: str) -> Dict[str, Any]:
    """
    解析模型返回的JSON响应
    处理各种可能的格式问题
    """
    try:
        # 尝试直接解析
        return json.loads(response)
    except json.JSONDecodeError:
        try:
            # 尝试提取JSON部分
            import re
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"error": "无法解析JSON响应"}
        except Exception:
            return {"error": "响应格式错误"}

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    计算文本的token数量
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # 如果无法使用tiktoken，使用简单的估算
        return len(text.split()) * 1.3

def chunk_text(
    text: str,
    max_tokens: int = 2000,
    overlap: int = 200,
    model: str = "gpt-4"
) -> List[str]:
    """
    将长文本分割成小块，保持上下文重叠
    """
    chunks = []
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        if end >= len(tokens):
            chunks.append(encoding.decode(tokens[start:]))
            break
            
        # 在重叠区域内找到合适的分割点
        split_point = end - overlap
        while split_point < end:
            if tokens[split_point] in {encoding.encode(".")[0], encoding.encode("。")[0]}:
                break
            split_point += 1
                
        chunks.append(encoding.decode(tokens[start:split_point]))
        start = split_point
        
    return chunks

def validate_prompt_variables(template: str, variables: Dict[str, Any]) -> List[str]:
    """
    验证提示模板变量是否完整
    返回缺失的变量列表
    """
    import re
    required_vars = set(re.findall(r'\{(\w+)\}', template))
    provided_vars = set(variables.keys())
    return list(required_vars - provided_vars)

def sanitize_prompt_input(text: str) -> str:
    """
    清理和验证提示输入
    """
    # 移除可能导致注入的特殊字符
    text = text.replace("{", "").replace("}", "")
    # 限制长度
    max_length = 8000
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def merge_generations(responses: List[str], mode: str = "concat") -> str:
    """
    合并多个生成结果
    """
    if mode == "concat":
        return "\n".join(responses)
    elif mode == "first":
        return responses[0] if responses else ""
    elif mode == "longest":
        return max(responses, key=len) if responses else ""
    elif mode == "shortest":
        return min(responses, key=len) if responses else ""
    else:
        return responses[0] if responses else ""

def extract_constraints(prompt: str) -> Dict[str, Any]:
    """
    从提示中提取约束条件
    """
    constraints = {
        "min_length": None,
        "max_length": None,
        "style": None,
        "tone": None,
        "format": None,
    }
    
    # 提取字数限制
    import re
    length_pattern = r'字数[要求限制][:：]?\s*(\d+)[-~](\d+)'
    length_match = re.search(length_pattern, prompt)
    if length_match:
        constraints["min_length"] = int(length_match.group(1))
        constraints["max_length"] = int(length_match.group(2))
    
    # 提取风格要求
    style_pattern = r'风格[要求限制][:：]?\s*([^\n]+)'
    style_match = re.search(style_pattern, prompt)
    if style_match:
        constraints["style"] = style_match.group(1).strip()
    
    # 提取语气要求
    tone_pattern = r'语气[要求限制][:：]?\s*([^\n]+)'
    tone_match = re.search(tone_pattern, prompt)
    if tone_match:
        constraints["tone"] = tone_match.group(1).strip()
    
    # 提取格式要求
    format_pattern = r'格式[要求限制][:：]?\s*([^\n]+)'
    format_match = re.search(format_pattern, prompt)
    if format_match:
        constraints["format"] = format_match.group(1).strip()
    
    return constraints

def rate_content_quality(
    content: str,
    criteria: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    评估生成内容的质量
    """
    if criteria is None:
        criteria = {
            "coherence": 1.0,  # 连贯性权重
            "creativity": 0.8,  # 创造性权重
            "relevance": 1.0,  # 相关性权重
            "grammar": 0.9,    # 语法权重
        }
    
    # 简单实现，后续可以接入更复杂的评估模型
    scores = {}
    for criterion, weight in criteria.items():
        # 临时使用随机分数，实际应该使用具体的评估方法
        import random
        scores[criterion] = random.uniform(0.7, 1.0) * weight
    
    # 计算加权平均分
    total_weight = sum(criteria.values())
    weighted_score = sum(scores.values()) / total_weight
    
    return {
        "scores": scores,
        "weighted_score": weighted_score
    }