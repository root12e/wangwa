"""
店铺管理权限模块
提供店铺相关的权限控制类
"""

from rest_framework import permissions
from .base import IsSuperAdmin, IsDepartmentManager, IsStoreOperator


class CanManageStore(permissions.BasePermission):
    """店铺管理权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Store):
            return request.user.can_manage_store(obj)
        return False


class StoreManagementPermission(permissions.BasePermission):
    """店铺管理综合权限"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # 超级管理员可以做任何操作
        if request.user.is_super_admin:
            return True
        
        # 部门部长可以管理自己部门的店铺
        if request.user.is_department_manager and request.method in ['GET', 'POST', 'PUT', 'PATCH']:
            return True
        
        # 店铺运营可以管理自己店铺的信息
        if request.user.is_store_operator and request.method in ['GET', 'PUT', 'PATCH']:
            return True
        
        # 普通员工只能查看店铺信息
        if request.user.is_staff and request.method in ['GET']:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # 超级管理员可以做任何操作
        if request.user.is_super_admin:
            return True
        
        # 部门部长可以管理自己部门的店铺
        if request.user.is_department_manager:
            if hasattr(obj, 'department') and obj.department == request.user.department:
                return True
        
        # 店铺运营只能管理自己店铺的信息
        if request.user.is_store_operator:
            if hasattr(obj, 'id') and obj.id == request.user.store.id:
                return True
        
        # 普通员工只能查看店铺信息
        if request.user.is_staff and request.method in ['GET']:
            return True
        
        return False
