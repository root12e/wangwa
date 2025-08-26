from rest_framework import permissions


class InventoryPermission(permissions.BasePermission):
    """库存管理权限类"""
    
    def has_permission(self, request, view):
        """检查用户是否有权限访问库存管理功能"""
        # 检查用户是否已认证
        if not request.user.is_authenticated:
            return False
        
        # 超级用户可以访问所有功能
        if request.user.is_superuser:
            return True
        
        # 检查用户是否有库存管理权限
        # 这里可以根据您的权限系统进行调整
        if hasattr(request.user, 'has_perm'):
            return request.user.has_perm('mk.can_manage_inventory')
        
        # 如果没有权限系统，检查用户是否是员工
        if hasattr(request.user, 'is_staff'):
            return request.user.is_staff
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """检查用户是否有权限操作特定对象"""
        # 超级用户可以操作所有对象
        if request.user.is_superuser:
            return True
        
        # 检查用户是否有库存管理权限
        if hasattr(request.user, 'has_perm'):
            return request.user.has_perm('mk.can_manage_inventory')
        
        # 如果没有权限系统，检查用户是否是员工
        if hasattr(request.user, 'is_staff'):
            return request.user.is_staff
        
        return False


class InventoryReadPermission(permissions.BasePermission):
    """库存只读权限类"""
    
    def has_permission(self, request, view):
        """检查用户是否有权限读取库存信息"""
        # 检查用户是否已认证
        if not request.user.is_authenticated:
            return False
        
        # 超级用户可以访问所有功能
        if request.user.is_superuser:
            return True
        
        # 检查用户是否有库存查看权限
        if hasattr(request.user, 'has_perm'):
            return request.user.has_perm('mk.can_view_inventory')
        
        # 如果没有权限系统，检查用户是否是员工
        if hasattr(request.user, 'is_staff'):
            return request.user.is_staff
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """检查用户是否有权限查看特定对象"""
        # 超级用户可以查看所有对象
        if request.user.is_superuser:
            return True
        
        # 检查用户是否有库存查看权限
        if hasattr(request.user, 'has_perm'):
            return request.user.has_perm('mk.can_view_inventory')
        
        # 如果没有权限系统，检查用户是否是员工
        if hasattr(request.user, 'is_staff'):
            return request.user.is_staff
        
        return False


class OrderPermission(permissions.BasePermission):
    """订单管理权限类"""
    
    def has_permission(self, request, view):
        """检查用户是否有权限访问订单管理功能"""
        # 检查用户是否已认证
        if not request.user.is_authenticated:
            return False
        
        # 超级用户可以访问所有功能
        if request.user.is_superuser:
            return True
        
        # 检查用户是否有订单管理权限
        if hasattr(request.user, 'has_perm'):
            return request.user.has_perm('mk.can_manage_orders')
        
        # 如果没有权限系统，检查用户是否是员工
        if hasattr(request.user, 'is_staff'):
            return request.user.is_staff
        
        return False


class WorkflowPermission(permissions.BasePermission):
    """工作流管理权限类"""
    
    def has_permission(self, request, view):
        """检查用户是否有权限管理工作流"""
        # 检查用户是否已认证
        if not request.user.is_authenticated:
            return False
        
        # 超级用户可以访问所有功能
        if request.user.is_superuser:
            return True
        
        # 检查用户是否有工作流管理权限
        if hasattr(request.user, 'has_perm'):
            return request.user.has_perm('mk.can_manage_workflow')
        
        # 如果没有权限系统，检查用户是否是员工
        if hasattr(request.user, 'is_staff'):
            return request.user.is_staff
        
        return False
