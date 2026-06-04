#!/bin/bash
# 修复GitHub连接问题 - 切换到SSH

echo "========================================"
echo "GitHub连接修复 - 切换到SSH"
echo "========================================"
echo

cd ~/guji/guji-lable

echo "当前远程仓库配置:"
git remote -v
echo

echo "[1/3] 切换到SSH..."
git remote set-url origin git@github.com:Brwaey/guji-lable.git

echo "[2/3] 验证SSH密钥..."
if [ -f ~/.ssh/id_rsa ]; then
    echo "✓ SSH密钥存在"
    ls -la ~/.ssh/id_rsa*
else
    echo "✗ 未找到SSH密钥"
    echo "需要生成SSH密钥:"
    echo "  ssh-keygen -t rsa -b 4096 -C 'your_email@example.com'"
    echo "  cat ~/.ssh/id_rsa.pub  # 添加到GitHub"
    exit 1
fi

echo "[3/3] 测试SSH连接..."
ssh -T git@github.com

echo
echo "========================================"
echo "修复完成"
echo "========================================"
echo
echo "新的远程仓库配置:"
git remote -v
echo
echo "现在可以执行: git pull"