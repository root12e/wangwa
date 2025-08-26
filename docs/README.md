# 权限管理系统

## 概述

这是一个完整的权限管理系统，按照功能模块组织，提供细粒度的权限控制。系统支持多种用户角色，包括超级管理员、部门部长、店铺运营和普通员工。

## 权限结构

```
permissions/
├── __init__.py              # 包初始化文件，提供统一导入接口
├── base.py                  # 基础权限类
├── Department_Management.py # 部门管理权限
├── User.py                  # 用户管理权限
├── Store.py                 # 店铺管理权限
├── Inventory.py             # 库存管理权限
├── System.py                # 系统设置权限
└── README.md                # 本文档
```

## 用户角色

### 1. 超级管理员 (super_admin)
- 拥有所有权限
- 可以管理所有数据
- 可以修改系统设置

### 2. 部门部长 (department_manager)
- 可以管理自己部门的数据
- 可以管理自己部门的用户和店铺
- 可以查看部门相关的日志

### 3. 店铺运营 (store_operator)
- 可以管理自己店铺的数据
- 可以管理自己店铺的用户
- 可以管理自己店铺的库存

### 4. 普通员工 (staff)
- 只能查看和修改自己的信息
- 可以查看部门、店铺、库存等公开信息
- 权限受限

## 权限类详解

### 基础权限类 (base.py)

#### IsSuperAdmin
```python
from mk.permissions import IsSuperAdmin

# 只允许超级管理员访问
permission_classes = [IsSuperAdmin]
```

#### IsDepartmentManager
```python
from mk.permissions import IsDepartmentManager

# 只允许部门部长访问
permission_classes = [IsDepartmentManager]
```

#### IsStoreOperator
```python
from mk.permissions import IsStoreOperator

# 只允许店铺运营访问
permission_classes = [IsStoreOperator]
```

#### CanManageOwnData
```python
from mk.permissions import CanManageOwnData

# 允许用户管理自己的数据
permission_classes = [CanManageOwnData]
```

### 部门管理权限 (Department_Management.py)

#### DepartmentManagementPermission
```python
from mk.permissions import DepartmentManagementPermission

# 部门管理权限：超级管理员和部门部长可以增删改查
permission_classes = [DepartmentManagementPermission]
```

**权限规则：**
- 查看：所有认证用户
- 创建/更新/删除：超级管理员和部门部长（部门部长只能管理自己部门）

#### CanManageDepartment
```python
from mk.permissions import CanManageDepartment

# 检查是否可以管理部门
permission_classes = [CanManageDepartment]
```

### 用户管理权限 (User.py)

#### UserManagementPermission
```python
from mk.permissions import UserManagementPermission

# 用户管理权限
permission_classes = [UserManagementPermission]
```

**权限规则：**
- 超级管理员：可以管理所有用户
- 部门部长：可以管理自己部门的用户
- 店铺运营：可以管理自己店铺的用户和自己的信息
- 普通员工：只能管理自己的信息

#### CanManageUser
```python
from mk.permissions import CanManageUser

# 检查是否可以管理用户
permission_classes = [CanManageUser]
```

### 店铺管理权限 (Store.py)

#### StoreManagementPermission
```python
from mk.permissions import StoreManagementPermission

# 店铺管理权限
permission_classes = [StoreManagementPermission]
```

**权限规则：**
- 超级管理员：可以管理所有店铺
- 部门部长：可以管理自己部门的店铺
- 店铺运营：可以管理自己店铺的信息
- 普通员工：只能查看店铺信息

#### CanManageStore
```python
from mk.permissions import CanManageStore

# 检查是否可以管理店铺
permission_classes = [CanManageStore]
```

### 库存管理权限 (Inventory.py)

#### InventoryManagementPermission
```python
from mk.permissions import InventoryManagementPermission

# 库存管理权限
permission_classes = [InventoryManagementPermission]
```

**权限规则：**
- 超级管理员：可以管理所有库存
- 部门部长：可以管理自己部门的库存
- 店铺运营：可以管理自己店铺的库存
- 普通员工：只能查看库存信息

#### InventoryReadOnlyPermission
```python
from mk.permissions import InventoryReadOnlyPermission

# 库存只读权限
permission_classes = [InventoryReadOnlyPermission]
```

### 系统设置权限 (System.py)

#### SystemSettingsPermission
```python
from mk.permissions import SystemSettingsPermission

# 系统设置权限
permission_classes = [SystemSettingsPermission]
```

**权限规则：**
- 查看：超级管理员和员工
- 修改：只有超级管理员

#### LogViewPermission
```python
from mk.permissions import LogViewPermission

# 日志查看权限
permission_classes = [LogViewPermission]
```

**权限规则：**
- 只有超级管理员和部门部长可以查看日志

#### BackupRestorePermission
```python
from mk.permissions import BackupRestorePermission

# 备份恢复权限
permission_classes = [BackupRestorePermission]
```

**权限规则：**
- 只有超级管理员可以进行备份恢复操作

## 使用示例

### 1. 在视图中使用权限

```python
from rest_framework import viewsets
from mk.permissions import (
    DepartmentManagementPermission,
    UserManagementPermission,
    StoreManagementPermission
)

class DepartmentViewSet(viewsets.ModelViewSet):
    """部门管理视图集"""
    permission_classes = [DepartmentManagementPermission]
    # ... 其他配置

class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    permission_classes = [UserManagementPermission]
    # ... 其他配置

class StoreViewSet(viewsets.ModelViewSet):
    """店铺管理视图集"""
    permission_classes = [StoreManagementPermission]
    # ... 其他配置
```

### 2. 组合使用多个权限

```python
from mk.permissions import IsSuperAdmin, IsDepartmentManager

class AdvancedViewSet(viewsets.ModelViewSet):
    """高级视图集"""
    permission_classes = [IsSuperAdmin | IsDepartmentManager]
    # ... 其他配置
```

### 3. 自定义权限组合

```python
from rest_framework import permissions
from mk.permissions import IsSuperAdmin, CanManageOwnData

class CustomPermission(permissions.BasePermission):
    """自定义权限组合"""
    
    def has_permission(self, request, view):
        # 超级管理员可以做任何操作
        if IsSuperAdmin().has_permission(request, view):
            return True
        
        # 普通用户只能查看
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # 超级管理员可以做任何操作
        if IsSuperAdmin().has_object_permission(request, view, obj):
            return True
        
        # 普通用户只能管理自己的数据
        return CanManageOwnData().has_object_permission(request, view, obj)
```

## 权限检查方法

### 在视图中检查权限

```python
class MyViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        
        if user.is_super_admin:
            # 超级管理员可以看到所有数据
            return Model.objects.all()
        elif user.is_department_manager:
            # 部门部长只能看到自己部门的数据
            return Model.objects.filter(department=user.department)
        else:
            # 普通用户只能看到自己的数据
            return Model.objects.filter(user=user)
```

### 在序列化器中检查权限

```python
class MySerializer(serializers.ModelSerializer):
    def validate(self, data):
        user = self.context['request'].user
        
        if not user.is_super_admin:
            # 非超级管理员不能修改某些字段
            if 'sensitive_field' in data:
                raise serializers.ValidationError("您没有权限修改此字段")
        
        return data
```

## 最佳实践

### 1. 权限命名规范
- 使用描述性的类名
- 遵循 `ActionObjectPermission` 的命名模式
- 例如：`CanManageDepartment`、`UserManagementPermission`

### 2. 权限粒度控制
- 提供粗粒度和细粒度两种权限控制
- 粗粒度：基于角色的权限（如 `IsSuperAdmin`）
- 细粒度：基于对象的权限（如 `CanManageDepartment`）

### 3. 权限缓存
- 避免重复的权限检查
- 在用户对象中缓存权限状态

### 4. 错误处理
- 提供清晰的权限错误信息
- 记录权限检查失败的日志

## 扩展权限

### 添加新的权限类

```python
# 在相应的模块文件中添加新权限类
class NewFeaturePermission(permissions.BasePermission):
    """新功能权限"""
    
    def has_permission(self, request, view):
        # 实现权限检查逻辑
        pass
    
    def has_object_permission(self, request, view, obj):
        # 实现对象级权限检查逻辑
        pass
```

### 在__init__.py中导出

```python
# 在 __init__.py 中添加导入和导出
from .Department_Management import NewFeaturePermission

__all__ = [
    # ... 现有权限类
    'NewFeaturePermission',
]
```

## 测试权限

### 单元测试

```python
from django.test import TestCase
from rest_framework.test import APITestCase
from mk.permissions import DepartmentManagementPermission

class PermissionTestCase(APITestCase):
    def setUp(self):
        # 创建测试用户和权限
        pass
    
    def test_super_admin_permission(self):
        # 测试超级管理员权限
        pass
    
    def test_department_manager_permission(self):
        # 测试部门部长权限
        pass
```

### 集成测试

```python
class PermissionIntegrationTest(APITestCase):
    def test_permission_integration(self):
        # 测试权限在完整流程中的表现
        pass
```

## 故障排除

### 常见问题

1. **权限检查失败**
   - 检查用户是否已认证
   - 检查用户角色是否正确设置
   - 检查权限类是否正确导入

2. **权限冲突**
   - 确保权限类之间没有冲突
   - 检查权限检查的顺序

3. **性能问题**
   - 避免在权限检查中进行复杂查询
   - 使用缓存减少重复检查

### 调试技巧

```python
# 在视图中添加调试信息
class DebugViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        permissions = super().get_permissions()
        print(f"当前权限类: {[p.__class__.__name__ for p in permissions]}")
        return permissions
```

## 总结

这个权限管理系统提供了：

1. **模块化设计**：按功能组织权限类
2. **灵活配置**：支持多种权限组合
3. **细粒度控制**：支持对象级权限检查
4. **易于扩展**：可以轻松添加新的权限类
5. **清晰文档**：提供详细的使用说明

通过合理使用这些权限类，可以构建安全、可控的Web应用程序。
