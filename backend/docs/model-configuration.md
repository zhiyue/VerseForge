# AI模型配置指南

## 概述

VerseForge系统支持为每个智能体（Agent）独立配置不同的AI模型供应商，使系统具有更高的灵活性和可控性。

## 配置方式

### 1. 通过管理界面配置

访问管理界面的Agent配置页面：

```
http://your-domain/admin/agents/{agent_id}/model-config
```

填写以下信息：
- 供应商选择（如：OpenAI、Claude等）
- 模型名称（如：gpt-4、gpt-3.5-turbo等）
- API密钥
- 组织ID（可选）
- 模型参数
- 使用限制

### 2. 通过API配置

```http
POST /api/v1/model-configs
Content-Type: application/json
Authorization: Bearer your-token

{
  "agent_id": 1,
  "provider_config": {
    "provider": "openai",
    "model_name": "gpt-4",
    "api_key": "your-api-key",
    "organization_id": "your-org-id"
  },
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 0.9
  },
  "usage_limits": {
    "max_requests_per_minute": 60,
    "max_tokens_per_request": 4096,
    "max_daily_tokens": 1000000
  }
}
```

## 支持的模型供应商

1. OpenAI
   - 支持的模型：gpt-4, gpt-3.5-turbo
   - 配置项：api_key, organization_id
   - 特殊功能：embedding支持

2. Anthropic Claude（计划中）
   - 支持的模型：claude-2, claude-instant
   - 配置项：api_key

3. 本地模型（计划中）
   - 支持自定义本地模型
   - 配置项：model_path, device

## 使用限制配置

可以为每个Agent设置以下使用限制：

```json
{
  "usage_limits": {
    "max_requests_per_minute": 60,    // 每分钟最大请求数
    "max_tokens_per_request": 4096,   // 单次请求最大token数
    "max_daily_tokens": 1000000,      // 每日最大token数
    "max_cost_per_day": 100.0        // 每日最大成本（美元）
  }
}
```

## 使用统计

系统会自动记录每个Agent的模型使用统计：

```http
GET /api/v1/model-configs/{agent_id}/usage
```

返回示例：
```json
{
  "total_requests": 1000,
  "total_tokens": 50000,
  "total_cost": 25.50,
  "daily_stats": {
    "2025-03-20": {
      "requests": 100,
      "tokens": 5000,
      "cost": 2.50
    }
  }
}
```

## 成本控制

1. 设置使用限制
2. 监控使用统计
3. 配置告警阈值
4. 自动暂停超限Agent

## 故障转移

可以配置备用供应商在主要供应商不可用时自动切换：

```json
{
  "fallback_provider": "openai",
  "fallback_config": {
    "model_name": "gpt-3.5-turbo",
    "api_key": "backup-api-key"
  }
}
```

## 最佳实践

1. API密钥安全
   - 使用环境变量
   - 定期轮换密钥
   - 设置适当的权限

2. 成本控制
   - 设置合理的使用限制
   - 监控使用情况
   - 配置成本告警

3. 性能优化
   - 选择合适的模型
   - 合理设置token限制
   - 使用缓存减少请求

4. 错误处理
   - 配置重试策略
   - 设置备用供应商
   - 记录详细日志

## 开发者API

系统提供了完整的API来管理模型配置：

1. 创建配置
```http
POST /api/v1/model-configs
```

2. 更新配置
```http
PUT /api/v1/model-configs/{agent_id}
```

3. 获取配置
```http
GET /api/v1/model-configs/{agent_id}
```

4. 删除配置
```http
DELETE /api/v1/model-configs/{agent_id}
```

5. 检查使用限制
```http
GET /api/v1/model-configs/{agent_id}/limits?tokens_required=1000
```

## 监控和告警

系统提供以下监控指标：

1. 使用量指标
   - 请求数量
   - Token使用量
   - 费用统计

2. 性能指标
   - 响应时间
   - 错误率
   - 成功率

3. 告警设置
   - 使用量告警
   - 成本告警
   - 错误告警

## 常见问题

1. 如何更换API密钥？
   - 通过API更新配置
   - 确保新密钥已经过测试
   - 系统会自动切换

2. 如何处理超限情况？
   - 系统自动暂停相关Agent
   - 发送通知
   - 等待限制重置或调整限制

3. 如何优化成本？
   - 使用较低成本的模型
   - 实施缓存策略
   - 优化提示设计