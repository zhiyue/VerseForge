# 使用官方Python镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# 复制项目文件
COPY pyproject.toml poetry.lock* ./

# 配置Poetry不创建虚拟环境（在Docker中不需要）
RUN poetry config virtualenvs.create false

# 安装项目依赖
RUN poetry install --no-dev --no-interaction --no-ansi

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]