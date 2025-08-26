import os
from celery import Celery
from django.conf import settings

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wwkc.settings')

# 创建Celery应用
app = Celery('wwkc')

# 从Django设置中读取Celery配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# 配置定时任务
app.conf.beat_schedule = {
    # 每5分钟执行一次库存工作流
    'execute-inventory-workflow': {
        'task': 'mk.tasks.execute_scheduled_workflow',
        'schedule': 300.0,  # 5分钟 = 300秒
    },
    
    # 每小时处理未处理订单
    'process-unprocessed-orders': {
        'task': 'mk.tasks.process_unprocessed_orders',
        'schedule': 3600.0,  # 1小时 = 3600秒
    },
    
    # 每天凌晨2点清理旧数据
    'cleanup-old-data': {
        'task': 'mk.tasks.cleanup_old_data',
        'schedule': 86400.0,  # 24小时 = 86400秒
        'args': (90,),  # 保留90天的数据
    },
    
    # 每天上午9点生成库存报告
    'generate-inventory-report': {
        'task': 'mk.tasks.generate_inventory_report',
        'schedule': 86400.0,  # 24小时
    },
    
    # 每30分钟执行系统健康检查
    'health-check': {
        'task': 'mk.tasks.health_check',
        'schedule': 1800.0,  # 30分钟 = 1800秒
    },
}

# 任务路由配置
app.conf.task_routes = {
    'mk.tasks.*': {'queue': 'inventory'},
}

# 任务序列化配置
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# 时区配置
app.conf.timezone = 'Asia/Shanghai'
app.conf.enable_utc = False

# 结果后端配置
app.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# 工作进程配置
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True

# 任务执行配置
app.conf.task_always_eager = False
app.conf.task_eager_propagates = True

# 日志配置
app.conf.worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
app.conf.worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

@app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')
