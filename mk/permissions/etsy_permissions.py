from rest_framework import permissions


class EtsyPermission(permissions.BasePermission):
    """
    Etsy模块权限控制
    只有etsy部门的人和超级管理员能查看和修改
    """
    
    def has_permission(self, request, view):
        # 超级管理员拥有所有权限
        if request.user.is_superuser:
            return True
            
        # 检查用户角色是否为超级管理员
        if hasattr(request.user, 'role') and request.user.role == 'super_admin':
            return True
            
        # 检查用户是否属于etsy部门
        if hasattr(request.user, 'department') and request.user.department:
            # 检查部门名称是否包含'etsy'（不区分大小写）
            if 'etsy' in request.user.department.name.lower():
                return True
                
        return False
    
    def has_object_permission(self, request, view, obj):
        # 对象级权限检查
        return self.has_permission(request, view)


class EtsyReadOnlyPermission(permissions.BasePermission):
    """
    Etsy模块只读权限控制
    只有etsy部门的人和超级管理员能查看
    """
    
    def has_permission(self, request, view):
        # 超级管理员拥有所有权限
        if request.user.is_superuser:
            return True
            
        # 检查用户角色是否为超级管理员
        if hasattr(request.user, 'role') and request.user.role == 'super_admin':
            return True
            
        # 检查用户是否属于etsy部门
        if hasattr(request.user, 'department') and request.user.department:
            # 检查部门名称是否包含'etsy'（不区分大小写）
            if 'etsy' in request.user.department.name.lower():
                return True
                
        return False
    
    def has_object_permission(self, request, view, obj):
        # 对象级权限检查
        return self.has_permission(request, view)
