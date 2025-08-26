# Celery配置说明

## 概述

本文档说明如何配置和使用Celery来管理库存管理系统的定时任务。

## 文件结构

```
wwkc/
├── celery.py              # Celery主配置文件
├── celeryconfig.py        # Celery详细配置
├── start_celery.py        # Python启动脚本
├── start_celery.bat       # Windows批处理启动脚本
├── start_celery.sh        # Linux/Mac Shell启动脚本
└── logs/                  # 日志目录
    ├── celery.log         # Celery日志
    └── celerybeat.pid     # Beat进程ID文件
```

## 配置说明

### 1. 主配置文件 (wwkc/celery.py)

- 设置Django环境
- 自动发现任务
- 配置定时任务调度
- 设置任务路由和序列化

### 2. 详细配置文件 (wwkc/celeryconfig.py)

- 基础配置（broker、result_backend）
- 任务限制和超时设置
- 工作进程配置
- 监控和日志配置

### 3. 定时任务配置

| 任务名称 | 执行频率 | 说明 |
|---------|---------|------|
| execute-inventory-workflow | 每5分钟 | 执行库存工作流，获取订单数据 |
| process-unprocessed-orders | 每小时 | 处理未处理的订单，扣除库存 |
| cleanup-old-data | 每天 | 清理90天前的旧数据 |
| generate-inventory-report | 每天 | 生成库存报告 |
| health-check | 每30分钟 | 系统健康检查 |

## 安装依赖

确保已安装以下依赖包：

```bash
pip install celery==5.3.4
pip install django-celery-beat==2.5.0
pip install django-celery-results==2.5.1
pip install redis==5.0.1
pip install flower  # 可选，用于监控
```

## 启动服务

### Windows用户

双击运行 `start_celery.bat`，选择要启动的服务。

### Linux/Mac用户

```bash
# 给脚本执行权限
chmod +x start_celery.sh

# 运行脚本
./start_celery.sh
```

### 手动启动

```bash
# 启动工作进程
celery -A wwkc worker --loglevel=info --queues=inventory

# 启动定时任务调度器
celery -A wwkc beat --loglevel=info

# 启动监控界面（可选）
celery -A wwkc flower --port=5555
```

## 监控和管理

### 1. Flower监控界面

访问 http://localhost:5555/flower 查看：
- 任务执行状态
- 工作进程状态
- 任务历史记录
- 实时监控

### 2. 命令行管理

```bash
# 查看任务状态
celery -A wwkc inspect active

# 查看队列状态
celery -A wwkc inspect stats

# 停止所有任务
celery -A wwkc control shutdown
```

### 3. Django管理命令

```bash
# 运行库存定时任务
python manage.py run_inventory_scheduler

# 强制执行工作流
python manage.py run_inventory_scheduler --force

# 查看状态
python manage.py run_inventory_scheduler --status
```

## 配置选项

### 环境变量

在 `local.env` 中配置：

```env
# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 工作流配置
WORKFLOW_EXECUTION_INTERVAL=300
WORKFLOW_BATCH_SIZE=20
```

### 任务配置

在 `mk/tasks.py` 中定义任务：

```python
@shared_task(bind=True, name='inventory.execute_scheduled_workflow')
def execute_scheduled_workflow(self):
    """执行定时工作流任务"""
    # 任务逻辑
    pass
```

## 故障排除

### 1. 常见问题

**问题**: Redis连接失败
**解决**: 检查Redis服务是否启动，端口是否正确

**问题**: 任务不执行
**解决**: 检查beat进程是否启动，定时配置是否正确

**问题**: 工作进程无响应
**解决**: 重启worker进程，检查任务是否有死锁

### 2. 日志查看

```bash
# 查看Celery日志
tail -f logs/celery.log

# 查看Django日志
tail -f logs/debug.log
```

### 3. 性能调优

- 调整并发数：`--concurrency=4`
- 设置内存限制：`--max-memory-per-child=500000`
- 配置任务超时：在celeryconfig.py中设置

## 安全注意事项

1. 生产环境不要暴露Flower监控界面
2. 设置Redis密码和访问控制
3. 限制任务执行权限
4. 定期清理任务结果和日志

## 扩展功能

### 1. 添加新任务

```python
# 在mk/tasks.py中添加
@shared_task(bind=True, name='inventory.new_task')
def new_task(self):
    """新任务"""
    pass

# 在celery.py中添加调度
'new-task': {
    'task': 'mk.tasks.new_task',
    'schedule': 3600.0,  # 每小时执行
},
```

### 2. 自定义队列

```python
# 创建专用队列
app.conf.task_routes = {
    'mk.tasks.high_priority.*': {'queue': 'high_priority'},
    'mk.tasks.low_priority.*': {'queue': 'low_priority'},
}
```

### 3. 任务重试机制

```python
@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def retry_task(self):
    """带重试机制的任务"""
    pass
```

## 联系支持

如有问题，请查看：
1. Celery官方文档：https://docs.celeryproject.org/
2. Django Celery Beat文档：https://django-celery-beat.readthedocs.io/
3. 项目日志文件
4. 系统管理员
