from rest_framework import permissions
from ..models import User, Store, Product


class ProductPermission(permissions.BasePermission):
    """产品管理权限控制"""
    
    def has_permission(self, request, view):
        """检查用户是否有权限访问产品管理"""
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # 超级管理员可以访问所有产品
        if user.is_super_admin:
            return True
        
        # 部门管理员可以访问本部门所有店铺的产品
        if user.is_department_manager and user.department:
            return True
        
        # 店铺运营可以访问自己店铺的产品
        if user.is_store_operator and user.store:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """检查用户是否有权限操作特定产品"""
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # 超级管理员可以操作所有产品
        if user.is_super_admin:
            return True
        
        # 部门管理员可以操作本部门所有店铺的产品
        if user.is_department_manager and user.department:
            if hasattr(obj, 'store') and obj.store.department == user.department:
                return True
            elif hasattr(obj, 'department') and obj.department == user.department:
                return True
        
        # 店铺运营只能操作自己店铺的产品
        if user.is_store_operator and user.store:
            if hasattr(obj, 'store') and obj.store == user.store:
                return True
        
        return False


class ProductCreatePermission(permissions.BasePermission):
    """产品创建权限控制"""
    
    def has_permission(self, request, view):
        """检查用户是否有权限创建产品"""
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # 超级管理员可以创建产品到任何店铺
        if user.is_super_admin:
            return True
        
        # 部门管理员可以创建产品到本部门任何店铺
        if user.is_department_manager and user.department:
            return True
        
        # 店铺运营只能创建产品到自己店铺
        if user.is_store_operator and user.store:
            return True
        
        return False


class ProductUpdatePermission(permissions.BasePermission):
    """产品更新权限控制"""
    
    def has_object_permission(self, request, view, obj):
        """检查用户是否有权限更新特定产品"""
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # 超级管理员可以更新所有产品
        if user.is_super_admin:
            return True
        
        # 部门管理员可以更新本部门所有店铺的产品
        if user.is_department_manager and user.department:
            if hasattr(obj, 'store') and obj.store.department == user.department:
                return True
        
        # 店铺运营只能更新自己店铺的产品
        if user.is_store_operator and user.store:
            if hasattr(obj, 'store') and obj.store == user.store:
                return True
        
        return False


class ProductDeletePermission(permissions.BasePermission):
    """产品删除权限控制"""
    
    def has_object_permission(self, request, view, obj):
        """检查用户是否有权限删除特定产品"""
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # 超级管理员可以删除所有产品
        if user.is_super_admin:
            return True
        
        # 部门管理员可以删除本部门所有店铺的产品
        if user.is_department_manager and user.department:
            if hasattr(obj, 'store') and obj.store.department == user.department:
                return True
        
        # 店铺运营只能删除自己店铺的产品
        if user.is_store_operator and user.store:
            if hasattr(obj, 'store') and obj.store == user.store:
                return True
        
        return False


class ProductViewPermission(permissions.BasePermission):
    """产品查看权限控制"""
    
    def has_permission(self, request, view):
        """检查用户是否有权限查看产品"""
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # 所有已认证用户都可以查看产品
        return True
    
    def has_object_permission(self, request, view, obj):
        """检查用户是否有权限查看特定产品"""
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # 超级管理员可以查看所有产品
        if user.is_super_admin:
            return True
        
        # 部门管理员可以查看本部门所有店铺的产品
        if user.is_department_manager and user.department:
            if hasattr(obj, 'store') and obj.store.department == user.department:
                return True
            elif hasattr(obj, 'department') and obj.department == user.department:
                return True
        
        # 店铺运营可以查看自己店铺的产品
        if user.is_store_operator and user.store:
            if hasattr(obj, 'store') and obj.store == user.store:
                return True
        
        return False


class StoreProductPermission(permissions.BasePermission):
    """店铺产品权限控制"""
    
    def has_permission(self, request, view):
        """检查用户是否有权限访问店铺产品"""
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # 超级管理员可以访问所有店铺的产品
        if user.is_super_admin:
            return True
        
        # 部门管理员可以访问本部门所有店铺的产品
        if user.is_department_manager and user.department:
            return True
        
        # 店铺运营可以访问自己店铺的产品
        if user.is_store_operator and user.store:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """检查用户是否有权限操作特定店铺的产品"""
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # 超级管理员可以操作所有店铺的产品
        if user.is_super_admin:
            return True
        
        # 部门管理员可以操作本部门所有店铺的产品
        if user.is_department_manager and user.department:
            if hasattr(obj, 'store') and obj.store.department == user.department:
                return True
            elif hasattr(obj, 'department') and obj.department == user.department:
                return True
        
        # 店铺运营只能操作自己店铺的产品
        if user.is_store_operator and user.store:
            if hasattr(obj, 'store') and obj.store == user.store:
                return True
        
        return False
