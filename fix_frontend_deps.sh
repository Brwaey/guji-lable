#!/bin/bash
# 修复前端依赖并安装

echo "========================================"
echo "修复前端依赖"
echo "========================================"
echo

cd frontend

# 清理旧的依赖
echo "[1/3] 清理旧依赖..."
rm -rf node_modules package-lock.json

# 清理npm缓存
echo "[2/3] 清理npm缓存..."
npm cache clean --force

# 重新安装
echo "[3/3] 重新安装依赖..."
npm install

echo
echo "========================================"
echo "安装完成！"
echo "========================================"
echo
echo "启动开发服务器:"
echo "  npm run dev -- --host 0.0.0.0"