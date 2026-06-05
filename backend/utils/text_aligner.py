#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本对齐器 - 基于ocr_quality_evaluator.py的完整实现
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ChunkData:
    """文本块数据"""
    text: str
    start_pos: int
    end_pos: int
    chapter: str = ""
    index: int = 0
    embedding: Optional[List[float]] = None
    
    @property
    def length(self) -> int:
        return len(self.text)


class TextAligner:
    """文本对齐器 - 使用智能章节匹配策略"""
    
    def __init__(self, similarity_threshold: float = 0.3, position_tolerance: float = 0.15):
        """
        初始化文本对齐器
        
        Args:
            similarity_threshold: 章节名称相似度阈值（默认0.3）
            position_tolerance: 全局对齐时的位置容差（默认0.15）
        """
        self.similarity_threshold = similarity_threshold
        self.position_tolerance = position_tolerance
    
    def align_chunks(
        self, 
        chunks1: List[ChunkData], 
        chunks2: List[ChunkData]
    ) -> List[Tuple[ChunkData, Optional[ChunkData]]]:
        """
        对齐两个文本块列表
        
        Args:
            chunks1: OCR文本块列表
            chunks2: 参考文本块列表
            
        Returns:
            对齐的文本块对列表
        """
        aligned = []
        
        if not chunks1 or not chunks2:
            # 处理空列表情况
            for chunk in chunks1:
                aligned.append((chunk, None))
            for chunk in chunks2:
                aligned.append((ChunkData(text="", start_pos=0, end_pos=0), chunk))
            return aligned
        
        # 按章节分组
        chapters1 = self._group_by_chapter(chunks1)
        chapters2 = self._group_by_chapter(chunks2)
        
        logger.info(f"章节对齐: OCR {len(chapters1)} 个章节, 参考 {len(chapters2)} 个章节")
        
        # 匹配章节名称
        matched_chapters = self._match_chapters(chapters1, chapters2)
        
        # 统计匹配成功率
        successful_matches = sum(1 for m in matched_chapters if m[0] and m[1])
        total_ch1 = len([m for m in matched_chapters if m[0]])
        
        logger.info(f"章节匹配成功: {successful_matches}/{total_ch1}")
        
        # 如果章节匹配率太低（<30%），使用全局对齐
        if total_ch1 > 0 and successful_matches / total_ch1 < 0.3:
            logger.warning(f"章节匹配率过低 ({successful_matches}/{total_ch1})，使用全局对齐策略")
            return self._global_align(chunks1, chunks2)
        
        # 按章节对齐
        for ch1, ch2 in matched_chapters:
            ch_chunks1 = chapters1.get(ch1, [])
            ch_chunks2 = chapters2.get(ch2, []) if ch2 else []
            
            if not ch_chunks1 and not ch_chunks2:
                continue
            
            if not ch_chunks1:
                # OCR缺失该章节
                for chunk in ch_chunks2:
                    aligned.append((ChunkData(text="", start_pos=0, end_pos=0, chapter=ch2), chunk))
                continue
            
            if not ch_chunks2:
                # 参考文本缺失该章节
                for chunk in ch_chunks1:
                    aligned.append((chunk, None))
                continue
            
            # 章节内对齐
            chapter_aligned = self._align_within_chapter(ch_chunks1, ch_chunks2)
            aligned.extend(chapter_aligned)
        
        logger.info(f"对齐完成: {len(aligned)} 个文本块对")
        
        return aligned
    
    def _match_chapters(
        self, 
        chapters1: Dict[str, List[ChunkData]], 
        chapters2: Dict[str, List[ChunkData]]
    ) -> List[Tuple[str, Optional[str]]]:
        """匹配两个文件的章节名称"""
        matched = []
        used_ch2 = set()
        
        # 首先尝试精确匹配
        for ch1 in chapters1.keys():
            if ch1 in chapters2:
                matched.append((ch1, ch1))
                used_ch2.add(ch1)
        
        # 然后尝试模糊匹配（包含关系）
        for ch1 in chapters1.keys():
            if any(m[0] == ch1 for m in matched):
                continue
            
            best_match = None
            best_score = 0
            
            for ch2 in chapters2.keys():
                if ch2 in used_ch2:
                    continue
                
                # 计算相似度
                score = self._chapter_name_similarity(ch1, ch2)
                if score > best_score and score > self.similarity_threshold:
                    best_score = score
                    best_match = ch2
            
            if best_match:
                matched.append((ch1, best_match))
                used_ch2.add(best_match)
            else:
                matched.append((ch1, None))
        
        # 添加参考文本中未匹配的章节
        for ch2 in chapters2.keys():
            if ch2 not in used_ch2:
                matched.append(("", ch2))
        
        return matched
    
    def _chapter_name_similarity(self, name1: str, name2: str) -> float:
        """计算章节名称相似度"""
        if not name1 or not name2:
            return 0.0
        
        # 精确匹配
        if name1 == name2:
            return 1.0
        
        # 提取关键信息函数
        def extract_key_info(name):
            """从章节名称中提取关键信息"""
            info = {}
            
            # 提取卷号（如"卷一"、"卷十二"）
            vol_match = re.search(r'卷([一二三四五六七八九十百]+|\d+)', name)
            if vol_match:
                # 转换中文数字为阿拉伯数字
                cn_num = vol_match.group(1)
                cn_to_arab = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
                             '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
                             '十一': '11', '十二': '12', '十三': '13', '十四': '14', '十五': '15',
                             '十六': '16', '十七': '17', '十八': '18', '十九': '19', '二十': '20',
                             '三十': '30', '四十': '40', '五十': '50'}
                info['volume'] = cn_to_arab.get(cn_num, cn_num)
            
            # 提取帝纪/志/列传序号
            diji_match = re.search(r'帝紀第([一二三四五六七八九十]+|\d+)', name)
            if diji_match:
                info['type'] = '帝紀'
                info['seq'] = diji_match.group(1)
            
            zhi_match = re.search(r'志第([一二三四五六七八九十]+|\d+)', name)
            if zhi_match:
                info['type'] = '志'
                info['seq'] = zhi_match.group(1)
            
            liezhuan_match = re.search(r'列傳第([一二三四五六七八九十百]+|\d+)', name)
            if liezhuan_match:
                info['type'] = '列傳'
                info['seq'] = liezhuan_match.group(1)
            
            # 提取人物名（如"高祖上"、"煬帝下"）
            person_match = re.search(r'(高祖|煬帝|恭帝)[上下]?', name)
            if person_match:
                info['person'] = person_match.group(0)
            
            # 提取志名（如"禮儀一"、"音樂上"、"天文下"）
            zhi_name_match = re.search(r'(禮儀|音樂|律曆|天文|五行|食貨|刑法|百官|地理|經籍)[上下一二三四五六七八九十\d]*', name)
            if zhi_name_match:
                info['zhi_name'] = zhi_name_match.group(0)
            
            return info
        
        info1 = extract_key_info(name1)
        info2 = extract_key_info(name2)
        
        # 计算匹配分数
        score = 0.0
        total_checks = 0
        
        # 检查卷号
        if 'volume' in info1 and 'volume' in info2:
            total_checks += 1
            if info1['volume'] == info2['volume']:
                score += 1.0
        
        # 检查类型（帝纪/志/列传）
        if 'type' in info1 and 'type' in info2:
            total_checks += 1
            if info1['type'] == info2['type']:
                score += 1.0
                # 如果类型相同，检查序号
                if 'seq' in info1 and 'seq' in info2:
                    total_checks += 0.5
                    if info1['seq'] == info2['seq']:
                        score += 0.5
        
        # 检查人物名
        if 'person' in info1 and 'person' in info2:
            total_checks += 1
            if info1['person'] == info2['person']:
                score += 1.0
        
        # 检查志名
        if 'zhi_name' in info1 and 'zhi_name' in info2:
            total_checks += 1
            if info1['zhi_name'] == info2['zhi_name']:
                score += 1.0
            elif info1['zhi_name'].rstrip('上下一二三四五六七八九十') == info2['zhi_name'].rstrip('上下一二三四五六七八九十'):
                score += 0.7  # 志名相同但后缀不同
        
        # 如果没有关键信息匹配，使用字符重叠
        if total_checks == 0:
            set1 = set(name1)
            set2 = set(name2)
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            return intersection / union if union > 0 else 0.0
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _group_by_chapter(self, chunks: List[ChunkData]) -> Dict[str, List[ChunkData]]:
        """按章节分组"""
        grouped = defaultdict(list)
        for chunk in chunks:
            grouped[chunk.chapter].append(chunk)
        return grouped
    
    def _align_within_chapter(
        self, 
        chunks1: List[ChunkData], 
        chunks2: List[ChunkData]
    ) -> List[Tuple[ChunkData, Optional[ChunkData]]]:
        """章节内对齐"""
        aligned = []
        
        if not chunks1 or not chunks2:
            for chunk in chunks1:
                aligned.append((chunk, None))
            for chunk in chunks2:
                aligned.append((ChunkData(text="", start_pos=0, end_pos=0), chunk))
            return aligned
        
        # 基于位置比例对齐
        len1 = sum(c.length for c in chunks1)
        len2 = sum(c.length for c in chunks2)
        
        pos1 = 0
        pos2 = 0
        idx1 = 0
        idx2 = 0
        
        while idx1 < len(chunks1) or idx2 < len(chunks2):
            if idx1 >= len(chunks1):
                # 剩余的chunks2
                aligned.append((ChunkData(text="", start_pos=0, end_pos=0), chunks2[idx2]))
                idx2 += 1
            elif idx2 >= len(chunks2):
                # 剩余的chunks1
                aligned.append((chunks1[idx1], None))
                idx1 += 1
            else:
                # 计算相对位置
                rel_pos1 = pos1 / len1 if len1 > 0 else 0
                rel_pos2 = pos2 / len2 if len2 > 0 else 0
                
                if abs(rel_pos1 - rel_pos2) < 0.1:  # 位置相近
                    aligned.append((chunks1[idx1], chunks2[idx2]))
                    pos1 += chunks1[idx1].length
                    pos2 += chunks2[idx2].length
                    idx1 += 1
                    idx2 += 1
                elif rel_pos1 < rel_pos2:
                    # chunks1落后
                    aligned.append((chunks1[idx1], None))
                    pos1 += chunks1[idx1].length
                    idx1 += 1
                else:
                    # chunks2落后
                    aligned.append((ChunkData(text="", start_pos=0, end_pos=0), chunks2[idx2]))
                    pos2 += chunks2[idx2].length
                    idx2 += 1
        
        return aligned
    
    def _global_align(
        self, 
        chunks1: List[ChunkData], 
        chunks2: List[ChunkData]
    ) -> List[Tuple[ChunkData, Optional[ChunkData]]]:
        """全局文本对齐（当章节匹配失败时使用）"""
        logger.info("使用全局对齐策略")
        aligned = []
        
        if not chunks1 or not chunks2:
            for chunk in chunks1:
                aligned.append((chunk, None))
            for chunk in chunks2:
                aligned.append((ChunkData(text="", start_pos=0, end_pos=0), chunk))
            return aligned
        
        # 计算总长度
        len1 = sum(c.length for c in chunks1)
        len2 = sum(c.length for c in chunks2)
        
        # 基于位置比例的全局对齐
        pos1 = 0
        pos2 = 0
        idx1 = 0
        idx2 = 0
        
        while idx1 < len(chunks1) and idx2 < len(chunks2):
            chunk1 = chunks1[idx1]
            chunk2 = chunks2[idx2]
            
            # 计算相对位置
            rel_pos1 = pos1 / len1 if len1 > 0 else 0
            rel_pos2 = pos2 / len2 if len2 > 0 else 0
            
            # 如果位置相近，配对
            if abs(rel_pos1 - rel_pos2) < self.position_tolerance:
                aligned.append((chunk1, chunk2))
                pos1 += chunk1.length
                pos2 += chunk2.length
                idx1 += 1
                idx2 += 1
            elif rel_pos1 < rel_pos2:
                # OCR落后
                aligned.append((chunk1, None))
                pos1 += chunk1.length
                idx1 += 1
            else:
                # 参考文本落后
                aligned.append((ChunkData(text="", start_pos=0, end_pos=0), chunk2))
                pos2 += chunk2.length
                idx2 += 1
        
        # 处理剩余
        while idx1 < len(chunks1):
            aligned.append((chunks1[idx1], None))
            idx1 += 1
        while idx2 < len(chunks2):
            aligned.append((ChunkData(text="", start_pos=0, end_pos=0), chunks2[idx2]))
            idx2 += 1
        
        return aligned
