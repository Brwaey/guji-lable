#!/bin/bash
# 服务器快速启动脚本

set -e

echo "========================================"
echo "古籍标注平台 - 快速启动"
echo "========================================"
echo

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 检查Node
if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm"
    exit 1
fi

# 后端
echo "[后端] 安装依赖..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --quiet -r requirements.txt

echo "[后端] 创建配置..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
DEBUG=true
USE_SSH=false
EMBEDDING_API_URL=http://localhost:8180/v1
EMBEDDING_MODEL=embedding
EOF
fi

echo "[后端] 启动服务 (后台运行)..."
nohup python main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端PID: $BACKEND_PID"

# 前端
cd ../frontend

echo "[前端] 安装依赖..."
npm install --silent

echo "[前端] 构建项目..."
npm run build --silent

echo
echo "========================================"
echo "启动完成！"
echo "========================================"
echo
echo "后端PID: $BACKEND_PID"
echo "访问地址:"
echo "  前端: 需要配置nginx或使用: npm run dev -- --host 0.0.0.0"
echo "  API: http://localhost:8000"
echo "  文档: http://localhost:8000/api/docs"
echo
echo "查看日志:"
echo "  tail -f logs/backend.log"
echo
echo "停止服务:"
echo "  kill $BACKEND_PID"