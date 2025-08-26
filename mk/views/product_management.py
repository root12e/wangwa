from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Avg, Count, F
from django.utils import timezone
from datetime import datetime, timedelta

from ..models.product_management import Product, ProductCategory, ProductImage, ProductTransaction
from ..models.store_management import Store
from ..models.User import User
from ..serializers.product_management import (
    ProductSerializer, ProductDetailSerializer, ProductListSerializer,
    ProductCreateSerializer, ProductUpdateSerializer, ProductTransactionSerializer,
    ProductTransactionCreateSerializer, ProductInventorySerializer,
    ProductSearchSerializer, ProductBulkUpdateSerializer, ProductExportSerializer,
    ProductCategorySerializer, ProductImageSerializer
)
from ..permissions.product_management import (
    ProductPermission, ProductCreatePermission, ProductUpdatePermission,
    ProductDeletePermission, ProductViewPermission, StoreProductPermission
)


class ProductPagination(PageNumberPagination):
    """产品分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    """产品管理视图集"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['store', 'category', 'production_method', 'is_active']
    search_fields = ['product_name', 'product_model', 'sku', 'production_batch']
    ordering_fields = ['created_at', 'updated_at', 'inventory', 'selling_price', 'sales_profit']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """根据用户权限过滤查询集"""
        user = self.request.user
        
        if user.is_super_admin:
            return Product.objects.all()
        elif user.is_department_manager and user.department:
            return Product.objects.filter(store__department=user.department)
        elif user.is_store_operator and user.store:
            return Product.objects.filter(store=user.store)
        else:
            return Product.objects.none()
    
    def get_serializer_class(self):
        """根据操作类型选择序列化器"""
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_permissions(self):
        """根据操作类型设置权限"""
        if self.action == 'create':
            permission_classes = [ProductCreatePermission]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [ProductUpdatePermission]
        elif self.action == 'destroy':
            permission_classes = [ProductDeletePermission]
        elif self.action == 'retrieve':
            permission_classes = [ProductViewPermission]
        else:
            permission_classes = [ProductPermission]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def inventory(self, request):
        """获取库存信息"""
        queryset = self.get_queryset()
        serializer = ProductInventorySerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """获取库存不足的产品"""
        queryset = self.get_queryset().filter(
            inventory__lte=F('min_stock')
        )
        serializer = ProductInventorySerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """产品搜索"""
        serializer = ProductSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        queryset = self.get_queryset()
        
        # 关键词搜索
        keyword = serializer.validated_data.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(product_name__icontains=keyword) |
                Q(product_model__icontains=keyword) |
                Q(sku__icontains=keyword) |
                Q(production_batch__icontains=keyword)
            )
        
        # 店铺过滤
        store_id = serializer.validated_data.get('store_id')
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        # 分类过滤
        category_id = serializer.validated_data.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 价格范围过滤
        min_price = serializer.validated_data.get('min_price')
        max_price = serializer.validated_data.get('max_price')
        if min_price is not None:
            queryset = queryset.filter(selling_price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(selling_price__lte=max_price)
        
        # 库存状态过滤
        stock_status = serializer.validated_data.get('stock_status')
        if stock_status:
            if stock_status == 'low':
                queryset = queryset.filter(inventory__lte=F('min_stock'))
            elif stock_status == 'high':
                queryset = queryset.filter(inventory__gte=F('max_stock'))
            else:  # normal
                queryset = queryset.filter(
                    inventory__gt=F('min_stock'),
                    inventory__lt=F('max_stock')
                )
        
        # 活跃状态过滤
        is_active = serializer.validated_data.get('is_active')
        if is_active is not None:
            now = timezone.now()
            if is_active:
                queryset = queryset.filter(
                    Q(listing_time__lte=now) &
                    (Q(delisting_time__isnull=True) | Q(delisting_time__gt=now))
                )
            else:
                queryset = queryset.filter(
                    Q(listing_time__gt=now) | Q(delisting_time__lte=now)
                )
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """批量更新产品"""
        serializer = ProductBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_ids = serializer.validated_data['product_ids']
        updates = serializer.validated_data['updates']
        
        # 检查权限
        products = self.get_queryset().filter(id__in=product_ids)
        if len(products) != len(product_ids):
            return Response(
                {'error': '部分产品不存在或无权限访问'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 批量更新
        updated_count = products.update(**updates)
        
        return Response({
            'message': f'成功更新 {updated_count} 个产品',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取产品统计信息"""
        queryset = self.get_queryset()
        
        # 基础统计
        total_products = queryset.count()
        active_products = queryset.filter(
            Q(listing_time__lte=timezone.now()) &
            (Q(delisting_time__isnull=True) | Q(delisting_time__gt=timezone.now()))
        ).count()
        
        # 库存统计
        total_inventory = queryset.aggregate(total=Sum('inventory'))['total'] or 0
        low_stock_count = queryset.filter(
            inventory__lte=F('min_stock')
        ).count()
        
        # 价格统计
        price_stats = queryset.aggregate(
            avg_purchase_price=Avg('purchase_price'),
            avg_selling_price=Avg('selling_price'),
            total_value=Sum(F('inventory') * F('selling_price'))
        )
        
        # 利润统计
        profit_stats = queryset.aggregate(
            total_profit=Sum('total_profit'),
            avg_profit_margin=Avg('sales_profit_margin')
        )
        
        return Response({
            'total_products': total_products,
            'active_products': active_products,
            'total_inventory': total_inventory,
            'low_stock_count': low_stock_count,
            'price_stats': price_stats,
            'profit_stats': profit_stats
        })
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出产品数据"""
        serializer = ProductExportSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        queryset = self.get_queryset()
        
        # 应用过滤条件
        store_id = serializer.validated_data.get('store_id')
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        
        category_id = serializer.validated_data.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        date_from = serializer.validated_data.get('date_from')
        date_to = serializer.validated_data.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # 这里应该实现实际的导出逻辑
        # 暂时返回数据统计
        export_format = serializer.validated_data.get('format', 'excel')
        
        return Response({
            'message': f'导出请求已接收，格式: {export_format}',
            'total_records': queryset.count(),
            'format': export_format
        })


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """产品分类视图集"""
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [ProductPermission]
    
    def get_queryset(self):
        """根据用户权限过滤查询集"""
        user = self.request.user
        
        if user.is_super_admin:
            return ProductCategory.objects.all()
        elif user.is_department_manager and user.department:
            # 部门管理员可以看到本部门产品使用的分类
            return ProductCategory.objects.filter(
                product__store__department=user.department
            ).distinct()
        elif user.is_store_operator and user.store:
            # 店铺运营可以看到本店铺产品使用的分类
            return ProductCategory.objects.filter(
                product__store=user.store
            ).distinct()
        else:
            return ProductCategory.objects.none()


class ProductImageViewSet(viewsets.ModelViewSet):
    """产品图片视图集"""
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [ProductPermission]
    
    def get_queryset(self):
        """根据用户权限过滤查询集"""
        user = self.request.user
        
        if user.is_super_admin:
            return ProductImage.objects.all()
        elif user.is_department_manager and user.department:
            return ProductImage.objects.filter(
                product__store__department=user.department
            )
        elif user.is_store_operator and user.store:
            return ProductImage.objects.filter(
                product__store=user.store
            )
        else:
            return ProductImage.objects.none()


class ProductTransactionViewSet(viewsets.ModelViewSet):
    """产品交易记录视图集"""
    queryset = ProductTransaction.objects.all()
    serializer_class = ProductTransactionSerializer
    permission_classes = [ProductPermission]
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'store', 'transaction_type', 'operator']
    ordering_fields = ['created_at', 'total_amount', 'quantity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """根据用户权限过滤查询集"""
        user = self.request.user
        
        if user.is_super_admin:
            return ProductTransaction.objects.all()
        elif user.is_department_manager and user.department:
            return ProductTransaction.objects.filter(
                store__department=user.department
            )
        elif user.is_store_operator and user.store:
            return ProductTransaction.objects.filter(
                store=user.store
            )
        else:
            return ProductTransaction.objects.none()
    
    def get_serializer_class(self):
        """根据操作类型选择序列化器"""
        if self.action == 'create':
            return ProductTransactionCreateSerializer
        return ProductTransactionSerializer
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取交易汇总信息"""
        queryset = self.get_queryset()
        
        # 按交易类型汇总
        type_summary = queryset.values('transaction_type').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity'),
            total_amount=Sum('total_amount')
        )
        
        # 按日期汇总（最近30天）
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        date_summary = queryset.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).values('created_at__date').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        ).order_by('created_at__date')
        
        return Response({
            'type_summary': type_summary,
            'date_summary': date_summary
        })


class StoreProductViewSet(viewsets.ModelViewSet):
    """店铺产品视图集"""
    serializer_class = ProductSerializer
    permission_classes = [StoreProductPermission]
    pagination_class = ProductPagination
    
    def get_queryset(self):
        """获取指定店铺的产品"""
        store_id = self.kwargs.get('store_id')
        user = self.request.user
        
        if user.is_super_admin:
            return Product.objects.filter(store_id=store_id)
        elif user.is_department_manager and user.department:
            return Product.objects.filter(
                store_id=store_id,
                store__department=user.department
            )
        elif user.is_store_operator and user.store:
            if str(user.store.id) == store_id:
                return Product.objects.filter(store_id=store_id)
            else:
                return Product.objects.none()
        else:
            return Product.objects.none()
    
    def get_serializer_class(self):
        """根据操作类型选择序列化器"""
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'])
    def store_inventory(self, request, store_id=None):
        """获取店铺库存信息"""
        queryset = self.get_queryset()
        serializer = ProductInventorySerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def store_statistics(self, request, store_id=None):
        """获取店铺产品统计信息"""
        queryset = self.get_queryset()
        
        total_products = queryset.count()
        total_inventory = queryset.aggregate(total=Sum('inventory'))['total'] or 0
        total_value = queryset.aggregate(
            total=Sum(F('inventory') * F('selling_price'))
        )['total'] or 0
        
        return Response({
            'store_id': store_id,
            'total_products': total_products,
            'total_inventory': total_inventory,
            'total_value': total_value
        })
