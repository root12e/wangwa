from rest_framework import serializers
from ..models.etsy_models import (
    EtsyProductRegistration, EtsyOrderImportSummary, EtsyOrderStatistics,
    EtsyDesignRequirement, EtsyPurchaseRequirement, EtsyProductionRequirement,
    EtsyShippingDelivery, EtsyQRCodeLabel, EtsyYunTuExport, 
    EtsyYunTuDeduction, EtsyStoreInformation
)


class EtsyProductRegistrationSerializer(serializers.ModelSerializer):
    """Etsy产品登记表序列化器"""
    
    class Meta:
        model = EtsyProductRegistration
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_unit_cost(self, value):
        """验证单位成本"""
        if value <= 0:
            raise serializers.ValidationError("单位成本必须大于0")
        return value
    
    def validate_estimated_price(self, value):
        """验证预估售价"""
        if value <= 0:
            raise serializers.ValidationError("预估售价必须大于0")
        return value
    
    def validate_inventory_standard_line(self, value):
        """验证库存标准线"""
        if value < 0:
            raise serializers.ValidationError("库存标准线不能为负数")
        return value


class EtsyOrderImportSummarySerializer(serializers.ModelSerializer):
    """Etsy订单导入汇总表序列化器"""
    
    class Meta:
        model = EtsyOrderImportSummary
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def validate_quantity(self, value):
        """验证数量"""
        if value <= 0:
            raise serializers.ValidationError("数量必须大于0")
        return value
    
    def validate_unit_price(self, value):
        """验证单价"""
        if value <= 0:
            raise serializers.ValidationError("单价必须大于0")
        return value


class EtsyOrderStatisticsSerializer(serializers.ModelSerializer):
    """Etsy订单统计表序列化器"""
    
    class Meta:
        model = EtsyOrderStatistics
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_total_quantity(self, value):
        """验证总数"""
        if value <= 0:
            raise serializers.ValidationError("总数必须大于0")
        return value


class EtsyDesignRequirementSerializer(serializers.ModelSerializer):
    """Etsy设计需求表序列化器"""
    
    class Meta:
        model = EtsyDesignRequirement
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def validate_quantity(self, value):
        """验证数量"""
        if value <= 0:
            raise serializers.ValidationError("数量必须大于0")
        return value


class EtsyPurchaseRequirementSerializer(serializers.ModelSerializer):
    """Etsy采购需求表序列化器"""
    
    class Meta:
        model = EtsyPurchaseRequirement
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def validate_quantity(self, value):
        """验证数量"""
        if value <= 0:
            raise serializers.ValidationError("数量必须大于0")
        return value


class EtsyProductionRequirementSerializer(serializers.ModelSerializer):
    """Etsy生产需求表序列化器"""
    
    class Meta:
        model = EtsyProductionRequirement
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def validate_total_quantity(self, value):
        """验证总数"""
        if value <= 0:
            raise serializers.ValidationError("总数必须大于0")
        return value


class EtsyShippingDeliverySerializer(serializers.ModelSerializer):
    """Etsy配货发货表序列化器"""
    
    class Meta:
        model = EtsyShippingDelivery
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def validate_package_total_weight(self, value):
        """验证包裹总重量"""
        if value <= 0:
            raise serializers.ValidationError("包裹总重量必须大于0")
        return value


class EtsyQRCodeLabelSerializer(serializers.ModelSerializer):
    """Etsy草料二维码表序列化器"""
    
    class Meta:
        model = EtsyQRCodeLabel
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def validate_n_quantity(self, value):
        """验证数量"""
        if value <= 0:
            raise serializers.ValidationError("数量必须大于0")
        return value


class EtsyYunTuExportSerializer(serializers.ModelSerializer):
    """Etsy云途导出表序列化器"""
    
    class Meta:
        model = EtsyYunTuExport
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def validate_package_weight(self, value):
        """验证包裹重量"""
        if value <= 0:
            raise serializers.ValidationError("包裹重量必须大于0")
        return value


class EtsyYunTuDeductionSerializer(serializers.ModelSerializer):
    """Etsy云途扣费表序列化器"""
    
    class Meta:
        model = EtsyYunTuDeduction
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def validate_transaction_amount(self, value):
        """验证交易金额"""
        if value < 0:
            raise serializers.ValidationError("交易金额不能为负数")
        return value


class EtsyStoreInformationSerializer(serializers.ModelSerializer):
    """Etsy店铺信息表序列化器"""
    
    class Meta:
        model = EtsyStoreInformation
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_store_rent(self, value):
        """验证店铺租金"""
        if value < 0:
            raise serializers.ValidationError("店铺租金不能为负数")
        return value


# 批量操作序列化器
class EtsyBulkCreateSerializer(serializers.Serializer):
    """批量创建序列化器"""
    data = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=1000
    )


class EtsyBulkUpdateSerializer(serializers.Serializer):
    """批量更新序列化器"""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=1000
    )
    data = serializers.DictField()


class EtsyBulkDeleteSerializer(serializers.Serializer):
    """批量删除序列化器"""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=1000
    )


class EtsyFilterSerializer(serializers.Serializer):
    """筛选序列化器"""
    search = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    store = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    operation_personnel = serializers.CharField(required=False, allow_blank=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    min_quantity = serializers.IntegerField(required=False, min_value=0)
    max_quantity = serializers.IntegerField(required=False, min_value=0)


class EtsySortSerializer(serializers.Serializer):
    """排序序列化器"""
    field = serializers.CharField(required=True)
    order = serializers.ChoiceField(choices=['asc', 'desc'], default='desc')
