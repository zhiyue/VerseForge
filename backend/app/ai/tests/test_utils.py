import pytest
from unittest.mock import patch
import json

from app.ai.utils import (
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

def test_load_prompt_template():
    """
    测试提示模板加载
    """
    template = "你好，{name}！"
    result = load_prompt_template(template, name="测试")
    assert result == "你好，测试！"
    
    # 测试缺少变量
    with pytest.raises(KeyError):
        load_prompt_template(template)

def test_parse_json_response():
    """
    测试JSON响应解析
    """
    # 测试有效JSON
    valid_json = '{"key": "value"}'
    result = parse_json_response(valid_json)
    assert result == {"key": "value"}
    
    # 测试无效JSON
    invalid_json = 'not a json'
    result = parse_json_response(invalid_json)
    assert "error" in result
    
    # 测试嵌入JSON
    embedded_json = 'Some text {"key": "value"} more text'
    result = parse_json_response(embedded_json)
    assert result == {"key": "value"}

@pytest.mark.parametrize("text,expected_count", [
    ("这是一个测试", 4),
    ("Hello World", 2),
    ("", 0),
])
def test_count_tokens(text, expected_count):
    """
    测试Token计数
    """
    # 模拟tiktoken
    with patch('tiktoken.encoding_for_model') as mock_encoding:
        mock_encoding.return_value.encode.return_value = [0] * expected_count
        count = count_tokens(text)
        assert count == expected_count

def test_chunk_text():
    """
    测试文本分块
    """
    text = "这是第一句。这是第二句。这是第三句。"
    max_tokens = 10
    overlap = 2
    
    # 模拟tiktoken
    with patch('tiktoken.encoding_for_model') as mock_encoding:
        mock_encoding.return_value.encode.return_value = list(range(15))
        mock_encoding.return_value.decode.side_effect = lambda x: "".join(str(i) for i in x)
        
        chunks = chunk_text(text, max_tokens, overlap)
        
        assert len(chunks) > 0
        assert isinstance(chunks[0], str)

def test_validate_prompt_variables():
    """
    测试提示模板变量验证
    """
    template = "Hello {name}, welcome to {place}!"
    variables = {"name": "test"}
    
    missing = validate_prompt_variables(template, variables)
    assert "place" in missing
    assert "name" not in missing
    
    # 测试完整变量
    variables["place"] = "here"
    missing = validate_prompt_variables(template, variables)
    assert len(missing) == 0

def test_sanitize_prompt_input():
    """
    测试提示输入清理
    """
    # 测试特殊字符移除
    input_text = "Hello {name}!"
    cleaned = sanitize_prompt_input(input_text)
    assert "{" not in cleaned
    assert "}" not in cleaned
    
    # 测试长度限制
    long_text = "a" * 10000
    cleaned = sanitize_prompt_input(long_text)
    assert len(cleaned) < 10000
    assert cleaned.endswith("...")

def test_merge_generations():
    """
    测试生成结果合并
    """
    generations = ["第一段", "第二段", "第三段"]
    
    # 测试concat模式
    result = merge_generations(generations, mode="concat")
    assert isinstance(result, str)
    assert "第一段" in result
    assert "第二段" in result
    
    # 测试first模式
    result = merge_generations(generations, mode="first")
    assert result == "第一段"
    
    # 测试longest模式
    result = merge_generations(["short", "longest text", "medium"], mode="longest")
    assert result == "longest text"

def test_extract_constraints():
    """
    测试约束条件提取
    """
    prompt = """
    字数要求：1000-2000
    风格要求：轻松幽默
    语气要求：温和
    格式要求：分段落
    """
    
    constraints = extract_constraints(prompt)
    
    assert constraints["min_length"] == 1000
    assert constraints["max_length"] == 2000
    assert constraints["style"] == "轻松幽默"
    assert constraints["tone"] == "温和"
    assert constraints["format"] == "分段落"

def test_rate_content_quality():
    """
    测试内容质量评估
    """
    content = "这是一段测试文本。"
    
    # 使用默认权重
    result = rate_content_quality(content)
    assert isinstance(result, dict)
    assert "scores" in result
    assert "weighted_score" in result
    
    # 使用自定义权重
    criteria = {
        "coherence": 0.5,
        "creativity": 0.5
    }
    result = rate_content_quality(content, criteria)
    assert set(result["scores"].keys()) == set(criteria.keys())
    assert 0 <= result["weighted_score"] <= 1