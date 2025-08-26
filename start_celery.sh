#!/bin/bash

# 库存管理系统 - Celery服务启动脚本

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python是否安装
check_python() {
    if ! command -v python3 &> /dev/null; then
        if ! command -v python &> /dev/null; then
            print_error "未找到Python，请先安装Python"
            exit 1
        else
            PYTHON_CMD="python"
        fi
    else
        PYTHON_CMD="python3"
    fi
    print_info "使用Python命令: $PYTHON_CMD"
}

# 检查虚拟环境
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "未检测到虚拟环境，建议在虚拟环境中运行"
    else
        print_info "虚拟环境: $VIRTUAL_ENV"
    fi
}

# 创建日志目录
create_log_dir() {
    if [[ ! -d "logs" ]]; then
        mkdir -p logs
        print_info "创建日志目录: logs/"
    fi
}

# 启动所有服务
start_all() {
    print_info "启动所有Celery服务..."
    print_info "工作进程: 2个并发"
    print_info "监控界面: http://localhost:5555/flower"
    echo
    print_info "按 Ctrl+C 停止所有服务"
    echo
    
    $PYTHON_CMD start_celery.py start --concurrency 2 --port 5555
}

# 启动工作进程
start_worker() {
    print_info "启动工作进程..."
    print_info "按 Ctrl+C 停止服务"
    echo
    
    $PYTHON_CMD start_celery.py worker --concurrency 2 --queue inventory
}

# 启动定时任务调度器
start_beat() {
    print_info "启动定时任务调度器..."
    print_info "按 Ctrl+C 停止服务"
    echo
    
    $PYTHON_CMD start_celery.py beat
}

# 启动监控界面
start_flower() {
    print_info "启动监控界面..."
    print_info "访问地址: http://localhost:5555/flower"
    print_info "按 Ctrl+C 停止服务"
    echo
    
    $PYTHON_CMD start_celery.py flower --port 5555
}

# 查看服务状态
show_status() {
    print_info "查看服务状态..."
    $PYTHON_CMD start_celery.py status
}

# 停止所有服务
stop_all() {
    print_info "停止所有服务..."
    $PYTHON_CMD start_celery.py stop
}

# 显示菜单
show_menu() {
    echo "========================================"
    echo "库存管理系统 - Celery服务启动脚本"
    echo "========================================"
    echo
    echo "选择要启动的服务:"
    echo "1. 启动所有服务 (推荐)"
    echo "2. 仅启动工作进程"
    echo "3. 仅启动定时任务调度器"
    echo "4. 仅启动监控界面"
    echo "5. 查看服务状态"
    echo "6. 停止所有服务"
    echo "0. 退出"
    echo
}

# 主函数
main() {
    # 检查Python
    check_python
    
    # 检查虚拟环境
    check_venv
    
    # 创建日志目录
    create_log_dir
    
    # 显示菜单
    show_menu
    
    # 读取用户选择
    read -p "请输入选择 (0-6): " choice
    
    case $choice in
        1)
            start_all
            ;;
        2)
            start_worker
            ;;
        3)
            start_beat
            ;;
        4)
            start_flower
            ;;
        5)
            show_status
            echo
            read -p "按回车键继续..."
            ;;
        6)
            stop_all
            echo
            read -p "按回车键继续..."
            ;;
        0)
            print_info "退出"
            exit 0
            ;;
        *)
            print_error "无效选择，请重新运行脚本"
            exit 1
            ;;
    esac
    
    echo
    print_info "服务已停止"
}

# 捕获中断信号
trap 'echo; print_info "收到中断信号，正在退出..."; exit 0' INT

# 运行主函数
main
