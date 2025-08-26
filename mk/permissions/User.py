"""
用户管理权限模块
提供用户相关的权限控制类
"""

from rest_framework import permissions
from ..models.User import User
from .base import IsSuperAdmin, IsDepartmentManager, IsStoreOperator


class CanManageUser(permissions.BasePermission):
    """用户管理权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # 如果对象是用户模型
        if isinstance(obj, User):
            return request.user.can_manage_user(obj)
        return False


class UserManagementPermission(permissions.BasePermission):
    """用户管理综合权限"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # 超级管理员可以做任何操作
        if hasattr(request.user, 'role') and request.user.role == 'super_admin':
            return True
        
        # 部门部长可以管理自己部门的用户
        if hasattr(request.user, 'role') and request.user.role == 'department_manager' and request.method in ['GET', 'POST', 'PUT', 'PATCH']:
            return True
        
        # 店铺运营只能查看和修改自己的信息
        if hasattr(request.user, 'role') and request.user.role == 'store_operator' and request.method in ['GET', 'PUT', 'PATCH']:
            return True
        
        # 普通员工只能查看和修改自己的信息
        if hasattr(request.user, 'role') and request.user.role == 'staff' and request.method in ['GET', 'PUT', 'PATCH']:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # 超级管理员可以做任何操作
        if hasattr(request.user, 'role') and request.user.role == 'super_admin':
            return True
        
        # 部门部长可以管理自己部门的用户
        if hasattr(request.user, 'role') and request.user.role == 'department_manager':
            if hasattr(obj, 'department') and obj.department == request.user.department:
                return True
            if hasattr(obj, 'id') and obj.id == request.user.id:
                return True
        
        # 店铺运营只能管理自己店铺的用户和自己的信息
        if hasattr(request.user, 'role') and request.user.role == 'store_operator':
            if hasattr(obj, 'store') and obj.store == request.user.store:
                return True
            if hasattr(obj, 'id') and obj.id == request.user.id:
                return True
        
        # 普通员工只能管理自己的信息
        if hasattr(request.user, 'role') and request.user.role == 'staff':
            return obj.id == request.user.id
        
        return False
