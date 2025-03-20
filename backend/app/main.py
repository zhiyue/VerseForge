from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.core.config import settings
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.api.api_v1.api import api_router

def create_application() -> FastAPI:
    """
    创建FastAPI应用实例
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 设置CORS中间件
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 注册事件处理器
    application.add_event_handler(
        "startup",
        create_start_app_handler(application)
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(application)
    )

    # 异常处理
    @application.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    # 注册路由
    application.include_router(
        api_router, 
        prefix=settings.API_V1_STR
    )

    return application

# 创建应用实例
app = create_application()

@app.get("/")
async def root():
    """
    根路径处理
    """
    return {
        "message": "欢迎使用VerseForge API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )