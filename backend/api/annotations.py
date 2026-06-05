#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标注管理API路由
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from models.schemas import (
    AnnotationCreate,
    AnnotationUpdate,
    Annotation,
    AnnotationListResponse,
    AnnotationStats,
    AnnotationExportRequest
)
from services.annotation_service import AnnotationService

router = APIRouter(prefix="/annotations", tags=["标注管理"])

# 创建服务实例
annotation_service = AnnotationService()


@router.post("/create", response_model=Annotation)
async def create_annotation(data: AnnotationCreate):
    """
    创建标注
    
    创建一个新的标注记录
    """
    try:
        annotation = annotation_service.create_annotation(data)
        return annotation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建标注失败: {str(e)}")


@router.get("/list", response_model=AnnotationListResponse)
async def list_annotations(
    file_path: Optional[str] = Query(None, description="文件路径过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    annotation_type: Optional[str] = Query(None, description="类型过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量")
):
    """
    列出标注
    
    根据条件筛选标注列表
    """
    try:
        result = annotation_service.list_annotations(
            file_path=file_path,
            status=status,
            annotation_type=annotation_type,
            page=page,
            page_size=page_size
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取标注列表失败: {str(e)}")


@router.get("/stats", response_model=AnnotationStats)
async def get_statistics(
    scope: str = Query("all", description="统计范围：all, file"),
    file_path: Optional[str] = Query(None, description="文件路径（当scope=file时）")
):
    """
    获取统计信息
    
    获取标注的统计数据
    """
    try:
        stats = annotation_service.get_statistics(scope, file_path)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/types")
async def get_annotation_types():
    """
    获取标注类型列表
    
    返回所有可用的标注类型
    """
    from models.schemas import AnnotationType
    
    types = [
        {"code": AnnotationType.ERROR_CHAR.value, "name": "识别错误", "description": "字符被错误识别为其他字符"},
        {"code": AnnotationType.MISSING.value, "name": "缺失内容", "description": "OCR遗漏的内容"},
        {"code": AnnotationType.EXTRA.value, "name": "多余内容", "description": "OCR多识别的内容"},
        {"code": AnnotationType.FORMAT.value, "name": "格式错误", "description": "标点、分段等格式问题"},
        {"code": AnnotationType.UNCLEAR.value, "name": "模糊不清", "description": "原图模糊导致无法识别"},
        {"code": AnnotationType.OTHER.value, "name": "其他问题", "description": "其他类型错误"},
    ]
    
    return {"types": types}


@router.get("/statuses")
async def get_annotation_statuses():
    """
    获取标注状态列表
    
    返回所有可用的标注状态
    """
    from models.schemas import AnnotationStatus
    
    statuses = [
        {"code": AnnotationStatus.DRAFT.value, "name": "草稿", "description": "未提交的标注"},
        {"code": AnnotationStatus.CONFIRMED.value, "name": "已确认", "description": "已确认的标注"},
        {"code": AnnotationStatus.REVIEWED.value, "name": "已审核", "description": "已审核的标注"},
    ]
    
    return {"statuses": statuses}


@router.post("/export")
async def export_annotations(request: AnnotationExportRequest):
    """
    导出标注
    
    将标注数据导出为指定格式
    """
    try:
        data = annotation_service.export_annotations(
            format=request.format,
            scope=request.scope,
            file_path=request.file_path
        )
        
        return {
            "format": request.format,
            "data": data,
            "message": "导出成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


# 动态路由放在最后，避免与静态路由冲突
@router.get("/{annotation_id}", response_model=Annotation)
async def get_annotation(annotation_id: str):
    """
    获取标注详情
    
    根据ID获取单个标注的详细信息
    """
    annotation = annotation_service.get_annotation(annotation_id)
    
    if not annotation:
        raise HTTPException(status_code=404, detail="标注不存在")
    
    return annotation


@router.put("/{annotation_id}", response_model=Annotation)
async def update_annotation(annotation_id: str, data: AnnotationUpdate):
    """
    更新标注
    
    更新现有标注的内容
    """
    annotation = annotation_service.update_annotation(annotation_id, data)
    
    if not annotation:
        raise HTTPException(status_code=404, detail="标注不存在")
    
    return annotation


@router.delete("/{annotation_id}")
async def delete_annotation(annotation_id: str):
    """
    删除标注
    
    删除指定ID的标注
    """
    success = annotation_service.delete_annotation(annotation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="标注不存在")
    
    return {"message": "标注已删除", "annotation_id": annotation_id}