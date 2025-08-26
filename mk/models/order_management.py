from django.db import models
from django.utils import timezone
from .store_management import Store


class Order(models.Model):
    """订单数据表 - 按照扣子工作流返回的格式"""
    
    # 基础信息
    order_number = models.CharField(max_length=100, unique=True, verbose_name="订单号")
    country = models.CharField(max_length=50, verbose_name="国家")
    store_code = models.CharField(max_length=50, verbose_name="店铺代号")
    sku = models.CharField(max_length=100, verbose_name="SKU")
    detail = models.TextField(verbose_name="Detail")
    n_quantity = models.IntegerField(verbose_name="N数量")
    c1_value = models.CharField(max_length=100, verbose_name="C1")
    c2_value = models.CharField(max_length=100, verbose_name="C2")
    
    # 日期和时间
    order_date = models.DateField(verbose_name="出单日期")
    label_status = models.CharField(max_length=50, verbose_name="标签状态")
    package_status = models.CharField(max_length=50, verbose_name="包裹状态")
    
    # 物流信息
    combined_express_waybill = models.CharField(max_length=100, verbose_name="寄合快递单号")
    yuntu_info = models.CharField(max_length=100, verbose_name="云途")
    last_mile = models.CharField(max_length=100, verbose_name="尾程")
    
    # 店铺信息
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="店铺", null=True, blank=True)
    store_name = models.CharField(max_length=200, verbose_name="店铺名称")
    english_name = models.CharField(max_length=200, verbose_name="英文名")
    first_sku = models.CharField(max_length=100, verbose_name="第一个sku")
    
    # 系统字段
    last_update_time = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    page_token = models.CharField(max_length=500, verbose_name="分页令牌", null=True, blank=True)
    
    # 处理状态
    is_processed = models.BooleanField(default=False, verbose_name="是否已处理")
    inventory_deducted = models.BooleanField(default=False, verbose_name="库存是否已扣除")
    
    class Meta:
        db_table = 'orders'
        verbose_name = "订单"
        verbose_name_plural = "订单"
        ordering = ['-order_date', '-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['store_code']),
            models.Index(fields=['sku']),
            models.Index(fields=['order_date']),
            models.Index(fields=['is_processed']),
        ]
    
    def __str__(self):
        return f"{self.order_number} - {self.store_name} - {self.sku}"
    
    def get_detail_attributes(self):
        """解析Detail字段，提取属性和数量"""
        try:
            # 假设Detail字段格式为: "属性1:数量1,属性2:数量2"
            attributes = {}
            if self.detail:
                parts = self.detail.split(',')
                for part in parts:
                    if ':' in part:
                        attr, qty = part.split(':', 1)
                        attributes[attr.strip()] = int(qty.strip())
            return attributes
        except:
            return {}
    
    def get_total_quantity(self):
        """获取总数量（N字段）"""
        return self.n_quantity or 0


class OrderBatch(models.Model):
    """订单批次记录 - 记录每次工作流执行的情况"""
    
    batch_id = models.CharField(max_length=100, unique=True, verbose_name="批次ID")
    execution_time = models.DateTimeField(auto_now_add=True, verbose_name="执行时间")
    page_token = models.CharField(max_length=500, verbose_name="分页令牌", null=True, blank=True)
    orders_count = models.IntegerField(default=0, verbose_name="订单数量")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    error_message = models.TextField(verbose_name="错误信息", null=True, blank=True)
    
    class Meta:
        db_table = 'order_batches'
        verbose_name = "订单批次"
        verbose_name_plural = "订单批次"
        ordering = ['-execution_time']
    
    def __str__(self):
        return f"批次 {self.batch_id} - {self.execution_time.strftime('%Y-%m-%d %H:%M:%S')}"
