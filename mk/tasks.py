from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from .services.scheduler_service import SchedulerService

logger = get_task_logger(__name__)


@shared_task(bind=True, name='inventory.execute_scheduled_workflow')
def execute_scheduled_workflow(self):
    """
    执行定时工作流任务
    
    Returns:
        执行结果
    """
    try:
        logger.info("开始执行定时工作流任务")
        
        scheduler = SchedulerService()
        result = scheduler.execute_scheduled_workflow()
        
        if result["success"]:
            logger.info(f"定时工作流执行成功: {result.get('message', '')}")
        else:
            logger.warning(f"定时工作流执行失败: {result.get('message', '')}")
        
        return result
        
    except Exception as e:
        error_msg = f"执行定时工作流任务失败: {str(e)}"
        logger.error(error_msg)
        
        # 更新任务状态
        self.update_state(
            state='FAILURE',
            meta={'error': error_msg}
        )
        
        return {
            "success": False,
            "message": error_msg
        }


@shared_task(bind=True, name='inventory.process_unprocessed_orders')
def process_unprocessed_orders(self):
    """
    处理未处理订单任务
    
    Returns:
        处理结果
    """
    try:
        logger.info("开始处理未处理订单任务")
        
        from .services.inventory_service import InventoryService
        
        inventory_service = InventoryService()
        result = inventory_service.process_all_unprocessed_orders()
        
        if result["success"]:
            logger.info(f"订单处理完成: 成功 {result.get('success_count', 0)} 个，失败 {result.get('failed_count', 0)} 个")
        else:
            logger.warning(f"订单处理失败: {result.get('message', '')}")
        
        return result
        
    except Exception as e:
        error_msg = f"处理未处理订单任务失败: {str(e)}"
        logger.error(error_msg)
        
        # 更新任务状态
        self.update_state(
            state='FAILURE',
            meta={'error': error_msg}
        )
        
        return {
            "success": False,
            "message": error_msg
        }


@shared_task(bind=True, name='inventory.cleanup_old_data')
def cleanup_old_data(self, days_to_keep=90):
    """
    清理旧数据任务
    
    Args:
        days_to_keep: 保留天数，默认90天
        
    Returns:
        清理结果
    """
    try:
        logger.info(f"开始清理 {days_to_keep} 天前的旧数据")
        
        from django.utils import timezone
        from datetime import timedelta
        from .models.order_management import OrderBatch
        from .models.inventory_management import InventoryTransaction
        
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # 清理旧的批次记录
        old_batches = OrderBatch.objects.filter(
            execution_time__lt=cutoff_date,
            is_completed=True
        )
        old_batches_count = old_batches.count()
        old_batches.delete()
        
        # 清理旧的交易记录
        old_transactions = InventoryTransaction.objects.filter(
            created_at__lt=cutoff_date
        )
        old_transactions_count = old_transactions.count()
        old_transactions.delete()
        
        result = {
            "success": True,
            "message": f"清理完成，删除了 {old_batches_count} 个旧批次记录和 {old_transactions_count} 个旧交易记录",
            "deleted_batches": old_batches_count,
            "deleted_transactions": old_transactions_count
        }
        
        logger.info(result["message"])
        return result
        
    except Exception as e:
        error_msg = f"清理旧数据任务失败: {str(e)}"
        logger.error(error_msg)
        
        # 更新任务状态
        self.update_state(
            state='FAILURE',
            meta={'error': error_msg}
        )
        
        return {
            "success": False,
            "message": error_msg
        }


@shared_task(bind=True, name='inventory.generate_inventory_report')
def generate_inventory_report(self, store_id=None):
    """
    生成库存报告任务
    
    Args:
        store_id: 店铺ID，如果为None则生成所有店铺的报告
        
    Returns:
        报告结果
    """
    try:
        logger.info(f"开始生成库存报告，店铺ID: {store_id}")
        
        from .services.inventory_service import InventoryService
        
        inventory_service = InventoryService()
        summary = inventory_service.get_inventory_summary(store_id)
        
        if "error" in summary:
            logger.error(f"生成库存报告失败: {summary['error']}")
            return {
                "success": False,
                "message": summary["error"]
            }
        
        # 这里可以添加报告生成逻辑，比如导出到Excel或发送邮件
        # 为了简化，我们只返回摘要数据
        
        result = {
            "success": True,
            "message": "库存报告生成成功",
            "summary": summary,
            "generated_at": timezone.now().isoformat()
        }
        
        logger.info("库存报告生成完成")
        return result
        
    except Exception as e:
        error_msg = f"生成库存报告任务失败: {str(e)}"
        logger.error(error_msg)
        
        # 更新任务状态
        self.update_state(
            state='FAILURE',
            meta={'error': error_msg}
        )
        
        return {
            "success": False,
            "message": error_msg
        }


@shared_task(bind=True, name='inventory.health_check')
def health_check(self):
    """
    系统健康检查任务
    
    Returns:
        健康检查结果
    """
    try:
        logger.info("开始系统健康检查")
        
        from django.db import connection
        from .models.order_management import Order, OrderBatch
        from .models.inventory_management import Inventory
        
        health_status = {
            "timestamp": timezone.now().isoformat(),
            "database": "healthy",
            "models": {},
            "overall": "healthy"
        }
        
        # 检查数据库连接
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status["database"] = "healthy"
        except Exception as e:
            health_status["database"] = f"unhealthy: {str(e)}"
            health_status["overall"] = "unhealthy"
        
        # 检查各模型状态
        try:
            # 检查订单模型
            total_orders = Order.objects.count()
            unprocessed_orders = Order.objects.filter(is_processed=False).count()
            health_status["models"]["orders"] = {
                "total": total_orders,
                "unprocessed": unprocessed_orders,
                "status": "healthy"
            }
        except Exception as e:
            health_status["models"]["orders"] = {
                "status": f"unhealthy: {str(e)}"
            }
            health_status["overall"] = "unhealthy"
        
        try:
            # 检查批次模型
            total_batches = OrderBatch.objects.count()
            failed_batches = OrderBatch.objects.filter(is_completed=False).count()
            health_status["models"]["batches"] = {
                "total": total_batches,
                "failed": failed_batches,
                "status": "healthy"
            }
        except Exception as e:
            health_status["models"]["batches"] = {
                "status": f"unhealthy: {str(e)}"
            }
            health_status["overall"] = "unhealthy"
        
        try:
            # 检查库存模型
            total_inventory = Inventory.objects.count()
            active_inventory = Inventory.objects.filter(is_active=True).count()
            health_status["models"]["inventory"] = {
                "total": total_inventory,
                "active": active_inventory,
                "status": "healthy"
            }
        except Exception as e:
            health_status["models"]["inventory"] = {
                "status": f"unhealthy: {str(e)}"
            }
            health_status["overall"] = "unhealthy"
        
        # 检查工作流服务
        try:
            from .services.coze_workflow_service import CozeWorkflowService
            workflow_service = CozeWorkflowService()
            workflow_status = workflow_service.get_workflow_status()
            
            if "error" in workflow_status:
                health_status["models"]["workflow"] = {
                    "status": f"unhealthy: {workflow_status['error']}"
                }
                health_status["overall"] = "unhealthy"
            else:
                health_status["models"]["workflow"] = {
                    "status": "healthy",
                    "total_orders": workflow_status.get("total_orders", 0)
                }
        except Exception as e:
            health_status["models"]["workflow"] = {
                "status": f"unhealthy: {str(e)}"
            }
            health_status["overall"] = "unhealthy"
        
        logger.info(f"系统健康检查完成，状态: {health_status['overall']}")
        return health_status
        
    except Exception as e:
        error_msg = f"系统健康检查任务失败: {str(e)}"
        logger.error(error_msg)
        
        # 更新任务状态
        self.update_state(
            state='FAILURE',
            meta={'error': error_msg}
        )
        
        return {
            "success": False,
            "message": error_msg,
            "overall": "unhealthy"
        }


@shared_task
def check_inventory_warnings_task():
    """检查库存预警的定时任务"""
    try:
        from .services.inventory_warning_service import InventoryWarningService
        warnings_created = InventoryWarningService.check_inventory_warnings()
        logger.info(f"库存预警检查任务完成，创建了 {warnings_created} 个预警")
        return warnings_created
    except Exception as e:
        logger.error(f"库存预警检查任务失败: {str(e)}")
        return 0


@shared_task
def send_inventory_warning_emails_task():
    """发送库存预警邮件的定时任务"""
    try:
        from .services.inventory_warning_service import InventoryWarningService
        from .models.message_system import InventoryWarning
        
        # 获取所有未发送邮件的活跃预警
        unsent_warnings = InventoryWarning.objects.filter(
            status='active',
            email_sent=False
        )
        
        sent_count = 0
        for warning in unsent_warnings:
            try:
                InventoryWarningService._send_email_notification(warning)
                sent_count += 1
            except Exception as e:
                logger.error(f"发送预警邮件失败 {warning.id}: {str(e)}")
                continue
        
        logger.info(f"库存预警邮件发送任务完成，发送了 {sent_count} 封邮件")
        return sent_count
    except Exception as e:
        logger.error(f"库存预警邮件发送任务失败: {str(e)}")
        return 0

# -*- coding: utf-8 -*-
from celery import shared_task
from django.utils import timezone
import logging

from .services.etsy_sync_service import etsy_sync
from .services.redis_cache_service import redis_cache

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def sync_etsy_data_task(self, model_name=None):
    """Etsy数据同步任务"""
    try:
        if model_name:
            # 同步指定模型
            success = etsy_sync.sync_model_data(model_name)
            if success:
                logger.info(f"模型 {model_name} 数据同步成功")
                return f"模型 {model_name} 数据同步成功"
            else:
                logger.error(f"模型 {model_name} 数据同步失败")
                return f"模型 {model_name} 数据同步失败"
        else:
            # 同步所有模型
            results = etsy_sync.sync_all_models()
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            logger.info(f"Etsy数据同步完成，成功: {success_count}/{total_count}")
            return f"Etsy数据同步完成，成功: {success_count}/{total_count}"
            
    except Exception as e:
        logger.error(f"Etsy数据同步任务失败: {e}")
        raise self.retry(countdown=60, max_retries=3)


@shared_task(bind=True)
def sync_etsy_product_registration_task(self):
    """同步Etsy产品登记数据"""
    return sync_etsy_data_task.delay('product_registration')


@shared_task(bind=True)
def sync_etsy_order_import_summary_task(self):
    """同步Etsy订单导入汇总数据"""
    return sync_etsy_data_task.delay('order_import_summary')


@shared_task(bind=True)
def sync_etsy_order_statistics_task(self):
    """同步Etsy订单统计数据"""
    return sync_etsy_data_task.delay('order_statistics')


@shared_task(bind=True)
def sync_etsy_design_requirement_task(self):
    """同步Etsy设计需求数据"""
    return sync_etsy_data_task.delay('design_requirement')


@shared_task(bind=True)
def sync_etsy_purchase_requirement_task(self):
    """同步Etsy采购需求数据"""
    return sync_etsy_data_task.delay('purchase_requirement')


@shared_task(bind=True)
def sync_etsy_production_requirement_task(self):
    """同步Etsy生产需求数据"""
    return sync_etsy_data_task.delay('production_requirement')


@shared_task(bind=True)
def sync_etsy_shipping_delivery_task(self):
    """同步Etsy配货发货数据"""
    return sync_etsy_data_task.delay('shipping_delivery')


@shared_task(bind=True)
def sync_etsy_qr_code_label_task(self):
    """同步Etsy二维码标签数据"""
    return sync_etsy_data_task.delay('qr_code_label')


@shared_task(bind=True)
def sync_etsy_yuntu_export_task(self):
    """同步Etsy云途导出数据"""
    return sync_etsy_data_task.delay('yuntu_export')


@shared_task(bind=True)
def sync_etsy_yuntu_deduction_task(self):
    """同步Etsy云途扣费数据"""
    return sync_etsy_data_task.delay('yuntu_deduction')


@shared_task(bind=True)
def sync_etsy_store_information_task(self):
    """同步Etsy店铺信息数据"""
    return sync_etsy_data_task.delay('store_information')


@shared_task(bind=True)
def cleanup_expired_cache_task(self):
    """清理过期缓存任务"""
    try:
        # 这里可以添加清理过期缓存的逻辑
        # 目前Redis会自动清理过期键，所以这个任务主要用于监控
        cache_info = redis_cache.get_cache_info()
        logger.info(f"缓存清理任务完成，当前缓存信息: {cache_info}")
        return "缓存清理任务完成"
        
    except Exception as e:
        logger.error(f"缓存清理任务失败: {e}")
        raise self.retry(countdown=300, max_retries=2)


@shared_task(bind=True)
def health_check_task(self):
    """健康检查任务"""
    try:
        # 检查Redis连接
        redis_health = redis_cache.health_check()
        
        # 检查同步状态
        sync_status = etsy_sync.get_sync_status()
        
        health_info = {
            'redis_health': redis_health,
            'sync_status': sync_status,
            'timestamp': timezone.now().isoformat()
        }
        
        if not redis_health:
            logger.warning("Redis连接异常")
        
        logger.info(f"健康检查完成: {health_info}")
        return health_info
        
    except Exception as e:
        logger.error(f"健康检查任务失败: {e}")