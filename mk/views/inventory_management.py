from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from ..models.inventory_management import Inventory, InventoryTransaction, InventoryConsumption
from ..models.order_management import Order, OrderBatch
from ..serializers.inventory_management import (
    InventorySerializer, InventoryTransactionSerializer, 
    InventoryConsumptionSerializer, OrderSerializer, OrderBatchSerializer
)
from ..services.coze_workflow_service import CozeWorkflowService
from ..services.inventory_service import InventoryService
from ..services.scheduler_service import SchedulerService
from ..permissions.inventory_management import InventoryPermission


class InventoryViewSet(viewsets.ModelViewSet):
    """库存管理视图集"""
    
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated, InventoryPermission]
    
    def get_queryset(self):
        """根据店铺过滤库存"""
        queryset = super().get_queryset()
        store_id = self.request.query_params.get('store_id')
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取库存摘要"""
        try:
            store_id = request.query_params.get('store_id')
            inventory_service = InventoryService()
            summary = inventory_service.get_inventory_summary(store_id)
            
            if "error" in summary:
                return Response(
                    {"error": summary["error"]}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(summary)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def adjust(self, request, pk=None):
        """调整库存"""
        try:
            adjustment_type = request.data.get('adjustment_type')
            quantity = request.data.get('quantity')
            notes = request.data.get('notes', '')
            
            if not adjustment_type or quantity is None:
                return Response(
                    {"error": "adjustment_type 和 quantity 是必需的"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            inventory_service = InventoryService()
            result = inventory_service.adjust_inventory(
                inventory_id=pk,
                adjustment_type=adjustment_type,
                quantity=quantity,
                notes=notes,
                user_id=request.user.id
            )
            
            if result["success"]:
                return Response(result)
            else:
                return Response(
                    {"error": result["message"]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_adjust(self, request):
        """批量调整库存"""
        try:
            adjustments = request.data.get('adjustments', [])
            
            if not adjustments:
                return Response(
                    {"error": "adjustments 是必需的"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            inventory_service = InventoryService()
            results = []
            
            for adjustment in adjustments:
                result = inventory_service.adjust_inventory(
                    inventory_id=adjustment['inventory_id'],
                    adjustment_type=adjustment['adjustment_type'],
                    quantity=adjustment['quantity'],
                    notes=adjustment.get('notes', ''),
                    user_id=request.user.id
                )
                results.append(result)
            
            success_count = sum(1 for r in results if r["success"])
            failed_count = len(results) - success_count
            
            return Response({
                "total": len(results),
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """库存交易记录视图集"""
    
    queryset = InventoryTransaction.objects.all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated, InventoryPermission]
    
    def get_queryset(self):
        """根据条件过滤交易记录"""
        queryset = super().get_queryset()
        
        # 按库存过滤
        inventory_id = self.request.query_params.get('inventory_id')
        if inventory_id:
            queryset = queryset.filter(inventory_id=inventory_id)
        
        # 按交易类型过滤
        transaction_type = self.request.query_params.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # 按日期范围过滤
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取交易统计"""
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            queryset = self.get_queryset()
            
            if start_date:
                queryset = queryset.filter(created_at__date__gte=start_date)
            if end_date:
                queryset = queryset.filter(created_at__date__lte=end_date)
            
            # 按交易类型统计
            type_stats = {}
            for transaction_type, _ in InventoryTransaction.TRANSACTION_TYPES:
                count = queryset.filter(transaction_type=transaction_type).count()
                total_quantity = queryset.filter(transaction_type=transaction_type).aggregate(
                    total=models.Sum('quantity')
                )['total'] or 0
                type_stats[transaction_type] = {
                    'count': count,
                    'total_quantity': total_quantity
                }
            
            # 按日期统计
            date_stats = queryset.extra(
                select={'date': 'DATE(created_at)'}
            ).values('date').annotate(
                count=models.Count('id'),
                total_quantity=models.Sum('quantity')
            ).order_by('date')
            
            return Response({
                'type_statistics': type_stats,
                'date_statistics': list(date_stats),
                'total_transactions': queryset.count()
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InventoryConsumptionViewSet(viewsets.ReadOnlyModelViewSet):
    """库存消耗统计视图集"""
    
    queryset = InventoryConsumption.objects.all()
    serializer_class = InventoryConsumptionSerializer
    permission_classes = [IsAuthenticated, InventoryPermission]
    
    def get_queryset(self):
        """根据店铺过滤消耗统计"""
        queryset = super().get_queryset()
        store_id = self.request.query_params.get('store_id')
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        return queryset


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """订单视图集"""
    
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, InventoryPermission]
    
    def get_queryset(self):
        """根据条件过滤订单"""
        queryset = super().get_queryset()
        
        # 按店铺过滤
        store_id = self.request.query_params.get('store_id')
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        # 按处理状态过滤
        is_processed = self.request.query_params.get('is_processed')
        if is_processed is not None:
            queryset = queryset.filter(is_processed=is_processed.lower() == 'true')
        
        # 按日期范围过滤
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def process_inventory(self, request):
        """处理订单库存"""
        try:
            order_ids = request.data.get('order_ids', [])
            
            if not order_ids:
                return Response(
                    {"error": "order_ids 是必需的"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            inventory_service = InventoryService()
            results = []
            
            for order_id in order_ids:
                try:
                    order = Order.objects.get(id=order_id)
                    result = inventory_service.process_order_inventory(order)
                    results.append({
                        "order_id": order_id,
                        "order_number": order.order_number,
                        "result": result
                    })
                except Order.DoesNotExist:
                    results.append({
                        "order_id": order_id,
                        "result": {"success": False, "message": "订单不存在"}
                    })
            
            success_count = sum(1 for r in results if r["result"]["success"])
            failed_count = len(results) - success_count
            
            return Response({
                "total": len(results),
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def process_all_unprocessed(self, request):
        """处理所有未处理的订单"""
        try:
            inventory_service = InventoryService()
            result = inventory_service.process_all_unprocessed_orders()
            
            if result["success"]:
                return Response(result)
            else:
                return Response(
                    {"error": result["message"]}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderBatchViewSet(viewsets.ReadOnlyModelViewSet):
    """订单批次视图集"""
    
    queryset = OrderBatch.objects.all()
    serializer_class = OrderBatchSerializer
    permission_classes = [IsAuthenticated, InventoryPermission]
    
    def get_queryset(self):
        """根据条件过滤批次记录"""
        queryset = super().get_queryset()
        
        # 按完成状态过滤
        is_completed = self.request.query_params.get('is_completed')
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == 'true')
        
        # 按日期范围过滤
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(execution_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(execution_time__date__lte=end_date)
        
        return queryset.order_by('-execution_time')


class WorkflowManagementViewSet(viewsets.ViewSet):
    """工作流管理视图集"""
    
    permission_classes = [IsAuthenticated, InventoryPermission]
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """获取工作流状态"""
        try:
            workflow_service = CozeWorkflowService()
            status_info = workflow_service.get_workflow_status()
            
            if "error" in status_info:
                return Response(
                    {"error": status_info["error"]}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(status_info)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def execute(self, request):
        """手动执行工作流"""
        try:
            workflow_service = CozeWorkflowService()
            result = workflow_service.manual_refresh()
            
            if result["success"]:
                return Response(result)
            else:
                return Response(
                    {"error": result.get("error", "执行失败")}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def scheduler_status(self, request):
        """获取定时任务状态"""
        try:
            scheduler_service = SchedulerService()
            status_info = scheduler_service.get_scheduler_status()
            
            if "error" in status_info:
                return Response(
                    {"error": status_info["error"]}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(status_info)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def force_execute(self, request):
        """强制执行工作流（忽略时间间隔）"""
        try:
            scheduler_service = SchedulerService()
            result = scheduler_service.force_execute_workflow()
            
            if result["success"]:
                return Response(result)
            else:
                return Response(
                    {"error": result.get("message", "执行失败")}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def update_interval(self, request):
        """更新执行间隔"""
        try:
            new_interval = request.data.get('interval')
            
            if not new_interval:
                return Response(
                    {"error": "interval 是必需的"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            scheduler_service = SchedulerService()
            result = scheduler_service.update_execution_interval(new_interval)
            
            if result["success"]:
                return Response(result)
            else:
                return Response(
                    {"error": result["message"]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
