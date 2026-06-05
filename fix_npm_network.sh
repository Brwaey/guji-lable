#!/bin/bash
# npm网络问题修复 - 使用国内镜像

echo "========================================"
echo "npm网络问题修复"
echo "========================================"
echo

cd ~/guji/guji-lable/frontend

echo "问题: npm访问国外资源超时"
echo "解决: 使用国内镜像源"
echo

echo "[1/4] 设置淘宝npm镜像..."
npm config set registry https://registry.npmmirror.com

echo "[2/4] 设置其他镜像..."
npm config set puppeteer_download_host https://npmmirror.com/mirrors
npm config set chromedriver_cdnurl https://npmmirror.com/mirrors/chromedriver
npm config set electron_mirror https://npmmirror.com/mirrors/electron
npm config set sass_binary_site https://npmmirror.com/mirrors/node-sass
npm config set phantomjs_cdnurl https://npmmirror.com/mirrors/phantomjs
npm config set python_mirror https://npmmirror.com/mirrors/python

echo "[3/4] 清理缓存..."
npm cache clean --force

echo "[4/4] 安装依赖..."
npm install

echo
echo "========================================"
echo "安装完成"
echo "========================================"
echo

# 验证
echo "验证安装:"
ls -la node_modules | head -10