#!/bin/bash
# 开发模式启动脚本（适合调试）

echo "========================================"
echo "古籍标注平台 - 开发模式启动"
echo "========================================"
echo

# 启动后端（前台运行，可看到日志）
echo "启动后端..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
DEBUG=true
USE_SSH=false
EMBEDDING_API_URL=http://localhost:8180/v1
EMBEDDING_MODEL=embedding
EOF
fi

pip install --quiet -r requirements.txt

echo
echo "后端启动中... (Ctrl+C 停止)"
echo "API地址: http://localhost:8000"
echo "API文档: http://localhost:8000/api/docs"
echo

python main.py