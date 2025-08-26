import os
import logging
from datetime import datetime, timedelta
from typing import Dict
from django.utils import timezone
from django.conf import settings
from .coze_workflow_service import CozeWorkflowService
from .inventory_service import InventoryService

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务服务"""
    
    def __init__(self):
        self.workflow_service = CozeWorkflowService()
        self.inventory_service = InventoryService()
        self.execution_interval = int(os.getenv('WORKFLOW_EXECUTION_INTERVAL', 300))  # 5分钟
    
    def should_execute_workflow(self) -> bool:
        """
        检查是否应该执行工作流
        
        Returns:
            是否应该执行
        """
        try:
            from ..models.order_management import OrderBatch
            
            # 获取最后一次成功执行的时间
            last_execution = OrderBatch.objects.filter(
                is_completed=True
            ).order_by('-execution_time').first()
            
            if not last_execution:
                # 如果没有执行记录，应该执行
                logger.info("没有执行记录，应该执行工作流")
                return True
            
            # 检查是否已经过了执行间隔
            time_since_last = timezone.now() - last_execution.execution_time
            should_execute = time_since_last.total_seconds() >= self.execution_interval
            
            if should_execute:
                logger.info(f"距离上次执行已过 {time_since_last.total_seconds()} 秒，应该执行工作流")
            else:
                logger.info(f"距离上次执行仅过 {time_since_last.total_seconds()} 秒，暂不执行")
            
            return should_execute
            
        except Exception as e:
            logger.error(f"检查执行条件失败: {str(e)}")
            return False
    
    def execute_scheduled_workflow(self) -> Dict:
        """
        执行定时工作流
        
        Returns:
            执行结果
        """
        try:
            # 检查是否应该执行
            if not self.should_execute_workflow():
                return {
                    "success": False,
                    "message": "未到执行时间",
                    "scheduled": True
                }
            
            logger.info("开始执行定时工作流")
            
            # 执行工作流
            workflow_result = self.workflow_service.execute_full_workflow()
            
            if workflow_result["success"]:
                logger.info(f"工作流执行成功，获取 {workflow_result['total_orders']} 个订单")
                
                # 处理订单库存
                inventory_result = self.inventory_service.process_all_unprocessed_orders()
                
                if inventory_result["success"]:
                    logger.info(f"库存处理完成，成功: {inventory_result['success_count']}，失败: {inventory_result['failed_count']}")
                else:
                    logger.warning(f"库存处理失败: {inventory_result['message']}")
                
                return {
                    "success": True,
                    "workflow_result": workflow_result,
                    "inventory_result": inventory_result,
                    "message": "定时工作流执行完成"
                }
            else:
                logger.error(f"工作流执行失败: {workflow_result.get('error', '未知错误')}")
                return {
                    "success": False,
                    "workflow_result": workflow_result,
                    "message": "工作流执行失败"
                }
                
        except Exception as e:
            logger.error(f"执行定时工作流失败: {str(e)}")
            return {
                "success": False,
                "message": f"执行定时工作流失败: {str(e)}"
            }
    
    def get_next_execution_time(self) -> Dict:
        """
        获取下次执行时间
        
        Returns:
            下次执行时间信息
        """
        try:
            from ..models.order_management import OrderBatch
            
            last_execution = OrderBatch.objects.filter(
                is_completed=True
            ).order_by('-execution_time').first()
            
            if not last_execution:
                return {
                    "next_execution": timezone.now(),
                    "time_until_next": 0,
                    "last_execution": None
                }
            
            next_execution = last_execution.execution_time + timedelta(seconds=self.execution_interval)
            time_until_next = (next_execution - timezone.now()).total_seconds()
            
            return {
                "next_execution": next_execution,
                "time_until_next": max(0, time_until_next),
                "last_execution": last_execution.execution_time
            }
            
        except Exception as e:
            logger.error(f"获取下次执行时间失败: {str(e)}")
            return {"error": str(e)}
    
    def get_scheduler_status(self) -> Dict:
        """
        获取定时任务状态
        
        Returns:
            定时任务状态信息
        """
        try:
            from ..models.order_management import Order, OrderBatch
            
            # 获取执行统计
            total_batches = OrderBatch.objects.count()
            completed_batches = OrderBatch.objects.filter(is_completed=True).count()
            failed_batches = OrderBatch.objects.filter(is_completed=False).count()
            
            # 获取订单统计
            total_orders = Order.objects.count()
            processed_orders = Order.objects.filter(is_processed=True).count()
            unprocessed_orders = Order.objects.filter(is_processed=False).count()
            
            # 获取下次执行时间
            next_execution_info = self.get_next_execution_time()
            
            # 获取工作流状态
            workflow_status = self.workflow_service.get_workflow_status()
            
            status = {
                "scheduler": {
                    "execution_interval": self.execution_interval,
                    "total_batches": total_batches,
                    "completed_batches": completed_batches,
                    "failed_batches": failed_batches,
                    "next_execution": next_execution_info.get("next_execution"),
                    "time_until_next": next_execution_info.get("time_until_next"),
                    "last_execution": next_execution_info.get("last_execution")
                },
                "orders": {
                    "total": total_orders,
                    "processed": processed_orders,
                    "unprocessed": unprocessed_orders
                },
                "workflow": workflow_status
            }
            
            return status
            
        except Exception as e:
            logger.error(f"获取定时任务状态失败: {str(e)}")
            return {"error": str(e)}
    
    def force_execute_workflow(self) -> Dict:
        """
        强制执行工作流（忽略时间间隔）
        
        Returns:
            执行结果
        """
        try:
            logger.info("开始强制执行工作流")
            
            # 执行工作流
            workflow_result = self.workflow_service.execute_full_workflow()
            
            if workflow_result["success"]:
                logger.info(f"强制工作流执行成功，获取 {workflow_result['total_orders']} 个订单")
                
                # 处理订单库存
                inventory_result = self.inventory_service.process_all_unprocessed_orders()
                
                return {
                    "success": True,
                    "workflow_result": workflow_result,
                    "inventory_result": inventory_result,
                    "message": "强制工作流执行完成"
                }
            else:
                logger.error(f"强制工作流执行失败: {workflow_result.get('error', '未知错误')}")
                return {
                    "success": False,
                    "workflow_result": workflow_result,
                    "message": "强制工作流执行失败"
                }
                
        except Exception as e:
            logger.error(f"强制执行工作流失败: {str(e)}")
            return {
                "success": False,
                "message": f"强制执行工作流失败: {str(e)}"
            }
    
    def update_execution_interval(self, new_interval: int) -> Dict:
        """
        更新执行间隔
        
        Args:
            new_interval: 新的执行间隔（秒）
            
        Returns:
            更新结果
        """
        try:
            if new_interval < 60:  # 最小1分钟
                return {
                    "success": False,
                    "message": "执行间隔不能少于60秒"
                }
            
            self.execution_interval = new_interval
            
            # 这里可以将新的间隔保存到数据库或配置文件中
            # 为了简化，我们暂时只更新内存中的值
            
            logger.info(f"执行间隔已更新为 {new_interval} 秒")
            
            return {
                "success": True,
                "message": f"执行间隔已更新为 {new_interval} 秒",
                "new_interval": new_interval
            }
            
        except Exception as e:
            logger.error(f"更新执行间隔失败: {str(e)}")
            return {
                "success": False,
                "message": f"更新执行间隔失败: {str(e)}"
            }
