from django.db import models
from django.utils import timezone
import uuid
from .Department import Department


def generate_store_code():
    """生成店铺编码"""
    import random
    import string
    # 生成8位随机字符串
    return 'STORE_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


class Store(models.Model):
    """店铺模型"""
    STATUS_CHOICES = [
        ('active', '营业中'),
        ('inactive', '暂停营业'),
        ('closed', '已关闭'),
        ('maintenance', '维护中'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='店铺名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='店铺编码', default=generate_store_code)
    address = models.TextField(verbose_name='店铺地址')
    phone = models.CharField(max_length=20, verbose_name='店铺电话')
    email = models.EmailField(blank=True, verbose_name='店铺邮箱')
    manager = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='managed_stores', verbose_name='店铺经理')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属部门')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='店铺状态')
    description = models.TextField(blank=True, verbose_name='店铺描述')
    business_hours = models.CharField(max_length=100, blank=True, verbose_name='营业时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '店铺'
        verbose_name_plural = '店铺'
        db_table = 'stores'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_employee_count(self):
        """获取店铺员工数量"""
        return User.objects.filter(store=self).count()
    
    def get_active_employee_count(self):
        """获取店铺活跃员工数量"""
        return User.objects.filter(store=self, is_active=True).count()

class StoreInventory(models.Model):
    """店铺库存模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='所属店铺')
    product_name = models.CharField(max_length=200, verbose_name='产品名称')
    product_code = models.CharField(max_length=50, verbose_name='产品编码')
    quantity = models.IntegerField(default=0, verbose_name='库存数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    min_stock = models.IntegerField(default=0, verbose_name='最低库存')
    max_stock = models.IntegerField(default=1000, verbose_name='最高库存')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '店铺库存'
        verbose_name_plural = '店铺库存'
        db_table = 'store_inventory'
        unique_together = ['store', 'product_code']
    
    def __str__(self):
        return f"{self.store.name} - {self.product_name}"

class StoreTransaction(models.Model):
    """店铺交易记录模型"""
    TRANSACTION_TYPES = [
        ('sale', '销售'),
        ('purchase', '采购'),
        ('return', '退货'),
        ('adjustment', '库存调整'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='所属店铺')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='交易类型')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='交易金额')
    description = models.TextField(blank=True, verbose_name='交易描述')
    operator = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, verbose_name='操作员')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '店铺交易记录'
        verbose_name_plural = '店铺交易记录'
        db_table = 'store_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.store.name} - {self.get_transaction_type_display()} - {self.amount}"
