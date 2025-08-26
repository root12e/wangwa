from rest_framework import permissions

class CanManageDepartment(permissions.BasePermission):
    """部门管理权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['super_admin', 'department_manager']
    
    def has_object_permission(self, request, view, obj):
        return request.user.can_manage_department(obj)

class CanInviteAdmin(permissions.BasePermission):
    """管理员邀请权限"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['super_admin', 'department_manager']
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'super_admin':
            return True
        elif request.user.role == 'department_manager':
            return obj.department == request.user.department
        return False
