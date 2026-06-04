#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试脚本
测试后端API的各个端点
"""

import requests
import json
import sys
from pathlib import Path

# API基础URL
BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("\n" + "="*60)
    print("测试: 健康检查")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 健康检查通过")
            return True
        else:
            print("❌ 健康检查失败")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


def test_config():
    """测试配置接口"""
    print("\n" + "="*60)
    print("测试: 配置接口")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/config")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"OCR路径数: {len(data.get('ocr_base_paths', []))}")
            print(f"参考路径: {data.get('reference_base_path')}")
            print(f"Embedding API: {data.get('embedding_api_url')}")
            print("✅ 配置接口正常")
            return True
        else:
            print("❌ 配置接口失败")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_file_base_paths():
    """测试文件基础路径"""
    print("\n" + "="*60)
    print("测试: 文件基础路径")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/files/base-paths")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"OCR路径: {data.get('ocr_paths')}")
            print(f"参考路径: {data.get('reference_path')}")
            print("✅ 文件基础路径接口正常")
            return True
        else:
            print("❌ 文件基础路径接口失败")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_file_browse():
    """测试文件浏览"""
    print("\n" + "="*60)
    print("测试: 文件浏览")
    print("="*60)
    
    try:
        # 先获取基础路径
        config_resp = requests.get(f"{BASE_URL}/api/files/base-paths")
        if config_resp.status_code != 200:
            print("❌ 无法获取基础路径")
            return False
        
        base_paths = config_resp.json().get('ocr_paths', [])
        if not base_paths:
            print("⚠️  未配置OCR路径，跳过测试")
            return True
        
        # 测试浏览第一个路径
        test_path = base_paths[0]
        print(f"测试路径: {test_path}")
        
        response = requests.get(f"{BASE_URL}/api/files/browse", params={"path": test_path})
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"项目数: {data.get('total_items')}")
            print(f"前5个项目:")
            for item in data.get('items', [])[:5]:
                print(f"  - {item['name']} ({item['type']})")
            print("✅ 文件浏览接口正常")
            return True
        else:
            print(f"❌ 文件浏览失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_annotation_types():
    """测试标注类型接口"""
    print("\n" + "="*60)
    print("测试: 标注类型接口")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/annotations/types")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"标注类型数: {len(data.get('types', []))}")
            for t in data.get('types', []):
                print(f"  - {t['icon']} {t['name']}: {t['description']}")
            print("✅ 标注类型接口正常")
            return True
        else:
            print("❌ 标注类型接口失败")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_annotation_stats():
    """测试标注统计接口"""
    print("\n" + "="*60)
    print("测试: 标注统计接口")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/annotations/stats")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"总标注数: {data.get('total_annotations')}")
            print(f"平均确信度: {data.get('avg_confidence')}")
            print(f"按状态: {data.get('by_status')}")
            print("✅ 标注统计接口正常")
            return True
        else:
            print("❌ 标注统计接口失败")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_embedding_api_status():
    """测试Embedding API状态"""
    print("\n" + "="*60)
    print("测试: Embedding API状态")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/similarity/api-status")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API URL: {data.get('api_url')}")
            print(f"状态: {data.get('status', {}).get('status')}")
            
            if data.get('status', {}).get('status') == 'online':
                print("✅ Embedding API可用")
                return True
            else:
                print("⚠️  Embedding API不可用，但接口正常")
                return True
        else:
            print("❌ Embedding API状态检查失败")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("古籍标注平台 - 集成测试")
    print("="*60)
    
    print(f"\n测试目标: {BASE_URL}")
    print("请确保后端服务已启动\n")
    
    # 运行所有测试
    tests = [
        ("健康检查", test_health),
        ("配置接口", test_config),
        ("文件基础路径", test_file_base_paths),
        ("文件浏览", test_file_browse),
        ("标注类型", test_annotation_types),
        ("标注统计", test_annotation_stats),
        ("Embedding API状态", test_embedding_api_status),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}测试异常: {e}")
            results.append((name, False))
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常。")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查相关功能。")
        sys.exit(1)


if __name__ == "__main__":
    main()