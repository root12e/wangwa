from rest_framework import serializers
from ..models.store_management import Store, StoreInventory, StoreTransaction
from ..models.Department import Department
from ..models.User import User

class DepartmentSimpleSerializer(serializers.ModelSerializer):
    """部门简单信息序列化器"""
    class Meta:
        model = Department
        fields = ['id', 'name']

class UserSimpleSerializer(serializers.ModelSerializer):
    """用户简单信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email']

class StoreSerializer(serializers.ModelSerializer):
    """店铺序列化器"""
    department = DepartmentSimpleSerializer(read_only=True)
    department_id = serializers.UUIDField(write_only=True, required=True)
    manager = UserSimpleSerializer(read_only=True)
    manager_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    employee_count = serializers.SerializerMethodField()
    active_employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'code', 'address', 'phone', 'email', 
            'department', 'department_id', 'manager', 'manager_id',
            'status', 'description', 'business_hours', 
            'employee_count', 'active_employee_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'employee_count', 'active_employee_count']
    
    def get_employee_count(self, obj):
        return obj.get_employee_count()
    
    def get_active_employee_count(self, obj):
        return obj.get_active_employee_count()
    
    def validate_code(self, value):
        """验证店铺编码唯一性"""
        if Store.objects.filter(code=value).exists():
            raise serializers.ValidationError("店铺编码已存在")
        return value
    
    def validate_department_id(self, value):
        """验证部门ID是否存在"""
        try:
            Department.objects.get(id=value)
        except Department.DoesNotExist:
            raise serializers.ValidationError("指定的部门不存在")
        return value
    
    def validate_manager_id(self, value):
        """验证店铺经理ID是否存在"""
        if value:
            try:
                User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("指定的店铺经理不存在")
        return value

class StoreListSerializer(serializers.ModelSerializer):
    """店铺列表序列化器（简化版）"""
    department = DepartmentSimpleSerializer(read_only=True)
    manager = UserSimpleSerializer(read_only=True)
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'code', 'address', 'phone', 'status',
            'department', 'manager', 'employee_count', 'created_at'
        ]
    
    def get_employee_count(self, obj):
        return obj.get_employee_count()

class StoreInventorySerializer(serializers.ModelSerializer):
    """店铺库存序列化器"""
    store = StoreSerializer(read_only=True)
    store_id = serializers.UUIDField(write_only=True, required=True)
    
    class Meta:
        model = StoreInventory
        fields = [
            'id', 'store', 'store_id', 'product_name', 'product_code',
            'quantity', 'unit_price', 'min_stock', 'max_stock',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_store_id(self, value):
        """验证店铺ID是否存在"""
        try:
            Store.objects.get(id=value)
        except Store.DoesNotExist:
            raise serializers.ValidationError("指定的店铺不存在")
        return value
    
    def validate(self, data):
        """验证库存数量逻辑"""
        if data.get('min_stock', 0) > data.get('max_stock', 1000):
            raise serializers.ValidationError("最低库存不能大于最高库存")
        if data.get('quantity', 0) < 0:
            raise serializers.ValidationError("库存数量不能为负数")
        return data

class StoreTransactionSerializer(serializers.ModelSerializer):
    """店铺交易记录序列化器"""
    store = StoreSerializer(read_only=True)
    store_id = serializers.UUIDField(write_only=True, required=True)
    operator = UserSimpleSerializer(read_only=True)
    operator_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = StoreTransaction
        fields = [
            'id', 'store', 'store_id', 'transaction_type', 'amount',
            'description', 'operator', 'operator_id', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_store_id(self, value):
        """验证店铺ID是否存在"""
        try:
            Store.objects.get(id=value)
        except Store.DoesNotExist:
            raise serializers.ValidationError("指定的店铺不存在")
        return value
    
    def validate_operator_id(self, value):
        """验证操作员ID是否存在"""
        if value:
            try:
                User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("指定的操作员不存在")
        return value
    
    def validate_amount(self, value):
        """验证交易金额"""
        if value <= 0:
            raise serializers.ValidationError("交易金额必须大于0")
        return value

class StoreStatisticsSerializer(serializers.Serializer):
    """店铺统计信息序列化器"""
    total_stores = serializers.IntegerField()
    active_stores = serializers.IntegerField()
    total_employees = serializers.IntegerField()
    total_inventory_items = serializers.IntegerField()
    total_transactions = serializers.IntegerField()
    total_transaction_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
