# API接口设计文档

## 1. 接口概述

### 1.1 接口规范
- **基础URL**: `https://api.wwkc.com/v1`
- **认证方式**: JWT Token
- **数据格式**: JSON
- **字符编码**: UTF-8
- **HTTP版本**: HTTP/1.1

### 1.2 响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": {},
    "timestamp": "2024-12-19T10:00:00Z"
}
```

### 1.3 状态码说明
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 禁止访问
- `404`: 资源不存在
- `500`: 服务器内部错误

## 2. 认证接口

### 2.1 用户登录
- **接口**: `POST /auth/login`
- **描述**: 用户登录获取token
- **请求参数**:
```json
{
    "username": "admin",
    "password": "password123"
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "id": 1,
            "username": "admin",
            "email": "admin@wwkc.com",
            "first_name": "管理员",
            "last_name": "",
            "roles": ["admin"]
        }
    }
}
```

### 2.2 刷新Token
- **接口**: `POST /auth/refresh`
- **描述**: 刷新访问token
- **请求参数**:
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 2.3 用户登出
- **接口**: `POST /auth/logout`
- **描述**: 用户登出
- **请求头**: `Authorization: Bearer {token}`

## 3. 用户管理接口

### 3.1 获取用户列表
- **接口**: `GET /users`
- **描述**: 获取用户列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码 (默认: 1)
  - `page_size`: 每页数量 (默认: 20)
  - `search`: 搜索关键词
  - `role`: 角色筛选
  - `status`: 状态筛选

### 3.2 创建用户
- **接口**: `POST /users`
- **描述**: 创建新用户
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
```json
{
    "username": "newuser",
    "email": "newuser@wwkc.com",
    "password": "password123",
    "first_name": "新",
    "last_name": "用户",
    "phone": "13800138000",
    "roles": [1, 2]
}
```

### 3.3 更新用户
- **接口**: `PUT /users/{id}`
- **描述**: 更新用户信息
- **请求头**: `Authorization: Bearer {token}`

### 3.4 删除用户
- **接口**: `DELETE /users/{id}`
- **描述**: 删除用户
- **请求头**: `Authorization: Bearer {token}`

## 4. 部门管理接口

### 4.1 获取部门列表
- **接口**: `GET /departments`
- **描述**: 获取部门列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码
  - `page_size`: 每页数量
  - `search`: 搜索关键词
  - `parent_id`: 父部门ID
  - `status`: 状态筛选

### 4.2 创建部门
- **接口**: `POST /departments`
- **描述**: 创建新部门
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
```json
{
    "name": "技术部",
    "code": "TECH",
    "description": "负责技术开发",
    "parent_id": null,
    "manager_id": 1,
    "status": "active"
}
```

### 4.3 获取部门详情
- **接口**: `GET /departments/{id}`
- **描述**: 获取部门详细信息
- **请求头**: `Authorization: Bearer {token}`

### 4.4 更新部门
- **接口**: `PUT /departments/{id}`
- **描述**: 更新部门信息
- **请求头**: `Authorization: Bearer {token}`

### 4.5 删除部门
- **接口**: `DELETE /departments/{id}`
- **描述**: 删除部门
- **请求头**: `Authorization: Bearer {token}`

### 4.6 获取部门树结构
- **接口**: `GET /departments/tree`
- **描述**: 获取部门树形结构
- **请求头**: `Authorization: Bearer {token}`

## 5. 店铺管理接口

### 5.1 获取店铺列表
- **接口**: `GET /stores`
- **描述**: 获取店铺列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码
  - `page_size`: 每页数量
  - `search`: 搜索关键词
  - `department_id`: 部门ID筛选
  - `status`: 状态筛选

### 5.2 创建店铺
- **接口**: `POST /stores`
- **描述**: 创建新店铺
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
```json
{
    "name": "北京朝阳店",
    "code": "BJ-CY-001",
    "department_id": 1,
    "manager_id": 2,
    "address": "北京市朝阳区xxx街道xxx号",
    "phone": "010-12345678",
    "email": "bjcy@wwkc.com",
    "status": "active"
}
```

### 5.3 获取店铺详情
- **接口**: `GET /stores/{id}`
- **描述**: 获取店铺详细信息
- **请求头**: `Authorization: Bearer {token}`

### 5.4 更新店铺
- **接口**: `PUT /stores/{id}`
- **描述**: 更新店铺信息
- **请求头**: `Authorization: Bearer {token}`

### 5.5 删除店铺
- **接口**: `DELETE /stores/{id}`
- **描述**: 删除店铺
- **请求头**: `Authorization: Bearer {token}`

### 5.6 获取店铺库存汇总
- **接口**: `GET /stores/{id}/inventory-summary`
- **描述**: 获取店铺库存汇总信息
- **请求头**: `Authorization: Bearer {token}`

## 6. 产品管理接口

### 6.1 获取产品列表
- **接口**: `GET /products`
- **描述**: 获取产品列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码
  - `page_size`: 每页数量
  - `search`: 搜索关键词
  - `category_id`: 分类ID筛选
  - `store_id`: 店铺ID筛选
  - `status`: 状态筛选

### 6.2 创建产品
- **接口**: `POST /products`
- **描述**: 创建新产品
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
```json
{
    "name": "iPhone 15 Pro",
    "code": "IPHONE-15-PRO",
    "category_id": 1,
    "store_id": 1,
    "description": "苹果最新旗舰手机",
    "specifications": {
        "color": "深空黑色",
        "storage": "256GB",
        "screen": "6.1英寸"
    },
    "unit": "台",
    "price": 8999.00,
    "cost_price": 7500.00,
    "status": "active"
}
```

### 6.3 获取产品详情
- **接口**: `GET /products/{id}`
- **描述**: 获取产品详细信息
- **请求头**: `Authorization: Bearer {token}`

### 6.4 更新产品
- **接口**: `PUT /products/{id}`
- **描述**: 更新产品信息
- **请求头**: `Authorization: Bearer {token}`

### 6.5 删除产品
- **接口**: `DELETE /products/{id}`
- **描述**: 删除产品
- **请求头**: `Authorization: Bearer {token}`

### 6.6 上传产品图片
- **接口**: `POST /products/{id}/images`
- **描述**: 上传产品图片
- **请求头**: `Authorization: Bearer {token}`
- **请求类型**: `multipart/form-data`
- **请求参数**:
  - `image`: 图片文件
  - `alt_text`: 图片描述
  - `is_primary`: 是否主图

## 7. 库存管理接口

### 7.1 获取库存列表
- **接口**: `GET /inventory`
- **描述**: 获取库存列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码
  - `page_size`: 每页数量
  - `store_id`: 店铺ID筛选
  - `product_id`: 产品ID筛选
  - `low_stock`: 是否只显示低库存

### 7.2 更新库存
- **接口**: `PUT /inventory/{id}`
- **描述**: 更新库存数量
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
```json
{
    "current_quantity": 100,
    "min_quantity": 20,
    "max_quantity": 500,
    "notes": "手动调整库存"
}
```

### 7.3 获取库存变动记录
- **接口**: `GET /inventory/{id}/transactions`
- **描述**: 获取库存变动记录
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码
  - `page_size`: 每页数量
  - `transaction_type`: 变动类型筛选
  - `start_date`: 开始日期
  - `end_date`: 结束日期

### 7.4 库存盘点
- **接口**: `POST /inventory/check`
- **描述**: 创建库存盘点
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
```json
{
    "store_id": 1,
    "check_date": "2024-12-19",
    "items": [
        {
            "product_id": 1,
            "expected_quantity": 100,
            "actual_quantity": 95
        }
    ]
}
```

### 7.5 获取库存统计
- **接口**: `GET /inventory/statistics`
- **描述**: 获取库存统计数据
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `store_id`: 店铺ID
  - `department_id`: 部门ID
  - `date_range`: 日期范围

## 8. 预警系统接口

### 8.1 获取预警规则列表
- **接口**: `GET /alert-rules`
- **描述**: 获取预警规则列表
- **请求头**: `Authorization: Bearer {token}`

### 8.2 创建预警规则
- **接口**: `POST /alert-rules`
- **描述**: 创建新的预警规则
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
```json
{
    "name": "库存不足预警",
    "rule_type": "low_stock",
    "threshold_value": 20,
    "comparison_operator": "<=",
    "store_id": 1,
    "product_id": null,
    "notification_methods": ["email", "sms"],
    "is_active": true
}
```

### 8.3 获取预警记录
- **接口**: `GET /alerts`
- **描述**: 获取预警记录列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码
  - `page_size`: 每页数量
  - `status`: 状态筛选
  - `alert_level`: 预警级别筛选
  - `start_date`: 开始日期
  - `end_date`: 结束日期

### 8.4 处理预警
- **接口**: `PUT /alerts/{id}/resolve`
- **描述**: 标记预警为已处理
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
```json
{
    "resolution_notes": "已联系供应商补货",
    "resolved_by": 1
}
```

## 9. 采购管理接口

### 9.1 获取采购需求列表
- **接口**: `GET /purchase-requests`
- **描述**: 获取采购需求列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码
  - `page_size`: 每页数量
  - `status`: 状态筛选
  - `store_id`: 店铺ID筛选
  - `priority`: 优先级筛选

### 9.2 创建采购需求
- **接口**: `POST /purchase-requests`
- **描述**: 创建新的采购需求
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
```json
{
    "store_id": 1,
    "priority": "high",
    "notes": "库存不足，急需补货",
    "items": [
        {
            "product_id": 1,
            "quantity": 100,
            "unit_price": 100.00,
            "urgency_level": "urgent"
        }
    ]
}
```

### 9.3 审核采购需求
- **接口**: `PUT /purchase-requests/{id}/approve`
- **描述**: 审核采购需求
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
```json
{
    "approved": true,
    "approval_notes": "同意采购",
    "approved_by": 1
}
```

### 9.4 获取采购订单列表
- **接口**: `GET /purchase-orders`
- **描述**: 获取采购订单列表
- **请求头**: `Authorization: Bearer {token}`

### 9.5 创建采购订单
- **接口**: `POST /purchase-orders`
- **描述**: 根据采购需求创建采购订单
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
```json
{
    "request_id": 1,
    "supplier_id": 1,
    "expected_delivery_date": "2024-12-25",
    "notes": "尽快发货"
}
```

### 9.6 更新采购订单状态
- **接口**: `PUT /purchase-orders/{id}/status`
- **描述**: 更新采购订单状态
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
```json
{
    "status": "shipped",
    "tracking_number": "SF1234567890",
    "notes": "已发货"
}
```

## 10. 数据统计接口

### 10.1 获取库存统计
- **接口**: `GET /statistics/inventory`
- **描述**: 获取库存统计数据
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `store_id`: 店铺ID
  - `department_id`: 部门ID
  - `date_range`: 日期范围

### 10.2 获取销售统计
- **接口**: `GET /statistics/sales`
- **描述**: 获取销售统计数据
- **请求头**: `Authorization: Bearer {token}`

### 10.3 获取采购统计
- **接口**: `GET /statistics/purchase`
- **描述**: 获取采购统计数据
- **请求头**: `Authorization: Bearer {token}`

### 10.4 获取预警统计
- **接口**: `GET /statistics/alerts`
- **描述**: 获取预警统计数据
- **请求头**: `Authorization: Bearer {token}`

## 11. 系统管理接口

### 11.1 获取操作日志
- **接口**: `GET /operation-logs`
- **描述**: 获取操作日志列表
- **请求头**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码
  - `page_size`: 每页数量
  - `user_id`: 用户ID筛选
  - `action`: 操作类型筛选
  - `start_date`: 开始日期
  - `end_date`: 结束日期

### 11.2 获取系统配置
- **接口**: `GET /system-config`
- **描述**: 获取系统配置信息
- **请求头**: `Authorization: Bearer {token}`

### 11.3 更新系统配置
- **接口**: `PUT /system-config/{key}`
- **描述**: 更新系统配置
- **请求头**: `Authorization: Bearer {token}`

## 12. 扣子工作流集成接口

### 12.1 接收库存数据
- **接口**: `POST /webhook/kouzi-inventory`
- **描述**: 接收扣子工作流推送的库存数据
- **认证**: API Key
- **请求参数**:
```json
{
    "store_code": "BJ-CY-001",
    "product_code": "IPHONE-15-PRO",
    "quantity": 95,
    "timestamp": "2024-12-19T10:00:00Z",
    "transaction_type": "sale"
}
```

### 12.2 获取库存同步状态
- **接口**: `GET /webhook/kouzi-sync-status`
- **描述**: 获取与扣子工作流的同步状态
- **请求头**: `Authorization: Bearer {token}`

## 13. 接口限流和监控

### 13.1 限流规则
- 认证接口: 100次/小时
- 普通接口: 1000次/小时
- 文件上传: 50次/小时

### 13.2 监控指标
- 接口响应时间
- 接口调用频率
- 错误率统计
- 并发用户数

## 14. 错误码说明

### 14.1 业务错误码
- `10001`: 参数验证失败
- `10002`: 资源不存在
- `10003`: 权限不足
- `10004`: 操作失败
- `10005`: 数据重复

### 14.2 系统错误码
- `20001`: 数据库连接失败
- `20002`: 缓存服务异常
- `20003`: 外部服务调用失败
- `20004`: 文件上传失败

## 15. 接口测试

### 15.1 测试环境
- **开发环境**: `https://dev-api.wwkc.com/v1`
- **测试环境**: `https://test-api.wwkc.com/v1`
- **生产环境**: `https://api.wwkc.com/v1`

### 15.2 测试工具
- Postman
- Swagger UI
- 自动化测试脚本

### 15.3 测试用例
- 接口功能测试
- 参数验证测试
- 权限控制测试
- 性能压力测试
- 安全漏洞测试
