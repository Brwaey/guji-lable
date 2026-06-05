#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相似度计算服务
"""

import os
import json
import uuid
import time
import logging
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any

from config import settings
from models.schemas import (
    SimilarityComputeRequest,
    TaskInfo,
    TaskStatus,
    SimilarityResultDetail,
    TextChunk,
    ChapterStats
)
from utils.text_processor import TextProcessor
from utils.embedding_client import EmbeddingClient
from utils.text_aligner import TextAligner, ChunkData

logger = logging.getLogger(__name__)


class SimilarityService:
    """相似度计算服务"""
    
    def __init__(self):
        self.tasks: Dict[str, TaskStatus] = {}
        self.results: Dict[str, SimilarityResultDetail] = {}
        self.text_processor = TextProcessor(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            min_chunk_size=settings.MIN_CHUNK_SIZE
        )
        self.embedding_client = EmbeddingClient(
            api_url=settings.EMBEDDING_API_URL,
            model=settings.EMBEDDING_MODEL,
            batch_size=settings.EMBEDDING_BATCH_SIZE,
            timeout=settings.EMBEDDING_TIMEOUT,
            max_retries=settings.EMBEDDING_MAX_RETRIES
        )
        self.text_aligner = TextAligner(
            similarity_threshold=0.3,
            position_tolerance=0.15
        )
        
        # 缓存目录
        self.cache_dir = Path(settings.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def create_task(self, request: SimilarityComputeRequest) -> TaskInfo:
        """创建计算任务"""
        task_id = f"sim_{uuid.uuid4().hex[:12]}"
        
        task_status = TaskStatus(
            task_id=task_id,
            status="pending",
            progress=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.tasks[task_id] = task_status
        
        # 启动后台任务
        asyncio.create_task(self._compute_task(task_id, request))
        
        return TaskInfo(
            task_id=task_id,
            status="pending",
            created_at=datetime.now()
        )
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def get_result(self, task_id: str) -> Optional[SimilarityResultDetail]:
        """获取计算结果"""
        return self.results.get(task_id)
    
    async def _compute_task(self, task_id: str, request: SimilarityComputeRequest):
        """执行计算任务"""
        task = self.tasks[task_id]
        
        try:
            # 更新状态
            task.status = "processing"
            task.progress = 5
            task.updated_at = datetime.now()
            
            # 加载文件
            task.message = "正在加载文件..."
            ocr_text = self._load_file(request.ocr_file)
            ref_text = self._load_file(request.reference_file)
            
            if not ocr_text or not ref_text:
                task.status = "failed"
                task.message = "文件加载失败"
                return
            
            task.progress = 10
            
            # 文本预处理
            task.message = "正在预处理文本..."
            ocr_cleaned = self.text_processor.clean_mineru_text(ocr_text)
            ref_cleaned = self.text_processor.clean_reference_text(ref_text)
            
            # 统一为繁体
            ocr_cleaned = self.text_processor.normalize_text(ocr_cleaned)
            ref_cleaned = self.text_processor.normalize_text(ref_cleaned)
            
            task.progress = 15
            
            # 提取章节
            task.message = "正在提取章节..."
            ocr_chapters = self.text_processor.extract_chapters(ocr_cleaned, is_reference=False)
            ref_chapters = self.text_processor.extract_chapters(ref_cleaned, is_reference=True)
            
            task.progress = 20
            
            # 文本分块
            task.message = "正在进行文本分块..."
            ocr_chunks = []
            ref_chunks = []
            
            if ocr_chapters:
                for ch_name, ch_text in ocr_chapters.items():
                    chunks = self.text_processor.chunk_text(ch_text, ch_name)
                    ocr_chunks.extend(chunks)
            else:
                ocr_chunks = self.text_processor.chunk_text(ocr_cleaned, "全文")
            
            if ref_chapters:
                for ch_name, ch_text in ref_chapters.items():
                    chunks = self.text_processor.chunk_text(ch_text, ch_name)
                    ref_chunks.extend(chunks)
            else:
                ref_chunks = self.text_processor.chunk_text(ref_cleaned, "全文")
            
            task.progress = 25
            
            # 检查缓存
            task.message = "检查embedding缓存..."
            ocr_cache = self._load_embeddings_cache(request.ocr_file)
            ref_cache = self._load_embeddings_cache(request.reference_file)
            
            task.progress = 30
            
            # 获取embeddings
            task.message = "正在计算embeddings..."
            
            ocr_embeddings = await self._get_embeddings_with_cache(
                [c.text for c in ocr_chunks],
                request.ocr_file,
                ocr_cache,
                task
            )
            
            if not task.status == "processing":
                return
            
            task.progress = 60
            
            ref_embeddings = await self._get_embeddings_with_cache(
                [c.text for c in ref_chunks],
                request.reference_file,
                ref_cache,
                task
            )
            
            if not task.status == "processing":
                return
            
            task.progress = 80
            
            # 对齐和计算相似度
            task.message = "正在计算相似度..."
            
            # 转换为ChunkData格式
            ocr_chunk_data = [
                ChunkData(
                    text=c.text,
                    start_pos=c.start_pos,
                    end_pos=c.end_pos,
                    chapter=c.chapter,
                    index=c.index,
                    embedding=ocr_embeddings[i] if i < len(ocr_embeddings) else None
                )
                for i, c in enumerate(ocr_chunks)
            ]
            
            ref_chunk_data = [
                ChunkData(
                    text=c.text,
                    start_pos=c.start_pos,
                    end_pos=c.end_pos,
                    chapter=c.chapter,
                    index=c.index,
                    embedding=ref_embeddings[i] if i < len(ref_embeddings) else None
                )
                for i, c in enumerate(ref_chunks)
            ]
            
            # 使用新的对齐器
            aligned_pairs = self.text_aligner.align_chunks(ocr_chunk_data, ref_chunk_data)
            
            # 计算相似度
            chunk_results = []
            chapter_sims = {}
            
            for ocr_chunk, ref_chunk in aligned_pairs:
                if not ocr_chunk.text:
                    continue
                
                similarity = 0.0
                if ocr_chunk.embedding and ref_chunk and ref_chunk.embedding:
                    similarity = self.embedding_client.cosine_similarity(ocr_chunk.embedding, ref_chunk.embedding)
                
                chunk_result = TextChunk(
                    chunk_index=ocr_chunk.index,
                    chapter=ocr_chunk.chapter,
                    ocr_text=ocr_chunk.text,
                    ref_text=ref_chunk.text if ref_chunk else None,
                    similarity=similarity,
                    position={"start": ocr_chunk.start_pos, "end": ocr_chunk.end_pos}
                )
                
                chunk_results.append(chunk_result)
                
                if ocr_chunk.chapter not in chapter_sims:
                    chapter_sims[ocr_chunk.chapter] = []
                chapter_sims[ocr_chunk.chapter].append(similarity)
            
            task.progress = 90
            
            # 计算章节统计
            chapter_stats = []
            for ch_name, sims in chapter_sims.items():
                if sims:
                    chapter_stats.append(ChapterStats(
                        chapter_name=ch_name,
                        total_chunks=len(sims),
                        avg_similarity=sum(sims) / len(sims),
                        low_similarity_count=sum(1 for s in sims if s < settings.SIMILARITY_THRESHOLD_LOW)
                    ))
            
            # 计算整体相似度
            overall_similarity = sum(c.similarity for c in chunk_results) / len(chunk_results) if chunk_results else 0
            matched_chunks = sum(1 for c in chunk_results if c.similarity >= settings.SIMILARITY_THRESHOLD_MEDIUM)
            
            # 保存结果
            result = SimilarityResultDetail(
                overall_similarity=overall_similarity,
                total_chunks=len(chunk_results),
                matched_chunks=matched_chunks,
                processing_time=0,  # 稍后计算
                chunks=chunk_results,
                chapter_stats=chapter_stats
            )
            
            self.results[task_id] = result
            
            # 完成
            task.status = "completed"
            task.progress = 100
            task.message = "计算完成"
            task.updated_at = datetime.now()
            
        except Exception as e:
            logger.error(f"任务执行失败: {task_id}, {e}", exc_info=True)
            task.status = "failed"
            task.message = str(e)
            task.updated_at = datetime.now()
    
    def _load_file(self, file_path: str) -> Optional[str]:
        """加载文件"""
        try:
            # 尝试不同编码
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            
            logger.error(f"无法解码文件: {file_path}")
            return None
            
        except Exception as e:
            logger.error(f"加载文件失败: {file_path}, {e}")
            return None
    
    def _get_file_hash(self, file_path: str) -> str:
        """计算文件哈希"""
        return hashlib.md5(file_path.encode()).hexdigest()
    
    def _load_embeddings_cache(self, file_path: str) -> Optional[Dict]:
        """加载embedding缓存"""
        if not settings.CACHE_ENABLED:
            return None
        
        file_hash = self._get_file_hash(file_path)
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载缓存失败: {e}")
        
        return None
    
    def _save_embeddings_cache(self, file_path: str, chunks: list, embeddings: list):
        """保存embedding缓存"""
        if not settings.CACHE_ENABLED:
            return
        
        file_hash = self._get_file_hash(file_path)
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        try:
            cache_data = {
                "file_path": file_path,
                "chunks": chunks,
                "embeddings": embeddings,
                "computed_at": datetime.now().isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"缓存已保存: {cache_file}")
            
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    async def _get_embeddings_with_cache(
        self,
        texts: list,
        file_path: str,
        cache: Optional[Dict],
        task: TaskStatus
    ) -> list:
        """获取embeddings（使用缓存）"""
        if cache and "embeddings" in cache:
            # 检查缓存是否有效
            cached_texts = cache.get("chunks", [])
            if len(cached_texts) == len(texts):
                # 使用缓存
                logger.info(f"使用缓存的embeddings: {file_path}")
                return cache["embeddings"]
        
        # 计算新的embeddings
        task.message = f"正在计算embeddings ({file_path})..."
        
        embeddings = await asyncio.get_event_loop().run_in_executor(
            None,
            self.embedding_client.get_embeddings_batch,
            texts
        )
        
        # 保存缓存
        self._save_embeddings_cache(file_path, texts, embeddings)
        
        return embeddings