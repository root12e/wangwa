import logging
from typing import Dict, List, Any, Optional
from django.db import transaction
from django.db.models import Q, Count, Sum, Avg, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from ..models.etsy_models import (
    EtsyProductRegistration, EtsyOrderImportSummary, EtsyOrderStatistics,
    EtsyDesignRequirement, EtsyPurchaseRequirement, EtsyProductionRequirement,
    EtsyShippingDelivery, EtsyQRCodeLabel, EtsyYunTuExport, 
    EtsyYunTuDeduction, EtsyStoreInformation
)
from .redis_cache_service import redis_cache

logger = logging.getLogger(__name__)

class EtsySyncService:
    """Etsy数据同步服务，负责MySQL和Redis之间的数据同步"""
    
    def __init__(self):
        self.max_workers = 4  # 最大工作线程数
        self.batch_size = 500  # 批量处理大小
        self.sync_lock = threading.Lock()
    
    def sync_all_models(self) -> Dict[str, bool]:
        """同步所有Etsy模型数据"""
        results = {}
        
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有同步任务
                future_to_model = {
                    executor.submit(self.sync_model_data, 'product_registration'): 'product_registration',
                    executor.submit(self.sync_model_data, 'order_import_summary'): 'order_import_summary',
                    executor.submit(self.sync_model_data, 'order_statistics'): 'order_statistics',
                    executor.submit(self.sync_model_data, 'design_requirement'): 'design_requirement',
                    executor.submit(self.sync_model_data, 'purchase_requirement'): 'purchase_requirement',
                    executor.submit(self.sync_model_data, 'production_requirement'): 'production_requirement',
                    executor.submit(self.sync_model_data, 'shipping_delivery'): 'shipping_delivery',
                    executor.submit(self.sync_model_data, 'qr_code_label'): 'qr_code_label',
                    executor.submit(self.sync_model_data, 'yuntu_export'): 'yuntu_export',
                    executor.submit(self.sync_model_data, 'yuntu_deduction'): 'yuntu_deduction',
                    executor.submit(self.sync_model_data, 'store_information'): 'store_information'
                }
                
                # 收集结果
                for future in as_completed(future_to_model):
                    model_name = future_to_model[future]
                    try:
                        result = future.result()
                        results[model_name] = result
                        logger.info(f"模型 {model_name} 同步完成: {result}")
                    except Exception as e:
                        results[model_name] = False
                        logger.error(f"模型 {model_name} 同步失败: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"同步所有模型失败: {e}")
            return {model: False for model in [
                'product_registration', 'order_import_summary', 'order_statistics',
                'design_requirement', 'purchase_requirement', 'production_requirement',
                'shipping_delivery', 'qr_code_label', 'yuntu_export', 'yuntu_deduction',
                'store_information'
            ]}
    
    def sync_model_data(self, model_name: str) -> bool:
        """同步指定模型的数据"""
        try:
            with self.sync_lock:
                if model_name == 'product_registration':
                    return self._sync_product_registration()
                elif model_name == 'order_import_summary':
                    return self._sync_order_import_summary()
                elif model_name == 'order_statistics':
                    return self._sync_order_statistics()
                elif model_name == 'design_requirement':
                    return self._sync_design_requirement()
                elif model_name == 'purchase_requirement':
                    return self._sync_purchase_requirement()
                elif model_name == 'production_requirement':
                    return self._sync_production_requirement()
                elif model_name == 'shipping_delivery':
                    return self._sync_shipping_delivery()
                elif model_name == 'qr_code_label':
                    return self._sync_qr_code_label()
                elif model_name == 'yuntu_export':
                    return self._sync_yuntu_export()
                elif model_name == 'yuntu_deduction':
                    return self._sync_yuntu_deduction()
                elif model_name == 'store_information':
                    return self._sync_store_information()
                else:
                    logger.error(f"未知的模型名称: {model_name}")
                    return False
        except Exception as e:
            logger.error(f"同步模型 {model_name} 失败: {e}")
            return False
    
    def _sync_product_registration(self) -> bool:
        """同步产品登记数据"""
        try:
            # 获取统计数据
            stats = self._get_product_registration_stats()
            redis_cache.set_statistics_cache('product_registration', stats)
            
            # 分批同步列表数据
            total_count = EtsyProductRegistration.objects.count()
            for offset in range(0, total_count, self.batch_size):
                queryset = EtsyProductRegistration.objects.all()[offset:offset + self.batch_size]
                data = self._serialize_queryset(queryset)
                
                # 设置缓存
                page = (offset // self.batch_size) + 1
                redis_cache.set_list_cache('product_registration', {}, data, page, self.batch_size)
            
            logger.info(f"产品登记数据同步完成，共 {total_count} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"同步产品登记数据失败: {e}")
            return False
    
    def _sync_order_import_summary(self) -> bool:
        """同步订单导入汇总数据"""
        try:
            # 获取统计数据
            stats = self._get_order_import_summary_stats()
            redis_cache.set_statistics_cache('order_import_summary', stats)
            
            # 分批同步列表数据
            total_count = EtsyOrderImportSummary.objects.count()
            for offset in range(0, total_count, self.batch_size):
                queryset = EtsyOrderImportSummary.objects.all()[offset:offset + self.batch_size]
                data = self._serialize_queryset(queryset)
                
                # 设置缓存
                page = (offset // self.batch_size) + 1
                redis_cache.set_list_cache('order_import_summary', {}, data, page, self.batch_size)
            
            logger.info(f"订单导入汇总数据同步完成，共 {total_count} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"同步订单导入汇总数据失败: {e}")
            return False
    
    def _sync_order_statistics(self) -> bool:
        """同步订单统计数据"""
        try:
            # 获取统计数据
            stats = self._get_order_statistics_stats()
            redis_cache.set_statistics_cache('order_statistics', stats)
            
            # 分批同步列表数据
            total_count = EtsyOrderStatistics.objects.count()
            for offset in range(0, total_count, self.batch_size):
                queryset = EtsyOrderStatistics.objects.all()[offset:offset + self.batch_size]
                data = self._serialize_queryset(queryset)
                
                # 设置缓存
                page = (offset // self.batch_size) + 1
                redis_cache.set_list_cache('order_statistics', {}, data, page, self.batch_size)
            
            logger.info(f"订单统计数据同步完成，共 {total_count} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"同步订单统计数据失败: {e}")
            return False
    
    def _sync_design_requirement(self) -> bool:
        """同步设计需求数据"""
        try:
            total_count = EtsyDesignRequirement.objects.count()
            for offset in range(0, total_count, self.batch_size):
                queryset = EtsyDesignRequirement.objects.all()[offset:offset + self.batch_size]
                data = self._serialize_queryset(queryset)
                
                page = (offset // self.batch_size) + 1
                redis_cache.set_list_cache('design_requirement', {}, data, page, self.batch_size)
            
            logger.info(f"设计需求数据同步完成，共 {total_count} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"同步设计需求数据失败: {e}")
            return False
    
    def _sync_purchase_requirement(self) -> bool:
        """同步采购需求数据"""
        try:
            total_count = EtsyPurchaseRequirement.objects.count()
            for offset in range(0, total_count, self.batch_size):
                queryset = EtsyPurchaseRequirement.objects.all()[offset:offset + self.batch_size]
                data = self._serialize_queryset(queryset)
                
                page = (offset // self.batch_size) + 1
                redis_cache.set_list_cache('purchase_requirement', {}, data, page, self.batch_size)
            
            logger.info(f"采购需求数据同步完成，共 {total_count} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"同步采购需求数据失败: {e}")
            return False
    
    def _sync_production_requirement(self) -> bool:
        """同步生产需求数据"""
        try:
            total_count = EtsyProductionRequirement.objects.count()
            for offset in range(0, total_count, self.batch_size):
                queryset = EtsyProductionRequirement.objects.all()[offset:offset + self.batch_size]
                data = self._serialize_queryset(queryset)
                
                page = (offset // self.batch_size) + 1
                redis_cache.set_list_cache('production_requirement', {}, data, page, self.batch_size)
            
            logger.info(f"生产需求数据同步完成，共 {total_count} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"同步生产需求数据失败: {e}")
            return False
    
    def _sync_shipping_delivery(self) -> bool:
        """同步配货发货数据"""
        try:
            total_count = EtsyShippingDelivery.objects.count()
            for offset in range(0, total_count, self.batch_size):
                queryset = EtsyShippingDelivery.objects.all()[offset:offset + self.batch_size]
                data = self._serialize_queryset(queryset)
                
                page = (offset // self.batch_size) + 1
                redis_cache.set_list_cache('shipping_delivery', {}, data, page, self.batch_size)
            
            logger.info(f"配货发货数据同步完成，共 {total_count} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"同步配货发货数据失败: {e}")
            return False
    
    def _sync_qr_code_label(self) -> bool:
        """同步二维码标签数据"""
        try:
            total_count = EtsyQRCodeLabel.objects.count()
            for offset in range(0, total_count, self.batch_size):
                queryset = EtsyQRCodeLabel.objects.all()[offset:offset + self.batch_size]
                data = self._serialize_queryset(queryset)
                
                page = (offset // self.batch_size) + 1
                redis_cache.set_list_cache('qr_code_label', {}, data, page, self.batch_size)
            
            logger.info(f"二维码标签数据同步完成，共 {total_count} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"同步二维码标签数据失败: {e}")
            return False
    
    def _sync_yuntu_export(self) -> bool:
        """同步云途导出数据"""
        try:
            total_count = EtsyYunTuExport.objects.count()
            for offset in range(0, total_count, self.batch_size):
                queryset = EtsyYunTuExport.objects.all()[offset:offset + self.batch_size]
                data = self._serialize_queryset(queryset)
                
                page = (offset // self.batch_size) + 1
                redis_cache.set_list_cache('yuntu_export', {}, data, page, self.batch_size)
            
            logger.info(f"云途导出数据同步完成，共 {total_count} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"同步云途导出数据失败: {e}")
            return False
    
    def _sync_yuntu_deduction(self) -> bool:
        """同步云途扣费数据"""
        try:
            total_count = EtsyYunTuDeduction.objects.count()
            for offset in range(0, total_count, self.batch_size):
                queryset = EtsyYunTuDeduction.objects.all()[offset:offset + self.batch_size]
                data = self._serialize_queryset(queryset)
                
                page = (offset // self.batch_size) + 1
                redis_cache.set_list_cache('yuntu_deduction', {}, data, page, self.batch_size)
            
            logger.info(f"云途扣费数据同步完成，共 {total_count} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"同步云途扣费数据失败: {e}")
            return False
    
    def _sync_store_information(self) -> bool:
        """同步店铺信息数据"""
        try:
            total_count = EtsyStoreInformation.objects.count()
            for offset in range(0, total_count, self.batch_size):
                queryset = EtsyStoreInformation.objects.all()[offset:offset + self.batch_size]
                data = self._serialize_queryset(queryset)
                
                page = (offset // self.batch_size) + 1
                redis_cache.set_list_cache('store_information', {}, data, page, self.batch_size)
            
            logger.info(f"店铺信息数据同步完成，共 {total_count} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"同步店铺信息数据失败: {e}")
            return False
    
    def _get_product_registration_stats(self) -> Dict:
        """获取产品登记统计信息"""
        try:
            queryset = EtsyProductRegistration.objects.all()
            
            stats = {
                'total_count': queryset.count(),
                'today_count': queryset.filter(
                    created_at__date=timezone.now().date()
                ).count(),
                'low_inventory_count': queryset.filter(
                    inventory__lte=models.F('inventory_warning_line')
                ).count(),
                'avg_cost': float(queryset.aggregate(Avg('unit_cost'))['unit_cost__avg'] or 0),
                'avg_price': float(queryset.aggregate(Avg('estimated_price'))['estimated_price__avg'] or 0),
                'avg_profit_margin': float(queryset.aggregate(Avg('estimated_gross_profit_margin'))['estimated_gross_profit_margin__avg'] or 0),
                'total_inventory': queryset.aggregate(Sum('inventory'))['inventory__sum'] or 0,
                'last_sync_time': timezone.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取产品登记统计信息失败: {e}")
            return {}
    
    def _get_order_import_summary_stats(self) -> Dict:
        """获取订单导入汇总统计信息"""
        try:
            queryset = EtsyOrderImportSummary.objects.all()
            today = timezone.now().date()
            
            stats = {
                'total_count': queryset.count(),
                'today_count': queryset.filter(order_date=today).count(),
                'total_quantity': queryset.aggregate(Sum('quantity'))['quantity__sum'] or 0,
                'total_amount': float(queryset.aggregate(Sum('unit_price'))['unit_price__sum'] or 0),
                'avg_quantity': float(queryset.aggregate(Avg('quantity'))['quantity__avg'] or 0),
                'last_sync_time': timezone.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取订单导入汇总统计信息失败: {e}")
            return {}
    
    def _get_order_statistics_stats(self) -> Dict:
        """获取订单统计信息"""
        try:
            queryset = EtsyOrderStatistics.objects.all()
            
            stats = {
                'total_count': queryset.count(),
                'total_quantity': queryset.aggregate(Sum('total_quantity'))['total_quantity__sum'] or 0,
                'avg_logistics_cost': float(queryset.aggregate(Avg('logistics_cost'))['logistics_cost__avg'] or 0),
                'status_distribution': dict(queryset.values('status_indication').annotate(count=Count('id'))),
                'last_sync_time': timezone.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取订单统计信息失败: {e}")
            return {}
    
    def _serialize_queryset(self, queryset) -> List[Dict]:
        """序列化查询集"""
        try:
            data = []
            for obj in queryset:
                obj_dict = {}
                for field in obj._meta.fields:
                    value = getattr(obj, field.name)
                    if hasattr(value, 'isoformat'):  # 处理日期时间字段
                        obj_dict[field.name] = value.isoformat()
                    else:
                        obj_dict[field.name] = value
                data.append(obj_dict)
            return data
        except Exception as e:
            logger.error(f"序列化查询集失败: {e}")
            return []
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        try:
            models = [
                'product_registration', 'order_import_summary', 'order_statistics',
                'design_requirement', 'purchase_requirement', 'production_requirement',
                'shipping_delivery', 'qr_code_label', 'yuntu_export', 'yuntu_deduction',
                'store_information'
            ]
            
            status_info = {}
            for model in models:
                cache_key = redis_cache.get_cache_key(model, 'statistics')
                cached_data = redis_cache.get_cache(cache_key)
                
                if cached_data:
                    status_info[model] = {
                        'synced': True,
                        'last_sync_time': cached_data.get('last_sync_time'),
                        'record_count': cached_data.get('total_count', 0)
                    }
                else:
                    status_info[model] = {
                        'synced': False,
                        'last_sync_time': None,
                        'record_count': 0
                    }
            
            return {
                'overall_status': all(info['synced'] for info in status_info.values()),
                'models': status_info,
                'redis_health': redis_cache.health_check(),
                'cache_info': redis_cache.get_cache_info()
            }
            
        except Exception as e:
            logger.error(f"获取同步状态失败: {e}")
            return {}


# 全局同步服务实例
etsy_sync = EtsySyncService()
