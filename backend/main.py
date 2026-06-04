#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古籍标注平台 - FastAPI主入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from config import settings
from api import files_router, similarity_router, annotations_router

# 配置日志
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="古籍OCR质量评估与标注平台API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(files_router, prefix="/api")
app.include_router(similarity_router, prefix="/api")
app.include_router(annotations_router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


@app.get("/api/config")
async def get_config():
    """获取配置信息"""
    return {
        "ocr_base_paths": settings.OCR_BASE_PATHS,
        "reference_base_path": settings.REFERENCE_BASE_PATH,
        "embedding_api_url": settings.EMBEDDING_API_URL,
        "annotation_output_path": settings.ANNOTATION_OUTPUT_PATH,
        "cache_enabled": settings.CACHE_ENABLED
    }


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info(f"🚀 {settings.APP_NAME} 启动中...")
    logger.info(f"📝 版本: {settings.APP_VERSION}")
    logger.info(f"🔧 调试模式: {settings.DEBUG}")
    logger.info(f"📡 API文档: http://{settings.HOST}:{settings.PORT}/api/docs")
    
    # 检查远程服务器连接
    logger.info(f"🖥️  远程服务器: {settings.REMOTE_SERVER_HOST}")
    logger.info(f"📂 OCR路径数: {len(settings.OCR_BASE_PATHS)}")
    logger.info(f"📚 参考文本路径: {settings.REFERENCE_BASE_PATH}")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info(f"👋 {settings.APP_NAME} 关闭中...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )