@echo off
echo ========================================
echo 古籍标注平台 - 启动脚本
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [2/3] 安装后端依赖...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo [3/3] 启动后端服务...
echo.
echo 后端服务将在 http://localhost:8000 启动
echo API文档: http://localhost:8000/api/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

python main.py

pause