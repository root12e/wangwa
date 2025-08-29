from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import io
import os
import logging

from ..models.etsy_models import (
    EtsyProductRegistration, EtsyOrderImportSummary, EtsyOrderStatistics,
    EtsyDesignRequirement, EtsyPurchaseRequirement, EtsyProductionRequirement,
    EtsyShippingDelivery, EtsyQRCodeLabel, EtsyYunTuExport, 
    EtsyYunTuDeduction, EtsyStoreInformation
)
from ..serializers.etsy_serializers import (
    EtsyProductRegistrationSerializer, EtsyOrderImportSummarySerializer, EtsyOrderStatisticsSerializer,
    EtsyDesignRequirementSerializer, EtsyPurchaseRequirementSerializer, EtsyProductionRequirementSerializer,
    EtsyShippingDeliverySerializer, EtsyQRCodeLabelSerializer, EtsyYunTuExportSerializer,
    EtsyYunTuDeductionSerializer, EtsyStoreInformationSerializer,
    EtsyBulkCreateSerializer, EtsyBulkUpdateSerializer, EtsyBulkDeleteSerializer,
    EtsyFilterSerializer, EtsySortSerializer
)
from ..permissions.etsy_permissions import EtsyPermission
from ..services.redis_cache_service import redis_cache
from ..services.etsy_sync_service import etsy_sync

logger = logging.getLogger(__name__)


class EtsyPagination(PageNumberPagination):
    """Etsy分页器"""
    page_size = 20
    page_size_query_param = 'page_size'


class BaseEtsyViewSet(viewsets.ModelViewSet):
    """Etsy基础视图集"""
    permission_classes = [EtsyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['sku', 'store_name', 'product_name']
    ordering_fields = ['created_at', 'updated_at', 'order_date']
    ordering = ['-created_at']
    pagination_class = EtsyPagination
    
    def get_model_name(self):
        """获取模型名称"""
        return self.model.__name__.lower()

    def get_queryset(self):
        """获取查询集，支持高级筛选和缓存"""
        # 尝试从缓存获取数据
        cache_key = self._get_cache_key()
        cached_data = redis_cache.get_cache(cache_key)
        
        if cached_data:
            logger.info(f"从缓存获取 {self.get_model_name()} 数据")
            return self._create_queryset_from_cache(cached_data)
        
        # 缓存未命中，从数据库获取
        logger.info(f"从数据库获取 {self.get_model_name()} 数据")
        queryset = super().get_queryset()
        queryset = self._apply_filters(queryset)
        
        # 将数据存入缓存
        self._cache_queryset(queryset)
        
        return queryset
    
    def _get_cache_key(self):
        """生成缓存键"""
        filters = self._get_filter_params()
        page = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', 20)
        
        return redis_cache.get_cache_key(
            self.get_model_name(), 'list',
            page=page, page_size=page_size, **filters
        )
    
    def _get_filter_params(self):
        """获取筛选参数"""
        return {
            'search': self.request.query_params.get('search', ''),
            'start_date': self.request.query_params.get('start_date', ''),
            'end_date': self.request.query_params.get('end_date', ''),
            'store': self.request.query_params.get('store', ''),
            'status': self.request.query_params.get('status', ''),
            'operation_personnel': self.request.query_params.get('operation_personnel', ''),
            'min_price': self.request.query_params.get('min_price', ''),
            'max_price': self.request.query_params.get('max_price', ''),
            'min_quantity': self.request.query_params.get('min_quantity', ''),
            'max_quantity': self.request.query_params.get('max_quantity', '')
        }
    
    def _apply_filters(self, queryset):
        """应用筛选条件"""
        filters = self._get_filter_params()
        
        if filters['search']:
            queryset = queryset.filter(
                Q(sku__icontains=filters['search']) |
                Q(store_name__icontains=filters['search']) |
                Q(product_name__icontains=filters['search'])
            )
        
        if filters['start_date']:
            try:
                start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
                if hasattr(self.model, 'order_date'):
                    queryset = queryset.filter(order_date__gte=start_date)
                elif hasattr(self.model, 'created_at'):
                    queryset = queryset.filter(created_at__date__gte=start_date)
            except ValueError:
                pass
        
        if filters['end_date']:
            try:
                end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
                if hasattr(self.model, 'order_date'):
                    queryset = queryset.filter(order_date__lte=end_date)
                elif hasattr(self.model, 'created_at'):
                    queryset = queryset.filter(created_at__date__lte=end_date)
            except ValueError:
                pass
        
        if filters['store']:
            if hasattr(self.model, 'store_name'):
                queryset = queryset.filter(store_name__icontains=filters['store'])
            elif hasattr(self.model, 'store'):
                queryset = queryset.filter(store__icontains=filters['store'])
        
        if filters['status']:
            if hasattr(self.model, 'status_indication'):
                queryset = queryset.filter(status_indication__icontains=filters['status'])
            elif hasattr(self.model, 'label_status'):
                queryset = queryset.filter(label_status__icontains=filters['status'])
        
        if filters['operation_personnel']:
            if hasattr(self.model, 'operation_personnel'):
                queryset = queryset.filter(operation_personnel__icontains=filters['operation_personnel'])
        
        # 价格筛选
        if filters['min_price']:
            try:
                min_price = float(filters['min_price'])
                if hasattr(self.model, 'unit_price'):
                    queryset = queryset.filter(unit_price__gte=min_price)
                elif hasattr(self.model, 'estimated_price'):
                    queryset = queryset.filter(estimated_price__gte=min_price)
            except ValueError:
                pass
        
        if filters['max_price']:
            try:
                max_price = float(filters['max_price'])
                if hasattr(self.model, 'unit_price'):
                    queryset = queryset.filter(unit_price__lte=max_price)
                elif hasattr(self.model, 'estimated_price'):
                    queryset = queryset.filter(estimated_price__lte=max_price)
            except ValueError:
                pass
        
        # 数量筛选
        if filters['min_quantity']:
            try:
                min_quantity = int(filters['min_quantity'])
                if hasattr(self.model, 'quantity'):
                    queryset = queryset.filter(quantity__gte=min_quantity)
                elif hasattr(self.model, 'total_quantity'):
                    queryset = queryset.filter(total_quantity__gte=min_quantity)
            except ValueError:
                pass
        
        if filters['max_quantity']:
            try:
                max_quantity = int(filters['max_quantity'])
                if hasattr(self.model, 'quantity'):
                    queryset = queryset.filter(quantity__lte=max_quantity)
                elif hasattr(self.model, 'total_quantity'):
                    queryset = queryset.filter(total_quantity__lte=max_quantity)
            except ValueError:
                pass
        
        return queryset
    
    def _cache_queryset(self, queryset):
        """缓存查询集"""
        try:
            filters = self._get_filter_params()
            page = int(self.request.query_params.get('page', 1))
            page_size = int(self.request.query_params.get('page_size', 20))
            
            # 序列化数据
            data = self.get_serializer(queryset, many=True).data
            
            # 设置缓存
            redis_cache.set_list_cache(
                self.get_model_name(), filters, data, page, page_size
            )
            
            logger.info(f"缓存 {self.get_model_name()} 数据，共 {len(data)} 条记录")
            
        except Exception as e:
            logger.error(f"缓存查询集失败: {e}")
    
    def _create_queryset_from_cache(self, cached_data):
        """从缓存数据创建查询集"""
        try:
            # 这里返回一个模拟的查询集，实际使用时需要根据具体需求调整
            from django.db.models.query import QuerySet
            
            # 创建一个空的查询集
            queryset = QuerySet(model=self.model)
            
            # 将缓存数据附加到查询集
            queryset._result_cache = cached_data
            
            return queryset
            
        except Exception as e:
            logger.error(f"从缓存创建查询集失败: {e}")
            return super().get_queryset()
    
    def perform_create(self, serializer):
        """创建时使缓存失效"""
        instance = serializer.save()
        redis_cache.invalidate_cache_on_update(self.get_model_name())
        return instance
    
    def perform_update(self, serializer):
        """更新时使缓存失效"""
        instance = serializer.save()
        redis_cache.invalidate_cache_on_update(self.get_model_name(), instance.id)
        return instance
    
    def perform_destroy(self, instance):
        """删除时使缓存失效"""
        instance_id = instance.id
        instance.delete()
        redis_cache.invalidate_cache_on_update(self.get_model_name(), instance_id)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """批量创建"""
        serializer = EtsyBulkCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data['data']
            created_objects = []
            errors = []
            
            for item in data:
                try:
                    model_serializer = self.get_serializer(data=item)
                    if model_serializer.is_valid():
                        obj = model_serializer.save()
                        created_objects.append(obj)
                    else:
                        errors.append({
                            'data': item,
                            'errors': model_serializer.errors
                        })
                except Exception as e:
                    errors.append({
                        'data': item,
                        'errors': str(e)
                    })
            
            # 批量创建后使缓存失效
            redis_cache.invalidate_cache_on_update(self.get_model_name())
            
            return Response({
                'message': f'成功创建 {len(created_objects)} 条记录',
                'created_count': len(created_objects),
                'error_count': len(errors),
                'errors': errors
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """批量更新"""
        serializer = EtsyBulkUpdateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data['data']
            updated_objects = []
            errors = []
            
            for item in data:
                try:
                    obj_id = item.get('id')
                    if obj_id:
                        instance = self.get_queryset().filter(id=obj_id).first()
                        if instance:
                            model_serializer = self.get_serializer(instance, data=item, partial=True)
                            if model_serializer.is_valid():
                                obj = model_serializer.save()
                                updated_objects.append(obj)
                            else:
                                errors.append({
                                    'id': obj_id,
                                    'errors': model_serializer.errors
                                })
                        else:
                            errors.append({
                                'id': obj_id,
                                'errors': '对象不存在'
                            })
                    else:
                        errors.append({
                            'data': item,
                            'errors': '缺少ID字段'
                        })
                except Exception as e:
                    errors.append({
                        'data': item,
                        'errors': str(e)
                    })
            
            # 批量更新后使缓存失效
            redis_cache.invalidate_cache_on_update(self.get_model_name())
            
            return Response({
                'message': f'成功更新 {len(updated_objects)} 条记录',
                'updated_count': len(updated_objects),
                'error_count': len(errors),
                'errors': errors
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """批量删除"""
        serializer = EtsyBulkDeleteSerializer(data=request.data)
        if serializer.is_valid():
            ids = serializer.validated_data['ids']
            deleted_count = 0
            errors = []
            
            for obj_id in ids:
                try:
                    instance = self.get_queryset().filter(id=obj_id).first()
                    if instance:
                        instance.delete()
                        deleted_count += 1
                    else:
                        errors.append({
                            'id': obj_id,
                            'error': '对象不存在'
                        })
                except Exception as e:
                    errors.append({
                        'id': obj_id,
                        'error': str(e)
                    })
            
            # 批量删除后使缓存失效
            redis_cache.invalidate_cache_on_update(self.get_model_name())
            
            return Response({
                'message': f'成功删除 {deleted_count} 条记录',
                'deleted_count': deleted_count,
                'error_count': len(errors),
                'errors': errors
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        """导出Excel"""
        try:
            queryset = self.get_queryset()
            data = self.get_serializer(queryset, many=True).data
            
            # 创建DataFrame
            df = pd.DataFrame(data)
            
            # 创建Excel文件
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='数据', index=False)
            
            output.seek(0)
            
            # 生成响应
            filename = f"{self.get_model_name()}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            response = Response(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"导出Excel失败: {e}")
            return Response({'error': '导出失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取统计信息"""
        try:
            # 尝试从缓存获取统计信息
            cached_stats = redis_cache.get_statistics_cache(self.get_model_name())
            if cached_stats:
                return Response(cached_stats)
            
            # 缓存未命中，从数据库计算
            queryset = self.get_queryset()
            
            # 基础统计
            stats = {
                'total_count': queryset.count(),
                'last_sync_time': timezone.now().isoformat()
            }
            
            # 根据模型类型添加特定统计
            if hasattr(self.model, 'unit_cost'):
                stats['avg_cost'] = float(queryset.aggregate(Avg('unit_cost'))['unit_cost__avg'] or 0)
            
            if hasattr(self.model, 'estimated_price'):
                stats['avg_price'] = float(queryset.aggregate(Avg('estimated_price'))['estimated_price__avg'] or 0)
            
            if hasattr(self.model, 'inventory'):
                stats['total_inventory'] = queryset.aggregate(Sum('inventory'))['inventory__sum'] or 0
            
            if hasattr(self.model, 'quantity'):
                stats['total_quantity'] = queryset.aggregate(Sum('quantity'))['quantity__sum'] or 0
            
            # 设置缓存
            redis_cache.set_statistics_cache(self.get_model_name(), stats)
            
            return Response(stats)
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return Response({'error': '获取统计信息失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def sync_data(self, request):
        """手动同步数据到Redis"""
        try:
            model_name = self.get_model_name()
            success = etsy_sync.sync_model_data(model_name)
            
            if success:
                return Response({
                    'message': f'{model_name} 数据同步成功',
                    'success': True
                })
            else:
                return Response({
                    'message': f'{model_name} 数据同步失败',
                    'success': False
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"手动同步数据失败: {e}")
            return Response({
                'message': '数据同步失败',
                'error': str(e),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 具体的视图集类
class EtsyProductRegistrationViewSet(BaseEtsyViewSet):
    """Etsy产品登记视图集"""
    queryset = EtsyProductRegistration.objects.all()
    serializer_class = EtsyProductRegistrationSerializer
    search_fields = ['product_name', 'store_sku', 'sku_1688', 'listing_store']
    
    @action(detail=False, methods=['get'])
    def inventory_warning(self, request):
        """库存预警"""
        try:
            # 尝试从缓存获取
            cache_key = redis_cache.get_cache_key('product_registration', 'inventory_warning')
            cached_data = redis_cache.get_cache(cache_key)
            
            if cached_data:
                return Response(cached_data)
            
            # 从数据库获取
            queryset = self.get_queryset()
            warning_items = queryset.filter(
                inventory__lte=models.F('inventory_warning_line')
            )
            serializer = self.get_serializer(warning_items, many=True)
            
            # 缓存结果
            redis_cache.set_cache(cache_key, serializer.data, timeout=3600)  # 1小时过期
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"获取库存预警失败: {e}")
            return Response({'error': '获取库存预警失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EtsyOrderImportSummaryViewSet(BaseEtsyViewSet):
    """Etsy订单导入汇总视图集"""
    queryset = EtsyOrderImportSummary.objects.all()
    serializer_class = EtsyOrderImportSummarySerializer
    search_fields = ['order_number', 'buyer_name', 'sku', 'store']


class EtsyOrderStatisticsViewSet(BaseEtsyViewSet):
    """Etsy订单统计视图集"""
    queryset = EtsyOrderStatistics.objects.all()
    serializer_class = EtsyOrderStatisticsSerializer
    search_fields = ['platform_order_number', 'sku', 'store_name']


class EtsyDesignRequirementViewSet(BaseEtsyViewSet):
    """Etsy设计需求视图集"""
    queryset = EtsyDesignRequirement.objects.all()
    serializer_class = EtsyDesignRequirementSerializer
    search_fields = ['order_number', 'sku', 'chinese_name']


class EtsyPurchaseRequirementViewSet(BaseEtsyViewSet):
    """Etsy采购需求视图集"""
    queryset = EtsyPurchaseRequirement.objects.all()
    serializer_class = EtsyPurchaseRequirementSerializer
    search_fields = ['order_number', 'sku', 'chinese_name']


class EtsyProductionRequirementViewSet(BaseEtsyViewSet):
    """Etsy生产需求视图集"""
    queryset = EtsyProductionRequirement.objects.all()
    serializer_class = EtsyProductionRequirementSerializer
    search_fields = ['order_number', 'sku']


class EtsyShippingDeliveryViewSet(BaseEtsyViewSet):
    """Etsy配货发货视图集"""
    queryset = EtsyShippingDelivery.objects.all()
    serializer_class = EtsyShippingDeliverySerializer
    search_fields = ['customer_order_number', 'sku', 'store_name']


class EtsyQRCodeLabelViewSet(BaseEtsyViewSet):
    """Etsy草料二维码视图集"""
    queryset = EtsyQRCodeLabel.objects.all()
    serializer_class = EtsyQRCodeLabelSerializer
    search_fields = ['order_number', 'sku', 'store_name']


class EtsyYunTuExportViewSet(BaseEtsyViewSet):
    """Etsy云途导出视图集"""
    queryset = EtsyYunTuExport.objects.all()
    serializer_class = EtsyYunTuExportSerializer
    search_fields = ['customer_order_number', 'tracking_number']


class EtsyYunTuDeductionViewSet(BaseEtsyViewSet):
    """Etsy云途扣费视图集"""
    queryset = EtsyYunTuDeduction.objects.all()
    serializer_class = EtsyYunTuDeductionSerializer
    search_fields = ['customer_order_number', 'tracking_number']


class EtsyStoreInformationViewSet(BaseEtsyViewSet):
    """Etsy店铺信息视图集"""
    queryset = EtsyStoreInformation.objects.all()
    serializer_class = EtsyStoreInformationSerializer
    search_fields = ['store', 'store_code', 'responsible_person']


# 数据同步管理视图
class EtsySyncManagementViewSet(viewsets.ViewSet):
    """Etsy数据同步管理视图集"""
    permission_classes = [EtsyPermission]
    
    @action(detail=False, methods=['post'])
    def sync_all(self, request):
        """同步所有模型数据"""
        try:
            results = etsy_sync.sync_all_models()
            return Response({
                'message': '数据同步完成',
                'results': results,
                'success': True
            })
        except Exception as e:
            logger.error(f"同步所有模型失败: {e}")
            return Response({
                'message': '数据同步失败',
                'error': str(e),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def sync_status(self, request):
        """获取同步状态"""
        try:
            status_info = etsy_sync.get_sync_status()
            return Response(status_info)
        except Exception as e:
            logger.error(f"获取同步状态失败: {e}")
            return Response({
                'error': '获取同步状态失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def cache_info(self, request):
        """获取缓存信息"""
        try:
            cache_info = redis_cache.get_cache_info()
            return Response(cache_info)
        except Exception as e:
            logger.error(f"获取缓存信息失败: {e}")
            return Response({
                'error': '获取缓存信息失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
