"""
系统设置权限模块
提供系统配置和设置相关的权限控制类
"""

from rest_framework import permissions
from .base import IsSuperAdmin


class SystemSettingsPermission(permissions.BasePermission):
    """系统设置权限"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # 只有超级管理员可以管理系统设置
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_super_admin or request.user.is_staff
        
        # 只有超级管理员可以修改系统设置
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_super_admin
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # 只有超级管理员可以修改系统设置
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_super_admin
        
        # 超级管理员和员工可以查看系统设置
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_super_admin or request.user.is_staff
        
        return False


class LogViewPermission(permissions.BasePermission):
    """日志查看权限"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # 只有超级管理员和部门部长可以查看日志
        return request.user.is_super_admin or request.user.is_department_manager
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # 只有超级管理员和部门部长可以查看日志
        return request.user.is_super_admin or request.user.is_department_manager


class BackupRestorePermission(permissions.BasePermission):
    """备份恢复权限"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # 只有超级管理员可以进行备份恢复操作
        return request.user.is_super_admin
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # 只有超级管理员可以进行备份恢复操作
        return request.user.is_super_admin
