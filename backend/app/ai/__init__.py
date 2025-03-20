from .base import (
    BaseModelAdapter,
    ModelResponse,
    ModelError,
    TokenLimitError,
    ContentFilterError,
    ModelAPIError,
    ModelTimeoutError,
    ModelRateLimitError,
    ModelManager,
)
from .openai_adapter import OpenAIAdapter
from .utils import (
    load_prompt_template,
    parse_json_response,
    count_tokens,
    chunk_text,
    validate_prompt_variables,
    sanitize_prompt_input,
    merge_generations,
    extract_constraints,
    rate_content_quality,
)
import prompts

# 创建全局模型管理器实例
model_manager = ModelManager()

# 注册默认的OpenAI模型
def setup_default_models():
    """
    初始化并注册默认的AI模型
    """
    from app.core.config import settings
    
    # 注册GPT-4模型
    gpt4_model = OpenAIAdapter(
        api_key=settings.AI_MODEL_API_KEY,
        model_name="gpt-4",
        organization=settings.OPENAI_ORG_ID
    )
    model_manager.register_model("gpt4", gpt4_model, is_default=True)
    
    # 注册GPT-3.5-Turbo模型
    gpt35_model = OpenAIAdapter(
        api_key=settings.AI_MODEL_API_KEY,
        model_name="gpt-3.5-turbo",
        organization=settings.OPENAI_ORG_ID
    )
    model_manager.register_model("gpt35", gpt35_model)

# 导出所有模块
__all__ = [
    # 基础类和接口
    "BaseModelAdapter",
    "ModelResponse",
    "ModelError",
    "TokenLimitError",
    "ContentFilterError",
    "ModelAPIError",
    "ModelTimeoutError",
    "ModelRateLimitError",
    "ModelManager",
    
    # 模型适配器
    "OpenAIAdapter",
    
    # 工具函数
    "load_prompt_template",
    "parse_json_response",
    "count_tokens",
    "chunk_text",
    "validate_prompt_variables",
    "sanitize_prompt_input",
    "merge_generations",
    "extract_constraints",
    "rate_content_quality",
    
    # 提示模板
    "prompts",
    
    # 全局实例
    "model_manager",
    "setup_default_models",
]

# 异常类型导出
__exceptions__ = [
    "ModelError",
    "TokenLimitError",
    "ContentFilterError",
    "ModelAPIError",
    "ModelTimeoutError",
    "ModelRateLimitError",
]

# 工具函数导出
__utils__ = [
    "load_prompt_template",
    "parse_json_response",
    "count_tokens",
    "chunk_text",
    "validate_prompt_variables",
    "sanitize_prompt_input",
    "merge_generations",
    "extract_constraints",
    "rate_content_quality",
]