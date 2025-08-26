from django.db import models
from django.utils import timezone


class EtsyProductRegistration(models.Model):
    """Etsy产品登记表"""
    
    # 产品基本信息
    product_name = models.CharField(max_length=255, verbose_name="产品名称")
    listing_time = models.DateField(verbose_name="上市时间")
    sku_1688 = models.CharField(max_length=100, verbose_name="1688SKU")
    product_model = models.CharField(max_length=100, verbose_name="产品型号")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单位成本")
    unit_price_or = models.CharField(max_length=100, verbose_name="单价或")
    unit_selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单位售价")
    production_method = models.CharField(max_length=100, verbose_name="生产方式")
    t2_code = models.CharField(max_length=50, verbose_name="T2")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="采购价")
    remarks = models.TextField(blank=True, verbose_name="备注")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="销售价")
    promotion_advertising_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="推广广告费")
    sales_profit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="销售利润")
    unit_type = models.CharField(max_length=50, verbose_name="单位类型")
    sales_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="销售利润率")
    sales_series = models.CharField(max_length=100, verbose_name="销售系列")
    text_link = models.CharField(max_length=255, verbose_name="文字链")
    delisting_time = models.DateField(null=True, blank=True, verbose_name="下架时间")
    product_image = models.ImageField(upload_to='etsy_products/', blank=True, verbose_name="产品图片")
    
    # 申报信息
    declaration_chinese_name = models.CharField(max_length=255, verbose_name="申报中文名")
    declaration_english_name = models.CharField(max_length=255, verbose_name="申报英文名")
    purchase_link = models.URLField(blank=True, verbose_name="采购链接")
    craft_technology = models.CharField(max_length=100, verbose_name="工艺")
    
    # 店铺SKU关联
    store_sku = models.CharField(max_length=100, verbose_name="店铺SKU")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'etsy_product_registration'
        verbose_name = 'Etsy产品登记'
        verbose_name_plural = 'Etsy产品登记'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product_name} - {self.sku_1688}"


class EtsyOrderImportSummary(models.Model):
    """Etsy订单导入汇总表"""
    
    # 订单基本信息
    order_number = models.CharField(max_length=100, unique=True, verbose_name="订单号")
    store_code = models.CharField(max_length=50, verbose_name="店铺代号")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    detail = models.CharField(max_length=255, verbose_name="Detail")
    n_quantity = models.IntegerField(verbose_name="N")
    c1_custom_info1 = models.CharField(max_length=255, blank=True, verbose_name="C1")
    c2_custom_info2 = models.CharField(max_length=255, blank=True, verbose_name="C2")
    english_name = models.CharField(max_length=255, verbose_name="英文名")
    order_date = models.DateField(verbose_name="出单日期")
    label_status = models.CharField(max_length=50, verbose_name="标签状态")
    package_status = models.CharField(max_length=50, verbose_name="包裹状态")
    last_mile_tracking_number = models.CharField(max_length=100, verbose_name="尾程跟踪号")
    yuntu_carrier = models.CharField(max_length=50, verbose_name="云途")
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="运费")
    store_name = models.CharField(max_length=255, verbose_name="店铺名称")
    last_update_time = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")
    first_sku = models.CharField(max_length=100, verbose_name="第一个sku")
    parent_record = models.CharField(max_length=100, blank=True, verbose_name="父记录")
    
    # 收件人信息
    recipient_country = models.CharField(max_length=10, verbose_name="国家")
    recipient_name = models.CharField(max_length=255, verbose_name="收件人姓名")
    recipient_address = models.TextField(verbose_name="收件人地址")
    recipient_city = models.CharField(max_length=100, verbose_name="收件人城市")
    recipient_state = models.CharField(max_length=100, verbose_name="收件人省/州")
    postal_code = models.CharField(max_length=20, verbose_name="邮编")
    
    # 产品信息
    attribute_quantity = models.IntegerField(verbose_name="属性数量")
    quantity = models.IntegerField(verbose_name="数量")
    gift_message = models.TextField(blank=True, verbose_name="礼品赠言")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'etsy_order_import_summary'
        verbose_name = 'Etsy订单导入汇总'
        verbose_name_plural = 'Etsy订单导入汇总'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.store_name}"


class EtsyOrderStatistics(models.Model):
    """Etsy订单统计表"""
    
    # 订单基本信息
    order_number = models.CharField(max_length=100, unique=True, verbose_name="订单号")
    status_indication = models.CharField(max_length=50, verbose_name="状态指示")
    production_method = models.CharField(max_length=100, verbose_name="生产方式")
    production_process = models.CharField(max_length=100, verbose_name="生产工艺")
    production_progress = models.CharField(max_length=50, verbose_name="生产进度")
    design_drawings = models.CharField(max_length=255, blank=True, verbose_name="设计图纸")
    post_order_period = models.CharField(max_length=100, verbose_name="出单后期")
    product_image = models.ImageField(upload_to='etsy_products/', blank=True, verbose_name="产品图片")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    attribute = models.CharField(max_length=255, verbose_name="属性")
    total_quantity = models.IntegerField(verbose_name="总数")
    gift_giveaway = models.CharField(max_length=255, blank=True, verbose_name="礼品赠")
    message = models.TextField(blank=True, verbose_name="留言")
    order_remarks = models.TextField(blank=True, verbose_name="订单备注")
    first_sku = models.CharField(max_length=100, verbose_name="第一个SKU")
    statistics_month = models.DateField(verbose_name="统计月份")
    
    # 店铺和负责人信息（根据SKU公式计算）
    store_name = models.CharField(max_length=255, verbose_name="店铺名称")
    responsible_person = models.CharField(max_length=100, verbose_name="负责人")
    
    # 订单信息
    order_date = models.DateField(verbose_name="出单日期")
    shipping_method = models.CharField(max_length=50, verbose_name="运输方式")
    system_status = models.CharField(max_length=50, verbose_name="系统状态")
    production_days = models.IntegerField(verbose_name="生产天数")
    express_delivery = models.CharField(max_length=50, verbose_name="快递")
    shipping_status = models.CharField(max_length=50, verbose_name="发货状态")
    logistics_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="物流成本")
    outbound_destination = models.CharField(max_length=100, verbose_name="出库目标地")
    sku_return_warehouse = models.CharField(max_length=100, blank=True, verbose_name="SKU回库")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'etsy_order_statistics'
        verbose_name = 'Etsy订单统计'
        verbose_name_plural = 'Etsy订单统计'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.store_name}"


class EtsyDesignRequirement(models.Model):
    """Etsy设计需求表"""
    
    # 基本信息
    order_date = models.DateField(verbose_name="出单日期")
    status_indication = models.CharField(max_length=50, verbose_name="指示状态")
    platform_order_number = models.CharField(max_length=100, verbose_name="平台订单号")
    product_image = models.ImageField(upload_to='etsy_designs/', blank=True, verbose_name="产品图片")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    chinese_name = models.CharField(max_length=255, verbose_name="中文名")
    store = models.CharField(max_length=255, verbose_name="店铺")
    attribute = models.IntegerField(verbose_name="属性")
    order_remarks = models.TextField(blank=True, verbose_name="订单备注")
    quantity = models.IntegerField(verbose_name="数量")
    purchase_link = models.URLField(blank=True, verbose_name="采购链接")
    order_date_summary = models.DateField(verbose_name="出单日期总结")
    first_sku = models.CharField(max_length=100, verbose_name="第一个SKU")
    statistics_month = models.DateField(verbose_name="统计月份")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'etsy_design_requirement'
        verbose_name = 'Etsy设计需求'
        verbose_name_plural = 'Etsy设计需求'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.platform_order_number} - {self.chinese_name}"


class EtsyPurchaseRequirement(models.Model):
    """Etsy采购需求表"""
    
    # 基本信息
    purchase_requirement = models.CharField(max_length=50, verbose_name="采购需求")
    order_date = models.DateField(verbose_name="出单日期")
    status_indication = models.CharField(max_length=50, verbose_name="状态指示")
    product_image = models.ImageField(upload_to='etsy_purchases/', blank=True, verbose_name="产品图片")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    chinese_name = models.CharField(max_length=255, verbose_name="中文名")
    english_name = models.CharField(max_length=255, verbose_name="英文名")
    store = models.CharField(max_length=255, verbose_name="店铺")
    attribute = models.IntegerField(verbose_name="属性")
    gift_message = models.TextField(blank=True, verbose_name="礼品赠言")
    order_remarks = models.TextField(blank=True, verbose_name="订单备注")
    purchase_link = models.URLField(blank=True, verbose_name="采购链接")
    order_date_summary = models.DateField(verbose_name="出单日期总结")
    first_sku = models.CharField(max_length=100, verbose_name="第一个SKU")
    statistics_month = models.DateField(verbose_name="统计月份")
    operation_personnel = models.CharField(max_length=100, verbose_name="运营人员")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'etsy_purchase_requirement'
        verbose_name = 'Etsy采购需求'
        verbose_name_plural = 'Etsy采购需求'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.sku} - {self.chinese_name}"


class EtsyProductionRequirement(models.Model):
    """Etsy生产需求表"""
    
    # 基本信息
    status_indication = models.CharField(max_length=50, verbose_name="状态指示")
    production_method = models.CharField(max_length=100, verbose_name="生产方式")
    production_technology = models.CharField(max_length=100, verbose_name="生产工艺")
    production_progress = models.CharField(max_length=50, verbose_name="生产进度")
    order_date = models.DateField(verbose_name="出单日期")
    product_image = models.ImageField(upload_to='etsy_productions/', blank=True, verbose_name="产品图片")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    attribute = models.IntegerField(verbose_name="属性")
    total_quantity = models.IntegerField(verbose_name="总数")
    gift_message = models.TextField(blank=True, verbose_name="礼品赠言")
    order_remarks = models.TextField(blank=True, verbose_name="订单备注")
    first_sku = models.CharField(max_length=100, verbose_name="第一个SKU")
    statistics_month = models.DateField(verbose_name="统计月份")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'etsy_production_requirement'
        verbose_name = 'Etsy生产需求'
        verbose_name_plural = 'Etsy生产需求'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.sku} - {self.production_progress}"


class EtsyShippingDelivery(models.Model):
    """Etsy配货发货表"""
    
    # 基本信息
    store_name = models.CharField(max_length=255, verbose_name="店铺名")
    operation_personnel = models.CharField(max_length=100, verbose_name="运营")
    status_indication = models.CharField(max_length=50, verbose_name="状态指示")
    label_print_status = models.CharField(max_length=50, verbose_name="标签打印状态")
    shipping_status = models.CharField(max_length=50, verbose_name="发货状态")
    order_time = models.DateTimeField(verbose_name="出单时间")
    warehouse = models.CharField(max_length=50, verbose_name="仓库")
    product_image = models.ImageField(upload_to='etsy_shipping/', blank=True, verbose_name="产品图片")
    attribute_quantity = models.IntegerField(verbose_name="属性数量")
    order_remarks = models.TextField(blank=True, verbose_name="订单备注")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    shipping_method_code = models.CharField(max_length=50, verbose_name="运输方式编码")
    tracking_query = models.URLField(blank=True, verbose_name="轨迹查询")
    
    # 收件人信息
    recipient_country = models.CharField(max_length=10, verbose_name="收件人国家")
    recipient_name = models.CharField(max_length=255, verbose_name="收件人姓名")
    recipient_address = models.TextField(verbose_name="收件人地址")
    recipient_city = models.CharField(max_length=100, verbose_name="收件人城市")
    recipient_state = models.CharField(max_length=100, verbose_name="收件人省州")
    postal_code = models.CharField(max_length=20, verbose_name="邮编")
    
    # 包裹信息
    package_count = models.IntegerField(default=1, verbose_name="件数")
    package_total_weight = models.DecimalField(max_digits=8, decimal_places=3, default=0.1, verbose_name="包裹总重量")
    
    # 发件人信息
    sender_name = models.CharField(max_length=255, default="Oncewow", verbose_name="发件人姓名")
    sender_address = models.TextField(default="Building 2, Unit 107, Pengyu Cloud Warehouse, 13 Xianfeng Road, Baima, Nancheng District, Dongguan City, Guangdong Province", verbose_name="发件人地址")
    sender_city = models.CharField(max_length=100, default="Xi'an", verbose_name="发件人城市")
    sender_state = models.CharField(max_length=100, default="ShanXi", verbose_name="发件人省州")
    sender_postal_code = models.CharField(max_length=20, default="710000", verbose_name="发件人邮编")
    sender_email = models.EmailField(default="lessersnowj@gmail.com", verbose_name="发件人邮箱")
    
    # 申报信息
    declaration_currency = models.CharField(max_length=10, default="USD", verbose_name="申报币种")
    declaration_quantity1 = models.IntegerField(default=1, verbose_name="申报数量1")
    declaration_unit_price1 = models.DecimalField(max_digits=10, decimal_places=2, default=1.00, verbose_name="申报单价1")
    declaration_unit_weight1 = models.DecimalField(max_digits=8, decimal_places=3, default=0.1, verbose_name="申报单重1")
    
    # 计算字段
    order_date_summary = models.DateField(verbose_name="出单日期总结")
    first_sku = models.CharField(max_length=100, verbose_name="第一个SKU")
    statistics_month = models.DateField(verbose_name="统计月份")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'etsy_shipping_delivery'
        verbose_name = 'Etsy配货发货'
        verbose_name_plural = 'Etsy配货发货'
        ordering = ['-order_time']
    
    def __str__(self):
        return f"{self.store_name} - {self.sku}"


class EtsyQRCodeLabel(models.Model):
    """Etsy草料二维码表"""
    
    # 基本信息
    country = models.CharField(max_length=10, verbose_name="国家")
    store_code = models.CharField(max_length=50, verbose_name="店铺代号")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    detail = models.CharField(max_length=255, verbose_name="Detail")
    n_quantity = models.IntegerField(verbose_name="N")
    c1_custom_info1 = models.CharField(max_length=255, blank=True, verbose_name="C1")
    c2_custom_info2 = models.CharField(max_length=255, blank=True, verbose_name="C2")
    order_date = models.DateField(verbose_name="出单日期")
    package_status = models.CharField(max_length=50, verbose_name="包裹状态")
    store_details = models.CharField(max_length=255, verbose_name="店铺明细")
    last_update_time = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")
    english_name = models.CharField(max_length=255, verbose_name="英文名")
    first_sku = models.CharField(max_length=100, verbose_name="第一个sku")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'etsy_qr_code_label'
        verbose_name = 'Etsy草料二维码'
        verbose_name_plural = 'Etsy草料二维码'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.store_code} - {self.sku}"


class EtsyYunTuExport(models.Model):
    """Etsy云途导出表"""
    
    # 基本信息
    final_deduction = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="最终扣款")
    recipient_country = models.CharField(max_length=10, verbose_name="收件人国家")
    shipping_fee_statistics = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="运费统计值")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'etsy_yuntu_export'
        verbose_name = 'Etsy云途导出'
        verbose_name_plural = 'Etsy云途导出'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient_country} - {self.shipping_fee_statistics}"


class EtsyYunTuDeduction(models.Model):
    """Etsy云途扣费表"""
    
    # 基本信息
    order_time = models.DateField(verbose_name="出单时间")
    store = models.CharField(max_length=255, verbose_name="店铺")
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="交易金额")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'etsy_yuntu_deduction'
        verbose_name = 'Etsy云途扣费'
        verbose_name_plural = 'Etsy云途扣费'
        ordering = ['-order_time']
    
    def __str__(self):
        return f"{self.store} - {self.transaction_amount}"


class EtsyStoreInformation(models.Model):
    """Etsy店铺信息表"""
    
    # 基本信息
    store = models.CharField(max_length=255, verbose_name="店铺")
    store_code = models.CharField(max_length=50, verbose_name="店铺代号")
    country = models.CharField(max_length=50, verbose_name="国家")
    currency = models.CharField(max_length=10, verbose_name="货币")
    source = models.CharField(max_length=100, verbose_name="来源")
    category = models.CharField(max_length=100, verbose_name="类目")
    responsible_person = models.CharField(max_length=100, verbose_name="负责人")
    store_status = models.CharField(max_length=50, verbose_name="店铺状态")
    store_rent = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="店铺租金")
    expiration_time = models.DateField(verbose_name="到期时间")
    store_opening_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="开店费用")
    owner_commission1 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="店主佣金1")
    equipment_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="设备费用")
    owner_commission2 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="店主佣金2")
    owner_commission3 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="店主佣金3")
    intermediary_commission = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="中间人佣金")
    remarks = models.TextField(blank=True, verbose_name="备注")
    transaction_record = models.TextField(blank=True, verbose_name="交易记录")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'etsy_store_information'
        verbose_name = 'Etsy店铺信息'
        verbose_name_plural = 'Etsy店铺信息'
        ordering = ['store']
    
    def __str__(self):
        return f"{self.store} - {self.store_code}"
