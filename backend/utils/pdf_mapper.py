#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF页码映射工具
基于OCR文件路径和文本位置推断原PDF文件的页码
"""

import re
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class PDFMapper:
    """PDF页码映射器"""
    
    def __init__(self, pdf_base_paths: list):
        """
        初始化PDF映射器
        
        Args:
            pdf_base_paths: PDF文件基础路径列表
                          例如: ["/mnt/skill/guji/十三经注疏", "/mnt/skill/guji/二十四史附清史稿"]
        """
        self.pdf_base_paths = [Path(p) for p in pdf_base_paths]
    
    def map_ocr_to_pdf(
        self,
        ocr_file_path: str,
        text_position: Dict[str, int],
        total_text_length: int
    ) -> Optional[Dict]:
        """
        从OCR文件路径和文本位置推断PDF文件和页码
        
        Args:
            ocr_file_path: OCR文件路径
            text_position: 文本位置 {start, end}
            total_text_length: 文本总长度
            
        Returns:
            {
                "pdf_file": "/path/to/file.pdf",
                "pdf_page": 123,
                "confidence": 0.8  # 推断置信度
            }
            或 None（无法映射）
        """
        try:
            # 1. 从OCR文件名推断PDF文件名
            pdf_file = self._infer_pdf_file(ocr_file_path)
            if not pdf_file:
                logger.warning(f"无法推断PDF文件: {ocr_file_path}")
                return None
            
            # 2. 从文本位置推断页码
            # 假设每个PDF页面的平均字符数（古籍通常每页300-500字）
            avg_chars_per_page = 400
            
            # 计算相对位置
            relative_position = text_position.get("start", 0) / max(total_text_length, 1)
            
            # 估算页码（从1开始）
            estimated_page = int(relative_position * (total_text_length / avg_chars_per_page)) + 1
            
            # 计算置信度（基于位置接近程度）
            # 越靠前越可信（因为前面的文本通常更稳定）
            confidence = max(0.5, 1.0 - relative_position * 0.5)
            
            return {
                "pdf_file": str(pdf_file),
                "pdf_page": estimated_page,
                "confidence": round(confidence, 2)
            }
            
        except Exception as e:
            logger.error(f"PDF映射失败: {e}")
            return None
    
    def _infer_pdf_file(self, ocr_file_path: str) -> Optional[Path]:
        """
        从OCR文件路径推断原PDF文件路径
        
        命名规则示例:
        - OCR: /home/maxuejiao/guji/mineru_ocr/二十四史附清史稿_ocr/隋书·[唐]魏征·(二十五史)·中华书局1973/隋书·[唐]魏征·(二十五史)·中华书局1973.md
        - PDF: /mnt/skill/guji/二十四史附清史稿/隋书/隋书.pdf
        
        逻辑:
        1. 提取书名（如"隋书"）
        2. 在PDF基础路径中搜索匹配的文件
        """
        try:
            ocr_path = Path(ocr_file_path)
            
            # 提取书名（简化版：取OCR文件名的第一部分）
            file_name = ocr_path.stem  # 不含扩展名
            
            # 常见模式：书名·作者·版本
            # 尝试提取书名
            book_name = file_name.split('·')[0] if '·' in file_name else file_name
            
            # 清理书名
            book_name = book_name.replace('_', '').strip()
            
            # 在PDF基础路径中搜索
            for base_path in self.pdf_base_paths:
                if not base_path.exists():
                    continue
                
                # 递归搜索匹配的PDF文件
                for pdf_file in base_path.rglob("*.pdf"):
                    # 简单匹配：PDF文件名包含书名
                    if book_name in pdf_file.stem:
                        logger.info(f"找到PDF文件: {pdf_file}")
                        return pdf_file
            
            logger.warning(f"未找到匹配的PDF文件: {book_name}")
            return None
            
        except Exception as e:
            logger.error(f"推断PDF文件失败: {e}")
            return None
    
    def get_pdf_info_from_ocr_dir(self, ocr_dir: str) -> Dict[str, str]:
        """
        从OCR目录结构推断PDF文件映射表
        
        Args:
            ocr_dir: OCR文件目录
            
        Returns:
            {ocr_subdir_name: pdf_file_path}
        """
        mapping = {}
        
        try:
            ocr_path = Path(ocr_dir)
            if not ocr_path.exists():
                return mapping
            
            # 遍历OCR目录
            for item in ocr_path.iterdir():
                if item.is_dir():
                    # 尝试匹配PDF文件
                    pdf_file = self._infer_pdf_file(str(item))
                    if pdf_file:
                        mapping[item.name] = str(pdf_file)
            
        except Exception as e:
            logger.error(f"生成PDF映射表失败: {e}")
        
        return mapping


# 使用示例
if __name__ == "__main__":
    mapper = PDFMapper([
        "/mnt/skill/guji/十三经注疏",
        "/mnt/skill/guji/二十四史附清史稿"
    ])
    
    result = mapper.map_ocr_to_pdf(
        ocr_file_path="/home/maxuejiao/guji/mineru_ocr/二十四史附清史稿_ocr/隋书·[唐]魏征·(二十五史)·中华书局1973/隋书·[唐]魏征·(二十五史)·中华书局1973.md",
        text_position={"start": 5000, "end": 5500},
        total_text_length=100000
    )
    
    print(f"映射结果: {result}")
