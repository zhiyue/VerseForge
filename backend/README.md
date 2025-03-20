# VerseForge 后端服务

基于多智能体的网络小说自动写作系统后端服务。

## 技术栈

- Python 3.9+
- FastAPI
- SQLAlchemy
- Celery
- PostgreSQL
- Redis
- Apache Kafka
- Milvus

## 目录结构

```
backend/
├── app/
│   ├── api/            # API路由和端点
│   ├── core/           # 核心配置和功能
│   ├── agents/         # AI代理模块
│   ├── models/         # 数据库模型
│   ├── schemas/        # Pydantic模型
│   ├── services/       # 业务逻辑
│   └── utils/          # 工具函数
├── tests/              # 测试文件
├── alembic/            # 数据库迁移
├── docker/             # Docker配置
└── scripts/            # 辅助脚本
```

## 开发环境设置

1. 安装依赖

```bash
# 安装 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 安装项目依赖
poetry install
```

2. 环境变量配置

复制 `.env.example` 到 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

3. 启动开发环境

```bash
# 启动所有服务
docker-compose up -d

# 运行数据库迁移
poetry run alembic upgrade head

# 启动开发服务器
poetry run uvicorn app.main:app --reload
```

## API文档

启动服务后，可以访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 代码质量

```bash
# 运行测试
poetry run pytest

# 代码格式化
poetry run black .
poetry run isort .

# 类型检查
poetry run mypy .

# 代码风格检查
poetry run flake8
```

## 生产环境部署

1. 构建Docker镜像

```bash
docker build -t verseforge-backend .
```

2. 部署服务

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Agent模块

系统包含以下核心Agent：

- 故事大纲规划Agent (PlotAgent)
- 人物塑造Agent (CharacterAgent)
- 剧情生成Agent (SceneAgent)
- 文字描写Agent (WritingAgent)
- 质量审核Agent (QAAgent)
- 连贯性维护Agent (CoherenceAgent)

每个Agent都是独立的微服务，通过事件驱动架构进行通信。

## 事件系统

系统使用Kafka作为事件总线，处理以下类型的事件：

- 故事进度事件
- 人物行为事件
- 场景转换事件
- 冲突升级事件
- 情节衔接事件

## 贡献指南

1. Fork本项目
2. 创建特性分支
3. 提交改动
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License