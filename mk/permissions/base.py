"""
基础权限类模块
提供所有权限类的基础定义和通用功能
"""

from rest_framework import permissions
from ..models import User
from ..models.Department import Department
from ..models.store_management import Store


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


class IsAuthenticated(permissions.BasePermission):
    """认证用户权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
