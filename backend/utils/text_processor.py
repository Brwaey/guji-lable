#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本处理工具
基于 ocr_quality_evaluator.py 的实现
"""

import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

# 尝试导入可选依赖
try:
    from opencc import OpenCC
    HAS_OPENCC = True
except ImportError:
    HAS_OPENCC = False

logger = logging.getLogger(__name__)


@dataclass
class TextChunkData:
    """文本块数据"""
    text: str
    start_pos: int
    end_pos: int
    chapter: str = ""
    index: int = 0


class TextProcessor:
    """文本预处理器"""
    
    def __init__(self, chunk_size: int = 350, chunk_overlap: int = 50, min_chunk_size: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.cc_s2t = None
        
        if HAS_OPENCC:
            self.cc_s2t = OpenCC('s2t')  # 简转繁
    
    def clean_mineru_text(self, text: str) -> str:
        """清洗MineRU OCR输出"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if not line.strip():
                continue
            
            # 跳过图片引用
            if line.strip().startswith('!['):
                continue
            
            # 跳过HTML标签
            if any(tag in line for tag in ['<details>', '</details>', '<summary>', '</summary>']):
                continue
            
            # 跳过特殊标记
            if any(marker in line for marker in ['## 分片', '来源:', '---']):
                continue
            
            # 跳过纯数字行(页码)
            if line.strip().isdigit():
                continue
            
            # 跳过图片hash文件名
            if re.match(r'^[a-f0-9]{40,}\.jpg$', line.strip()):
                continue
            
            cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)
        result = re.sub(r' {2,}', ' ', result)
        
        return result.strip()
    
    def clean_paddleocr_text(self, text: str) -> str:
        """清洗PaddleOCR输出"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if not line.strip():
                continue
            
            # PaddleOCR可能有特定的标记，根据实际情况调整
            cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip()
    
    def clean_reference_text(self, text: str) -> str:
        """清洗参考文本(识典古籍)"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if not line.strip():
                continue
            
            # 跳过HTML注释
            if line.strip().startswith('<!--') and '-->' in line:
                continue
            if '<!--' in line and line.strip().endswith('-->'):
                continue
            
            cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip()
    
    def normalize_text(self, text: str, target_variant: str = 'traditional') -> str:
        """标准化文本(统一为繁体)"""
        if not HAS_OPENCC:
            return text
        
        return self.cc_s2t.convert(text)
    
    def extract_chapters(self, text: str, is_reference: bool = False) -> Dict[str, str]:
        """提取章节内容"""
        chapters = {}
        current_chapter = "前言"
        current_content = []
        
        # 章节标题模式
        if is_reference:
            chapter_pattern = re.compile(r'^##\s+(.+?)(?:\s+隋書[\d]+)?$')
        else:
            chapter_pattern = re.compile(r'^#\s*(.+?卷[\d一二三四五六七八九十百]+|帝紀[第上下\d]+|志[第上下\d]+|列傳[第上下\d]+|卷[\d一二三四五六七八九十百]+.*)$')
        
        lines = text.split('\n')
        for line in lines:
            line_stripped = line.strip()
            
            chapter_match = chapter_pattern.match(line_stripped)
            if chapter_match:
                if current_content:
                    chapters[current_chapter] = '\n'.join(current_content)
                    current_content = []
                current_chapter = line_stripped.lstrip('#').strip()
                continue
            
            if line_stripped.startswith('#') and len(line_stripped) < 50:
                potential_chapter = line_stripped.lstrip('#').strip()
                if potential_chapter and len(potential_chapter) > 2:
                    if current_content:
                        chapters[current_chapter] = '\n'.join(current_content)
                        current_content = []
                    current_chapter = potential_chapter
                    continue
            
            current_content.append(line)
        
        if current_content:
            chapters[current_chapter] = '\n'.join(current_content)
        
        return chapters
    
    def chunk_text(self, text: str, chapter_name: str = "", start_index: int = 0) -> List[TextChunkData]:
        """将文本分块"""
        chunks = []
        paragraphs = re.split(r'\n\n+', text)
        
        current_chunk = ""
        current_start = 0
        pos = 0
        chunk_index = start_index
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(para) > self.chunk_size * 1.5:
                # 长段落按句子分割
                if current_chunk:
                    chunks.append(TextChunkData(
                        text=current_chunk.strip(),
                        start_pos=current_start,
                        end_pos=pos,
                        chapter=chapter_name,
                        index=chunk_index
                    ))
                    chunk_index += 1
                    current_chunk = ""
                
                sentences = self._split_sentences(para)
                sentence_chunk = ""
                sentence_start = pos
                
                for sent in sentences:
                    if len(sentence_chunk) + len(sent) > self.chunk_size:
                        if sentence_chunk:
                            chunks.append(TextChunkData(
                                text=sentence_chunk.strip(),
                                start_pos=sentence_start,
                                end_pos=pos,
                                chapter=chapter_name,
                                index=chunk_index
                            ))
                            chunk_index += 1
                            sentence_chunk = ""
                            sentence_start = pos
                    sentence_chunk += sent
                    pos += len(sent) + 1
                
                if sentence_chunk and len(sentence_chunk) >= self.min_chunk_size:
                    chunks.append(TextChunkData(
                        text=sentence_chunk.strip(),
                        start_pos=sentence_start,
                        end_pos=pos,
                        chapter=chapter_name,
                        index=chunk_index
                    ))
                    chunk_index += 1
            else:
                if len(current_chunk) + len(para) > self.chunk_size:
                    if current_chunk and len(current_chunk) >= self.min_chunk_size:
                        chunks.append(TextChunkData(
                            text=current_chunk.strip(),
                            start_pos=current_start,
                            end_pos=pos,
                            chapter=chapter_name,
                            index=chunk_index
                        ))
                        chunk_index += 1
                        overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else ""
                        current_chunk = overlap_text + para
                        current_start = pos - len(overlap_text)
                    else:
                        current_chunk += "\n\n" + para
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + para
                    else:
                        current_chunk = para
                        current_start = pos
            
            pos += len(para) + 2
        
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunks.append(TextChunkData(
                text=current_chunk.strip(),
                start_pos=current_start,
                end_pos=pos,
                chapter=chapter_name,
                index=chunk_index
            ))
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """分割句子"""
        pattern = re.compile(r'([。！？；：，、]+[""』」\s]*)')
        parts = pattern.split(text)
        
        sentences = []
        current = ""
        
        for part in parts:
            current += part
            if pattern.match(part) or len(current) > 20:
                if current.strip():
                    sentences.append(current.strip())
                current = ""
        
        if current.strip():
            sentences.append(current.strip())
        
        return sentences if sentences else [text]