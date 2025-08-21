from rest_framework import permissions
from .models import User, Department, Store

class IsSuperAdmin(permissions.BasePermission):
    """超级管理员权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin

class IsDepartmentManager(permissions.BasePermission):
    """部门部长权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_department_manager

class IsStoreOperator(permissions.BasePermission):
    """店铺运营权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_store_operator

class CanManageUser(permissions.BasePermission):
    """用户管理权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # 如果对象是用户模型
        if isinstance(obj, User):
            return request.user.can_manage_user(obj)
        return False

class CanManageDepartment(permissions.BasePermission):
    """部门管理权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Department):
            return request.user.can_manage_department(obj)
        return False

class CanManageStore(permissions.BasePermission):
    """店铺管理权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Store):
            return request.user.can_manage_store(obj)
        return False

class CanManageOwnData(permissions.BasePermission):
    """管理自己数据的权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # 超级管理员可以管理所有数据
        if request.user.is_super_admin:
            return True
        
        # 部门部长可以管理自己部门的数据
        if request.user.is_department_manager:
            if hasattr(obj, 'department') and obj.department == request.user.department:
                return True
            if hasattr(obj, 'user') and obj.user.department == request.user.department:
                return True
        
        # 店铺运营可以管理自己店铺的数据
        if request.user.is_store_operator:
            if hasattr(obj, 'store') and obj.store == request.user.store:
                return True
            if hasattr(obj, 'user') and obj.user.store == request.user.store:
                return True
        
        # 普通用户只能管理自己的数据
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        if hasattr(obj, 'id') and obj.id == request.user.id:
            return True
        
        return False

class UserManagementPermission(permissions.BasePermission):
    """用户管理综合权限"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # 超级管理员可以做任何操作
        if request.user.is_super_admin:
            return True
        
        # 部门部长可以管理自己部门的用户
        if request.user.is_department_manager and request.method in ['GET', 'POST', 'PUT', 'PATCH']:
            return True
        
        # 店铺运营只能查看和修改自己的信息
        if request.user.is_store_operator and request.method in ['GET', 'PUT', 'PATCH']:
            return True
        
        # 普通员工只能查看和修改自己的信息
        if request.user.is_staff and request.method in ['GET', 'PUT', 'PATCH']:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # 超级管理员可以做任何操作
        if request.user.is_super_admin:
            return True
        
        # 部门部长可以管理自己部门的用户
        if request.user.is_department_manager:
            if hasattr(obj, 'department') and obj.department == request.user.department:
                return True
            if hasattr(obj, 'id') and obj.id == request.user.id:
                return True
        
        # 店铺运营只能管理自己店铺的用户和自己的信息
        if request.user.is_store_operator:
            if hasattr(obj, 'store') and obj.store == request.user.store:
                return True
            if hasattr(obj, 'id') and obj.id == request.user.id:
                return True
        
        # 普通员工只能管理自己的信息
        if request.user.is_staff:
            return obj.id == request.user.id
        
        return False
