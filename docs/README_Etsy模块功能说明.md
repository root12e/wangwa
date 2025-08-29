# Etsy模块功能说明

## 概述
Etsy模块是一个完整的三级菜单管理系统，专门用于管理Etsy相关的所有业务数据和流程。该模块实现了完整的增删改查功能，支持批量操作、数据导入导出、筛选排序等高级功能。

## 功能特性

### 1. 三级菜单结构
- **第一级**: Etsy（主模块）
- **第二级**: 
  - 工作协同
  - 场外协同
  - 云途导出数据
  - 数据统计
  - 月度汇总
- **第三级**: 具体的功能模块

### 2. 权限控制
- 只有Etsy部门的人和超级管理员能查看和修改
- 基于角色的访问控制
- 对象级权限验证

### 3. 数据管理功能
每个数据表都支持以下操作：
- ✅ 新增记录
- ✅ 编辑记录
- ✅ 删除记录
- ✅ 查询记录
- ✅ 批量创建
- ✅ 批量更新
- ✅ 批量删除
- ✅ 数据导入
- ✅ 数据导出
- ✅ 模板下载

### 4. 高级筛选和排序
- 多字段搜索
- 日期范围筛选
- 店铺筛选
- 状态筛选
- 运营人员筛选
- 多字段排序
- 升序/降序支持

## 模块详细说明

### 工作协同模块

#### 产品登记表
- **功能**: 管理Etsy产品的基本信息
- **特色**: 支持根据店铺筛选产品
- **字段**: 产品名称、SKU、成本、售价、生产方式等

#### 订单导入汇总
- **功能**: 管理从Etsy平台导入的订单数据
- **特色**: 完整的订单信息管理
- **字段**: 订单号、店铺、SKU、收件人信息等

#### 订单统计
- **功能**: 订单数据的统计分析
- **特色**: 按发货状态排列的专门视图
- **字段**: 订单状态、生产进度、物流信息等

#### 设计需求表
- **功能**: 管理产品设计需求
- **特色**: 支持筛选和排序
- **字段**: 设计状态、产品图片、采购链接等

#### 采购需求表
- **功能**: 管理采购需求
- **特色**: 根据运营人员筛选店铺商品
- **字段**: 采购需求、运营人员、店铺信息等

#### 生产需求表
- **功能**: 管理生产需求
- **特色**: 生产进度跟踪
- **字段**: 生产方式、生产工艺、生产进度等

#### 配货发货表
- **功能**: 管理配货和发货流程
- **特色**: 
  - 固定筛选：标签打印状态为空，出单日期大于2025年7月1日
  - 支持提交到草料二维码
- **字段**: 店铺、运营、发货状态、包裹信息等

### 云途导出数据模块

#### 云途导出表
- **功能**: 管理云途导出的数据
- **特色**: 根据表内信息筛选和排序

#### 云途扣费表
- **功能**: 管理云途扣费记录
- **特色**: 根据表内信息筛选和排序

### 月度汇总模块

#### 店铺信息表
- **功能**: 管理Etsy店铺的基本信息
- **特色**: 完整的店铺信息管理
- **字段**: 店铺名称、国家、货币、负责人、租金等

### 草料二维码模块

#### 草料二维码表
- **功能**: 管理二维码标签
- **特色**: 
  - 固定筛选：标签状态为空（要打印的订单）
  - 固定筛选：标签状态为已包装，包裹状态为已包装，寄仓快递单号为空（要发货的订单）
- **字段**: 国家、店铺、SKU、包裹状态等

## 技术实现

### 后端技术栈
- **框架**: Django 4.2 + Django REST Framework
- **数据库**: 支持MySQL和PostgreSQL
- **权限**: 自定义权限系统
- **数据处理**: Pandas + OpenPyXL
- **API**: RESTful API设计

### 前端技术栈
- **框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios

### 核心功能实现

#### 1. 权限控制
```python
class EtsyPermission(BasePermission):
    def has_permission(self, request, view):
        # 超级管理员拥有所有权限
        if request.user.is_superuser:
            return True
            
        # 检查用户是否属于etsy部门
        if hasattr(request.user, 'department') and request.user.department:
            if 'etsy' in request.user.department.name.lower():
                return True
                
        return False
```

#### 2. 批量操作
```python
@action(detail=False, methods=['post'])
def bulk_create(self, request):
    """批量创建"""
    serializer = EtsyBulkCreateSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data['data']
        created_objects = []
        
        for item in data:
            item_serializer = self.get_serializer(data=item)
            if item_serializer.is_valid():
                obj = item_serializer.save()
                created_objects.append(obj)
        
        return Response({
            'message': f'成功创建 {len(created_objects)} 条记录',
            'created_count': len(created_objects)
        })
```

#### 3. 数据导入
```python
@action(detail=False, methods=['post'])
def import_data(self, request):
    """导入数据"""
    file = request.FILES['file']
    
    # 读取Excel文件
    if file.name.endswith('.xlsx'):
        df = pd.read_excel(file)
    elif file.name.endswith('.csv'):
        df = pd.read_csv(file)
    
    # 验证和导入数据
    # ... 详细实现
```

#### 4. 高级筛选
```python
def get_queryset(self):
    """获取查询集，支持筛选"""
    queryset = super().get_queryset()
    
    # 获取筛选参数
    search = self.request.query_params.get('search', '')
    start_date = self.request.query_params.get('start_date', '')
    end_date = self.request.query_params.get('end_date', '')
    store = self.request.query_params.get('store', '')
    
    # 应用筛选条件
    if search:
        queryset = queryset.filter(
            Q(sku__icontains=search) |
            Q(store_name__icontains=search) |
            Q(product_name__icontains=search)
        )
    
    # ... 更多筛选逻辑
```

## 使用说明

### 1. 访问权限
- 确保用户属于Etsy部门或具有超级管理员权限
- 登录系统后，在左侧导航栏选择"Etsy管理"

### 2. 数据操作
- **新增**: 点击"新增"按钮，填写表单信息
- **编辑**: 在表格中点击"编辑"按钮
- **删除**: 在表格中点击"删除"按钮
- **批量操作**: 选择多行数据，使用批量操作功能

### 3. 数据导入
- 下载对应的Excel模板
- 填写数据后上传文件
- 系统自动验证和导入数据

### 4. 筛选和排序
- 使用筛选表单设置筛选条件
- 选择排序字段和方向
- 点击"搜索"按钮应用筛选

## 注意事项

1. **权限要求**: 只有Etsy部门用户和超级管理员可以访问
2. **文件格式**: 支持.xlsx和.csv格式的文件导入
3. **数据验证**: 导入时会自动验证数据格式和必填字段
4. **批量操作**: 批量操作有数量限制（最多1000条）
5. **数据备份**: 建议定期备份重要数据

## 扩展功能

### 1. 报表统计
- 销售数据统计
- 库存周转分析
- 成本利润分析

### 2. 工作流管理
- 订单状态流转
- 审批流程
- 任务分配

### 3. 集成功能
- Etsy API集成
- 第三方物流集成
- 财务系统集成

## 技术支持

如有技术问题或功能需求，请联系开发团队或查看相关文档。
