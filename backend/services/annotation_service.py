#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标注管理服务
"""

import os
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

from config import settings
from models.schemas import (
    AnnotationCreate,
    AnnotationUpdate,
    Annotation,
    AnnotationListResponse,
    AnnotationStats,
    AnnotationStatus
)

logger = logging.getLogger(__name__)


class AnnotationService:
    """标注管理服务"""
    
    def __init__(self):
        self.output_path = Path(settings.ANNOTATION_OUTPUT_PATH)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # 内存缓存
        self.annotations_cache: Dict[str, Annotation] = {}
        self._load_all_annotations()
    
    def _load_all_annotations(self):
        """加载所有标注到内存"""
        try:
            for root, dirs, files in os.walk(self.output_path):
                for file in files:
                    if file.endswith('.json') and file.startswith('ann_'):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                annotation = Annotation(**data)
                                self.annotations_cache[annotation.annotation_id] = annotation
                        except Exception as e:
                            logger.warning(f"加载标注失败: {file_path}, {e}")
            
            logger.info(f"已加载 {len(self.annotations_cache)} 个标注")
            
        except Exception as e:
            logger.error(f"加载标注失败: {e}")
    
    def _get_annotation_path(self, annotation_id: str) -> Path:
        """获取标注文件路径"""
        return self.output_path / f"{annotation_id}.json"
    
    def _get_book_dir(self, ocr_file: str) -> Path:
        """获取书籍目录"""
        # 从OCR文件路径提取书籍名
        parts = Path(ocr_file).parts
        # 找到基础路径后的第一级目录
        for base_path in settings.OCR_BASE_PATHS:
            if base_path in ocr_file:
                relative_path = Path(ocr_file).relative_to(base_path)
                if len(relative_path.parts) > 1:
                    book_name = relative_path.parts[0]
                    return self.output_path / book_name
        
        return self.output_path
    
    def create_annotation(self, data: AnnotationCreate) -> Annotation:
        """创建标注"""
        annotation_id = f"ann_{uuid.uuid4().hex[:12]}"
        
        annotation = Annotation(
            annotation_id=annotation_id,
            ocr_file=data.ocr_file,
            reference_file=data.reference_file,
            chunk_index=data.chunk_index,
            chapter=data.chapter,
            annotation_type=data.annotation_type,
            ocr_position=data.ocr_position,
            original_text=data.original_text,
            suggested_text=data.suggested_text,
            confidence=data.confidence,
            note=data.note,
            ocr_text=data.ocr_text,
            ref_text=data.ref_text,
            similarity=data.similarity,
            annotator=None,  # TODO: 从认证系统获取
            status=AnnotationStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 保存到文件
        self._save_annotation(annotation)
        
        # 添加到缓存
        self.annotations_cache[annotation_id] = annotation
        
        logger.info(f"创建标注: {annotation_id}")
        
        return annotation
    
    def update_annotation(self, annotation_id: str, data: AnnotationUpdate) -> Optional[Annotation]:
        """更新标注"""
        annotation = self.annotations_cache.get(annotation_id)
        
        if not annotation:
            logger.warning(f"标注不存在: {annotation_id}")
            return None
        
        # 更新字段
        update_data = data.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(annotation, key, value)
        
        annotation.updated_at = datetime.now()
        
        # 保存
        self._save_annotation(annotation)
        
        # 更新缓存
        self.annotations_cache[annotation_id] = annotation
        
        logger.info(f"更新标注: {annotation_id}")
        
        return annotation
    
    def delete_annotation(self, annotation_id: str) -> bool:
        """删除标注"""
        annotation = self.annotations_cache.get(annotation_id)
        
        if not annotation:
            logger.warning(f"标注不存在: {annotation_id}")
            return False
        
        # 删除文件
        file_path = self._get_annotation_path(annotation_id)
        
        if file_path.exists():
            file_path.unlink()
        
        # 从缓存移除
        del self.annotations_cache[annotation_id]
        
        logger.info(f"删除标注: {annotation_id}")
        
        return True
    
    def get_annotation(self, annotation_id: str) -> Optional[Annotation]:
        """获取单个标注"""
        return self.annotations_cache.get(annotation_id)
    
    def list_annotations(
        self,
        file_path: Optional[str] = None,
        status: Optional[str] = None,
        annotation_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> AnnotationListResponse:
        """列出标注"""
        filtered = list(self.annotations_cache.values())
        
        # 过滤
        if file_path:
            filtered = [a for a in filtered if a.ocr_file == file_path or a.reference_file == file_path]
        
        if status:
            filtered = [a for a in filtered if a.status == status]
        
        if annotation_type:
            filtered = [a for a in filtered if a.annotation_type == annotation_type]
        
        # 排序（按创建时间倒序）
        filtered.sort(key=lambda x: x.created_at, reverse=True)
        
        # 分页
        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        
        return AnnotationListResponse(
            annotations=filtered[start:end],
            total=total,
            page=page,
            page_size=page_size
        )
    
    def get_statistics(self, scope: str = "all", file_path: Optional[str] = None) -> AnnotationStats:
        """获取统计信息"""
        filtered = list(self.annotations_cache.values())
        
        # 过滤范围
        if scope == "file" and file_path:
            filtered = [a for a in filtered if a.ocr_file == file_path or a.reference_file == file_path]
        
        # 按类型统计
        by_type = {}
        for annotation in filtered:
            type_key = annotation.annotation_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1
        
        # 按状态统计
        by_status = {}
        for annotation in filtered:
            status_key = annotation.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1
        
        # 按章节统计
        by_chapter = {}
        for annotation in filtered:
            chapter = annotation.chapter
            by_chapter[chapter] = by_chapter.get(chapter, 0) + 1
        
        # 平均确信度
        avg_confidence = sum(a.confidence for a in filtered) / len(filtered) if filtered else 0
        
        return AnnotationStats(
            total_annotations=len(filtered),
            by_type=by_type,
            by_status=by_status,
            by_chapter=by_chapter,
            avg_confidence=avg_confidence
        )
    
    def export_annotations(
        self,
        format: str = "json",
        scope: str = "all",
        file_path: Optional[str] = None
    ) -> str:
        """导出标注"""
        filtered = list(self.annotations_cache.values())
        
        # 过滤范围
        if scope == "file" and file_path:
            filtered = [a for a in filtered if a.ocr_file == file_path or a.reference_file == file_path]
        
        if format == "json":
            return self._export_json(filtered)
        elif format == "csv":
            return self._export_csv(filtered)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def _export_json(self, annotations: List[Annotation]) -> str:
        """导出为JSON"""
        data = [a.dict() for a in annotations]
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)
    
    def _export_csv(self, annotations: List[Annotation]) -> str:
        """导出为CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        headers = [
            "annotation_id", "ocr_file", "reference_file", "chunk_index",
            "chapter", "annotation_type", "original_text", "suggested_text",
            "confidence", "note", "status", "created_at", "updated_at"
        ]
        writer.writerow(headers)
        
        # 写入数据
        for a in annotations:
            writer.writerow([
                a.annotation_id,
                a.ocr_file,
                a.reference_file,
                a.chunk_index,
                a.chapter,
                a.annotation_type.value,
                a.original_text,
                a.suggested_text or "",
                a.confidence,
                a.note or "",
                a.status.value,
                a.created_at,
                a.updated_at
            ])
        
        return output.getvalue()
    
    def _save_annotation(self, annotation: Annotation):
        """保存标注到文件"""
        book_dir = self._get_book_dir(annotation.ocr_file)
        book_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = book_dir / f"{annotation.annotation_id}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(annotation.dict(), f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"标注已保存: {file_path}")
            
        except Exception as e:
            logger.error(f"保存标注失败: {e}")
            raise