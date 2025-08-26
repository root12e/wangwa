# 部门管理API文档

## 概述

部门管理模块提供了完整的部门CRUD操作，支持权限控制和数据关联查询。根据用户角色，提供不同的操作权限：

- **超级管理员**: 可以管理所有部门
- **部门部长**: 可以管理自己所在的部门
- **其他用户**: 只能查看部门信息

## 权限说明

| 操作 | 超级管理员 | 部门部长 | 其他用户 |
|------|------------|----------|----------|
| 查看部门列表 | ✅ | ✅ | ✅ |
| 查看部门详情 | ✅ | ✅ | ✅ |
| 创建部门 | ✅ | ✅ | ❌ |
| 更新部门 | ✅ | ✅ (仅自己部门) | ❌ |
| 删除部门 | ✅ | ✅ (仅自己部门) | ❌ |

## API端点

### 1. 部门列表

**GET** `/api/departments/`

获取部门列表，支持分页、搜索和过滤。

**请求参数：**
- `page`: 页码（可选）
- `page_size`: 每页数量（可选）
- `search`: 搜索关键词（可选）
- `ordering`: 排序字段（可选，如：`name`, `-created_at`）

**响应示例：**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "name": "技术部",
            "description": "负责产品研发和技术支持",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "member_count": 15,
            "store_count": 3
        }
    ]
}
```

### 2. 部门详情

**GET** `/api/departments/{id}/`

获取指定部门的详细信息，包括成员和店铺信息。

**响应示例：**
```json
{
    "id": "uuid",
    "name": "技术部",
    "description": "负责产品研发和技术支持",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "members": [
        {
            "id": "uuid",
            "username": "tech_manager",
            "role": "部门部长",
            "phone": "13800000001",
            "email": "tech_manager@wwkc.com",
            "store": "技术部店铺",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ],
    "stores": [
        {
            "id": "uuid",
            "name": "技术部店铺",
            "address": "技术部办公地址",
            "phone": "400-0001-0001",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

### 3. 创建部门

**POST** `/api/departments/`

创建新部门（需要超级管理员或部门部长权限）。

**请求体：**
```json
{
    "name": "新部门",
    "description": "新部门的描述信息"
}
```

**响应示例：**
```json
{
    "id": "uuid",
    "name": "新部门",
    "description": "新部门的描述信息",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### 4. 更新部门

**PUT** `/api/departments/{id}/` 或 **PATCH** `/api/departments/{id}/`

更新部门信息（需要超级管理员或部门部长权限）。

**请求体：**
```json
{
    "name": "更新后的部门名称",
    "description": "更新后的描述信息"
}
```

### 5. 删除部门

**DELETE** `/api/departments/{id}/`

删除部门（需要超级管理员或部门部长权限）。

**注意：** 如果部门下还有用户或店铺，无法删除。

### 6. 部门成员列表

**GET** `/api/departments/{id}/members/`

获取指定部门的所有成员列表。

**响应示例：**
```json
{
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "username": "tech_staff_1",
            "role": "普通员工",
            "role_display": "普通员工",
            "phone": "13700000001",
            "email": "tech_staff_1@wwkc.com",
            "store": "uuid",
            "store_name": "技术部店铺",
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

### 7. 部门店铺列表

**GET** `/api/departments/{id}/stores/`

获取指定部门的所有店铺列表。

**响应示例：**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "name": "技术部店铺",
            "address": "技术部办公地址",
            "phone": "400-0001-0001",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

### 8. 部门统计信息

**GET** `/api/departments/{id}/statistics/`

获取指定部门的统计信息。

**响应示例：**
```json
{
    "department_id": "uuid",
    "department_name": "技术部",
    "total_users": 15,
    "total_stores": 3,
    "user_statistics": {
        "super_admin": {
            "name": "超级管理员",
            "count": 0
        },
        "department_manager": {
            "name": "部门部长",
            "count": 1
        },
        "store_operator": {
            "name": "店铺运营",
            "count": 3
        },
        "staff": {
            "name": "普通员工",
            "count": 11
        }
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### 9. 我的部门

**GET** `/api/departments/my_department/`

获取当前用户所在的部门信息。

**响应示例：**
```json
{
    "id": "uuid",
    "name": "技术部",
    "description": "负责产品研发和技术支持",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "members": [...],
    "stores": [...]
}
```

### 10. 搜索部门

**GET** `/api/departments/search/?q=关键词`

搜索部门（支持名称和描述搜索）。

**响应示例：**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "name": "技术部",
            "description": "负责产品研发和技术支持",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "member_count": 15,
            "store_count": 3
        }
    ]
}
```

## 错误处理

### 常见错误码

- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 权限不足
- `404 Not Found`: 部门不存在
- `409 Conflict`: 部门名称重复

### 错误响应示例

```json
{
    "error": "无法删除部门 '技术部'，该部门下还有 15 个用户和 3 个店铺"
}
```

## 使用示例

### Python示例

```python
import requests

# 获取部门列表
response = requests.get('http://localhost:8000/api/departments/')
departments = response.json()

# 创建部门
new_dept = {
    "name": "新部门",
    "description": "新部门的描述"
}
response = requests.post(
    'http://localhost:8000/api/departments/',
    json=new_dept,
    headers={'Authorization': 'Bearer your_token'}
)

# 获取部门详情
dept_id = "uuid"
response = requests.get(f'http://localhost:8000/api/departments/{dept_id}/')
dept_detail = response.json()
```

### JavaScript示例

```javascript
// 获取部门列表
fetch('/api/departments/')
    .then(response => response.json())
    .then(data => console.log(data));

// 创建部门
fetch('/api/departments/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your_token'
    },
    body: JSON.stringify({
        name: '新部门',
        description: '新部门的描述'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 注意事项

1. **权限控制**: 所有写操作都需要相应的权限
2. **数据完整性**: 删除部门前会检查是否有关联的用户或店铺
3. **搜索功能**: 支持模糊搜索，提高用户体验
4. **分页支持**: 大量数据时使用分页，避免性能问题
5. **关联查询**: 部门详情包含成员和店铺信息，减少API调用次数
