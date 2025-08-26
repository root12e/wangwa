from django.db import models
from django.utils import timezone
from .store_management import Store
from .product_management import Product


class Inventory(models.Model):
    """库存表 - 管理产品库存"""
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="店铺")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="产品", related_name='inventory_items')
    sku = models.CharField(max_length=100, verbose_name="SKU")
    
    # 库存数量
    current_stock = models.IntegerField(default=0, verbose_name="当前库存")
    reserved_stock = models.IntegerField(default=0, verbose_name="预留库存")
    available_stock = models.IntegerField(default=0, verbose_name="可用库存")
    
    # 库存阈值
    min_stock = models.IntegerField(default=0, verbose_name="最小库存")
    max_stock = models.IntegerField(default=0, verbose_name="最大库存")
    
    # 库存状态
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'inventory'
        verbose_name = "库存"
        verbose_name_plural = "库存"
        unique_together = ['store', 'product', 'sku']
        ordering = ['store', 'product', 'sku']
        indexes = [
            models.Index(fields=['store', 'sku']),
            models.Index(fields=['current_stock']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.store.name} - {self.product.name} - {self.sku} (库存: {self.current_stock})"
    
    def save(self, *args, **kwargs):
        """保存时自动计算可用库存"""
        self.available_stock = max(0, self.current_stock - self.reserved_stock)
        super().save(*args, **kwargs)
    
    def deduct_stock(self, quantity):
        """扣除库存"""
        if self.available_stock >= quantity:
            self.current_stock -= quantity
            self.save()
            return True
        return False
    
    def add_stock(self, quantity):
        """增加库存"""
        self.current_stock += quantity
        self.save()
        return True
    
    def reserve_stock(self, quantity):
        """预留库存"""
        if self.available_stock >= quantity:
            self.reserved_stock += quantity
            self.save()
            return True
        return False
    
    def release_reserved_stock(self, quantity):
        """释放预留库存"""
        if self.reserved_stock >= quantity:
            self.reserved_stock -= quantity
            self.save()
            return True
        return False


class InventoryTransaction(models.Model):
    """库存交易记录 - 记录所有库存变动"""
    
    TRANSACTION_TYPES = [
        ('IN', '入库'),
        ('OUT', '出库'),
        ('RESERVE', '预留'),
        ('RELEASE', '释放预留'),
        ('ADJUST', '调整'),
        ('DEDUCT_ORDER', '订单扣除'),
    ]
    
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, verbose_name="库存")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="交易类型")
    quantity = models.IntegerField(verbose_name="数量")
    
    # 关联订单（如果是订单扣除）
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="关联订单")
    
    # 交易前后状态
    before_stock = models.IntegerField(verbose_name="交易前库存")
    after_stock = models.IntegerField(verbose_name="交易后库存")
    
    # 备注信息
    notes = models.TextField(verbose_name="备注", null=True, blank=True)
    
    # 系统字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="操作人")
    
    class Meta:
        db_table = 'inventory_transactions'
        verbose_name = "库存交易记录"
        verbose_name_plural = "库存交易记录"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory', 'transaction_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"{self.inventory} - {self.get_transaction_type_display()} - {self.quantity}"


class InventoryConsumption(models.Model):
    """库存消耗统计 - 统计订单消耗的库存"""
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="店铺")
    sku = models.CharField(max_length=100, verbose_name="SKU")
    
    # 消耗统计
    total_consumed = models.IntegerField(default=0, verbose_name="总消耗数量")
    total_orders = models.IntegerField(default=0, verbose_name="总订单数")
    
    # 时间统计
    last_consumption_date = models.DateField(verbose_name="最后消耗日期", null=True, blank=True)
    first_consumption_date = models.DateField(verbose_name="首次消耗日期", null=True, blank=True)
    
    # 系统字段
    last_updated = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'inventory_consumption'
        verbose_name = "库存消耗统计"
        verbose_name_plural = "库存消耗统计"
        unique_together = ['store', 'sku']
        ordering = ['store', 'sku']
        indexes = [
            models.Index(fields=['store', 'sku']),
            models.Index(fields=['total_consumed']),
        ]
    
    def __str__(self):
        return f"{self.store.name} - {self.sku} (消耗: {self.total_consumed})"
    
    def add_consumption(self, quantity, order_date):
        """添加消耗记录"""
        self.total_consumed += quantity
        self.total_orders += 1
        
        if not self.first_consumption_date:
            self.first_consumption_date = order_date
        
        if not self.last_consumption_date or order_date > self.last_consumption_date:
            self.last_consumption_date = order_date
        
        self.save()
