from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """超级管理员权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'

class IsDepartmentManager(permissions.BasePermission):
    """部门管理员权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['super_admin', 'department_manager']

class IsStoreOperator(permissions.BasePermission):
    """店铺运营权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['super_admin', 'department_manager', 'store_operator']

class CanManageUser(permissions.BasePermission):
    """用户管理权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['super_admin', 'department_manager']
    
    def has_object_permission(self, request, view, obj):
        return request.user.can_manage_user(obj)

class CanApproveUser(permissions.BasePermission):
    """用户审批权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['super_admin', 'department_manager']
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'super_admin':
            return True
        elif request.user.role == 'department_manager':
            return obj.department == request.user.department
        return False
