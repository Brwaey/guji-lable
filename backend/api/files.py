#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件浏览API路由
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from models.schemas import (
    FileBrowseResponse,
    FilePreviewResponse,
    FileMatchRequest,
    FileMatchResponse
)
from services.file_service import FileService

router = APIRouter(prefix="/files", tags=["文件浏览"])

# 创建服务实例
file_service = FileService()


@router.get("/browse", response_model=FileBrowseResponse)
async def browse_directory(
    path: str = Query(default="/", description="目录路径")
):
    """
    浏览目录内容
    
    - **path**: 要浏览的目录路径
    """
    try:
        result = file_service.browse_directory(path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"浏览目录失败: {str(e)}")


@router.get("/preview", response_model=FilePreviewResponse)
async def preview_file(
    file_path: str = Query(..., description="文件路径"),
    lines: Optional[int] = Query(default=None, description="预览行数")
):
    """
    预览文件内容
    
    - **file_path**: 要预览的文件路径
    - **lines**: 预览行数（可选）
    """
    try:
        result = file_service.preview_file(file_path, lines)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览文件失败: {str(e)}")


@router.get("/search")
async def search_files(
    query: str = Query(..., description="搜索关键词"),
    scope: str = Query(default="all", description="搜索范围：all, ocr, reference")
):
    """
    搜索文件
    
    - **query**: 搜索关键词
    - **scope**: 搜索范围
    """
    try:
        results = file_service.search_files(query, scope)
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/match", response_model=FileMatchResponse)
async def match_files(request: FileMatchRequest):
    """
    匹配OCR文件到参考文件
    
    根据OCR文件名自动推荐匹配的参考文件
    """
    try:
        recommendations = file_service.match_files(request.ocr_file)
        return FileMatchResponse(
            ocr_file=request.ocr_file,
            recommended_files=recommendations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件匹配失败: {str(e)}")


@router.get("/tree")
async def get_file_tree():
    """
    获取完整文件树结构
    
    返回OCR和参考文件的目录树
    """
    try:
        tree = file_service.get_file_tree()
        return tree
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件树失败: {str(e)}")


@router.get("/base-paths")
async def get_base_paths():
    """
    获取配置的基础路径列表
    
    返回OCR和参考文件的根目录列表
    """
    from config import settings
    
    return {
        "ocr_paths": settings.OCR_BASE_PATHS,
        "reference_path": settings.REFERENCE_BASE_PATH
    }


@router.on_event("shutdown")
async def shutdown():
    """关闭服务"""
    file_service.close()