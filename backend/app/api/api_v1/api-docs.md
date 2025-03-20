# VerseForge API 文档

## 基础信息

- 基础URL: `/api/v1`
- 认证方式: Bearer Token
- 响应格式: JSON

## 认证接口

### 用户登录

```http
POST /auth/login
```

请求参数：
```json
{
  "username": "string (邮箱)",
  "password": "string"
}
```

响应格式：
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### 用户注册

```http
POST /auth/signup
```

请求参数：
```json
{
  "email": "string",
  "username": "string",
  "password": "string",
  "full_name": "string (可选)"
}
```

## 用户接口

### 获取当前用户信息

```http
GET /users/me
```

### 更新当前用户信息

```http
PUT /users/me
```

请求参数：
```json
{
  "email": "string (可选)",
  "full_name": "string (可选)",
  "password": "string (可选)"
}
```

### 获取用户偏好设置

```http
GET /users/me/preferences
```

### 更新用户偏好设置

```http
PUT /users/me/preferences
```

## 小说接口

### 获取小说列表

```http
GET /novels
```

查询参数：
- skip: 整数，跳过的数量（分页用）
- limit: 整数，返回的最大数量

### 创建新小说

```http
POST /novels
```

请求参数：
```json
{
  "title": "string",
  "description": "string (可选)",
  "genre": "string (可选)",
  "target_word_count": "integer"
}
```

### 获取小说详情

```http
GET /novels/{novel_id}
```

### 更新小说信息

```http
PUT /novels/{novel_id}
```

### 删除小说

```http
DELETE /novels/{novel_id}
```

### 开始生成小说

```http
GET /novels/{novel_id}/generate
```

### 获取生成状态

```http
GET /novels/{novel_id}/status
```

## Agent接口

### 获取Agent列表

```http
GET /agents
```

### 获取Agent状态

```http
GET /agents/{agent_id}/status
```

### 重置Agent

```http
POST /agents/{agent_id}/reset
```

### 获取系统状态

```http
GET /agents/system-status
```

## 任务接口

### 获取任务列表

```http
GET /tasks
```

查询参数：
- skip: 整数，跳过的数量
- limit: 整数，返回的最大数量
- status: 字符串，任务状态过滤
- novel_id: 整数，小说ID过滤

### 创建新任务

```http
POST /tasks
```

请求参数：
```json
{
  "agent_type": "string",
  "task_type": "string",
  "task_data": "object",
  "novel_id": "integer",
  "priority": "integer (可选)"
}
```

### 获取任务详情

```http
GET /tasks/{task_id}
```

### 取消任务

```http
DELETE /tasks/{task_id}
```

### 重试任务

```http
POST /tasks/{task_id}/retry
```

## 错误码

| 错误码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 请求体验证失败 |
| 500 | 服务器内部错误 |

## 数据模型

### User

```json
{
  "id": "integer",
  "email": "string",
  "username": "string",
  "full_name": "string",
  "is_active": "boolean",
  "is_superuser": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Novel

```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "genre": "string",
  "target_word_count": "integer",
  "current_word_count": "integer",
  "status": "string",
  "creator_id": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Agent

```json
{
  "id": "integer",
  "name": "string",
  "agent_type": "string",
  "status": "string",
  "parameters": "object",
  "stats": "object",
  "error_message": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Task

```json
{
  "id": "integer",
  "agent_id": "integer",
  "novel_id": "integer",
  "task_type": "string",
  "task_data": "object",
  "priority": "integer",
  "status": "string",
  "result": "object",
  "error_message": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}