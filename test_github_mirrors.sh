#!/bin/bash
# GitHub连接终极解决方案 - 测试所有可用镜像

echo "========================================"
echo "GitHub连接测试 - 查找最快镜像"
echo "========================================"
echo

cd ~/guji/guji-lable

# 定义镜像列表
mirrors=(
    "https://ghproxy.com/https://github.com"
    "https://mirror.ghproxy.com/https://github.com"
    "https://gh-proxy.com/https://github.com"
    "https://github.moeyy.xyz/https://github.com"
)

echo "测试可用镜像..."
echo

for mirror in "${mirrors[@]}"; do
    echo "测试: $mirror"
    test_url="$mirror/Brwaey/guji-lable.git"

    # 设置并测试
    git remote set-url origin "$test_url" 2>/dev/null

    # 测试连接（超时5秒）
    if timeout 5 git ls-remote origin 2>&1 | grep -q "head"; then
        echo "  ✓ 成功！"
        echo
        echo "使用镜像: $mirror"
        echo
        echo "现在执行: git pull"
        exit 0
    else
        echo "  ✗ 失败"
    fi
    echo
done

# 如果所有镜像都失败
echo "所有镜像都失败"
echo
echo "建议使用SSH方案:"
echo "  1. 生成SSH密钥: ssh-keygen"
echo "  2. 添加到GitHub: cat ~/.ssh/id_rsa.pub"
echo "  3. 切换URL: git remote set-url origin git@github.com:Brwaey/guji-lable.git"
echo "  4. Pull: git pull"