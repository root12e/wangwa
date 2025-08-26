import os
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from ..models.order_management import Order, OrderBatch
from ..models.store_management import Store

logger = logging.getLogger(__name__)


class CozeWorkflowService:
    """扣子工作流服务"""
    
    def __init__(self):
        self.bot_id = os.getenv('COZE_BOT_ID')
        self.space_id = os.getenv('COZE_SPACE_ID')
        self.workflow_id = os.getenv('COZE_WORKFLOW_ID')
        self.api_key = os.getenv('COZE_API_KEY')
        self.workflow_url = os.getenv('COZE_WORKFLOW_URL')
        self.batch_size = int(os.getenv('WORKFLOW_BATCH_SIZE', 20))
        
        if not all([self.bot_id, self.space_id, self.workflow_id, self.api_key]):
            raise ValueError("扣子工作流配置不完整，请检查环境变量")
    
    def execute_workflow(self, page_token: Optional[str] = None) -> Tuple[bool, List[Dict], Optional[str]]:
        """
        执行工作流
        
        Args:
            page_token: 分页令牌，第一次执行时为None
            
        Returns:
            success: 是否成功
            data: 返回的数据列表
            next_page_token: 下一页令牌，如果没有更多数据则为None
        """
        try:
            # 构建请求参数
            payload = {
                "bot_id": self.bot_id,
                "space_id": self.space_id,
                "workflow_id": self.workflow_id,
                "input": {}
            }
            
            # 如果有分页令牌，添加到输入中
            if page_token:
                payload["input"]["page_token"] = page_token
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"执行工作流，page_token: {page_token}")
            
            # 发送请求到扣子工作流
            response = requests.post(
                self.workflow_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"工作流执行失败: {response.status_code} - {response.text}")
                return False, [], None
            
            result = response.json()
            
            # 解析返回数据
            if "data" in result:
                data = result["data"]
                next_page_token = result.get("page_token")
                
                logger.info(f"工作流执行成功，返回 {len(data)} 条数据")
                return True, data, next_page_token
            else:
                logger.error(f"工作流返回数据格式错误: {result}")
                return False, [], None
                
        except Exception as e:
            logger.error(f"工作流执行异常: {str(e)}")
            return False, [], None
    
    def process_workflow_data(self, data: List[Dict]) -> int:
        """
        处理工作流返回的数据
        
        Args:
            data: 工作流返回的数据列表
            
        Returns:
            成功处理的订单数量
        """
        processed_count = 0
        
        for item in data:
            try:
                # 检查订单是否已存在
                if Order.objects.filter(order_number=item.get('订单号')).exists():
                    logger.info(f"订单 {item.get('订单号')} 已存在，跳过")
                    continue
                
                # 查找对应的店铺
                store = None
                store_code = item.get('店铺代号')
                if store_code:
                    store = Store.objects.filter(code=store_code).first()
                
                # 创建订单记录
                order = Order.objects.create(
                    order_number=item.get('订单号'),
                    country=item.get('国家', ''),
                    store_code=store_code or '',
                    sku=item.get('SKU', ''),
                    detail=item.get('Detail', ''),
                    n_quantity=int(item.get('N', 0)) if item.get('N') else 0,
                    c1_value=item.get('C1', ''),
                    c2_value=item.get('C2', ''),
                    order_date=datetime.strptime(item.get('出单日期', ''), '%Y-%m-%d').date() if item.get('出单日期') else timezone.now().date(),
                    label_status=item.get('标签状态', ''),
                    package_status=item.get('包裹状态', ''),
                    combined_express_waybill=item.get('寄合快递单号', ''),
                    yuntu_info=item.get('云途', ''),
                    last_mile=item.get('尾程', ''),
                    store=store,
                    store_name=item.get('店铺名称', ''),
                    english_name=item.get('英文名', ''),
                    first_sku=item.get('第一个sku', ''),
                    page_token=item.get('page_token', '')
                )
                
                processed_count += 1
                logger.info(f"成功创建订单: {order.order_number}")
                
            except Exception as e:
                logger.error(f"处理订单数据失败: {str(e)}, 数据: {item}")
                continue
        
        return processed_count
    
    def execute_full_workflow(self) -> Dict:
        """
        执行完整的工作流循环，获取所有数据
        
        Returns:
            执行结果统计
        """
        start_time = timezone.now()
        total_orders = 0
        total_batches = 0
        page_token = None
        has_more_data = True
        
        # 创建批次记录
        batch = OrderBatch.objects.create(
            batch_id=f"batch_{start_time.strftime('%Y%m%d_%H%M%S')}",
            page_token=page_token
        )
        
        try:
            while has_more_data:
                # 执行工作流
                success, data, next_page_token = self.execute_workflow(page_token)
                
                if not success:
                    batch.error_message = "工作流执行失败"
                    batch.save()
                    break
                
                if not data:
                    logger.info("工作流返回空数据，结束执行")
                    break
                
                # 处理数据
                processed_count = self.process_workflow_data(data)
                total_orders += processed_count
                total_batches += 1
                
                # 更新批次记录
                batch.orders_count = total_orders
                batch.page_token = page_token
                batch.save()
                
                # 检查是否还有更多数据
                if next_page_token:
                    page_token = next_page_token
                    logger.info(f"继续获取下一页数据，page_token: {page_token}")
                else:
                    has_more_data = False
                    logger.info("没有更多数据，工作流执行完成")
                
                # 添加延迟，避免请求过于频繁
                import time
                time.sleep(1)
            
            # 标记批次完成
            batch.is_completed = True
            batch.save()
            
            execution_time = timezone.now() - start_time
            
            result = {
                "success": True,
                "total_orders": total_orders,
                "total_batches": total_batches,
                "execution_time": execution_time.total_seconds(),
                "batch_id": batch.batch_id
            }
            
            logger.info(f"工作流执行完成: {result}")
            return result
            
        except Exception as e:
            error_msg = f"工作流执行异常: {str(e)}"
            logger.error(error_msg)
            batch.error_message = error_msg
            batch.save()
            
            return {
                "success": False,
                "error": error_msg,
                "total_orders": total_orders,
                "total_batches": total_batches,
                "batch_id": batch.batch_id
            }
    
    def manual_refresh(self) -> Dict:
        """
        手动刷新数据
        
        Returns:
            执行结果
        """
        logger.info("开始手动刷新数据")
        return self.execute_full_workflow()
    
    def get_workflow_status(self) -> Dict:
        """
        获取工作流状态
        
        Returns:
            工作流状态信息
        """
        try:
            # 获取最近的批次记录
            recent_batches = OrderBatch.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).order_by('-created_at')[:10]
            
            # 获取订单统计
            total_orders = Order.objects.count()
            processed_orders = Order.objects.filter(is_processed=True).count()
            unprocessed_orders = Order.objects.filter(is_processed=False).count()
            
            # 获取最近的执行状态
            last_execution = OrderBatch.objects.filter(is_completed=True).order_by('-execution_time').first()
            
            status = {
                "total_orders": total_orders,
                "processed_orders": processed_orders,
                "unprocessed_orders": unprocessed_orders,
                "recent_batches": [
                    {
                        "batch_id": batch.batch_id,
                        "execution_time": batch.execution_time,
                        "orders_count": batch.orders_count,
                        "is_completed": batch.is_completed,
                        "error_message": batch.error_message
                    }
                    for batch in recent_batches
                ],
                "last_execution": {
                    "batch_id": last_execution.batch_id,
                    "execution_time": last_execution.execution_time,
                    "orders_count": last_execution.orders_count
                } if last_execution else None
            }
            
            return status
            
        except Exception as e:
            logger.error(f"获取工作流状态失败: {str(e)}")
            return {"error": str(e)}
