#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置助手脚本
帮助用户正确配置远程服务器访问
"""

import os
import sys
from pathlib import Path

print("\n" + "="*60)
print("古籍标注平台 - 配置助手")
print("="*60 + "\n")

print("当前问题诊断：")
print("- SSH连接: 成功（22端口可访问）")
print("- Embedding API: 超时（8180端口无法访问）")
print("- 文件路径: 不存在（Linux路径在Windows上无效）")
print()

print("="*60)
print("解决方案选择")
print("="*60 + "\n")

print("请选择你要使用的方案：")
print()
print("【方案1】使用SSH访问文件（推荐）")
print("  适用：有SSH登录账号")
print("  操作：配置SSH用户名密码，通过SSH读取远程文件")
print("  步骤：")
print("    1. 准备SSH登录凭证（用户名和密码）")
print("    2. 编辑 backend/.env 文件")
print("    3. 设置 USE_SSH=true")
print("    4. 设置 REMOTE_SERVER_USER 和 PASSWORD")
print()
print("【方案2】映射网络驱动器（需要SMB）")
print("  适用：服务器配置了SMB/网络共享")
print("  操作：在Windows映射网络驱动器，修改路径")
print("  步骤：")
print("    1. 在Windows映射 \\172.23.40.162\\共享名")
print("    2. 修改 config.py 使用Windows路径")
print()
print("【方案3】检查Embedding服务")
print("  适用：怀疑Embedding服务配置问题")
print("  操作：SSH登录服务器检查服务状态")
print("  步骤：")
print("    1. ssh登录到172.23.40.162")
print("    2. 执行: curl http://localhost:8180/v1/models")
print("    3. 执行: netstat -tuln | grep 8180")
print()

# 提示用户输入
choice = input("请选择方案 (1/2/3) 或输入 'q' 退出: ").strip()

if choice == 'q':
    print("退出配置助手")
    sys.exit(0)

elif choice == '1':
    print("\n" + "="*60)
    print("方案1: SSH配置")
    print("="*60 + "\n")
    
    # 获取SSH信息
    username = input("请输入SSH用户名: ").strip()
    if not username:
        print("错误: 用户名不能为空")
        sys.exit(1)
    
    password = input("请输入SSH密码: ").strip()
    if not password:
        print("警告: 密码为空，连接可能失败")
    
    # 创建.env文件
    env_file = Path("backend/.env")
    env_content = f"""# 古籍标注平台配置
DEBUG=true

# SSH连接配置
USE_SSH=true
REMOTE_SERVER_HOST=172.23.40.162
REMOTE_SERVER_USER={username}
REMOTE_SERVER_PASSWORD={password}

# Embedding服务（保持原配置，后续检查）
EMBEDDING_API_URL=http://172.23.40.162:8180/v1
EMBEDDING_MODEL=embedding
"""
    
    # 写入文件
    env_file.write_text(env_content, encoding='utf-8')
    print(f"\n✅ 配置已写入: {env_file}")
    print()
    print("下一步:")
    print("  1. 运行: python test_connection.py")
    print("  2. 检查文件访问是否通过")
    print("  3. 如果Embedding仍超时，执行方案3")

elif choice == '2':
    print("\n" + "="*60)
    print("方案2: 网络驱动器映射")
    print("="*60 + "\n")
    
    print("步骤指导:")
    print()
    print("1. 在Windows文件资源管理器中:")
    print("   - 右键'此电脑'")
    print("   - 选择'映射网络驱动器'")
    print()
    print("2. 输入网络路径:")
    print("   格式: \\172.23.40.162\\共享名")
    print("   例如: \\172.23.40.162\\guji")
    print()
    print("3. 输入凭据:")
    print("   用户名和密码（如果需要）")
    print()
    print("4. 映射完成后，假设映射到 Z: 盘")
    print()
    
    drive_letter = input("请输入映射的驱动器字母 (例如 Z): ").strip().upper()
    if not drive_letter:
        drive_letter = 'Z'
    
    print(f"\n假设映射到 {drive_letter}: 盘")
    print("请手动编辑 backend/config.py，修改路径:")
    print()
    print(f"OCR_BASE_PATHS = [")
    print(f"    '{drive_letter}:\\mineru_ocr\\二十四史附清史稿_ocr',")
    print(f"    '{drive_letter}:\\mineru_ocr\\十三经注疏_ocr',")
    print(f"    '{drive_letter}:\\paddleocrvl_ocr\\二十四史附清史稿_ocr',")
    print(f"    '{drive_letter}:\\paddleocrvl_ocr\\十三经注疏_ocr',")
    print(f"]")
    print(f"REFERENCE_BASE_PATH = '{drive_letter}:\\shidianguji'")
    print()
    print("注意: 这需要服务器配置了SMB/CIFS共享")

elif choice == '3':
    print("\n" + "="*60)
    print("方案3: Embedding服务检查")
    print("="*60 + "\n")
    
    print("请SSH登录到服务器后执行以下命令:")
    print()
    print("# 1. 检查服务是否运行")
    print("curl http://localhost:8180/v1/models")
    print()
    print("# 2. 检查端口监听")
    print("netstat -tuln | grep 8180")
    print()
    print("# 3. 如果显示 127.0.0.1:8180，需要修改服务配置")
    print("# 让服务监听 0.0.0.0 而不是 localhost")
    print()
    print("# 4. 检查防火墙")
    print("sudo ufw status")
    print("sudo ufw allow 8180/tcp  # 如果需要开放端口")
    print()
    print("请将检查结果反馈，以便进一步诊断")

else:
    print("无效选择")
    sys.exit(1)

print()
print("="*60)
print("配置助手完成")
print("="*60)