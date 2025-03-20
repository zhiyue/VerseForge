# AI模型集成模块

本模块提供了AI模型的集成和管理功能，支持多种模型后端，并提供统一的接口进行访问。

## 主要功能

1. 模型抽象层
   - BaseModelAdapter：模型适配器基类
   - ModelManager：模型管理器
   - 统一的错误处理机制

2. 模型实现
   - OpenAI GPT模型适配器
   - 支持扩展其他模型

3. 提示模板管理
   - 预定义的提示模板
   - 模板变量管理
   - 模板验证

4. 工具函数
   - Token计数
   - 文本分块
   - JSON响应解析
   - 内容质量评估

## 使用方法

### 1. 初始化模型

```python
from app.ai import model_manager, OpenAIAdapter

# 注册模型实例
model = OpenAIAdapter(
    api_key="your-api-key",
    model_name="gpt-4"
)
model_manager.register_model("gpt4", model, is_default=True)
```

### 2. 生成文本

```python
# 获取模型实例
model = model_manager.get_model()

# 生成文本
response = await model.generate_text(
    prompt="你的提示文本",
    max_tokens=1000,
    temperature=0.7
)

print(response.content)
```

### 3. 使用提示模板

```python
from app.ai import prompts, load_prompt_template

# 加载并格式化模板
prompt = load_prompt_template(
    prompts.OUTLINE_PROMPT,
    genre="奇幻",
    target_words=50000
)

# 使用模板生成内容
response = await model.generate_text(prompt)
```

### 4. 工具函数使用

```python
from app.ai.utils import (
    count_tokens,
    chunk_text,
    parse_json_response
)

# 计算token数量
tokens = count_tokens("你的文本")

# 分割长文本
chunks = chunk_text("很长的文本", max_tokens=2000)

# 解析JSON响应
result = parse_json_response(response.content)
```

## 错误处理

```python
from app.ai import ModelError, TokenLimitError

try:
    response = await model.generate_text(prompt)
except TokenLimitError as e:
    print(f"Token数量超限：{e}")
except ModelError as e:
    print(f"模型错误：{e}")
```

## 自定义模型适配器

要添加新的模型支持，需要：

1. 继承BaseModelAdapter类
2. 实现所有抽象方法
3. 注册新的模型实例

```python
from app.ai import BaseModelAdapter

class CustomModelAdapter(BaseModelAdapter):
    async def generate_text(self, prompt: str, **kwargs):
        # 实现文本生成逻辑
        pass
    
    async def generate_embedding(self, text: str):
        # 实现文本嵌入逻辑
        pass
    
    # ... 实现其他抽象方法
```

## 配置说明

在 `.env` 文件中配置：

```env
AI_MODEL_API_KEY=your-api-key
AI_MODEL_MAX_TOKENS=2048
AI_MODEL_TEMPERATURE=0.7
```

## 性能优化

1. 使用异步API调用
2. 实现请求重试机制
3. 文本分块处理
4. 结果缓存（可选）

## 注意事项

1. 妥善保管API密钥
2. 注意Token使用限制
3. 处理模型响应超时
4. 实现请求限流
5. 定期检查模型状态

## TODO

- [ ] 添加更多模型支持
- [ ] 实现响应缓存
- [ ] 添加更多提示模板
- [ ] 优化Token计算
- [ ] 添加更多单元测试