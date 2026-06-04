#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目文件完整性检查脚本
"""

import os
from pathlib import Path

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    exists = Path(filepath).exists()
    status = "[OK]" if exists else "[MISS]"
    print(f"  {status} {description}: {filepath}")
    return exists

def main():
    """主函数"""
    print("\n" + "="*60)
    print("项目文件完整性检查")
    print("="*60 + "\n")
    
    base_dir = Path(__file__).parent
    
    # 定义需要检查的文件
    required_files = {
        "文档": [
            ("README.md", "项目说明"),
            (".gitignore", "Git忽略配置"),
            ("docs/project-plan.md", "项目计划"),
            ("docs/QUICKSTART.md", "快速开始指南"),
        ],
        "后端核心": [
            ("backend/main.py", "主入口"),
            ("backend/config.py", "配置文件"),
            ("backend/requirements.txt", "依赖列表"),
        ],
        "后端API": [
            ("backend/api/__init__.py", "API包初始化"),
            ("backend/api/files.py", "文件API"),
            ("backend/api/similarity.py", "相似度API"),
            ("backend/api/annotations.py", "标注API"),
        ],
        "后端服务": [
            ("backend/services/__init__.py", "服务包初始化"),
            ("backend/services/file_service.py", "文件服务"),
            ("backend/services/similarity_service.py", "相似度服务"),
            ("backend/services/annotation_service.py", "标注服务"),
        ],
        "后端模型": [
            ("backend/models/__init__.py", "模型包初始化"),
            ("backend/models/schemas.py", "数据模型"),
        ],
        "后端工具": [
            ("backend/utils/__init__.py", "工具包初始化"),
            ("backend/utils/text_processor.py", "文本处理器"),
            ("backend/utils/embedding_client.py", "Embedding客户端"),
        ],
        "前端核心": [
            ("frontend/package.json", "Node配置"),
            ("frontend/tsconfig.json", "TypeScript配置"),
            ("frontend/vite.config.ts", "Vite配置"),
            ("frontend/tailwind.config.js", "Tailwind配置"),
        ],
        "前端源码": [
            ("frontend/src/main.tsx", "应用入口"),
            ("frontend/src/App.tsx", "主应用"),
            ("frontend/src/index.css", "样式文件"),
        ],
        "前端组件": [
            ("frontend/src/components/Layout/MainLayout.tsx", "主布局"),
            ("frontend/src/components/FileBrowser/FileBrowser.tsx", "文件浏览器"),
            ("frontend/src/components/Annotation/AnnotationEditor.tsx", "标注编辑器"),
        ],
        "前端页面": [
            ("frontend/src/pages/HomePage.tsx", "首页"),
            ("frontend/src/pages/ComparePage.tsx", "对比页"),
            ("frontend/src/pages/AnnotationPage.tsx", "标注页"),
            ("frontend/src/pages/StatsPage.tsx", "统计页"),
        ],
        "前端服务": [
            ("frontend/src/services/api.ts", "API客户端"),
            ("frontend/src/services/fileApi.ts", "文件API"),
            ("frontend/src/services/similarityApi.ts", "相似度API"),
            ("frontend/src/services/annotationApi.ts", "标注API"),
        ],
        "测试脚本": [
            ("test_connection.py", "连接测试"),
            ("test_integration.py", "集成测试"),
        ],
        "启动脚本": [
            ("start-backend.bat", "后端启动脚本"),
            ("start-frontend.bat", "前端启动脚本"),
            ("run_tests.bat", "测试运行脚本"),
        ],
    }
    
    total_files = 0
    existing_files = 0
    
    for category, files in required_files.items():
        print(f"\n{category}:")
        for filepath, description in files:
            full_path = base_dir / filepath
            exists = check_file_exists(full_path, description)
            total_files += 1
            if exists:
                existing_files += 1
    
    # 打印统计
    print("\n" + "="*60)
    print("检查完成")
    print("="*60)
    print(f"\n总文件数: {total_files}")
    print(f"存在文件: {existing_files}")
    print(f"缺失文件: {total_files - existing_files}")
    
    if existing_files == total_files:
        print("\n[SUCCESS] All files are complete!")
        return 0
    else:
        print(f"\n[WARNING] {total_files - existing_files} files are missing")
        return 1

if __name__ == "__main__":
    exit(main())