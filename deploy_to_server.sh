#!/bin/bash
# 部署脚本 - 将项目部署到服务器
# 使用方法: bash deploy_to_server.sh

set -e  # 遇到错误立即退出

# 配置变量
SERVER_USER="${SERVER_USER:-maxuejiao}"
SERVER_HOST="${SERVER_HOST:-172.23.40.162}"
REMOTE_DIR="${REMOTE_DIR:-/home/maxuejiao/guji-lable}"
LOCAL_DIR="$(pwd)"

echo "========================================"
echo "古籍标注平台 - 服务器部署脚本"
echo "========================================"
echo
echo "本地目录: $LOCAL_DIR"
echo "服务器: $SERVER_USER@$SERVER_HOST"
echo "远程目录: $REMOTE_DIR"
echo

# 确认部署
read -p "确认部署？(y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "取消部署"
    exit 0
fi

# 1. 同步代码
echo
echo "[1/6] 同步代码到服务器..."
rsync -avz --progress \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='node_modules' \
    --exclude='.env' \
    --exclude='venv' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='annotations' \
    --exclude='embedding_cache' \
    "$LOCAL_DIR/" "$SERVER_USER@$SERVER_HOST:$REMOTE_DIR/"

# 2. 创建虚拟环境
echo
echo "[2/6] 创建Python虚拟环境..."
ssh "$SERVER_USER@$SERVER_HOST" "cd $REMOTE_DIR/backend && python3 -m venv venv"

# 3. 安装后端依赖
echo
echo "[3/6] 安装后端依赖..."
ssh "$SERVER_USER@$SERVER_HOST" "cd $REMOTE_DIR/backend && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# 4. 安装前端依赖
echo
echo "[4/6] 安装前端依赖..."
ssh "$SERVER_USER@$SERVER_HOST" "cd $REMOTE_DIR/frontend && npm install"

# 5. 创建配置文件
echo
echo "[5/6] 创建配置文件..."
ssh "$SERVER_USER@$SERVER_HOST" "cat > $REMOTE_DIR/backend/.env << 'EOF'
DEBUG=true
USE_SSH=false
EMBEDDING_API_URL=http://localhost:8180/v1
EMBEDDING_MODEL=embedding
EOF"

# 6. 测试连接
echo
echo "[6/6] 测试连接..."
ssh "$SERVER_USER@$SERVER_HOST" "cd $REMOTE_DIR && python test_connection.py"

echo
echo "========================================"
echo "部署完成！"
echo "========================================"
echo
echo "启动服务:"
echo "  1. 后端:"
echo "     ssh $SERVER_USER@$SERVER_HOST"
echo "     cd $REMOTE_DIR/backend"
echo "     source venv/bin/activate"
echo "     python main.py"
echo
echo "  2. 前端:"
echo "     ssh $SERVER_USER@$SERVER_HOST"
echo "     cd $REMOTE_DIR/frontend"
echo "     npm run dev -- --host 0.0.0.0"
echo
echo "访问地址:"
echo "  http://$SERVER_HOST:5173  (前端)"
echo "  http://$SERVER_HOST:8000  (后端API)"
echo "  http://$SERVER_HOST:8000/api/docs  (API文档)"
echo