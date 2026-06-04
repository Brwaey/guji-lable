@echo off
echo ========================================
echo 古籍标注平台 - 测试脚本
echo ========================================
echo.

echo [1/3] 测试连接...
python test_connection.py
if errorlevel 1 (
    echo.
    echo [警告] 连接测试失败，请检查配置
    echo.
)

echo.
echo [2/3] 启动后端服务（后台运行）...
cd backend
start /B python main.py > ..\backend.log 2>&1
timeout /t 5 /nobreak > nul
echo 后端服务已启动

echo.
echo [3/3] 运行集成测试...
cd ..
python test_integration.py

echo.
echo 测试完成！
pause