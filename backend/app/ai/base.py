from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class ModelResponse:
    """
    模型响应封装类
    """
    def __init__(
        self,
        content: str,
        tokens_used: int,
        model_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.tokens_used = tokens_used
        self.model_name = model_name
        self.metadata = metadata or {}

class BaseModelAdapter(ABC):
    """
    AI模型适配器基类
    定义了所有模型适配器必须实现的接口
    """

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stop: Optional[List[str]] = None,
        **kwargs: Any
    ) -> ModelResponse:
        """
        生成文本
        """
        pass

    @abstractmethod
    async def generate_embedding(
        self,
        text: str
    ) -> List[float]:
        """
        生成文本嵌入向量
        """
        pass

    @abstractmethod
    async def classify_text(
        self,
        text: str,
        labels: List[str]
    ) -> Dict[str, float]:
        """
        文本分类
        返回每个标签的概率
        """
        pass

    @abstractmethod
    async def analyze_sentiment(
        self,
        text: str
    ) -> Dict[str, float]:
        """
        情感分析
        """
        pass

    @abstractmethod
    async def extract_keywords(
        self,
        text: str,
        max_keywords: int = 10
    ) -> List[str]:
        """
        关键词提取
        """
        pass

    @abstractmethod
    async def check_content_safety(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        内容安全检查
        """
        pass

    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        获取文本的token数量
        """
        pass

class ModelError(Exception):
    """
    模型错误基类
    """
    def __init__(
        self,
        message: str,
        model_name: str,
        error_code: str,
        error_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.model_name = model_name
        self.error_code = error_code
        self.error_type = error_type
        self.metadata = metadata or {}
        super().__init__(self.message)

class TokenLimitError(ModelError):
    """
    Token数量超限错误
    """
    pass

class ContentFilterError(ModelError):
    """
    内容过滤错误
    """
    pass

class ModelAPIError(ModelError):
    """
    模型API调用错误
    """
    pass

class ModelTimeoutError(ModelError):
    """
    模型调用超时错误
    """
    pass

class ModelRateLimitError(ModelError):
    """
    模型调用频率限制错误
    """
    pass

class ModelManager:
    """
    模型管理器
    负责模型的初始化、切换和负载均衡
    """
    
    def __init__(self):
        self._models: Dict[str, BaseModelAdapter] = {}
        self._default_model: Optional[str] = None

    def register_model(
        self,
        name: str,
        model: BaseModelAdapter,
        is_default: bool = False
    ) -> None:
        """
        注册模型
        """
        self._models[name] = model
        if is_default or self._default_model is None:
            self._default_model = name

    def get_model(
        self,
        name: Optional[str] = None
    ) -> BaseModelAdapter:
        """
        获取模型实例
        """
        model_name = name or self._default_model
        if model_name not in self._models:
            raise ValueError(f"Model {model_name} not found")
        return self._models[model_name]

    def list_models(self) -> List[str]:
        """
        获取所有可用模型列表
        """
        return list(self._models.keys())

    def get_default_model(self) -> str:
        """
        获取默认模型名称
        """
        if self._default_model is None:
            raise ValueError("No default model set")
        return self._default_model

    def set_default_model(self, name: str) -> None:
        """
        设置默认模型
        """
        if name not in self._models:
            raise ValueError(f"Model {name} not found")
        self._default_model = name