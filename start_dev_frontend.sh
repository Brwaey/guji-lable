#!/bin/bash
# 前端开发模式启动

echo "========================================"
echo "前端开发模式启动"
echo "========================================"
echo

cd frontend

if [ ! -d "node_modules" ]; then
    echo "安装依赖..."
    npm install
fi

echo
echo "前端启动中... (Ctrl+C 停止)"
echo "访问地址: http://0.0.0.0:5173"
echo "内网访问: http://172.23.40.162:5173"
echo

npm run dev -- --host 0.0.0.0