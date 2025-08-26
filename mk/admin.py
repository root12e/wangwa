from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, EmailVerificationCode, PasswordResetToken
from .models.Department import Department
from .models.store_management import Store

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """部门管理"""
    list_display = ['name', 'description', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description')
        }),
        ('系统信息', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """店铺管理"""
    list_display = ['name', 'department', 'address', 'phone', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = ['name', 'address', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'address', 'phone')
        }),
        ('组织关系', {
            'fields': ('department',)
        }),
        ('系统信息', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """自定义用户管理"""
    list_display = ['username', 'email', 'phone', 'role', 'department', 'store', 'is_active', 'is_email_verified', 'created_at']
    list_filter = ['role', 'department', 'store', 'is_active', 'is_email_verified', 'created_at']
    search_fields = ['username', 'email', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login', 'date_joined']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'password')
        }),
        ('个人信息', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('权限设置', {
            'fields': ('role', 'department', 'store', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('状态信息', {
            'fields': ('is_email_verified', 'last_login', 'date_joined')
        }),
        ('系统信息', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('基本信息', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2', 'role', 'department', 'store'),
        }),
    )
    
    def get_queryset(self, request):
        """根据用户权限过滤数据"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif hasattr(request.user, 'department') and request.user.department:
            return qs.filter(department=request.user.department)
        elif hasattr(request.user, 'store') and request.user.store:
            return qs.filter(store=request.user.store)
        else:
            return qs.filter(id=request.user.id)
    
    def has_add_permission(self, request):
        """检查添加权限"""
        if request.user.is_superuser:
            return True
        elif hasattr(request.user, 'role') and request.user.role == 'department_manager':
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        """检查修改权限"""
        if request.user.is_superuser:
            return True
        elif obj is None:
            return True
        elif hasattr(request.user, 'role') and request.user.role == 'department_manager':
            return obj.department == request.user.department
        elif hasattr(request.user, 'role') and request.user.role == 'store_operator':
            return obj.store == request.user.store or obj.id == request.user.id
        else:
            return obj.id == request.user.id
    
    def has_delete_permission(self, request, obj=None):
        """检查删除权限"""
        if request.user.is_superuser:
            return True
        elif obj is None:
            return True
        elif hasattr(request.user, 'role') and request.user.role == 'department_manager':
            return obj.department == request.user.department and obj.id != request.user.id
        elif hasattr(request.user, 'role') and request.user.role == 'store_operator':
            return obj.store == request.user.store and obj.id != request.user.id
        return False

@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    """邮箱验证码管理"""
    list_display = ['email', 'code', 'is_used', 'created_at', 'expires_at', 'is_expired_display']
    list_filter = ['is_used', 'created_at']
    search_fields = ['email']
    readonly_fields = ['id', 'created_at']
    
    def is_expired_display(self, obj):
        """显示是否过期"""
        if obj.is_expired():
            return format_html('<span style="color: red;">已过期</span>')
        return format_html('<span style="color: green;">有效</span>')
    
    is_expired_display.short_description = '状态'

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """密码重置令牌管理"""
    list_display = ['user', 'token', 'is_used', 'created_at', 'expires_at', 'is_expired_display']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['id', 'created_at']
    
    def is_expired_display(self, obj):
        """显示是否过期"""
        if obj.is_expired():
            return format_html('<span style="color: red;">已过期</span>')
        return format_html('<span style="color: green;">有效</span>')
    
    is_expired_display.short_description = '状态'
