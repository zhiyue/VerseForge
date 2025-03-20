import pytest
from unittest.mock import Mock, patch
import openai

from app.ai import OpenAIAdapter, ModelResponse, TokenLimitError, ModelAPIError

@pytest.fixture
def mock_openai():
    with patch('openai.ChatCompletion') as mock_chat:
        yield mock_chat

@pytest.fixture
def adapter():
    return OpenAIAdapter(
        api_key="test-key",
        model_name="gpt-4"
    )

async def test_generate_text_success(mock_openai, adapter):
    """
    测试成功生成文本
    """
    # 模拟响应
    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(content="测试响应"),
            finish_reason="stop"
        )
    ]
    mock_response.usage = Mock(total_tokens=10)
    mock_response.id = "test-id"
    
    mock_openai.acreate.return_value = mock_response
    
    # 执行生成
    response = await adapter.generate_text("测试提示")
    
    # 验证结果
    assert isinstance(response, ModelResponse)
    assert response.content == "测试响应"
    assert response.tokens_used == 10
    assert response.model_name == "gpt-4"
    assert response.metadata["response_id"] == "test-id"

async def test_generate_text_token_limit(mock_openai, adapter):
    """
    测试Token限制错误
    """
    # 模拟Token限制错误
    error_msg = "maximum context length"
    mock_openai.acreate.side_effect = openai.error.InvalidRequestError(error_msg, "prompt")
    
    # 验证异常
    with pytest.raises(TokenLimitError) as exc_info:
        await adapter.generate_text("测试提示")
    
    assert str(exc_info.value) == error_msg

async def test_generate_text_api_error(mock_openai, adapter):
    """
    测试API错误
    """
    # 模拟API错误
    error_msg = "API error"
    mock_openai.acreate.side_effect = openai.error.APIError(error_msg)
    
    # 验证异常
    with pytest.raises(ModelAPIError) as exc_info:
        await adapter.generate_text("测试提示")
    
    assert str(exc_info.value) == error_msg

@pytest.mark.parametrize("text,labels,expected", [
    (
        "这是一个测试文本",
        ["积极", "消极"],
        {"积极": 0.7, "消极": 0.3}
    ),
])
async def test_classify_text(adapter, text, labels, expected):
    """
    测试文本分类
    """
    # 模拟生成响应
    mock_response = ModelResponse(
        content=str(expected),
        tokens_used=10,
        model_name="gpt-4"
    )
    
    # 替换generate_text方法
    adapter.generate_text = Mock(return_value=mock_response)
    
    # 执行分类
    result = await adapter.classify_text(text, labels)
    
    # 验证结果
    assert isinstance(result, dict)
    assert set(result.keys()) == set(labels)

async def test_generate_embedding(adapter):
    """
    测试生成文本嵌入向量
    """
    # 模拟Embedding响应
    mock_embedding = [0.1, 0.2, 0.3]
    with patch('openai.Embedding.acreate') as mock_create:
        mock_create.return_value = Mock(
            data=[Mock(embedding=mock_embedding)]
        )
        
        # 执行生成
        embedding = await adapter.generate_embedding("测试文本")
        
        # 验证结果
        assert isinstance(embedding, list)
        assert len(embedding) == len(mock_embedding)
        assert embedding == mock_embedding

async def test_analyze_sentiment(adapter):
    """
    测试情感分析
    """
    # 模拟响应
    mock_sentiment = {
        "positive": 0.6,
        "negative": 0.2,
        "neutral": 0.2
    }
    adapter.generate_text = Mock(return_value=ModelResponse(
        content=str(mock_sentiment),
        tokens_used=10,
        model_name="gpt-4"
    ))
    
    # 执行分析
    sentiment = await adapter.analyze_sentiment("这是一个测试文本")
    
    # 验证结果
    assert isinstance(sentiment, dict)
    assert set(sentiment.keys()) >= {"positive", "negative", "neutral"}
    assert sum(sentiment.values()) == pytest.approx(1.0)

async def test_check_content_safety(adapter):
    """
    测试内容安全检查
    """
    # 模拟响应
    mock_result = {
        "is_safe": True,
        "issues": []
    }
    adapter.generate_text = Mock(return_value=ModelResponse(
        content=str(mock_result),
        tokens_used=10,
        model_name="gpt-4"
    ))
    
    # 执行检查
    result = await adapter.check_content_safety("这是一个测试文本")
    
    # 验证结果
    assert isinstance(result, dict)
    assert "is_safe" in result

def test_get_token_count(adapter):
    """
    测试Token计数
    """
    text = "这是一个测试文本"
    count = adapter.get_token_count(text)
    assert isinstance(count, (int, float))
    assert count > 0