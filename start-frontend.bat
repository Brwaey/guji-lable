@echo off
echo ========================================
echo 古籍标注平台 - 前端启动脚本
echo ========================================
echo.

echo [1/3] 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

echo [2/3] 安装前端依赖...
cd frontend
call npm install
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo [3/3] 启动前端开发服务器...
echo.
echo 前端服务将在 http://localhost:5173 启动
echo.
echo 按 Ctrl+C 停止服务
echo.

call npm run dev

pause