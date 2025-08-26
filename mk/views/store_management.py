from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta

from ..models.store_management import Store, StoreInventory, StoreTransaction
from ..models.Department import Department
from ..models.User import User
from ..serializers.store_management import (
    StoreSerializer, StoreListSerializer, StoreInventorySerializer,
    StoreTransactionSerializer, StoreStatisticsSerializer
)
from ..permissions.Store import StoreManagementPermission

class StoreViewSet(viewsets.ModelViewSet):
    """店铺管理视图集"""
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [StoreManagementPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'department', 'manager']
    search_fields = ['name', 'code', 'address', 'phone']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """根据操作类型选择序列化器"""
        if self.action == 'list':
            return StoreListSerializer
        return StoreSerializer
    
    def get_queryset(self):
        """根据用户权限过滤查询集"""
        user = self.request.user
        
        if user.is_super_admin:
            # 超级管理员可以看到所有店铺
            return Store.objects.all()
        elif user.is_department_manager:
            # 部门部长只能看到自己部门的店铺
            return Store.objects.filter(department=user.department)
        elif user.is_store_operator:
            # 店铺运营只能看到自己的店铺
            if user.store:
                return Store.objects.filter(id=user.store.id)
            return Store.objects.none()
        else:
            # 普通员工只能查看店铺信息
            return Store.objects.all()
    
    def perform_create(self, serializer):
        """创建店铺时的额外处理"""
        # 自动设置操作员
        if not serializer.validated_data.get('operator_id'):
            serializer.save(operator_id=self.request.user.id)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """更新店铺时的额外处理"""
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def my_stores(self, request):
        """获取当前用户管理的店铺"""
        user = request.user
        if user.is_store_operator and user.store:
            serializer = self.get_serializer(user.store)
            return Response(serializer.data)
        elif user.is_department_manager:
            stores = Store.objects.filter(department=user.department)
            serializer = StoreListSerializer(stores, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': '没有管理的店铺'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """更改店铺状态"""
        store = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({'error': '请提供新的状态'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_status not in dict(Store.STATUS_CHOICES):
            return Response({'error': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)
        
        store.status = new_status
        store.save()
        
        serializer = self.get_serializer(store)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取店铺统计信息"""
        user = request.user
        
        # 根据用户权限过滤数据
        if user.is_super_admin:
            stores = Store.objects.all()
        elif user.is_department_manager:
            stores = Store.objects.filter(department=user.department)
        elif user.is_store_operator and user.store:
            stores = Store.objects.filter(id=user.store.id)
        else:
            stores = Store.objects.all()
        
        # 计算统计信息
        total_stores = stores.count()
        active_stores = stores.filter(status='active').count()
        total_employees = User.objects.filter(store__in=stores).count()
        total_inventory_items = StoreInventory.objects.filter(store__in=stores).count()
        total_transactions = StoreTransaction.objects.filter(store__in=stores).count()
        total_transaction_amount = StoreTransaction.objects.filter(store__in=stores).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        data = {
            'total_stores': total_stores,
            'active_stores': active_stores,
            'total_employees': total_employees,
            'total_inventory_items': total_inventory_items,
            'total_transactions': total_transactions,
            'total_transaction_amount': total_transaction_amount
        }
        
        serializer = StoreStatisticsSerializer(data)
        return Response(serializer.data)

class StoreInventoryViewSet(viewsets.ModelViewSet):
    """店铺库存管理视图集"""
    queryset = StoreInventory.objects.all()
    serializer_class = StoreInventorySerializer
    permission_classes = [StoreManagementPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['store', 'product_code']
    search_fields = ['product_name', 'product_code']
    ordering_fields = ['product_name', 'quantity', 'unit_price', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """根据用户权限过滤查询集"""
        user = self.request.user
        
        if user.is_super_admin:
            return StoreInventory.objects.all()
        elif user.is_department_manager:
            return StoreInventory.objects.filter(store__department=user.department)
        elif user.is_store_operator:
            if user.store:
                return StoreInventory.objects.filter(store=user.store)
            return StoreInventory.objects.none()
        else:
            return StoreInventory.objects.all()
    
    def perform_create(self, serializer):
        """创建库存时的额外处理"""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """调整库存数量"""
        inventory = self.get_object()
        adjustment = request.data.get('adjustment', 0)
        reason = request.data.get('reason', '库存调整')
        
        try:
            adjustment = int(adjustment)
        except (TypeError, ValueError):
            return Response({'error': '调整数量必须是整数'}, status=status.HTTP_400_BAD_REQUEST)
        
        new_quantity = inventory.quantity + adjustment
        if new_quantity < 0:
            return Response({'error': '库存数量不能为负数'}, status=status.HTTP_400_BAD_REQUEST)
        
        inventory.quantity = new_quantity
        inventory.save()
        
        # 记录交易
        StoreTransaction.objects.create(
            store=inventory.store,
            transaction_type='adjustment',
            amount=0,
            description=f'{reason}: {adjustment:+d}',
            operator=request.user
        )
        
        serializer = self.get_serializer(inventory)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """获取低库存商品"""
        user = request.user
        
        if user.is_super_admin:
            inventories = StoreInventory.objects.filter(quantity__lte=F('min_stock'))
        elif user.is_department_manager:
            inventories = StoreInventory.objects.filter(
                store__department=user.department,
                quantity__lte=F('min_stock')
            )
        elif user.is_store_operator and user.store:
            inventories = StoreInventory.objects.filter(
                store=user.store,
                quantity__lte=F('min_stock')
            )
        else:
            inventories = StoreInventory.objects.none()
        
        serializer = self.get_serializer(inventories, many=True)
        return Response(serializer.data)

class StoreTransactionViewSet(viewsets.ModelViewSet):
    """店铺交易记录视图集"""
    queryset = StoreTransaction.objects.all()
    serializer_class = StoreTransactionSerializer
    permission_classes = [StoreManagementPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['store', 'transaction_type', 'operator']
    search_fields = ['description']
    ordering_fields = ['amount', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """根据用户权限过滤查询集"""
        user = self.request.user
        
        if user.is_super_admin:
            return StoreTransaction.objects.all()
        elif user.is_department_manager:
            return StoreTransaction.objects.filter(store__department=user.department)
        elif user.is_store_operator:
            if user.store:
                return StoreTransaction.objects.filter(store=user.store)
            return StoreTransaction.objects.none()
        else:
            return StoreTransaction.objects.all()
    
    def perform_create(self, serializer):
        """创建交易记录时的额外处理"""
        if not serializer.validated_data.get('operator_id'):
            serializer.save(operator_id=self.request.user.id)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """获取每日交易汇总"""
        user = request.user
        date_str = request.query_params.get('date', timezone.now().strftime('%Y-%m-%d'))
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': '日期格式错误，请使用YYYY-MM-DD格式'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 根据用户权限过滤数据
        if user.is_super_admin:
            transactions = StoreTransaction.objects.filter(
                created_at__date=target_date
            )
        elif user.is_department_manager:
            transactions = StoreTransaction.objects.filter(
                store__department=user.department,
                created_at__date=target_date
            )
        elif user.is_store_operator and user.store:
            transactions = StoreTransaction.objects.filter(
                store=user.store,
                created_at__date=target_date
            )
        else:
            transactions = StoreTransaction.objects.none()
        
        # 按交易类型汇总
        summary = transactions.values('transaction_type').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        return Response({
            'date': date_str,
            'summary': summary,
            'total_count': transactions.count(),
            'total_amount': transactions.aggregate(total=Sum('amount'))['total'] or 0
        })
    
    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        """获取月度交易报告"""
        user = request.user
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', timezone.now().month)
        
        try:
            year, month = int(year), int(month)
        except ValueError:
            return Response({'error': '年份和月份必须是数字'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 根据用户权限过滤数据
        if user.is_super_admin:
            transactions = StoreTransaction.objects.filter(
                created_at__year=year,
                created_at__month=month
            )
        elif user.is_department_manager:
            transactions = StoreTransaction.objects.filter(
                store__department=user.department,
                created_at__year=year,
                created_at__month=month
            )
        elif user.is_store_operator and user.store:
            transactions = StoreTransaction.objects.filter(
                store=user.store,
                created_at__year=year,
                created_at__month=month
            )
        else:
            transactions = StoreTransaction.objects.none()
        
        # 按日期汇总
        daily_summary = transactions.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('day')
        
        return Response({
            'year': year,
            'month': month,
            'daily_summary': daily_summary,
            'total_count': transactions.count(),
            'total_amount': transactions.aggregate(total=Sum('amount'))['total'] or 0
        })
