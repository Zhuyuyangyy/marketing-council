"""
============================================
MarketingCouncil - 营销决策辩论团
FastAPI 主入口
端口：8009
============================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
)

# 导入路由
from app.routers import debate

app = FastAPI(
    title="MarketingCouncil - 营销决策辩论团",
    description="多Agent营销方案风险评估与可能性分析系统 | Multi-Agent Strategic Debate System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(debate.router)


@app.get("/")
async def root():
    return {
        "name": "MarketingCouncil - 营销决策辩论团",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "辩论接口": "/api/v1/debate",
            "流式辩论": "/api/v1/debate/stream",
            "演示模式": "/api/v1/debate/demo",
            "Agent列表": "/api/v1/debate/agents",
        }
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "MarketingCouncil"}


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 MarketingCouncil 启动中，端口: 8009")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8009, reload=True)
