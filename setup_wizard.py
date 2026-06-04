#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速配置向导
自动检测环境并生成合适的配置
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except:
        return -1, "", ""

print("\n" + "="*60)
print("古籍标注平台 - 快速配置向导")
print("="*60 + "\n")

# 检测操作系统
import platform
is_windows = platform.system() == 'Windows'
print(f"操作系统: {platform.system()}")
print(f"Python版本: {platform.python_version()}")
print()

# 检测SSH
print("="*60)
print("1. 检测SSH连接")
print("="*60 + "\n")

ssh_available = False
ssh_user = ""

if is_windows:
    # Windows下检测ssh命令
    ret, out, err = run_command("ssh -V")
    if ret == 0:
        print("✓ SSH客户端可用")
        print(f"  版本: {out or err}")
        ssh_available = True
    else:
        print("✗ SSH客户端不可用")
        print("  请安装OpenSSH或使用PuTTY")
else:
    ssh_available = True
    print("✓ SSH客户端可用")

# 测试SSH连接
if ssh_available:
    print("\n尝试测试SSH连接...")
    ret, out, err = run_command("ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no 172.23.40.162 'echo SSH_OK'")
    if "SSH_OK" in out:
        print("✓ SSH连接成功（可能已配置密钥）")
    else:
        print("✗ SSH连接需要密码认证")
        ssh_user = input("\n请输入SSH用户名（或按Enter跳过）: ").strip()
        if ssh_user:
            print(f"已记录用户名: {ssh_user}")

print()

# 检测Embedding服务
print("="*60)
print("2. 检测Embedding服务")
print("="*60 + "\n")

import urllib.request
import urllib.error

embedding_accessible = False
embedding_url = "http://172.23.40.162:8180/v1/models"

print(f"尝试访问: {embedding_url}")
try:
    req = urllib.request.Request(embedding_url, method='GET')
    with urllib.request.urlopen(req, timeout=5) as response:
        print("✓ Embedding服务可访问")
        print(f"  状态码: {response.status}")
        embedding_accessible = True
except urllib.error.URLError as e:
    print(f"✗ Embedding服务不可访问")
    print(f"  错误: {e.reason}")
except Exception as e:
    print(f"✗ 连接失败: {e}")

print()

# 检测文件路径
print("="*60)
print("3. 检测文件路径")
print("="*60 + "\n")

test_paths = [
    "/home/maxuejiao/guji/mineru_ocr",
    "/home/maxuejiao/guji/shidianguji",
]

local_accessible = False
for path in test_paths:
    exists = Path(path).exists()
    if exists:
        print(f"✓ 路径存在: {path}")
        local_accessible = True
    else:
        print(f"✗ 路径不存在: {path}")

if not local_accessible:
    print("\n文件路径无法直接访问")
    print("建议:")
    print("  - 使用SSH访问远程文件")
    print("  - 或映射网络驱动器")

print()

# 生成配置建议
print("="*60)
print("配置建议")
print("="*60 + "\n")

if ssh_available and ssh_user:
    print("【推荐方案】使用SSH访问")
    print("\n请创建 backend/.env 文件，内容如下：")
    print()
    print("```env")
    print("DEBUG=true")
    print("USE_SSH=true")
    print("REMOTE_SERVER_HOST=172.23.40.162")
    print(f"REMOTE_SERVER_USER={ssh_user}")
    print(f"REMOTE_SERVER_PASSWORD=你的密码")
    print()
    if not embedding_accessible:
        print("# Embedding服务待检查")
        print("# 请SSH登录服务器执行: curl http://localhost:8180/v1/models")
    print("EMBEDDING_API_URL=http://172.23.40.162:8180/v1")
    print("EMBEDDING_MODEL=embedding")
    print("```")
    print()
    
    # 自动创建.env
    create = input("是否自动创建配置文件？(y/n): ").strip().lower()
    if create == 'y':
        password = input("请输入SSH密码: ").strip()
        env_content = f"""DEBUG=true
USE_SSH=true
REMOTE_SERVER_HOST=172.23.40.162
REMOTE_SERVER_USER={ssh_user}
REMOTE_SERVER_PASSWORD={password}
EMBEDDING_API_URL=http://172.23.40.162:8180/v1
EMBEDDING_MODEL=embedding
"""
        env_file = Path("backend/.env")
        env_file.write_text(env_content, encoding='utf-8')
        print(f"\n✓ 配置文件已创建: {env_file}")
        print("\n下一步: python test_connection.py")

elif local_accessible:
    print("【当前方案】本地文件访问")
    print("文件路径可直接访问，无需特殊配置")
    
elif not ssh_available:
    print("【问题】无法使用SSH")
    print("\n解决方案:")
    print("1. 安装OpenSSH客户端")
    print("   Windows 10/11: 设置 -> 应用 -> 可选功能 -> 添加功能 -> OpenSSH客户端")
    print("2. 或使用PuTTY等SSH工具")

else:
    print("【需要更多信息】")
    print("\n请提供:")
    print("1. SSH用户名和密码")
    print("2. 确认文件路径是否正确")

print()
print("="*60)
print("配置向导完成")
print("="*60)