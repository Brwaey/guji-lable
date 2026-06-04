@echo off
REM Windows部署脚本

set SERVER_USER=maxuejiao
set SERVER_HOST=172.23.40.162
set REMOTE_DIR=/home/maxuejiao/guji-lable

echo ========================================
echo 古籍标注平台 - 服务器部署脚本
echo ========================================
echo.

echo 服务器: %SERVER_USER%@%SERVER_HOST%
echo 远程目录: %REMOTE_DIR%
echo.

set /p confirm="确认部署？(y/n): "
if /i not "%confirm%"=="y" (
    echo 取消部署
    pause
    exit /b 0
)

echo.
echo [1/5] 上传项目文件...
echo 使用scp上传（需要手动输入密码）:
echo.
echo scp -r . %SERVER_USER%@%SERVER_HOST%:%REMOTE_DIR%
echo.
echo 请在新打开的PowerShell窗口执行上述命令
echo 完成后按任意键继续...
pause >nul

echo.
echo [2/5] 安装后端依赖...
ssh %SERVER_USER%@%SERVER_HOST% "cd %REMOTE_DIR%/backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

echo.
echo [3/5] 安装前端依赖...
ssh %SERVER_USER%@%SERVER_HOST% "cd %REMOTE_DIR%/frontend && npm install"

echo.
echo [4/5] 创建配置文件...
ssh %SERVER_USER%@%SERVER_HOST% "cat > %REMOTE_DIR%/backend/.env << 'EOF'
DEBUG=true
USE_SSH=false
EMBEDDING_API_URL=http://localhost:8180/v1
EMBEDDING_MODEL=embedding
EOF"

echo.
echo [5/5] 测试连接...
ssh %SERVER_USER%@%SERVER_HOST% "cd %REMOTE_DIR% && python test_connection.py"

echo.
echo ========================================
echo 部署完成！
echo ========================================
echo.
echo 启动命令:
echo   ssh %SERVER_USER%@%SERVER_HOST%
echo   cd %REMOTE_DIR%/backend
echo   source venv/bin/activate
echo   python main.py
echo.
pause