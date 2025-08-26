"""
权限管理包
提供完整的权限控制系统，按功能模块组织

使用示例:
    from mk.permissions import (
        IsSuperAdmin,
        DepartmentManagementPermission,
        UserManagementPermission,
        StoreManagementPermission,
        InventoryManagementPermission,
        SystemSettingsPermission
    )
"""
from .product_management import *
from .inventory_management import *
from .PO import *
# 基础权限类
from .base import (
    IsSuperAdmin,
    IsDepartmentManager,
    IsStoreOperator,
    CanManageOwnData
)

# 部门管理权限
from .department_permissions import (
    CanManageDepartment,
    CanInviteAdmin
)

# 用户管理权限
from .User import (
    CanManageUser,
    UserManagementPermission
)

# 店铺管理权限
from .Store import (
    CanManageStore,
    StoreManagementPermission
)


# 系统设置权限
from .System import (
    SystemSettingsPermission,
    LogViewPermission,
    BackupRestorePermission
)

# 导出所有权限类
__all__ = [
    # 基础权限
    'IsSuperAdmin',
    'IsDepartmentManager',
    'IsStoreOperator',
    'CanManageOwnData',
    
    # 部门管理权限
    'CanManageDepartment',
    'CanInviteAdmin',
    
    # 用户管理权限
    'CanManageUser',
    'UserManagementPermission',
    
    # 店铺管理权限
    'CanManageStore',
    'StoreManagementPermission',
    
    # 系统设置权限
    'SystemSettingsPermission',
    'LogViewPermission',
    'BackupRestorePermission',
]