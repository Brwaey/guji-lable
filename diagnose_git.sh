#!/bin/bash
# Git问题诊断和解决脚本

echo "========================================"
echo "Git Pull 问题诊断"
echo "========================================"
echo

echo "检查1: Git状态"
git status
echo

echo "检查2: 远程仓库配置"
git remote -v
echo

echo "检查3: 检查是否有未提交的更改"
git diff
echo

echo "检查4: 检查是否有未跟踪的文件"
git ls-files --others --exclude-standard
echo

echo "检查5: 检查Git锁文件"
if [ -f ".git/index.lock" ]; then
    echo "⚠️  发现Git锁文件: .git/index.lock"
    echo "   这通常表示之前的Git操作未完成"
    echo
    read -p "是否删除锁文件？(y/n): " remove_lock
    if [ "$remove_lock" = "y" ]; then
        rm -f .git/index.lock
        echo "✓ 锁文件已删除"
    fi
else
    echo "✓ 未发现锁文件"
fi
echo

echo "检查6: 测试网络连接"
echo "尝试连接远程仓库..."
git ls-remote origin 2>&1 | head -5
echo

echo "========================================"
echo "诊断完成"
echo "========================================"