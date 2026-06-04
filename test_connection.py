#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接测试脚本
用于验证是否能访问远程服务器和Embedding服务
"""

import requests
import os
import sys
from pathlib import Path

# 添加backend目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from config import settings


def test_network_connection():
    """测试网络连接"""
    print("="*60)
    print("网络连接测试")
    print("="*60)
    
    host = settings.REMOTE_SERVER_HOST
    print(f"\n测试服务器连接: {host}")
    
    try:
        import socket
        socket.setdefaulttimeout(5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, 22))
        print(f"✅ 成功连接到服务器 {host}:22 (SSH)")
    except Exception as e:
        print(f"❌ 无法连接到服务器 {host}:22 - {e}")
        print("   建议: 检查网络连接，确保能访问内网")
    
    print()


def test_embedding_api():
    """测试Embedding API"""
    print("="*60)
    print("Embedding API测试")
    print("="*60)
    
    api_url = settings.EMBEDDING_API_URL
    print(f"\nAPI地址: {api_url}")
    
    # 测试模型列表接口
    try:
        response = requests.get(f"{api_url}/models", timeout=10)
        if response.status_code == 200:
            print("✅ Embedding API 可访问")
            print(f"   返回数据: {response.json()}")
        else:
            print(f"❌ API返回错误: {response.status_code}")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        print("   建议: 检查网络连接或增加超时时间")
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败")
        print("   建议: 检查API地址和网络连接")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 测试embedding计算
    print("\n测试文本embedding计算...")
    try:
        response = requests.post(
            f"{api_url}/embeddings",
            json={
                "input": "测试文本",
                "model": settings.EMBEDDING_MODEL
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                embedding = data["data"][0]["embedding"]
                print(f"✅ Embedding计算成功，维度: {len(embedding)}")
            else:
                print(f"❌ 返回数据格式异常: {data}")
        else:
            print(f"❌ 计算失败: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Embedding计算测试失败: {e}")
    
    print()


def test_file_access():
    """测试文件访问"""
    print("="*60)
    print("文件访问测试")
    print("="*60)
    
    print("\n配置的OCR路径:")
    for i, path in enumerate(settings.OCR_BASE_PATHS, 1):
        print(f"  {i}. {path}")
        if os.path.exists(path):
            print(f"     ✅ 路径存在")
            try:
                items = os.listdir(path)
                print(f"     📁 包含 {len(items)} 个项目")
            except Exception as e:
                print(f"     ❌ 无法列出目录: {e}")
        else:
            print(f"     ❌ 路径不存在")
    
    print(f"\n参考文本路径: {settings.REFERENCE_BASE_PATH}")
    if os.path.exists(settings.REFERENCE_BASE_PATH):
        print("  ✅ 路径存在")
    else:
        print("  ❌ 路径不存在")
    
    print("\n标注保存路径: {settings.ANNOTATION_OUTPUT_PATH}")
    try:
        os.makedirs(settings.ANNOTATION_OUTPUT_PATH, exist_ok=True)
        print("  ✅ 路径已创建/存在")
    except Exception as e:
        print(f"  ❌ 无法创建路径: {e}")
    
    print()


def main():
    """主函数"""
    print("\n"+"="*60)
    print("古籍标注平台 - 连接测试")
    print("="*60+"\n")
    
    print(f"服务器地址: {settings.REMOTE_SERVER_HOST}")
    print(f"Embedding API: {settings.EMBEDDING_API_URL}")
    print(f"调试模式: {settings.DEBUG}")
    print()
    
    # 运行测试
    test_network_connection()
    test_embedding_api()
    test_file_access()
    
    print("="*60)
    print("测试完成")
    print("="*60)
    print("\n如果所有测试都通过，可以启动服务:")
    print("  后端: python backend/main.py")
    print("  前端: cd frontend && npm run dev")
    print()


if __name__ == "__main__":
    main()