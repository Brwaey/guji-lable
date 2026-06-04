#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古籍标注平台 - 配置文件
"""

from typing import List
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "古籍标注平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"]
    
    # 远程文件服务器配置
    REMOTE_SERVER_HOST: str = "172.23.40.162"
    REMOTE_SERVER_USER: str = ""  # 如果需要SSH访问
    REMOTE_SERVER_PASSWORD: str = ""  # 如果需要SSH访问
    USE_SSH: bool = False  # 是否使用SSH连接（False表示使用SMB/网络共享）
    
    # OCR文件目录配置
    OCR_BASE_PATHS: List[str] = [
        "/home/maxuejiao/guji/mineru_ocr/二十四史附清史稿_ocr",
        "/home/maxuejiao/guji/mineru_ocr/十三经注疏_ocr",
        "/home/maxuejiao/guji/paddleocrvl_ocr/二十四史附清史稿_ocr",
        "/home/maxuejiao/guji/paddleocrvl_ocr/十三经注疏_ocr",
    ]
    
    # 参考文本目录配置（Ground Truth）
    REFERENCE_BASE_PATH: str = "/home/maxuejiao/guji/shidianguji"
    
    # Embedding服务配置
    EMBEDDING_API_URL: str = "http://172.23.40.162:8180/v1"
    EMBEDDING_MODEL: str = "embedding"
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_TIMEOUT: int = 60
    EMBEDDING_MAX_RETRIES: int = 3
    
    # 文本处理配置
    CHUNK_SIZE: int = 350  # 字符数
    CHUNK_OVERLAP: int = 50
    MIN_CHUNK_SIZE: int = 100
    
    # 相似度阈值配置
    SIMILARITY_THRESHOLD_LOW: float = 0.7
    SIMILARITY_THRESHOLD_MEDIUM: float = 0.85
    
    # 标注结果保存路径
    ANNOTATION_OUTPUT_PATH: str = "/home/maxuejiao/guji/annotations"
    
    # 缓存配置
    CACHE_DIR: str = "./cache/embeddings"
    CACHE_ENABLED: bool = True
    
    # 文件浏览配置
    FILE_PREVIEW_LINES: int = 100
    MAX_FILE_SIZE_MB: int = 50
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
