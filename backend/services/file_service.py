#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件浏览服务
支持本地和远程服务器文件访问
"""

import os
import re
import json
import logging
import hashlib
import paramiko
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

from config import settings
from models.schemas import FileInfo, FileType, FileBrowseResponse, FilePreviewResponse

logger = logging.getLogger(__name__)


class FileService:
    """文件浏览服务"""
    
    def __init__(self):
        self.use_ssh = settings.USE_SSH
        self.ssh_client = None
        
        # 如果配置了SSH，尝试连接
        if self.use_ssh and settings.REMOTE_SERVER_USER and settings.REMOTE_SERVER_PASSWORD:
            self._init_ssh_connection()
        
        # 配置基础路径映射
        # 如果在Windows上运行，可能需要映射远程路径到本地
        self.path_mapping = {}
        self._init_path_mapping()
    
    def _init_ssh_connection(self):
        """初始化SSH连接"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=settings.REMOTE_SERVER_HOST,
                username=settings.REMOTE_SERVER_USER,
                password=settings.REMOTE_SERVER_PASSWORD,
                timeout=10
            )
            logger.info(f"SSH连接成功: {settings.REMOTE_SERVER_HOST}")
        except Exception as e:
            logger.error(f"SSH连接失败: {e}")
            self.ssh_client = None
            self.use_ssh = False
    
    def _init_path_mapping(self):
        """初始化路径映射（用于Windows本地开发测试）"""
        # 如果远程路径映射到本地，可以在这里配置
        # 例如: self.path_mapping["/home/maxuejiao/guji"] = "G:\\映射的本地路径"
        pass
    
    def _map_path(self, path: str) -> str:
        """路径映射"""
        for remote_prefix, local_prefix in self.path_mapping.items():
            if path.startswith(remote_prefix):
                return path.replace(remote_prefix, local_prefix)
        return path
    
    def _is_remote_path(self, path: str) -> bool:
        """判断是否是远程路径"""
        # 如果路径以配置的远程基础路径开头，则是远程路径
        for base_path in settings.OCR_BASE_PATHS + [settings.REFERENCE_BASE_PATH]:
            if path.startswith(base_path):
                return True
        return False
    
    def _list_local_directory(self, path: str) -> List[FileInfo]:
        """列出本地目录内容"""
        items = []
        mapped_path = self._map_path(path)
        
        try:
            if not os.path.exists(mapped_path):
                logger.error(f"路径不存在: {mapped_path}")
                return items
            
            for item in os.listdir(mapped_path):
                item_path = os.path.join(mapped_path, item)
                full_path = path if not self.path_mapping else path
                
                # 保持原始路径（远程路径格式）
                original_item_path = os.path.join(full_path, item)
                
                try:
                    is_dir = os.path.isdir(item_path)
                    size = None if is_dir else os.path.getsize(item_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(item_path))
                    
                    file_count = None
                    if is_dir:
                        # 计算目录下的文件数量
                        try:
                            file_count = len([f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))])
                        except:
                            file_count = 0
                    
                    items.append(FileInfo(
                        name=item,
                        type=FileType.DIRECTORY if is_dir else FileType.FILE,
                        path=original_item_path,
                        size=size,
                        modified=modified,
                        file_count=file_count,
                        is_readable=True
                    ))
                except Exception as e:
                    logger.warning(f"读取文件信息失败: {item_path}, {e}")
                    items.append(FileInfo(
                        name=item,
                        type=FileType.FILE,
                        path=original_item_path,
                        is_readable=False
                    ))
            
            # 排序：目录在前，文件在后，按名称排序
            items.sort(key=lambda x: (x.type != FileType.DIRECTORY, x.name))
            
        except Exception as e:
            logger.error(f"列出目录失败: {path}, {e}")
        
        return items
    
    def _list_remote_directory_ssh(self, path: str) -> List[FileInfo]:
        """通过SSH列出远程目录内容"""
        items = []
        
        if not self.ssh_client:
            logger.error("SSH客户端未初始化")
            return items
        
        try:
            # 使用SSH执行命令列出目录
            command = f'ls -la "{path}"'
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            if error:
                logger.error(f"SSH命令错误: {error}")
                return items
            
            lines = output.split('\n')
            for line in lines[1:]:  # 跳过第一行(total ...)
                if not line.strip():
                    continue
                
                # 解析 ls -la 输出
                parts = line.split()
                if len(parts) < 9:
                    continue
                
                permissions = parts[0]
                name = parts[-1]
                
                # 跳过 . 和 ..
                if name in ['.', '..']:
                    continue
                
                is_dir = permissions.startswith('d')
                item_path = os.path.join(path, name)
                
                try:
                    size = int(parts[4]) if not is_dir else None
                    modified_str = f"{parts[5]} {parts[6]} {parts[7]}"
                    
                    # 获取目录下的文件数量
                    file_count = None
                    if is_dir:
                        count_cmd = f'find "{item_path}" -maxdepth 1 -type f | wc -l'
                        _, count_out, _ = self.ssh_client.exec_command(count_cmd)
                        file_count = int(count_out.read().decode('utf-8').strip())
                    
                    items.append(FileInfo(
                        name=name,
                        type=FileType.DIRECTORY if is_dir else FileType.FILE,
                        path=item_path,
                        size=size,
                        modified=None,  # SSH的日期解析比较复杂，暂时跳过
                        file_count=file_count,
                        is_readable=True
                    ))
                except Exception as e:
                    logger.warning(f"解析文件信息失败: {line}, {e}")
            
            # 排序
            items.sort(key=lambda x: (x.type != FileType.DIRECTORY, x.name))
            
        except Exception as e:
            logger.error(f"SSH列出目录失败: {path}, {e}")
        
        return items
    
    def browse_directory(self, path: str) -> FileBrowseResponse:
        """浏览目录"""
        if self._is_remote_path(path) and self.use_ssh:
            items = self._list_remote_directory_ssh(path)
        else:
            items = self._list_local_directory(path)
        
        # 计算父目录路径
        parent = None
        if path != "/" and path != "":
            parent = str(Path(path).parent)
        
        return FileBrowseResponse(
            path=path,
            items=items,
            parent=parent,
            total_items=len(items)
        )
    
    def preview_file(self, file_path: str, lines: int = None) -> FilePreviewResponse:
        """预览文件内容"""
        content = ""
        encoding = "utf-8"
        
        lines = lines or settings.FILE_PREVIEW_LINES
        
        if self._is_remote_path(file_path) and self.use_ssh:
            content = self._read_remote_file_ssh(file_path, lines)
        else:
            content = self._read_local_file(file_path, lines)
        
        total_lines = content.count('\n') + 1
        
        return FilePreviewResponse(
            path=file_path,
            content=content,
            total_lines=total_lines,
            encoding=encoding
        )
    
    def _read_local_file(self, file_path: str, lines: int) -> str:
        """读取本地文件"""
        mapped_path = self._map_path(file_path)
        
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5']
        
        for encoding in encodings:
            try:
                with open(mapped_path, 'r', encoding=encoding) as f:
                    content_lines = []
                    for i, line in enumerate(f):
                        if i >= lines:
                            break
                        content_lines.append(line)
                    return ''.join(content_lines)
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"读取文件失败: {file_path}, {e}")
                return f"读取文件失败: {str(e)}"
        
        return "无法解码文件"
    
    def _read_remote_file_ssh(self, file_path: str, lines: int) -> str:
        """通过SSH读取远程文件"""
        if not self.ssh_client:
            return "SSH客户端未初始化"
        
        try:
            # 使用 head 命令读取前N行
            command = f'head -n {lines} "{file_path}"'
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            
            content = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            if error:
                logger.warning(f"SSH读取警告: {error}")
            
            return content
            
        except Exception as e:
            logger.error(f"SSH读取文件失败: {file_path}, {e}")
            return f"读取文件失败: {str(e)}"
    
    def search_files(self, query: str, scope: str = "all") -> List[FileInfo]:
        """搜索文件"""
        results = []
        
        # 确定搜索范围
        search_paths = []
        if scope == "all":
            search_paths = settings.OCR_BASE_PATHS + [settings.REFERENCE_BASE_PATH]
        elif scope == "ocr":
            search_paths = settings.OCR_BASE_PATHS
        elif scope == "reference":
            search_paths = [settings.REFERENCE_BASE_PATH]
        else:
            search_paths = [scope]  # 自定义范围
        
        for base_path in search_paths:
            results.extend(self._search_in_path(base_path, query))
        
        return results
    
    def _search_in_path(self, path: str, query: str, max_results: int = 100) -> List[FileInfo]:
        """在指定路径下搜索"""
        results = []
        
        # 简化实现：只搜索当前目录
        try:
            browse_result = self.browse_directory(path)
            for item in browse_result.items:
                if query.lower() in item.name.lower():
                    results.append(item)
                    if len(results) >= max_results:
                        break
            
            # 如果结果不足，递归搜索子目录（简化版，只搜索一层）
            if len(results) < max_results:
                for item in browse_result.items:
                    if item.type == FileType.DIRECTORY:
                        sub_results = self._search_in_path(item.path, query, max_results - len(results))
                        results.extend(sub_results)
                        if len(results) >= max_results:
                            break
        
        except Exception as e:
            logger.error(f"搜索失败: {path}, {e}")
        
        return results[:max_results]
    
    def match_files(self, ocr_file: str) -> List[Dict[str, Any]]:
        """匹配OCR文件到参考文件"""
        recommendations = []
        
        # 提取OCR文件名中的关键信息
        ocr_filename = os.path.basename(ocr_file)
        ocr_dirname = os.path.basename(os.path.dirname(ocr_file))
        
        # 搜索参考文件目录
        try:
            browse_result = self.browse_directory(settings.REFERENCE_BASE_PATH)
            
            for item in browse_result.items:
                if item.type == FileType.DIRECTORY:
                    # 检查目录名是否匹配
                    score = self._calculate_name_similarity(ocr_dirname, item.name)
                    if score > 0.3:
                        # 进一步搜索子目录
                        sub_result = self.browse_directory(item.path)
                        for sub_item in sub_result.items:
                            if sub_item.type == FileType.FILE:
                                file_score = self._calculate_name_similarity(ocr_filename, sub_item.name)
                                if file_score > 0.5:
                                    recommendations.append({
                                        "path": sub_item.path,
                                        "score": file_score,
                                        "reason": f"文件名相似度: {file_score:.2f}"
                                    })
            
            # 按分数排序
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            
        except Exception as e:
            logger.error(f"文件匹配失败: {e}")
        
        return recommendations[:10]  # 返回前10个推荐
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """计算名称相似度"""
        # 简化实现：基于字符串包含关系
        name1_clean = re.sub(r'[·\[\]()（）\s]', '', name1.lower())
        name2_clean = re.sub(r'[·\[\]()（）\s]', '', name2.lower())
        
        if name1_clean == name2_clean:
            return 1.0
        
        if name1_clean in name2_clean or name2_clean in name1_clean:
            return 0.7
        
        # Jaccard相似度
        set1 = set(name1_clean)
        set2 = set(name2_clean)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_file_tree(self) -> Dict[str, Any]:
        """获取文件树结构"""
        tree = {
            "ocr": {},
            "reference": {}
        }
        
        # OCR文件树
        for base_path in settings.OCR_BASE_PATHS:
            category = os.path.basename(base_path)  # 如: "二十四史附清史稿_ocr"
            if category not in tree["ocr"]:
                tree["ocr"][category] = {}
            
            tree["ocr"][category][base_path] = self._build_tree(base_path)
        
        # 参考文件树
        tree["reference"][settings.REFERENCE_BASE_PATH] = self._build_tree(settings.REFERENCE_BASE_PATH)
        
        return tree
    
    def _build_tree(self, path: str, depth: int = 0, max_depth: int = 2) -> Dict[str, Any]:
        """构建目录树"""
        if depth >= max_depth:
            return {"path": path, "truncated": True}
        
        tree_node = {
            "path": path,
            "children": []
        }
        
        try:
            browse_result = self.browse_directory(path)
            
            for item in browse_result.items[:50]:  # 限制数量
                child_node = {
                    "name": item.name,
                    "type": item.type.value,
                    "path": item.path
                }
                
                if item.type == FileType.DIRECTORY:
                    child_node["children"] = self._build_tree(item.path, depth + 1, max_depth)
                
                tree_node["children"].append(child_node)
        
        except Exception as e:
            logger.error(f"构建树失败: {path}, {e}")
            tree_node["error"] = str(e)
        
        return tree_node
    
    def close(self):
        """关闭SSH连接"""
        if self.ssh_client:
            self.ssh_client.close()
            logger.info("SSH连接已关闭")