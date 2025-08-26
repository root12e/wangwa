from rest_framework import serializers
from ..models.product_management import Product, ProductCategory, ProductImage, ProductTransaction
from ..models.store_management import Store
from ..models.User import User


class ProductCategorySerializer(serializers.ModelSerializer):
    """产品分类序列化器"""
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'parent', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """产品图片序列化器"""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']


class StoreBasicSerializer(serializers.ModelSerializer):
    """店铺基本信息序列化器"""
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'code', 'address', 'status']


class UserBasicSerializer(serializers.ModelSerializer):
    """用户基本信息序列化器"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'role']


class ProductSerializer(serializers.ModelSerializer):
    """产品序列化器"""
    store = StoreBasicSerializer(read_only=True)
    store_id = serializers.UUIDField(write_only=True)
    created_by = UserBasicSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category = ProductCategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    # 计算字段
    is_active = serializers.ReadOnlyField()
    stock_status = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_model', 'sku', 'inventory', 'unit_weight',
            'min_stock', 'max_stock', 'production_date', 'production_method', 'production_batch',
            'purchase_price', 'selling_price', 'unit_cost', 'sales_purpose', 'sales_date',
            'sales_profit_margin', 'sales_profit', 'sales_gross_profit_margin', 'sales_gross_profit',
            'total_profit', 'listing_time', 'delisting_time', 'store', 'store_id', 'created_by',
            'category', 'category_id', 'remarks', 'images', 'is_active', 'stock_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'sales_profit_margin', 'sales_profit', 'sales_gross_profit_margin',
            'sales_gross_profit', 'total_profit', 'created_at', 'updated_at'
        ]
    
    def validate_sku(self, value):
        """验证SKU唯一性"""
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("SKU编码已存在")
        return value
    
    def validate(self, attrs):
        """验证数据完整性"""
        if attrs.get('selling_price', 0) < attrs.get('purchase_price', 0):
            raise serializers.ValidationError("销售价格不能低于采购价格")
        
        if attrs.get('inventory', 0) < 0:
            raise serializers.ValidationError("库存不能为负数")
        
        if attrs.get('min_stock', 0) > attrs.get('max_stock', 1000):
            raise serializers.ValidationError("最低库存不能大于最高库存")
        
        return attrs
    
    def create(self, validated_data):
        """创建产品时设置创建人"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProductDetailSerializer(ProductSerializer):
    """产品详情序列化器"""
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['category', 'images']


class ProductListSerializer(serializers.ModelSerializer):
    """产品列表序列化器"""
    store = StoreBasicSerializer(read_only=True)
    category = ProductCategorySerializer(read_only=True)
    is_active = serializers.ReadOnlyField()
    stock_status = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_model', 'sku', 'inventory', 'unit_weight',
            'production_date', 'purchase_price', 'selling_price', 'sales_profit',
            'listing_time', 'store', 'category', 'is_active', 'stock_status', 'created_at'
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    """产品创建序列化器"""
    store_id = serializers.UUIDField()
    category_id = serializers.UUIDField(required=False, allow_null=True)
    
    class Meta:
        model = Product
        fields = [
            'product_name', 'product_model', 'sku', 'inventory', 'unit_weight',
            'min_stock', 'max_stock', 'production_date', 'production_method', 'production_batch',
            'purchase_price', 'selling_price', 'unit_cost', 'sales_purpose', 'listing_time',
            'store_id', 'category_id', 'remarks'
        ]
    
    def validate_sku(self, value):
        """验证SKU唯一性"""
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("SKU编码已存在")
        return value


class ProductUpdateSerializer(serializers.ModelSerializer):
    """产品更新序列化器"""
    
    class Meta:
        model = Product
        fields = [
            'product_name', 'product_model', 'inventory', 'unit_weight', 'min_stock', 'max_stock',
            'production_method', 'purchase_price', 'selling_price', 'unit_cost', 'sales_purpose',
            'delisting_time', 'remarks'
        ]


class ProductTransactionSerializer(serializers.ModelSerializer):
    """产品交易记录序列化器"""
    product = serializers.StringRelatedField()
    store = StoreBasicSerializer(read_only=True)
    operator = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = ProductTransaction
        fields = [
            'id', 'product', 'store', 'transaction_type', 'quantity', 'unit_price',
            'total_amount', 'operator', 'reference_number', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'total_amount', 'created_at']


class ProductTransactionCreateSerializer(serializers.ModelSerializer):
    """产品交易记录创建序列化器"""
    product_id = serializers.UUIDField()
    store_id = serializers.UUIDField()
    
    class Meta:
        model = ProductTransaction
        fields = [
            'product_id', 'store_id', 'transaction_type', 'quantity', 'unit_price',
            'reference_number', 'notes'
        ]
    
    def validate(self, attrs):
        """验证交易数据"""
        if attrs.get('quantity', 0) <= 0:
            raise serializers.ValidationError("数量必须大于0")
        
        if attrs.get('unit_price', 0) < 0:
            raise serializers.ValidationError("单价不能为负数")
        
        return attrs
    
    def create(self, validated_data):
        """创建交易记录时设置操作员"""
        validated_data['operator'] = self.context['request'].user
        return super().create(validated_data)


class ProductInventorySerializer(serializers.ModelSerializer):
    """产品库存序列化器"""
    store = StoreBasicSerializer(read_only=True)
    stock_status = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'sku', 'inventory', 'min_stock', 'max_stock',
            'unit_weight', 'store', 'stock_status', 'updated_at'
        ]


class ProductSearchSerializer(serializers.Serializer):
    """产品搜索序列化器"""
    keyword = serializers.CharField(max_length=100, required=False)
    store_id = serializers.UUIDField(required=False)
    category_id = serializers.UUIDField(required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    stock_status = serializers.ChoiceField(
        choices=[('low', '库存不足'), ('normal', '库存正常'), ('high', '库存充足')],
        required=False
    )
    is_active = serializers.BooleanField(required=False)
    page = serializers.IntegerField(min_value=1, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=20)


class ProductBulkUpdateSerializer(serializers.Serializer):
    """产品批量更新序列化器"""
    product_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100
    )
    updates = serializers.DictField()
    
    def validate_updates(self, value):
        """验证更新字段"""
        allowed_fields = [
            'min_stock', 'max_stock', 'purchase_price', 'selling_price', 'unit_cost',
            'delisting_time', 'remarks'
        ]
        
        for field in value.keys():
            if field not in allowed_fields:
                raise serializers.ValidationError(f"不允许更新字段: {field}")
        
        return value


class ProductExportSerializer(serializers.Serializer):
    """产品导出序列化器"""
    store_id = serializers.UUIDField(required=False)
    category_id = serializers.UUIDField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    format = serializers.ChoiceField(
        choices=[('excel', 'Excel'), ('csv', 'CSV')],
        default='excel'
    )
