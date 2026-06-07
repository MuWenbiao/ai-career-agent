from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import users, jobs, resumes, ai_agents
from loguru import logger
import sys

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level,
)

# 创建 FastAPI 应用
app = FastAPI(
    title="AI Career Agent",
    description="AI-powered career assistant for intelligent job matching, resume generation, and HR communication",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """健康检查"""
    return {
        "message": "AI Career Agent API",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "llm_provider": settings.llm_provider,
    }


@app.get("/config")
async def get_config():
    """获取配置信息（不包含敏感信息）"""
    return {
        "llm_provider": settings.llm_provider,
        "database": "SQLite",
        "api_version": "0.1.0",
    }


# 注册路由
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(ai_agents.router)

logger.info(f"AI Career Agent API started with LLM provider: {settings.llm_provider}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )
