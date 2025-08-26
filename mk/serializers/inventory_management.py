from rest_framework import serializers
from ..models.inventory_management import Inventory, InventoryTransaction, InventoryConsumption
from ..models.order_management import Order, OrderBatch
from ..models.store_management import Store
from ..models.product_management import Product


class StoreSerializer(serializers.ModelSerializer):
    """店铺序列化器"""
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'code', 'description']


class ProductSerializer(serializers.ModelSerializer):
    """产品序列化器"""
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'description']


class InventorySerializer(serializers.ModelSerializer):
    """库存序列化器"""
    
    store = StoreSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    store_id = serializers.UUIDField(write_only=True)
    product_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'store', 'product', 'sku', 'current_stock', 'reserved_stock', 
            'available_stock', 'min_stock', 'max_stock', 'is_active', 
            'last_updated', 'created_at', 'store_id', 'product_id'
        ]
        read_only_fields = ['available_stock', 'last_updated', 'created_at']
    
    def validate(self, data):
        """验证数据"""
        # 检查最小库存不能大于最大库存
        min_stock = data.get('min_stock', 0)
        max_stock = data.get('max_stock', 0)
        
        if max_stock > 0 and min_stock > max_stock:
            raise serializers.ValidationError("最小库存不能大于最大库存")
        
        return data


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """库存交易记录序列化器"""
    
    inventory = InventorySerializer(read_only=True)
    inventory_id = serializers.UUIDField(write_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'inventory', 'transaction_type', 'transaction_type_display', 
            'quantity', 'order', 'before_stock', 'after_stock', 'notes', 
            'created_at', 'created_by', 'inventory_id'
        ]
        read_only_fields = ['before_stock', 'after_stock', 'created_at']


class InventoryConsumptionSerializer(serializers.ModelSerializer):
    """库存消耗统计序列化器"""
    
    store = StoreSerializer(read_only=True)
    
    class Meta:
        model = InventoryConsumption
        fields = [
            'id', 'store', 'sku', 'total_consumed', 'total_orders', 
            'last_consumption_date', 'first_consumption_date', 
            'last_updated', 'created_at'
        ]
        read_only_fields = ['total_consumed', 'total_orders', 'last_consumption_date', 
                           'first_consumption_date', 'last_updated', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    
    store = StoreSerializer(read_only=True)
    store_code = serializers.CharField(write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'country', 'store_code', 'sku', 'detail', 
            'n_quantity', 'c1_value', 'c2_value', 'order_date', 'label_status', 
            'package_status', 'combined_express_waybill', 'yuntu_info', 'last_mile', 
            'store', 'store_name', 'english_name', 'first_sku', 'last_update_time', 
            'created_at', 'page_token', 'is_processed', 'inventory_deducted'
        ]
        read_only_fields = ['last_update_time', 'created_at', 'is_processed', 'inventory_deducted']
    
    def validate_order_number(self, value):
        """验证订单号唯一性"""
        if Order.objects.filter(order_number=value).exists():
            raise serializers.ValidationError("订单号已存在")
        return value


class OrderBatchSerializer(serializers.ModelSerializer):
    """订单批次序列化器"""
    
    class Meta:
        model = OrderBatch
        fields = [
            'id', 'batch_id', 'execution_time', 'page_token', 'orders_count', 
            'is_completed', 'error_message'
        ]
        read_only_fields = ['execution_time']


class InventoryAdjustmentSerializer(serializers.Serializer):
    """库存调整序列化器"""
    
    adjustment_type = serializers.ChoiceField(
        choices=[('IN', '入库'), ('OUT', '出库'), ('ADJUST', '调整')],
        help_text="调整类型"
    )
    quantity = serializers.IntegerField(
        min_value=1,
        help_text="调整数量"
    )
    notes = serializers.CharField(
        max_length=500,
        required=False,
        help_text="备注"
    )


class BulkInventoryAdjustmentSerializer(serializers.Serializer):
    """批量库存调整序列化器"""
    
    adjustments = InventoryAdjustmentSerializer(many=True)


class OrderProcessingSerializer(serializers.Serializer):
    """订单处理序列化器"""
    
    order_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="要处理的订单ID列表"
    )


class WorkflowExecutionSerializer(serializers.Serializer):
    """工作流执行序列化器"""
    
    force = serializers.BooleanField(
        default=False,
        help_text="是否强制执行（忽略时间间隔）"
    )


class ExecutionIntervalSerializer(serializers.Serializer):
    """执行间隔序列化器"""
    
    interval = serializers.IntegerField(
        min_value=60,
        max_value=86400,
        help_text="执行间隔（秒），最小60秒，最大86400秒（24小时）"
    )


class InventorySummarySerializer(serializers.Serializer):
    """库存摘要序列化器"""
    
    store_id = serializers.UUIDField(
        required=False,
        help_text="店铺ID，如果不提供则获取所有店铺的摘要"
    )


class InventoryFilterSerializer(serializers.Serializer):
    """库存过滤序列化器"""
    
    store_id = serializers.UUIDField(required=False)
    sku = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    low_stock = serializers.BooleanField(required=False, help_text="是否只显示低库存")


class TransactionFilterSerializer(serializers.Serializer):
    """交易记录过滤序列化器"""
    
    inventory_id = serializers.UUIDField(required=False)
    transaction_type = serializers.CharField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)


class OrderFilterSerializer(serializers.Serializer):
    """订单过滤序列化器"""
    
    store_id = serializers.UUIDField(required=False)
    is_processed = serializers.BooleanField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    sku = serializers.CharField(required=False)
    order_number = serializers.CharField(required=False)


class BatchFilterSerializer(serializers.Serializer):
    """批次过滤序列化器"""
    
    is_completed = serializers.BooleanField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
