from django.db import models
from django.utils import timezone
import uuid
from .store_management import Store
from .User import User


class Product(models.Model):
    """产品模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 基本信息
    product_name = models.CharField(max_length=200, verbose_name='产品名')
    product_model = models.CharField(max_length=100, verbose_name='产品型号')
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU编码')
    
    # 库存信息
    stock_quantity = models.IntegerField(default=0, verbose_name='库存')
    unit_weight = models.DecimalField(max_digits=8, decimal_places=3, verbose_name='单位重量(kg)')
    min_stock = models.IntegerField(default=0, verbose_name='最低库存')
    max_stock = models.IntegerField(default=1000, verbose_name='最高库存')
    
    # 生产信息
    production_date = models.DateField(verbose_name='生产日期')
    production_method = models.CharField(max_length=50, verbose_name='生产方式')
    production_batch = models.CharField(max_length=50, verbose_name='生产批次')
    
    # 价格信息
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='采购价格')
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='销售售价')
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单位成本')
    
    # 销售信息
    sales_purpose = models.CharField(max_length=100, verbose_name='销售用途')
    sales_date = models.DateField(null=True, blank=True, verbose_name='销售日期')
    sales_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='销售利润率(%)')
    sales_profit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='销售利润')
    sales_gross_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='销售毛利率(%)')
    sales_gross_profit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='销售毛利')
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='总利润')
    
    # 上下架时间
    listing_time = models.DateTimeField(verbose_name='上架时间')
    delisting_time = models.DateTimeField(null=True, blank=True, verbose_name='下架时间')
    
    # 关联信息
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='所属店铺')
    category = models.ForeignKey('ProductCategory', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='产品分类')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    
    # 备注
    remarks = models.TextField(blank=True, verbose_name='备注')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '产品'
        verbose_name_plural = '产品'
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'product_name']),
            models.Index(fields=['sku']),
            models.Index(fields=['production_date']),
            models.Index(fields=['sales_date']),
        ]
    
    def __str__(self):
        return f"{self.product_name} ({self.sku})"
    
    def calculate_profit_margins(self):
        """计算利润率"""
        if self.purchase_price > 0:
            self.sales_profit_margin = ((self.selling_price - self.purchase_price) / self.purchase_price * 100)
            self.sales_gross_profit_margin = ((self.selling_price - self.unit_cost) / self.unit_cost * 100)
    
    def calculate_profits(self):
        """计算利润"""
        self.sales_profit = self.selling_price - self.purchase_price
        self.sales_gross_profit = self.selling_price - self.unit_cost
        self.total_profit = self.sales_profit
    
    def save(self, *args, **kwargs):
        """保存前自动计算利润和利润率"""
        self.calculate_profit_margins()
        self.calculate_profits()
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        """产品是否处于活跃状态"""
        now = timezone.now()
        return self.listing_time <= now and (self.delisting_time is None or self.delisting_time > now)
    
    @property
    def stock_status(self):
        """库存状态"""
        if self.stock_quantity <= self.min_stock:
            return 'low'
        elif self.stock_quantity >= self.max_stock:
            return 'high'
        else:
            return 'normal'


class ProductCategory(models.Model):
    """产品分类模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='父分类')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '产品分类'
        verbose_name_plural = '产品分类'
        db_table = 'product_categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """产品图片模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='产品')
    image = models.ImageField(upload_to='products/', verbose_name='产品图片')
    alt_text = models.CharField(max_length=200, blank=True, verbose_name='图片描述')
    is_primary = models.BooleanField(default=False, verbose_name='是否主图')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '产品图片'
        verbose_name_plural = '产品图片'
        db_table = 'product_images'
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        return f"{self.product.product_name} - {self.alt_text or '图片'}"


class ProductTransaction(models.Model):
    """产品交易记录模型"""
    TRANSACTION_TYPES = [
        ('purchase', '采购入库'),
        ('sale', '销售出库'),
        ('return', '退货入库'),
        ('adjustment', '库存调整'),
        ('transfer', '店铺调拨'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='产品')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店铺')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='交易类型')
    quantity = models.IntegerField(verbose_name='数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='总金额')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='操作员')
    reference_number = models.CharField(max_length=50, blank=True, verbose_name='参考单号')
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '产品交易记录'
        verbose_name_plural = '产品交易记录'
        db_table = 'product_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.product_name} - {self.get_transaction_type_display()} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        """保存前自动计算总金额"""
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
