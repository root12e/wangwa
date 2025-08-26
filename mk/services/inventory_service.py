import logging
from typing import Dict, List, Optional, Tuple
from django.db import transaction
from django.utils import timezone
from ..models.order_management import Order
from ..models.inventory_management import Inventory, InventoryTransaction, InventoryConsumption
from ..models.store_management import Store
from ..models.product_management import Product

logger = logging.getLogger(__name__)


class InventoryService:
    """库存管理服务"""
    
    def __init__(self):
        pass
    
    def process_order_inventory(self, order: Order) -> Dict:
        """
        处理订单的库存扣除
        
        Args:
            order: 订单对象
            
        Returns:
            处理结果
        """
        try:
            with transaction.atomic():
                # 检查订单是否已处理
                if order.inventory_deducted:
                    return {
                        "success": False,
                        "message": f"订单 {order.order_number} 的库存已扣除"
                    }
                
                # 查找对应的店铺和产品
                store = order.store
                if not store:
                    return {
                        "success": False,
                        "message": f"订单 {order.order_number} 未找到对应店铺"
                    }
                
                # 解析Detail字段，获取属性和数量
                detail_attributes = order.get_detail_attributes()
                total_quantity = order.get_total_quantity()
                
                if not detail_attributes:
                    logger.warning(f"订单 {order.order_number} 的Detail字段格式不正确")
                    # 如果没有Detail属性，使用SKU和N数量
                    return self._process_simple_inventory(order, store)
                
                # 处理每个属性的库存扣除
                deduction_results = []
                for attribute, quantity in detail_attributes.items():
                    result = self._deduct_attribute_inventory(
                        store, attribute, quantity, order
                    )
                    deduction_results.append(result)
                
                # 检查是否所有扣除都成功
                failed_deductions = [r for r in deduction_results if not r["success"]]
                if failed_deductions:
                    # 回滚所有扣除操作
                    raise Exception(f"库存扣除失败: {failed_deductions}")
                
                # 标记订单已处理
                order.is_processed = True
                order.inventory_deducted = True
                order.save()
                
                # 更新消耗统计
                self._update_consumption_statistics(order, store, total_quantity)
                
                return {
                    "success": True,
                    "message": f"订单 {order.order_number} 库存扣除成功",
                    "deductions": deduction_results
                }
                
        except Exception as e:
            logger.error(f"处理订单库存失败: {str(e)}")
            return {
                "success": False,
                "message": f"处理订单库存失败: {str(e)}"
            }
    
    def _process_simple_inventory(self, order: Order, store: Store) -> Dict:
        """
        处理简单库存扣除（使用SKU和N数量）
        
        Args:
            order: 订单对象
            store: 店铺对象
            
        Returns:
            处理结果
        """
        try:
            sku = order.sku
            quantity = order.get_total_quantity()
            
            if not sku or quantity <= 0:
                return {
                    "success": False,
                    "message": f"订单 {order.order_number} SKU或数量无效"
                }
            
            # 查找库存记录
            inventory = Inventory.objects.filter(
                store=store,
                sku=sku,
                is_active=True
            ).first()
            
            if not inventory:
                return {
                    "success": False,
                    "message": f"店铺 {store.name} 的SKU {sku} 没有库存记录"
                }
            
            # 扣除库存
            if inventory.available_stock < quantity:
                return {
                    "success": False,
                    "message": f"库存不足，需要 {quantity}，可用 {inventory.available_stock}"
                }
            
            # 记录交易前状态
            before_stock = inventory.current_stock
            
            # 扣除库存
            inventory.deduct_stock(quantity)
            
            # 创建交易记录
            InventoryTransaction.objects.create(
                inventory=inventory,
                transaction_type='DEDUCT_ORDER',
                quantity=quantity,
                order=order,
                before_stock=before_stock,
                after_stock=inventory.current_stock,
                notes=f"订单 {order.order_number} 扣除库存"
            )
            
            return {
                "success": True,
                "message": f"SKU {sku} 库存扣除成功，扣除数量: {quantity}",
                "sku": sku,
                "quantity": quantity
            }
            
        except Exception as e:
            logger.error(f"处理简单库存失败: {str(e)}")
            return {
                "success": False,
                "message": f"处理简单库存失败: {str(e)}"
            }
    
    def _deduct_attribute_inventory(self, store: Store, attribute: str, quantity: int, order: Order) -> Dict:
        """
        扣除指定属性的库存
        
        Args:
            store: 店铺对象
            attribute: 属性名称
            quantity: 数量
            order: 订单对象
            
        Returns:
            扣除结果
        """
        try:
            # 查找对应属性的库存记录
            # 这里假设属性名称对应产品的某个字段，您可以根据实际情况调整
            inventory = Inventory.objects.filter(
                store=store,
                sku__icontains=attribute,  # 或者使用其他匹配逻辑
                is_active=True
            ).first()
            
            if not inventory:
                return {
                    "success": False,
                    "message": f"店铺 {store.name} 的属性 {attribute} 没有库存记录"
                }
            
            # 检查库存是否足够
            if inventory.available_stock < quantity:
                return {
                    "success": False,
                    "message": f"属性 {attribute} 库存不足，需要 {quantity}，可用 {inventory.available_stock}"
                }
            
            # 记录交易前状态
            before_stock = inventory.current_stock
            
            # 扣除库存
            inventory.deduct_stock(quantity)
            
            # 创建交易记录
            InventoryTransaction.objects.create(
                inventory=inventory,
                transaction_type='DEDUCT_ORDER',
                quantity=quantity,
                order=order,
                before_stock=before_stock,
                after_stock=inventory.current_stock,
                notes=f"订单 {order.order_number} 扣除属性 {attribute} 库存"
            )
            
            return {
                "success": True,
                "message": f"属性 {attribute} 库存扣除成功，扣除数量: {quantity}",
                "attribute": attribute,
                "quantity": quantity,
                "inventory_id": inventory.id
            }
            
        except Exception as e:
            logger.error(f"扣除属性库存失败: {str(e)}")
            return {
                "success": False,
                "message": f"扣除属性库存失败: {str(e)}"
            }
    
    def _update_consumption_statistics(self, order: Order, store: Store, quantity: int):
        """
        更新消耗统计
        
        Args:
            order: 订单对象
            store: 店铺对象
            quantity: 数量
        """
        try:
            sku = order.sku
            if not sku:
                return
            
            # 获取或创建消耗统计记录
            consumption, created = InventoryConsumption.objects.get_or_create(
                store=store,
                sku=sku,
                defaults={
                    'total_consumed': 0,
                    'total_orders': 0
                }
            )
            
            # 更新统计
            consumption.add_consumption(quantity, order.order_date)
            
        except Exception as e:
            logger.error(f"更新消耗统计失败: {str(e)}")
    
    def process_all_unprocessed_orders(self) -> Dict:
        """
        处理所有未处理的订单
        
        Returns:
            处理结果统计
        """
        try:
            unprocessed_orders = Order.objects.filter(
                is_processed=False,
                inventory_deducted=False
            ).order_by('created_at')
            
            total_orders = unprocessed_orders.count()
            success_count = 0
            failed_count = 0
            failed_orders = []
            
            logger.info(f"开始处理 {total_orders} 个未处理订单")
            
            for order in unprocessed_orders:
                result = self.process_order_inventory(order)
                if result["success"]:
                    success_count += 1
                else:
                    failed_count += 1
                    failed_orders.append({
                        "order_number": order.order_number,
                        "error": result["message"]
                    })
                
                # 每处理100个订单记录一次日志
                if (success_count + failed_count) % 100 == 0:
                    logger.info(f"已处理 {success_count + failed_count}/{total_orders} 个订单")
            
            result = {
                "success": True,
                "total_orders": total_orders,
                "success_count": success_count,
                "failed_count": failed_count,
                "failed_orders": failed_orders
            }
            
            logger.info(f"订单处理完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"批量处理订单失败: {str(e)}")
            return {
                "success": False,
                "message": f"批量处理订单失败: {str(e)}"
            }
    
    def get_inventory_summary(self, store_id: Optional[str] = None) -> Dict:
        """
        获取库存摘要
        
        Args:
            store_id: 店铺ID，如果为None则获取所有店铺
            
        Returns:
            库存摘要信息
        """
        try:
            if store_id:
                inventories = Inventory.objects.filter(
                    store_id=store_id,
                    is_active=True
                )
            else:
                inventories = Inventory.objects.filter(is_active=True)
            
            summary = {
                "total_products": inventories.count(),
                "total_stock": sum(inv.current_stock for inv in inventories),
                "total_available": sum(inv.available_stock for inv in inventories),
                "total_reserved": sum(inv.reserved_stock for inv in inventories),
                "low_stock_count": sum(1 for inv in inventories if inv.current_stock <= inv.min_stock),
                "out_of_stock_count": sum(1 for inv in inventories if inv.current_stock == 0),
                "stores": {}
            }
            
            # 按店铺分组统计
            for inventory in inventories:
                store_name = inventory.store.name
                if store_name not in summary["stores"]:
                    summary["stores"][store_name] = {
                        "products": 0,
                        "total_stock": 0,
                        "available_stock": 0
                    }
                
                summary["stores"][store_name]["products"] += 1
                summary["stores"][store_name]["total_stock"] += inventory.current_stock
                summary["stores"][store_name]["available_stock"] += inventory.available_stock
            
            return summary
            
        except Exception as e:
            logger.error(f"获取库存摘要失败: {str(e)}")
            return {"error": str(e)}
    
    def adjust_inventory(self, inventory_id: str, adjustment_type: str, quantity: int, notes: str = "", user_id: Optional[str] = None) -> Dict:
        """
        调整库存
        
        Args:
            inventory_id: 库存ID
            adjustment_type: 调整类型 (IN, OUT, ADJUST)
            quantity: 数量
            notes: 备注
            user_id: 操作用户ID
            
        Returns:
            调整结果
        """
        try:
            with transaction.atomic():
                inventory = Inventory.objects.get(id=inventory_id)
                
                if adjustment_type == 'IN':
                    # 入库
                    before_stock = inventory.current_stock
                    inventory.add_stock(quantity)
                    transaction_type = 'IN'
                    
                elif adjustment_type == 'OUT':
                    # 出库
                    if inventory.available_stock < quantity:
                        return {
                            "success": False,
                            "message": f"库存不足，可用库存: {inventory.available_stock}"
                        }
                    before_stock = inventory.current_stock
                    inventory.deduct_stock(quantity)
                    transaction_type = 'OUT'
                    
                elif adjustment_type == 'ADJUST':
                    # 直接调整
                    before_stock = inventory.current_stock
                    inventory.current_stock = quantity
                    inventory.save()
                    transaction_type = 'ADJUST'
                    
                else:
                    return {
                        "success": False,
                        "message": f"不支持的调整类型: {adjustment_type}"
                    }
                
                # 创建交易记录
                InventoryTransaction.objects.create(
                    inventory=inventory,
                    transaction_type=transaction_type,
                    quantity=quantity,
                    before_stock=before_stock,
                    after_stock=inventory.current_stock,
                    notes=notes,
                    created_by_id=user_id
                )
                
                return {
                    "success": True,
                    "message": f"库存调整成功，调整前: {before_stock}，调整后: {inventory.current_stock}",
                    "inventory_id": inventory_id,
                    "before_stock": before_stock,
                    "after_stock": inventory.current_stock
                }
                
        except Inventory.DoesNotExist:
            return {
                "success": False,
                "message": f"库存记录不存在: {inventory_id}"
            }
        except Exception as e:
            logger.error(f"调整库存失败: {str(e)}")
            return {
                "success": False,
                "message": f"调整库存失败: {str(e)}"
            }
