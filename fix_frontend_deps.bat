@echo off
REM 修复前端依赖

echo ========================================
echo 修复前端依赖
echo ========================================
echo.

cd frontend

echo [1/3] 清理旧依赖...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json

echo [2/3] 清理npm缓存...
call npm cache clean --force

echo [3/3] 重新安装依赖...
call npm install

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 启动开发服务器:
echo   npm run dev -- --host 0.0.0.0
echo.
pause