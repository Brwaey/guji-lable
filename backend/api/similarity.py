#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相似度计算API路由
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from models.schemas import (
    SimilarityComputeRequest,
    TaskInfo,
    TaskStatus,
    SimilarityResult,
    SimilarityResultDetail
)
from services.similarity_service import SimilarityService

router = APIRouter(prefix="/similarity", tags=["相似度计算"])

# 创建服务实例
similarity_service = SimilarityService()


@router.post("/compute", response_model=TaskInfo)
async def compute_similarity(request: SimilarityComputeRequest):
    """
    计算相似度
    
    启动异步任务计算OCR文件与参考文件的embedding相似度
    """
    try:
        task_info = similarity_service.create_task(request)
        return task_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """
    获取任务状态
    
    查询计算任务的当前状态和进度
    """
    task_status = similarity_service.get_task_status(task_id)
    
    if not task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task_status


@router.get("/result/{task_id}", response_model=SimilarityResult)
async def get_result(task_id: str):
    """
    获取计算结果
    
    获取已完成任务的相似度计算结果
    """
    task_status = similarity_service.get_task_status(task_id)
    
    if not task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task_status.status != "completed":
        return SimilarityResult(
            task_id=task_id,
            status=task_status.status,
            result=None,
            error=task_status.message
        )
    
    result = similarity_service.get_result(task_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")
    
    return SimilarityResult(
        task_id=task_id,
        status="completed",
        result=result.dict(),
        error=None
    )


@router.get("/result/{task_id}/detail", response_model=SimilarityResultDetail)
async def get_result_detail(task_id: str):
    """
    获取详细结果
    
    获取已完成任务的详细相似度结果（包含所有文本块）
    """
    task_status = similarity_service.get_task_status(task_id)
    
    if not task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task_status.status != "completed":
        raise HTTPException(status_code=400, detail=f"任务未完成，当前状态: {task_status.status}")
    
    result = similarity_service.get_result(task_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")
    
    return result


@router.get("/api-status")
async def check_embedding_api_status():
    """
    检查Embedding API状态
    
    测试Embedding服务是否可用
    """
    from utils.embedding_client import EmbeddingClient
    from config import settings
    
    client = EmbeddingClient(
        api_url=settings.EMBEDDING_API_URL,
        model=settings.EMBEDDING_MODEL
    )
    
    status = client.check_api_status()
    
    return {
        "api_url": settings.EMBEDDING_API_URL,
        "status": status
    }


@router.delete("/task/{task_id}")
async def cancel_task(task_id: str):
    """
    取消任务
    
    取消正在进行的计算任务
    """
    task_status = similarity_service.get_task_status(task_id)
    
    if not task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task_status.status == "completed":
        raise HTTPException(status_code=400, detail="任务已完成，无法取消")
    
    # TODO: 实现任务取消逻辑
    task_status.status = "cancelled"
    task_status.message = "用户取消"
    
    return {"message": "任务已取消", "task_id": task_id}