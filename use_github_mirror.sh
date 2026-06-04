#!/bin/bash
# 使用GitHub镜像站点

echo "========================================"
echo "GitHub镜像加速方案"
echo "========================================"
echo

cd ~/guji/guji-lable

echo "可用镜像:"
echo "  1. https://gitclone.com"
echo "  2. https://hub.fastgit.xyz"
echo "  3. https://github.com.cnpmjs.org"
echo

read -p "选择镜像 (1/2/3): " choice

case $choice in
    1)
        mirror="https://gitclone.com/github.com"
        ;;
    2)
        mirror="https://hub.fastgit.xyz"
        ;;
    3)
        mirror="https://github.com.cnpmjs.org"
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo
echo "设置镜像: $mirror"
git remote set-url origin ${mirror}/Brwaey/guji-lable.git

echo
echo "测试连接..."
timeout 10 git ls-remote origin 2>&1 | head -5

echo
echo "配置完成！"
echo "现在可以执行: git pull"