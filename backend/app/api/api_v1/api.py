from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth,
    users,
    novels,
    chapters,
    characters,
    events,
    agents,
    tasks,
)

# 创建APIRouter实例
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用户"]
)

api_router.include_router(
    novels.router,
    prefix="/novels",
    tags=["小说"]
)

api_router.include_router(
    chapters.router,
    prefix="/chapters",
    tags=["章节"]
)

api_router.include_router(
    characters.router,
    prefix="/characters",
    tags=["人物"]
)

api_router.include_router(
    events.router,
    prefix="/events",
    tags=["事件"]
)

api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["智能体"]
)

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["任务"]
)