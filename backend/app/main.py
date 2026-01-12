# 加载环境变量
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import init_db

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="小红书热点监控工具API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 启动事件
@app.on_event("startup")
async def startup_event():
    """
    应用启动时执行
    """
    init_db()
    print("数据库初始化完成")


# 健康检查接口
@app.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# 注册路由
from app.api.v1 import auth, keywords, crawler, scheduler, mediacrawler, posts, reports

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["认证"])
app.include_router(keywords.router, prefix=f"{settings.API_V1_STR}/keywords", tags=["关键词管理"])
app.include_router(crawler.router, prefix=f"{settings.API_V1_STR}/crawler", tags=["数据抓取"])
app.include_router(scheduler.router, prefix=f"{settings.API_V1_STR}/scheduler", tags=["定时任务"])
app.include_router(mediacrawler.router, prefix=f"{settings.API_V1_STR}/mediacrawler", tags=["MediaCrawler登录"])
app.include_router(posts.router, prefix=f"{settings.API_V1_STR}/posts", tags=["帖子展示"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["报告生成"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )