# Celery配置文件
# 用于配置库存管理系统的定时任务

# 基础配置
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

# 任务序列化配置
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# 时区配置
timezone = 'Asia/Shanghai'
enable_utc = False

# 工作进程配置
worker_prefetch_multiplier = 1
task_acks_late = True
task_reject_on_worker_lost = True

# 任务执行配置
task_always_eager = False
task_eager_propagates = True

# 任务路由配置
task_routes = {
    'mk.tasks.*': {'queue': 'inventory'},
}

# 队列配置
task_default_queue = 'default'
task_default_exchange = 'default'
task_default_routing_key = 'default'

# 结果配置
result_expires = 3600  # 1小时
result_persistent = True

# 工作进程配置
worker_max_tasks_per_child = 1000
worker_max_memory_per_child = 200000  # 200MB

# 日志配置
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# 任务限制配置
task_annotations = {
    'mk.tasks.execute_scheduled_workflow': {
        'rate_limit': '1/m',  # 每分钟最多1次
        'time_limit': 300,    # 5分钟超时
        'soft_time_limit': 240,  # 4分钟软超时
    },
    'mk.tasks.process_unprocessed_orders': {
        'rate_limit': '1/h',  # 每小时最多1次
        'time_limit': 1800,   # 30分钟超时
        'soft_time_limit': 1500,  # 25分钟软超时
    },
    'mk.tasks.cleanup_old_data': {
        'rate_limit': '1/d',  # 每天最多1次
        'time_limit': 3600,   # 1小时超时
        'soft_time_limit': 3000,  # 50分钟软超时
    },
    'mk.tasks.generate_inventory_report': {
        'rate_limit': '1/d',  # 每天最多1次
        'time_limit': 1800,   # 30分钟超时
        'soft_time_limit': 1500,  # 25分钟软超时
    },
    'mk.tasks.health_check': {
        'rate_limit': '2/h',  # 每小时最多2次
        'time_limit': 300,    # 5分钟超时
        'soft_time_limit': 240,  # 4分钟软超时
    },
}

# 任务结果配置
task_ignore_result = False
task_store_errors_even_if_ignored = True

# 工作进程池配置
worker_pool = 'prefork'
worker_pool_restarts = True

# 任务重试配置
task_retry_policy = {
    'max_retries': 3,
    'interval_start': 0,
    'interval_step': 0.2,
    'interval_max': 0.2,
}

# 监控配置
worker_send_task_events = True
task_send_sent_event = True

# 安全配置
worker_disable_rate_limits = False
worker_direct = False

# 性能配置
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000
worker_max_memory_per_child = 200000

# 调试配置
worker_log_color = True
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
