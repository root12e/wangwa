# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone


class EtsyProductRegistration(models.Model):
    """Etsy产品登记表"""
    
    # 产品基本信息
    product_name = models.CharField(max_length=255, verbose_name="产品名")
    developer = models.CharField(max_length=100, verbose_name="开发者")
    listing_store = models.CharField(max_length=255, verbose_name="上架店铺")
    store_sku = models.CharField(max_length=100, verbose_name="店铺SKU", unique=True)
    sku_1688 = models.CharField(max_length=100, verbose_name="1688SKU")
    product_image = models.ImageField(upload_to='etsy_products/', blank=True, verbose_name="产品图片")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单位成本")
    declaration_chinese_name = models.CharField(max_length=255, verbose_name="申报中文名")
    declaration_english_name = models.CharField(max_length=255, verbose_name="申报英文名")
    production_method = models.CharField(max_length=100, verbose_name="生产方式")
    craft_technology = models.CharField(max_length=100, verbose_name="工艺")
    purchase_link = models.URLField(blank=True, verbose_name="采购链接")
    remarks = models.TextField(blank=True, verbose_name="备注")
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="预估售价")
    estimated_advertising_ratio = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="预估广告占比")
    estimated_commission = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="预估佣金")
    unit_weight = models.DecimalField(max_digits=8, decimal_places=3, verbose_name="单位重量")
    estimated_logistics_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="预估物流成本")
    estimated_gross_profit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="预估毛利")
    estimated_gross_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="预估毛利率")
    parent_record = models.CharField(max_length=100, blank=True, verbose_name="父记录")
    inventory = models.IntegerField(default=0, verbose_name="库存")
    inventory_standard_line = models.IntegerField(default=0, verbose_name="库存标准线")
    inventory_warning_line = models.IntegerField(default=0, verbose_name="库存告警线")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'etsy_product_registration'
        verbose_name = 'Etsy产品登记'
        verbose_name_plural = 'Etsy产品登记'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product_name} - {self.store_sku}"


class EtsyOrderImportSummary(models.Model):
    """Etsy订单导入汇总表"""
    
    # 订单基本信息
    order_date = models.DateField(verbose_name="订单日期")
    buyer_name = models.CharField(max_length=255, verbose_name="买家姓名", null=True, blank=True)
    email = models.EmailField(verbose_name="邮箱")
    phone = models.CharField(max_length=50, verbose_name="电话")
    recipient_name = models.CharField(max_length=255, verbose_name="收件人姓名", null=True)
    order_number = models.CharField(max_length=100, unique=True, verbose_name="订单号")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="单价")
    currency = models.CharField(max_length=10, verbose_name="币种")
    image = models.ImageField(upload_to='etsy_orders/', blank=True, verbose_name="图片")
    title = models.CharField(max_length=500, verbose_name="标题")
    quantity = models.IntegerField(verbose_name="数量")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    shipping_date = models.DateField(verbose_name="发货日期")
    country_code = models.CharField(max_length=10, verbose_name="国家二字码")
    state_province = models.CharField(max_length=100, verbose_name="省/州")
    city = models.CharField(max_length=100, verbose_name="城市")
    postal_code = models.CharField(max_length=20, verbose_name="邮编")
    address1 = models.TextField(verbose_name="地址1", null=True, blank=True)
    address2 = models.TextField(blank=True, verbose_name="地址2")
    complete_address = models.TextField(verbose_name="完整地址", null=True, blank=True)
    total_shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="总运费")
    user_remarks = models.TextField(blank=True, verbose_name="用户备注")
    as_gift = models.BooleanField(default=False, verbose_name="作为礼物")
    gift_message = models.TextField(blank=True, verbose_name="礼品赠言")
    seller_tax_number = models.CharField(max_length=100, blank=True, verbose_name="卖家税号")
    attributes = models.CharField(max_length=500, blank=True, verbose_name="属性")
    custom_info1 = models.CharField(max_length=500, blank=True, verbose_name="定制信息1")
    custom_info2 = models.CharField(max_length=500, blank=True, verbose_name="定制信息2")
    image_attachments = models.TextField(blank=True, verbose_name="图片附件")
    store = models.CharField(max_length=255, verbose_name="店铺")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    recipient_address = models.TextField(verbose_name="收件人地址", null=True, blank=True)
    attributes2 = models.CharField(max_length=500, blank=True, verbose_name="属性2")
    attribute_quantity = models.IntegerField(verbose_name="属性数量")
    date_formatted = models.CharField(max_length=100, verbose_name="日期格式化")
    attribute_quantity_en = models.CharField(max_length=100, blank=True, verbose_name="属性数量EN")
    last_update_time = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")
    purchase_status = models.CharField(max_length=50, blank=True, verbose_name="采购状态")
    purchase_sku = models.CharField(max_length=100, blank=True, verbose_name="采购SKU")
    purchase_link = models.URLField(blank=True, verbose_name="采购链接")
    inventory_quantity = models.IntegerField(default=0, verbose_name="库存数量")
    design_file = models.CharField(max_length=255, blank=True, verbose_name="设计文件")
    craft_technology = models.CharField(max_length=100, blank=True, verbose_name="工艺")
    
    class Meta:
        db_table = 'etsy_order_import_summary'
        verbose_name = 'Etsy订单导入汇总'
        verbose_name_plural = 'Etsy订单导入汇总'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.buyer_name}"


class EtsyOrderStatistics(models.Model):
    """Etsy订单统计表"""
    
    # 订单基本信息
    platform_order_number = models.CharField(max_length=100, unique=True, verbose_name="平台订单号")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    store_name = models.CharField(max_length=255, verbose_name="店铺名称")
    responsible_person = models.CharField(max_length=100, verbose_name="负责人")
    order_date = models.DateField(verbose_name="出单日期")
    product_image = models.ImageField(upload_to='etsy_statistics/', blank=True, verbose_name="产品图")
    attribute_quantity = models.IntegerField(verbose_name="属性数量")
    total_quantity = models.IntegerField(verbose_name="总数")
    order_remarks = models.TextField(blank=True, verbose_name="订单备注")
    shipping_method = models.CharField(max_length=50, verbose_name="运输方式", choices=[
        ('标快', '标快'),
        ('特快', '特快'),
    ])
    status_indication = models.CharField(max_length=50, verbose_name="状态指示", choices=[
        ('审核中', '审核中'),
        ('确认执行', '确认执行'),
        ('已暂停', '已暂停'),
        ('物流拦截', '物流拦截'),
        ('已取消', '已取消'),
        ('已补发', '已补发'),
    ])
    purchase_status = models.CharField(max_length=50, blank=True, verbose_name="采购状态")
    production_status = models.CharField(max_length=50, blank=True, verbose_name="生产状态")
    shipping_status = models.CharField(max_length=50, blank=True, verbose_name="发货状态")
    logistics_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="物流成本")
    order_date_summary = models.DateField(verbose_name="出单日期总结")
    statistics_month = models.DateField(verbose_name="统计月份")
    sku_new_line = models.CharField(max_length=255, verbose_name="SKU回车")
    order_date_summary_1 = models.DateField(verbose_name="出单日期总结 (1)")
    statistics_month_1 = models.DateField(verbose_name="统计月份 (1)")
    sku_new_line_1 = models.CharField(max_length=255, verbose_name="SKU回车 (1)")
    
    # 外键关联
    order_import_summary = models.ForeignKey(
        EtsyOrderImportSummary, 
        on_delete=models.CASCADE, 
        verbose_name="订单导入汇总",
        related_name="order_statistics"
    )
    
    class Meta:
        db_table = 'etsy_order_statistics'
        verbose_name = 'Etsy订单统计'
        verbose_name_plural = 'Etsy订单统计'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.platform_order_number} - {self.store_name}"


class EtsyDesignRequirement(models.Model):
    """Etsy设计需求表"""
    
    # 基本信息
    order_number = models.CharField(max_length=100, verbose_name="订单号", null=True, blank=True)
    order_date = models.DateField(verbose_name="出单日期")
    status_indication = models.CharField(max_length=50, verbose_name="状态指示")
    product_image = models.ImageField(upload_to='etsy_designs/', blank=True, verbose_name="产品图片")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    chinese_name = models.CharField(max_length=255, verbose_name="中文名")
    store = models.CharField(max_length=255, verbose_name="店铺")
    attributes = models.CharField(max_length=500, blank=True, verbose_name="属性")
    gift_message = models.TextField(blank=True, verbose_name="礼品赠言")
    order_remarks = models.TextField(blank=True, verbose_name="订单备注")
    quantity = models.IntegerField(verbose_name="数量")
    purchase_link = models.URLField(blank=True, verbose_name="采购链接")
    purchase_personnel = models.CharField(max_length=100, blank=True, verbose_name="采购人员")
    purchase_status = models.CharField(max_length=50, blank=True, verbose_name="采购状态")
    purchase_time = models.DateTimeField(blank=True, null=True, verbose_name="采购时间")
    purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="采购金额")
    logistics_tracking_number = models.CharField(max_length=100, blank=True, verbose_name="物流单号")
    logistics_tracking = models.TextField(blank=True, verbose_name="物流轨迹")
    logistics_latest_status = models.CharField(max_length=100, blank=True, verbose_name="物流轨迹.最新状态")
    logistics_detailed_status = models.CharField(max_length=100, blank=True, verbose_name="物流轨迹.详细状态")
    logistics_latest_update_date = models.DateTimeField(blank=True, null=True, verbose_name="物流轨迹.最新更新日期")
    logistics_latest_location = models.CharField(max_length=255, blank=True, verbose_name="物流轨迹.最新地点")
    logistics_latest_coordinates = models.CharField(max_length=100, blank=True, verbose_name="物流轨迹.最近经纬度")
    logistics_history = models.TextField(blank=True, verbose_name="物流轨迹.历史记录")
    order_date_summary = models.DateField(verbose_name="出单日期总结")
    first_sku = models.CharField(max_length=100, verbose_name="第一个SKU")
    statistics_month = models.DateField(verbose_name="统计月份")
    
    # 外键关联
    order_import_summary = models.ForeignKey(
        EtsyOrderImportSummary, 
        on_delete=models.CASCADE, 
        verbose_name="订单导入汇总",
        related_name="design_requirements",
        null=True,
        blank=True
    )
    order_statistics = models.ForeignKey(
        EtsyOrderStatistics, 
        on_delete=models.CASCADE, 
        verbose_name="订单统计",
        related_name="design_requirements",
        null=True,
        blank=True
    )
    product_registration = models.ForeignKey(
        EtsyProductRegistration, 
        on_delete=models.CASCADE, 
        verbose_name="产品登记",
        related_name="design_requirements",
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'etsy_design_requirement'
        verbose_name = 'Etsy设计需求'
        verbose_name_plural = 'Etsy设计需求'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.chinese_name}"


class EtsyPurchaseRequirement(models.Model):
    """Etsy采购需求表"""
    
    # 基本信息
    order_number = models.CharField(max_length=100, verbose_name="订单号", null=True, blank=True)
    purchase_requirement = models.CharField(max_length=50, verbose_name="采购需求")
    order_date = models.DateField(verbose_name="出单日期")
    status_indication = models.CharField(max_length=50, verbose_name="状态指示")
    product_image = models.ImageField(upload_to='etsy_purchases/', blank=True, verbose_name="产品图片")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    chinese_name = models.CharField(max_length=255, verbose_name="中文名")
    english_name = models.CharField(max_length=255, verbose_name="英文名")
    store = models.CharField(max_length=255, verbose_name="店铺")
    attributes = models.CharField(max_length=500, blank=True, verbose_name="属性")
    gift_message = models.TextField(blank=True, verbose_name="礼品赠言")
    order_remarks = models.TextField(blank=True, verbose_name="订单备注")
    quantity = models.IntegerField(verbose_name="数量")
    purchase_link = models.URLField(blank=True, verbose_name="采购链接")
    purchase_personnel = models.CharField(max_length=100, blank=True, verbose_name="采购人员")
    purchase_status = models.CharField(max_length=50, blank=True, verbose_name="采购状态")
    purchase_time = models.DateTimeField(blank=True, null=True, verbose_name="采购时间")
    purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="采购金额")
    logistics_tracking_number = models.CharField(max_length=100, blank=True, verbose_name="物流单号")
    logistics_tracking = models.TextField(blank=True, verbose_name="物流轨迹")
    logistics_latest_status = models.CharField(max_length=100, blank=True, verbose_name="物流轨迹.最新状态")
    logistics_detailed_status = models.CharField(max_length=100, blank=True, verbose_name="物流轨迹.详细状态")
    logistics_latest_update_date = models.DateTimeField(blank=True, null=True, verbose_name="物流轨迹.最新更新日期")
    logistics_latest_location = models.CharField(max_length=255, blank=True, verbose_name="物流轨迹.最新地点")
    logistics_latest_coordinates = models.CharField(max_length=100, blank=True, verbose_name="物流轨迹.最近经纬度")
    logistics_history = models.TextField(blank=True, verbose_name="物流轨迹.历史记录")
    order_date_summary = models.DateField(verbose_name="出单日期总结")
    first_sku = models.CharField(max_length=100, verbose_name="第一个SKU")
    statistics_month = models.DateField(verbose_name="统计月份")
    operation_personnel = models.CharField(max_length=100, verbose_name="运营人员")
    
    # 外键关联
    order_import_summary = models.ForeignKey(
        EtsyOrderImportSummary, 
        on_delete=models.CASCADE, 
        verbose_name="订单导入汇总",
        related_name="purchase_requirements",
        null=True,
        blank=True
    )
    order_statistics = models.ForeignKey(
        EtsyOrderStatistics, 
        on_delete=models.CASCADE, 
        verbose_name="订单统计",
        related_name="purchase_requirements",
        null=True,
        blank=True
    )
    product_registration = models.ForeignKey(
        EtsyProductRegistration, 
        on_delete=models.CASCADE, 
        verbose_name="产品登记",
        related_name="purchase_requirements",
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'etsy_purchase_requirement'
        verbose_name = 'Etsy采购需求'
        verbose_name_plural = 'Etsy采购需求'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.chinese_name}"


class EtsyProductionRequirement(models.Model):
    """Etsy生产需求表"""
    
    # 基本信息
    order_number = models.CharField(max_length=100, verbose_name="订单号", null=True, blank=True)
    status_indication = models.CharField(max_length=50, verbose_name="状态指示")
    production_method = models.CharField(max_length=100, verbose_name="生产方式")
    production_technology = models.CharField(max_length=100, verbose_name="生产工艺")
    production_progress = models.CharField(max_length=50, verbose_name="生产进度", choices=[
        ('无需生产', '无需生产'),
        ('等待中', '等待中'),
        ('加工中', '加工中'),
        ('已完成', '已完成'),
    ])
    design_drawings = models.CharField(max_length=255, blank=True, verbose_name="设计图纸")
    order_date = models.DateField(verbose_name="出单日期")
    product_image = models.ImageField(upload_to='etsy_productions/', blank=True, verbose_name="产品图片")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    attributes = models.CharField(max_length=500, blank=True, verbose_name="属性")
    total_quantity = models.IntegerField(verbose_name="总数")
    gift_message = models.TextField(blank=True, verbose_name="礼品赠言")
    order_remarks = models.TextField(blank=True, verbose_name="订单备注")
    first_sku = models.CharField(max_length=100, verbose_name="第一个SKU")
    statistics_month = models.DateField(verbose_name="统计月份")
    
    # 外键关联
    order_import_summary = models.ForeignKey(
        EtsyOrderImportSummary, 
        on_delete=models.CASCADE, 
        verbose_name="订单导入汇总",
        related_name="production_requirements"
    )
    order_statistics = models.ForeignKey(
        EtsyOrderStatistics, 
        on_delete=models.CASCADE, 
        verbose_name="订单统计",
        related_name="production_requirements",
        null=True,
        blank=True
    )
    product_registration = models.ForeignKey(
        EtsyProductRegistration, 
        on_delete=models.CASCADE, 
        verbose_name="产品登记",
        related_name="production_requirements",
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'etsy_production_requirement'
        verbose_name = 'Etsy生产需求'
        verbose_name_plural = 'Etsy生产需求'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.sku}"


class EtsyShippingDelivery(models.Model):
    """Etsy配货发货表"""
    
    # 基本信息
    customer_order_number = models.CharField(max_length=100, verbose_name="客户订单号", null=True, blank=True)
    last_update_time = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")
    store_name = models.CharField(max_length=255, verbose_name="店铺名")
    operation_personnel = models.CharField(max_length=100, verbose_name="运营")
    status_indication = models.CharField(max_length=50, verbose_name="状态指示")
    label_print_status = models.CharField(max_length=50, verbose_name="标签打印状态")
    shipping_status = models.CharField(max_length=50, verbose_name="发货状态", choices=[
        ('找货-待采购', '找货-待采购'),
        ('转运-待收货', '转运-待收货'),
        ('已发货', '已发货'),
        ('交付', '交付'),
        ('取消', '取消'),
        ('退款', '退款'),
    ])
    order_time = models.DateTimeField(verbose_name="出单时间")
    warehouse = models.CharField(max_length=50, verbose_name="仓库", choices=[
        ('西安仓', '西安仓'),
        ('东莞仓', '东莞仓'),
    ])
    product_image = models.ImageField(upload_to='etsy_shipping/', blank=True, verbose_name="产品图片")
    design_file = models.CharField(max_length=255, blank=True, verbose_name="设计文件")
    attribute_quantity = models.IntegerField(verbose_name="属性数量")
    order_remarks = models.TextField(blank=True, verbose_name="订单备注")
    sku = models.CharField(max_length=255, verbose_name="SKU")
    shipping_method_code = models.CharField(max_length=50, verbose_name="运输方式代码")
    additional_services = models.CharField(max_length=255, blank=True, verbose_name="附加服务")
    insurance_service = models.CharField(max_length=50, blank=True, verbose_name="保价服务")
    signature_service = models.CharField(max_length=50, blank=True, verbose_name="签名服务")
    vat_number = models.CharField(max_length=100, blank=True, verbose_name="增值税号")
    eu_tax_number = models.CharField(max_length=100, blank=True, verbose_name="欧盟税号")
    method_code_export = models.CharField(max_length=50, blank=True, verbose_name="方式代码（导出）")
    last_mile_carrier = models.CharField(max_length=100, blank=True, verbose_name="尾程物流商")
    last_mile_tracking_number = models.CharField(max_length=100, blank=True, verbose_name="尾程跟踪号")
    warehouse_express = models.CharField(max_length=100, blank=True, verbose_name="寄仓快递")
    sync_status = models.BooleanField(default=False, verbose_name="是否同步")
    ioss_code = models.CharField(max_length=100, blank=True, verbose_name="IOSS识别码")
    shipping_fee_statistics = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="运费统计值")
    tracking_query = models.URLField(blank=True, verbose_name="轨迹查询")
    
    # 收件人信息
    recipient_country = models.CharField(max_length=10, verbose_name="收件人国家")
    recipient_name = models.CharField(max_length=255, verbose_name="收件人姓名")
    recipient_id = models.CharField(max_length=100, blank=True, verbose_name="收件人ID")
    recipient_company = models.CharField(max_length=255, blank=True, verbose_name="收件人公司")
    recipient_address = models.TextField(verbose_name="收件人地址")
    recipient_city = models.CharField(max_length=100, verbose_name="收件人城市")
    recipient_state = models.CharField(max_length=100, verbose_name="收件人省州")
    postal_code = models.CharField(max_length=20, verbose_name="邮编")
    declaration_product_name1 = models.CharField(max_length=255, verbose_name="申报品名1")
    chinese_declaration_name1 = models.CharField(max_length=255, verbose_name="中文申报品名1")
    phone = models.CharField(max_length=50, verbose_name="电话")
    house_number = models.CharField(max_length=50, blank=True, verbose_name="门牌号")
    email = models.EmailField(verbose_name="邮箱")
    package_count = models.IntegerField(default=1, verbose_name="件数")
    package_total_weight = models.DecimalField(max_digits=8, decimal_places=3, default=0.1, verbose_name="包裹总重量")
    
    # 发件人信息
    sender_name = models.CharField(max_length=255, default="Oncewow", verbose_name="发件人姓名")
    sender_company = models.CharField(max_length=255, blank=True, verbose_name="发件人公司")
    sender_address = models.TextField(default="Building 2, Unit 107, Pengyu Cloud Warehouse, 13 Xianfeng Road, Baima, Nancheng District, Dongguan City, Guangdong Province", verbose_name="发件人地址")
    sender_city = models.CharField(max_length=100, default="Xi'an", verbose_name="发件人城市")
    sender_state = models.CharField(max_length=100, default="ShanXi", verbose_name="发件人省州")
    sender_postal_code = models.CharField(max_length=20, default="710000", verbose_name="发件人邮编")
    sender_country = models.CharField(max_length=50, default="China", verbose_name="发件人国家")
    sender_phone = models.CharField(max_length=50, blank=True, verbose_name="发件人电话")
    sender_email = models.EmailField(default="lessersnowj@gmail.com", verbose_name="发件人邮箱")
    sender_usci = models.CharField(max_length=100, blank=True, verbose_name="发件人USCI")
    
    # 平台信息
    platform_name = models.CharField(max_length=255, verbose_name="平台名称")
    platform_address = models.TextField(verbose_name="平台地址")
    platform_state = models.CharField(max_length=100, verbose_name="平台省州")
    platform_postal_code = models.CharField(max_length=20, verbose_name="平台邮编")
    platform_phone = models.CharField(max_length=50, verbose_name="平台电话")
    platform_email = models.EmailField(verbose_name="平台邮箱")
    
    # 申报信息
    declaration_currency = models.CharField(max_length=10, default="USD", verbose_name="申报币种")
    sku1 = models.CharField(max_length=100, verbose_name="SKU1")
    declaration_quantity1 = models.IntegerField(default=1, verbose_name="申报数量1")
    declaration_unit_price1 = models.DecimalField(max_digits=10, decimal_places=2, default=1.00, verbose_name="申报单价1")
    declaration_unit_weight1 = models.DecimalField(max_digits=8, decimal_places=3, default=0.1, verbose_name="申报单重1")
    customs_code1 = models.CharField(max_length=100, blank=True, verbose_name="海关编码1")
    picking_info1 = models.TextField(blank=True, verbose_name="配货信息1")
    sales_link1 = models.URLField(blank=True, verbose_name="销售链接1")
    material1 = models.CharField(max_length=100, blank=True, verbose_name="材质1")
    purpose1 = models.CharField(max_length=100, blank=True, verbose_name="用途1")
    brand1 = models.CharField(max_length=100, blank=True, verbose_name="品牌1")
    model1 = models.CharField(max_length=100, blank=True, verbose_name="型号1")
    specification1 = models.CharField(max_length=100, blank=True, verbose_name="规格1")
    manufacturer_id1 = models.CharField(max_length=100, blank=True, verbose_name="ManufacturerID1")
    
    # 支付信息
    payment_platform = models.CharField(max_length=100, blank=True, verbose_name="支付平台")
    payment_platform_account = models.CharField(max_length=100, blank=True, verbose_name="支付平台账号")
    payment_transaction_number = models.CharField(max_length=100, blank=True, verbose_name="支付交易号")
    
    # 计算字段
    order_date_summary = models.DateField(verbose_name="出单日期")
    first_sku = models.CharField(max_length=100, verbose_name="第一个SKU")
    statistics_month = models.DateField(verbose_name="统计月份")
    
    # 外键关联
    order_import_summary = models.ForeignKey(
        EtsyOrderImportSummary, 
        on_delete=models.CASCADE, 
        verbose_name="订单导入汇总",
        related_name="shipping_deliveries"
    )
    order_statistics = models.ForeignKey(
        EtsyOrderStatistics, 
        on_delete=models.CASCADE, 
        verbose_name="订单统计",
        related_name="shipping_deliveries",
        null=True,
        blank=True
    )
    product_registration = models.ForeignKey(
        EtsyProductRegistration, 
        on_delete=models.CASCADE, 
        verbose_name="产品登记",
        related_name="shipping_deliveries",
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'etsy_shipping_delivery'
        verbose_name = 'Etsy配货发货'
        verbose_name_plural = 'Etsy配货发货'
        ordering = ['-order_time']
    
    def __str__(self):
        return f"{self.customer_order_number} - {self.store_name}"


class EtsyQRCodeLabel(models.Model):
    """Etsy草料二维码表"""
    
    # 基本信息
    order_number = models.CharField(max_length=100, verbose_name="订单号", null=True, blank=True)
    country = models.CharField(max_length=10, verbose_name="国家")
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
    warehouse_express_tracking = models.CharField(max_length=100, blank=True, verbose_name="寄仓快递单号")
    yuntu_carrier = models.CharField(max_length=50, blank=True, verbose_name="云途")
    last_mile_carrier = models.CharField(max_length=50, blank=True, verbose_name="尾程")
    store_name = models.CharField(max_length=255, verbose_name="店铺名称")
    last_update_time = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")
    first_sku = models.CharField(max_length=100, verbose_name="第一个sku")
    parent_record = models.CharField(max_length=100, blank=True, verbose_name="父记录")
    
    # 外键关联
    order_statistics = models.ForeignKey(
        EtsyOrderStatistics, 
        on_delete=models.CASCADE, 
        verbose_name="订单统计",
        related_name="qr_code_labels",
        null=True,
        blank=True
    )
    shipping_delivery = models.ForeignKey(
        EtsyShippingDelivery, 
        on_delete=models.CASCADE, 
        verbose_name="配货发货",
        related_name="qr_code_labels"
    )
    product_registration = models.ForeignKey(
        EtsyProductRegistration, 
        on_delete=models.CASCADE, 
        verbose_name="产品登记",
        related_name="qr_code_labels",
        null=True,
        blank=True
    )
    store_information = models.ForeignKey(
        'EtsyStoreInformation', 
        on_delete=models.CASCADE, 
        verbose_name="店铺信息",
        related_name="qr_code_labels"
    )
    
    class Meta:
        db_table = 'etsy_qr_code_label'
        verbose_name = 'Etsy草料二维码'
        verbose_name_plural = 'Etsy草料二维码'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.store_code}"


class EtsyYunTuExport(models.Model):
    """Etsy云途导出表"""
    
    # 基本信息
    customer_order_number = models.CharField(max_length=100, verbose_name="客户单号", null=True, blank=True)
    tracking_number = models.CharField(max_length=100, verbose_name="运单号")
    tracking_code = models.CharField(max_length=100, verbose_name="跟踪号")
    created_at = models.DateTimeField(verbose_name="创建时间")
    order_status = models.CharField(max_length=50, verbose_name="订单状态")
    shipping_method_code = models.CharField(max_length=50, verbose_name="运输方式代码")
    
    # 收件人信息
    recipient_country = models.CharField(max_length=10, verbose_name="收件人国家")
    recipient_name = models.CharField(max_length=255, verbose_name="收件人姓名")
    recipient_company = models.CharField(max_length=255, blank=True, verbose_name="收件人公司")
    recipient_address = models.TextField(verbose_name="收件人地址")
    recipient_city = models.CharField(max_length=100, verbose_name="收件人城市")
    recipient_state = models.CharField(max_length=100, verbose_name="收件人州省")
    postal_code = models.CharField(max_length=20, verbose_name="邮编")
    recipient_phone = models.CharField(max_length=50, verbose_name="收件人电话")
    recipient_mobile = models.CharField(max_length=50, verbose_name="收件人手机号")
    email = models.EmailField(verbose_name="邮箱")
    
    # 包裹信息
    remote_address = models.BooleanField(default=False, verbose_name="是否偏远地址")
    return_status = models.BooleanField(default=False, verbose_name="是否退回")
    sensitive_goods = models.BooleanField(default=False, verbose_name="敏感货品")
    outer_package_count = models.IntegerField(default=1, verbose_name="外包装数量")
    package_weight = models.DecimalField(max_digits=8, decimal_places=3, verbose_name="包裹重量")
    platform_transaction_number = models.CharField(max_length=100, blank=True, verbose_name="平台交易号")
    tariff_prepaid = models.BooleanField(default=False, verbose_name="是否关税预付")
    
    # 时间信息
    receipt_time = models.DateTimeField(blank=True, null=True, verbose_name="收货时间")
    shipping_time = models.DateTimeField(blank=True, null=True, verbose_name="发货时间")
    prepaid_status = models.BooleanField(default=False, verbose_name="是否预缴")
    ioss_code = models.CharField(max_length=100, blank=True, verbose_name="IOSS识别码")
    signature_time = models.DateTimeField(blank=True, null=True, verbose_name="签收时间")
    return_reason = models.TextField(blank=True, verbose_name="退件原因")
    insurance_status = models.BooleanField(default=False, verbose_name="是否保价")
    
    # 支付信息
    payment_platform = models.CharField(max_length=100, blank=True, verbose_name="支付平台")
    payment_platform_account = models.CharField(max_length=100, blank=True, verbose_name="支付平台账号")
    payment_transaction_number = models.CharField(max_length=100, blank=True, verbose_name="支付交易号")
    
    # 费用信息
    final_deduction = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="最终扣款")
    shipping_fee_statistics = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="运费统计值")
    
    # 外键关联
    yuntu_deduction = models.ForeignKey(
        'EtsyYunTuDeduction', 
        on_delete=models.CASCADE, 
        verbose_name="云途扣费",
        related_name="yuntu_exports"
    )
    
    class Meta:
        db_table = 'etsy_yuntu_export'
        verbose_name = 'Etsy云途导出'
        verbose_name_plural = 'Etsy云途导出'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_order_number} - {self.tracking_number}"


class EtsyYunTuDeduction(models.Model):
    """Etsy云途扣费表"""
    
    # 基本信息
    transaction_type = models.CharField(max_length=100, verbose_name="交易类型")
    transaction_time = models.DateTimeField(verbose_name="发生时间")
    order_time = models.DateField(verbose_name="出单时间")
    transaction_product = models.CharField(max_length=255, verbose_name="交易产品")
    country_code = models.CharField(max_length=10, verbose_name="国家代码")
    country_name = models.CharField(max_length=100, verbose_name="国家名称")
    currency_code = models.CharField(max_length=10, verbose_name="币种代码")
    customer_order_number = models.CharField(max_length=100, verbose_name="客户单号", null=True, blank=True)
    tracking_number = models.CharField(max_length=100, verbose_name="运单号")
    tracking_code = models.CharField(max_length=100, verbose_name="跟踪号")
    
    # 重量信息
    billing_weight = models.DecimalField(max_digits=8, decimal_places=3, verbose_name="计费重")
    volume_weight = models.DecimalField(max_digits=8, decimal_places=3, verbose_name="体积重")
    actual_weight = models.DecimalField(max_digits=8, decimal_places=3, verbose_name="实重")
    
    # 费用信息
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="交易金额")
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="运费")
    fuel_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="燃油费")
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="挂号费")
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="处理费")
    vat_tax = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="VAT增值税")
    redispatch_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="重派费")
    tariff_prepaid_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="关税预付手续费")
    remote_additional_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="偏远附加费")
    return_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="退回费用")
    special_product_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="特殊产品加收费")
    other_fees = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="其他费")
    remarks = models.TextField(blank=True, verbose_name="备注")
    store = models.CharField(max_length=255, verbose_name="店铺")
    
    # 外键关联
    order_statistics = models.ForeignKey(
        EtsyOrderStatistics, 
        on_delete=models.CASCADE, 
        verbose_name="订单统计",
        related_name="yuntu_deductions",
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'etsy_yuntu_deduction'
        verbose_name = 'Etsy云途扣费'
        verbose_name_plural = 'Etsy云途扣费'
        ordering = ['-transaction_time']
    
    def __str__(self):
        return f"{self.customer_order_number} - {self.transaction_amount}"


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
    parent_record = models.CharField(max_length=100, blank=True, verbose_name="父记录")
    
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
 
