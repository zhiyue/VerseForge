from typing import Any, Dict, List, Optional
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential

from app.core.config import settings
from .base import (
    BaseModelAdapter,
    ModelResponse,
    ModelError,
    TokenLimitError,
    ModelAPIError,
    ModelTimeoutError,
    ModelRateLimitError,
)

class OpenAIAdapter(BaseModelAdapter):
    """
    OpenAI GPT模型适配器
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gpt-4",
        organization: Optional[str] = None
    ):
        """
        初始化OpenAI客户端
        """
        self.api_key = api_key or settings.AI_MODEL_API_KEY
        self.model_name = model_name
        self.organization = organization
        
        openai.api_key = self.api_key
        if organization:
            openai.organization = organization

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3)
    )
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
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop,
                **kwargs
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return ModelResponse(
                content=content,
                tokens_used=tokens_used,
                model_name=self.model_name,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id,
                }
            )
            
        except openai.error.InvalidRequestError as e:
            if "maximum context length" in str(e):
                raise TokenLimitError(
                    message=str(e),
                    model_name=self.model_name,
                    error_code="token_limit_exceeded",
                    error_type="token_limit"
                )
            raise ModelAPIError(
                message=str(e),
                model_name=self.model_name,
                error_code="invalid_request",
                error_type="api_error"
            )
            
        except openai.error.RateLimitError as e:
            raise ModelRateLimitError(
                message=str(e),
                model_name=self.model_name,
                error_code="rate_limit_exceeded",
                error_type="rate_limit"
            )
            
        except openai.error.Timeout as e:
            raise ModelTimeoutError(
                message=str(e),
                model_name=self.model_name,
                error_code="timeout",
                error_type="timeout"
            )
            
        except openai.error.APIError as e:
            raise ModelAPIError(
                message=str(e),
                model_name=self.model_name,
                error_code="api_error",
                error_type="api_error"
            )

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3)
    )
    async def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本嵌入向量
        """
        try:
            response = await openai.Embedding.acreate(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            raise ModelAPIError(
                message=str(e),
                model_name=self.model_name,
                error_code="embedding_error",
                error_type="api_error"
            )

    async def classify_text(
        self,
        text: str,
        labels: List[str]
    ) -> Dict[str, float]:
        """
        文本分类
        使用few-shot方式进行分类
        """
        prompt = f"""
        请对以下文本进行分类，可能的类别有：{', '.join(labels)}
        
        文本内容：
        {text}
        
        请以JSON格式返回每个类别的概率，概率之和应为1。
        """
        
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.3
        )
        
        try:
            import json
            probabilities = json.loads(response.content)
            return probabilities
        except Exception:
            return {label: 0.0 for label in labels}

    async def analyze_sentiment(
        self,
        text: str
    ) -> Dict[str, float]:
        """
        情感分析
        """
        prompt = """
        请对以下文本进行情感分析，返回积极、消极和中性的概率值。
        
        文本内容：
        {text}
        
        请以JSON格式返回分析结果，包含positive、negative和neutral三个字段，值为0-1之间的浮点数，总和为1。
        """
        
        response = await self.generate_text(
            prompt=prompt.format(text=text),
            temperature=0.3
        )
        
        try:
            import json
            sentiment = json.loads(response.content)
            return sentiment
        except Exception:
            return {
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0
            }

    async def extract_keywords(
        self,
        text: str,
        max_keywords: int = 10
    ) -> List[str]:
        """
        关键词提取
        """
        prompt = f"""
        请从以下文本中提取最多{max_keywords}个关键词，以JSON数组格式返回。
        
        文本内容：
        {text}
        """
        
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.3
        )
        
        try:
            import json
            keywords = json.loads(response.content)
            return keywords[:max_keywords]
        except Exception:
            return []

    async def check_content_safety(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        内容安全检查
        """
        prompt = """
        请对以下内容进行安全检查，检查是否包含：
        1. 暴力内容
        2. 色情内容
        3. 仇恨言论
        4. 歧视内容
        5. 有害信息
        
        文本内容：
        {text}
        
        请以JSON格式返回检查结果，包含is_safe字段和各项具体检查结果。
        """
        
        response = await self.generate_text(
            prompt=prompt.format(text=text),
            temperature=0.3
        )
        
        try:
            import json
            check_result = json.loads(response.content)
            return check_result
        except Exception:
            return {
                "is_safe": False,
                "reason": "检查失败"
            }

    def get_token_count(self, text: str) -> int:
        """
        获取文本的token数量
        使用tiktoken库进行计算
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model_name)
            return len(encoding.encode(text))
        except Exception:
            # 如果无法使用tiktoken，使用简单的估算
            return len(text.split()) * 1.3