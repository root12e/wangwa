# 部门管理功能说明

## 功能概述

部门管理模块是库存管理系统的核心功能之一，提供了完整的部门CRUD操作，支持权限控制和数据关联查询。该模块实现了基于角色的权限控制，确保数据安全和操作合规。

## 主要特性

### 1. 权限控制
- **超级管理员**: 可以管理所有部门
- **部门部长**: 可以管理自己所在的部门
- **其他用户**: 只能查看部门信息

### 2. 数据关联
- 部门与用户的关联关系
- 部门与店铺的关联关系
- 支持级联查询和统计

### 3. 功能完整
- 完整的CRUD操作
- 搜索和过滤功能
- 分页支持
- 数据统计

## 文件结构

```
mk/
├── models/
│   └── User.py                 # 包含Department和Store模型
├── serializers/
│   └── Department_Management.py # 部门管理序列化器
├── views/
│   └── Department_Management.py # 部门管理视图
├── permissions.py              # 权限控制类
├── urls.py                    # URL路由配置
└── management/commands/
    └── init_departments.py    # 初始化测试数据
```

## 快速开始

### 1. 初始化测试数据

```bash
# 创建基础测试数据
python manage.py init_system

# 创建部门管理测试数据
python manage.py init_departments
```

### 2. 启动开发服务器

```bash
python manage.py runserver
```

### 3. 测试API功能

```bash
# 运行测试脚本
python test_department_api.py
```

## API端点

### 基础操作
- `GET /api/departments/` - 获取部门列表
- `GET /api/departments/{id}/` - 获取部门详情
- `POST /api/departments/` - 创建部门
- `PUT /api/departments/{id}/` - 更新部门
- `DELETE /api/departments/{id}/` - 删除部门

### 扩展功能
- `GET /api/departments/{id}/members/` - 获取部门成员
- `GET /api/departments/{id}/stores/` - 获取部门店铺
- `GET /api/departments/{id}/statistics/` - 获取部门统计
- `GET /api/departments/my_department/` - 获取我的部门
- `GET /api/departments/search/?q=关键词` - 搜索部门

## 数据模型

### Department（部门）
```python
class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Store（店铺）
```python
class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### User（用户）
```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', '超级管理员'),
        ('department_manager', '部门部长'),
        ('store_operator', '店铺运营'),
        ('staff', '普通员工'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
```

## 权限控制

### DepartmentManagementPermission
```python
class DepartmentManagementPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # 所有认证用户都可以查看
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # 只有超级管理员和部门部长可以写操作
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_super_admin or request.user.is_department_manager
    
    def has_object_permission(self, request, view, obj):
        # 查看权限
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # 写权限控制
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if request.user.is_super_admin:
                return True
            elif request.user.is_department_manager:
                return obj == request.user.department
        
        return False
```

## 序列化器

### DepartmentListSerializer
用于部门列表展示，包含成员数量和店铺数量统计。

### DepartmentDetailSerializer
用于部门详情展示，包含完整的成员和店铺信息。

### DepartmentCreateSerializer
用于创建部门，包含名称唯一性验证。

### DepartmentUpdateSerializer
用于更新部门，包含名称唯一性验证（排除当前部门）。

## 视图功能

### DepartmentViewSet
- 支持完整的CRUD操作
- 根据用户权限过滤数据
- 提供扩展的action方法
- 支持搜索、过滤、排序、分页

### 主要方法
- `get_queryset()`: 根据用户权限过滤查询集
- `perform_destroy()`: 删除前检查关联数据
- `members()`: 获取部门成员列表
- `stores()`: 获取部门店铺列表
- `statistics()`: 获取部门统计信息
- `my_department()`: 获取当前用户的部门
- `search()`: 搜索部门

## 使用示例

### 1. 获取部门列表
```python
import requests

response = requests.get('http://localhost:8000/api/departments/')
departments = response.json()
```

### 2. 创建部门
```python
import requests

new_dept = {
    "name": "新部门",
    "description": "新部门的描述信息"
}

response = requests.post(
    'http://localhost:8000/api/departments/',
    json=new_dept,
    headers={'Authorization': 'Bearer your_token'}
)
```

### 3. 获取部门详情
```python
dept_id = "uuid"
response = requests.get(f'http://localhost:8000/api/departments/{dept_id}/')
dept_detail = response.json()
```

### 4. 获取部门成员
```python
response = requests.get(f'http://localhost:8000/api/departments/{dept_id}/members/')
members = response.json()
```

## 测试

### 运行测试
```bash
python test_department_api.py
```

### 测试覆盖
- 部门列表获取
- 部门详情获取
- 部门成员查询
- 部门店铺查询
- 部门统计信息
- 搜索功能
- 权限控制

## 注意事项

### 1. 数据完整性
- 删除部门前会检查是否有关联的用户或店铺
- 如果存在关联数据，删除操作会被拒绝

### 2. 权限控制
- 所有写操作都需要相应的权限
- 部门部长只能管理自己所在的部门

### 3. 性能优化
- 使用select_related和prefetch_related优化查询
- 支持分页，避免大量数据影响性能

### 4. 错误处理
- 提供详细的错误信息
- 支持国际化错误消息

## 扩展功能

### 1. 部门层级
可以扩展支持部门的层级结构，实现组织架构管理。

### 2. 部门权限
可以为不同部门设置不同的操作权限。

### 3. 部门统计
可以添加更多的统计维度，如部门业绩、人员流动等。

### 4. 批量操作
可以添加批量创建、更新、删除部门的功能。

## 常见问题

### Q: 如何修改部门名称？
A: 使用PUT或PATCH方法更新部门信息，系统会自动检查名称唯一性。

### Q: 为什么无法删除部门？
A: 如果部门下还有用户或店铺，系统会拒绝删除操作以保护数据完整性。

### Q: 部门部长可以管理其他部门吗？
A: 不可以，部门部长只能管理自己所在的部门。

### Q: 如何获取当前用户的部门信息？
A: 使用`/api/departments/my_department/`端点获取。

## 技术支持

如果遇到问题，请检查：
1. 数据库连接是否正常
2. 用户认证是否有效
3. 权限设置是否正确
4. 日志文件中的错误信息

更多详细信息请参考API文档：`docs/部门管理API文档.md`
