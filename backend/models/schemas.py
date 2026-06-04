#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class FileType(str, Enum):
    """文件类型"""
    FILE = "file"
    DIRECTORY = "directory"


class AnnotationType(str, Enum):
    """标注类型"""
    ERROR_CHAR = "error_char"          # 识别错误
    MISSING = "missing"                 # 缺失内容
    EXTRA = "extra"                     # 多余内容
    FORMAT = "format"                   # 格式错误
    UNCLEAR = "unclear"                 # 模糊不清
    OTHER = "other"                     # 其他问题


class AnnotationStatus(str, Enum):
    """标注状态"""
    DRAFT = "draft"           # 草稿
    CONFIRMED = "confirmed"   # 已确认
    REVIEWED = "reviewed"     # 已审核


# ============================================================================
# 文件相关模型
# ============================================================================

class FileInfo(BaseModel):
    """文件信息"""
    name: str
    type: FileType
    path: str
    size: Optional[int] = None
    modified: Optional[datetime] = None
    file_count: Optional[int] = None  # 目录下的文件数量
    is_readable: bool = True


class FileBrowseResponse(BaseModel):
    """文件浏览响应"""
    path: str
    items: List[FileInfo]
    parent: Optional[str] = None
    total_items: int


class FilePreviewResponse(BaseModel):
    """文件预览响应"""
    path: str
    content: str
    total_lines: int
    encoding: str = "utf-8"


class FileMatchRequest(BaseModel):
    """文件匹配请求"""
    ocr_file: str


class FileMatchResponse(BaseModel):
    """文件匹配响应"""
    ocr_file: str
    recommended_files: List[Dict[str, Any]]  # [{path, score, reason}]


# ============================================================================
# 相似度计算相关模型
# ============================================================================

class SimilarityComputeRequest(BaseModel):
    """相似度计算请求"""
    ocr_file: str
    reference_file: str
    options: Optional[Dict[str, Any]] = None


class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)


class TaskStatus(BaseModel):
    """任务状态"""
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: int = 0  # 0-100
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TextChunk(BaseModel):
    """文本块"""
    chunk_index: int
    chapter: str
    ocr_text: str
    ref_text: Optional[str] = None
    similarity: float
    position: Dict[str, int]  # {start, end}


class ChapterStats(BaseModel):
    """章节统计"""
    chapter_name: str
    total_chunks: int
    avg_similarity: float
    low_similarity_count: int


class SimilarityResult(BaseModel):
    """相似度计算结果"""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SimilarityResultDetail(BaseModel):
    """相似度结果详情"""
    overall_similarity: float
    total_chunks: int
    matched_chunks: int
    processing_time: float
    chunks: List[TextChunk]
    chapter_stats: List[ChapterStats]


# ============================================================================
# 标注相关模型
# ============================================================================

class AnnotationCreate(BaseModel):
    """创建标注请求"""
    ocr_file: str
    reference_file: str
    chunk_index: int
    chapter: str
    annotation_type: AnnotationType
    ocr_position: Dict[str, int]  # {start, end}
    original_text: str
    suggested_text: Optional[str] = None
    confidence: Optional[float] = 0.5
    note: Optional[str] = None
    ocr_text: Optional[str] = None
    ref_text: Optional[str] = None
    similarity: Optional[float] = None


class AnnotationUpdate(BaseModel):
    """更新标注请求"""
    annotation_type: Optional[AnnotationType] = None
    ocr_position: Optional[Dict[str, int]] = None
    original_text: Optional[str] = None
    suggested_text: Optional[str] = None
    confidence: Optional[float] = None
    note: Optional[str] = None
    status: Optional[AnnotationStatus] = None


class Annotation(BaseModel):
    """标注数据"""
    annotation_id: str
    ocr_file: str
    reference_file: str
    chunk_index: int
    chapter: str
    annotation_type: AnnotationType
    ocr_position: Dict[str, int]
    original_text: str
    suggested_text: Optional[str] = None
    confidence: float
    note: Optional[str] = None
    ocr_text: Optional[str] = None
    ref_text: Optional[str] = None
    similarity: Optional[float] = None
    annotator: Optional[str] = None
    status: AnnotationStatus = AnnotationStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AnnotationListResponse(BaseModel):
    """标注列表响应"""
    annotations: List[Annotation]
    total: int
    page: int
    page_size: int


class AnnotationStats(BaseModel):
    """标注统计"""
    total_annotations: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    by_chapter: Optional[Dict[str, int]] = None
    avg_confidence: float


class AnnotationExportRequest(BaseModel):
    """标注导出请求"""
    format: str = "json"  # json, csv, xlsx
    scope: str = "all"  # all, file, book
    file_path: Optional[str] = None
