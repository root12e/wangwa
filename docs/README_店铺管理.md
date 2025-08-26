# 店铺管理系统

## 概述

店铺管理系统提供了完整的店铺信息管理、库存管理和交易记录功能，支持基于角色的权限控制。

## 功能特性

### 1. 店铺管理
- 店铺的增删改查操作
- 店铺状态管理（营业中、暂停营业、已关闭、维护中）
- 店铺信息管理（名称、编码、地址、电话、邮箱等）
- 店铺经理分配
- 员工数量统计

### 2. 库存管理
- 商品库存的增删改查
- 库存数量调整
- 低库存预警
- 库存上下限设置

### 3. 交易记录
- 交易记录的创建和查询
- 支持多种交易类型（销售、采购、退货、库存调整）
- 每日交易汇总
- 月度交易报告

## 权限控制

### 超级管理员
- 可以管理所有店铺、库存和交易记录
- 拥有完整的增删改查权限

### 部门部长
- 可以管理本部门下的所有店铺
- 可以查看本部门的库存和交易记录
- 拥有店铺的增删改查权限

### 店铺运营
- 只能管理自己负责的店铺
- 可以管理本店铺的库存和交易记录
- 拥有查看和更新权限

### 普通员工
- 只能查看店铺信息
- 不能进行修改操作

## API接口

### 店铺管理接口

#### 获取店铺列表
```
GET /api/stores/
```

#### 获取店铺详情
```
GET /api/stores/{id}/
```

#### 创建店铺
```
POST /api/stores/
```

#### 更新店铺
```
PUT /api/stores/{id}/
PATCH /api/stores/{id}/
```

#### 删除店铺
```
DELETE /api/stores/{id}/
```

#### 获取我的店铺
```
GET /api/stores/my_stores/
```

#### 更改店铺状态
```
POST /api/stores/{id}/change_status/
```

#### 获取店铺统计
```
GET /api/stores/statistics/
```

### 库存管理接口

#### 获取库存列表
```
GET /api/store-inventory/
```

#### 创建库存记录
```
POST /api/store-inventory/
```

#### 更新库存
```
PUT /api/store-inventory/{id}/
PATCH /api/store-inventory/{id}/
```

#### 调整库存数量
```
POST /api/store-inventory/{id}/adjust_stock/
```

#### 获取低库存商品
```
GET /api/store-inventory/low_stock/
```

### 交易记录接口

#### 获取交易记录
```
GET /api/store-transactions/
```

#### 创建交易记录
```
POST /api/store-transactions/
```

#### 获取每日汇总
```
GET /api/store-transactions/daily_summary/?date=2024-01-01
```

#### 获取月度报告
```
GET /api/store-transactions/monthly_report/?year=2024&month=1
```

## 数据模型

### Store（店铺）
- `id`: UUID主键
- `name`: 店铺名称
- `code`: 店铺编码（唯一）
- `address`: 店铺地址
- `phone`: 店铺电话
- `email`: 店铺邮箱
- `manager`: 店铺经理（外键到User）
- `department`: 所属部门（外键到Department）
- `status`: 店铺状态
- `description`: 店铺描述
- `business_hours`: 营业时间
- `created_at`: 创建时间
- `updated_at`: 更新时间

### StoreInventory（店铺库存）
- `id`: UUID主键
- `store`: 所属店铺（外键到Store）
- `product_name`: 产品名称
- `product_code`: 产品编码
- `quantity`: 库存数量
- `unit_price`: 单价
- `min_stock`: 最低库存
- `max_stock`: 最高库存
- `created_at`: 创建时间
- `updated_at`: 更新时间

### StoreTransaction（店铺交易记录）
- `id`: UUID主键
- `store`: 所属店铺（外键到Store）
- `transaction_type`: 交易类型
- `amount`: 交易金额
- `description`: 交易描述
- `operator`: 操作员（外键到User）
- `created_at`: 创建时间

## 使用示例

### 1. 创建店铺
```python
import requests

# 创建店铺
store_data = {
    "name": "深圳南山店",
    "code": "SZ001",
    "address": "深圳市南山区科技园南区",
    "phone": "0755-12345678",
    "email": "sz001@example.com",
    "department_id": "department-uuid-here",
    "status": "active",
    "description": "深圳南山区主要店铺",
    "business_hours": "09:00-22:00"
}

response = requests.post(
    'http://localhost:8000/api/stores/',
    json=store_data,
    headers={'Authorization': 'Bearer your-token-here'}
)
```

### 2. 调整库存
```python
# 调整库存数量
adjustment_data = {
    "adjustment": 10,
    "reason": "补货入库"
}

response = requests.post(
    'http://localhost:8000/api/store-inventory/inventory-id-here/adjust_stock/',
    json=adjustment_data,
    headers={'Authorization': 'Bearer your-token-here'}
)
```

### 3. 创建交易记录
```python
# 创建销售交易
transaction_data = {
    "store_id": "store-uuid-here",
    "transaction_type": "sale",
    "amount": "299.99",
    "description": "销售商品A"
}

response = requests.post(
    'http://localhost:8000/api/store-transactions/',
    json=transaction_data,
    headers={'Authorization': 'Bearer your-token-here'}
)
```

## 初始化数据

使用以下命令初始化示例店铺数据：

```bash
python manage.py init_stores
```

## 注意事项

1. 店铺编码必须唯一
2. 库存数量不能为负数
3. 最低库存不能大于最高库存
4. 交易金额必须大于0
5. 所有操作都需要相应的权限
6. 删除店铺会同时删除相关的库存和交易记录

## 扩展功能

系统支持以下扩展功能：
- 批量导入店铺数据
- 库存预警通知
- 销售报表生成
- 店铺绩效分析
- 多店铺数据同步
