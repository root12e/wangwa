@echo off
chcp 65001 >nul
echo ========================================
echo 库存管理系统 - Celery服务启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查是否在虚拟环境中
if "%VIRTUAL_ENV%"=="" (
    echo 警告: 未检测到虚拟环境，建议在虚拟环境中运行
    echo.
)

REM 创建日志目录
if not exist "logs" mkdir logs

echo 选择要启动的服务:
echo 1. 启动所有服务 (推荐)
echo 2. 仅启动工作进程
echo 3. 仅启动定时任务调度器
echo 4. 仅启动监控界面
echo 5. 查看服务状态
echo 6. 停止所有服务
echo 0. 退出
echo.

set /p choice="请输入选择 (0-6): "

if "%choice%"=="1" (
    echo.
    echo 启动所有Celery服务...
    echo 工作进程: 2个并发
    echo 监控界面: http://localhost:5555/flower
    echo.
    echo 按 Ctrl+C 停止所有服务
    echo.
    python start_celery.py start --concurrency 2 --port 5555
) else if "%choice%"=="2" (
    echo.
    echo 启动工作进程...
    echo 按 Ctrl+C 停止服务
    echo.
    python start_celery.py worker --concurrency 2 --queue inventory
) else if "%choice%"=="3" (
    echo.
    echo 启动定时任务调度器...
    echo 按 Ctrl+C 停止服务
    echo.
    python start_celery.py beat
) else if "%choice%"=="4" (
    echo.
    echo 启动监控界面...
    echo 访问地址: http://localhost:5555/flower
    echo 按 Ctrl+C 停止服务
    echo.
    python start_celery.py flower --port 5555
) else if "%choice%"=="5" (
    echo.
    echo 查看服务状态...
    python start_celery.py status
    echo.
    pause
) else if "%choice%"=="6" (
    echo.
    echo 停止所有服务...
    python start_celery.py stop
    echo.
    pause
) else if "%choice%"=="0" (
    echo 退出
    exit /b 0
) else (
    echo 无效选择，请重新运行脚本
    pause
    exit /b 1
)

echo.
echo 服务已停止
pause
