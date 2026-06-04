#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Embedding API客户端
"""

import time
import logging
import requests
import numpy as np
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Embedding API客户端"""
    
    def __init__(
        self,
        api_url: str,
        model: str = "embedding",
        batch_size: int = 32,
        timeout: int = 60,
        max_retries: int = 3
    ):
        self.api_url = api_url
        self.model = model
        self.batch_size = batch_size
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.timeout = timeout
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """获取单个文本的embedding"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    f"{self.api_url}/embeddings",
                    json={
                        "input": text,
                        "model": self.model
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["data"][0]["embedding"]
                else:
                    logger.warning(f"API返回错误: {response.status_code}, {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时，尝试 {attempt + 1}/{self.max_retries}")
            except Exception as e:
                logger.error(f"获取embedding失败: {e}")
                
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
        
        return None
    
    def get_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """批量获取embeddings"""
        embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = []
            
            # 并行请求
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {
                    executor.submit(self.get_embedding, text): idx
                    for idx, text in enumerate(batch)
                }
                
                results = [None] * len(batch)
                for future in as_completed(futures):
                    idx = futures[future]
                    try:
                        results[idx] = future.result()
                    except Exception as e:
                        logger.error(f"批量请求失败: {e}")
                
                batch_embeddings = results
            
            embeddings.extend(batch_embeddings)
            logger.info(f"已处理 {min(i + self.batch_size, len(texts))}/{len(texts)} 个文本块")
            
            if i + self.batch_size < len(texts):
                time.sleep(0.5)
        
        return embeddings
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def compute_similarity_matrix(
        self,
        embeddings1: List[Optional[List[float]]],
        embeddings2: List[Optional[List[float]]]
    ) -> List[List[float]]:
        """计算相似度矩阵"""
        matrix = []
        
        for i, emb1 in enumerate(embeddings1):
            row = []
            if emb1 is None:
                row = [0.0] * len(embeddings2)
            else:
                for j, emb2 in enumerate(embeddings2):
                    if emb2 is None:
                        row.append(0.0)
                    else:
                        row.append(self.cosine_similarity(emb1, emb2))
            matrix.append(row)
        
        return matrix
    
    def check_api_status(self) -> Dict[str, Any]:
        """检查API状态"""
        try:
            response = self.session.get(
                f"{self.api_url}/models",
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "status": "online",
                    "models": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"API返回状态码: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "offline",
                "message": str(e)
            }