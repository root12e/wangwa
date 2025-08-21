from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid
from datetime import datetime, timedelta

class Department(models.Model):
    """部门模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='部门名称')
    description = models.TextField(blank=True, verbose_name='部门描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门'
        db_table = 'departments'
    
    def __str__(self):
        return self.name

class Store(models.Model):
    """店铺模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='店铺名称')
    address = models.TextField(verbose_name='店铺地址')
    phone = models.CharField(max_length=20, verbose_name='店铺电话')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='所属部门')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '店铺'
        verbose_name_plural = '店铺'
        db_table = 'stores'
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    """自定义用户模型"""
    ROLE_CHOICES = [
        ('super_admin', '超级管理员'),
        ('department_manager', '部门部长'),
        ('store_operator', '店铺运营'),
        ('staff', '普通员工'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True, verbose_name='用户名')
    phone = models.CharField(
        max_length=11, 
        unique=True, 
        verbose_name='手机号',
        validators=[
            RegexValidator(
                regex=r'^1[3-9]\d{9}$',
                message='请输入正确的手机号格式'
            )
        ]
    )
    email = models.EmailField(unique=True, verbose_name='邮箱')
    is_email_verified = models.BooleanField(default=False, verbose_name='邮箱是否验证')
    
    # 新增字段
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff', verbose_name='用户角色')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属部门')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属店铺')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone', 'email']
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'users'
    
    def __str__(self):
        return self.username
    
    @property
    def is_super_admin(self):
        """是否为超级管理员"""
        return self.role == 'super_admin'
    
    @property
    def is_department_manager(self):
        """是否为部门部长"""
        return self.role == 'department_manager'
    
    @property
    def is_store_operator(self):
        """是否为店铺运营"""
        return self.role == 'store_operator'
    
    @property
    def is_staff(self):
        """是否为普通员工"""
        return self.role == 'staff'
    
    def can_manage_user(self, target_user):
        """检查是否可以管理指定用户"""
        if self.is_super_admin:
            return True
        elif self.is_department_manager:
            return target_user.department == self.department
        elif self.is_store_operator:
            return target_user.store == self.store or target_user.id == self.id
        else:
            return target_user.id == self.id
    
    def can_manage_department(self, target_department):
        """检查是否可以管理部门"""
        if self.is_super_admin:
            return True
        elif self.is_department_manager:
            return target_department == self.department
        return False
    
    def can_manage_store(self, target_store):
        """检查是否可以管理店铺"""
        if self.is_super_admin:
            return True
        elif self.is_department_manager:
            return target_store.department == self.department
        elif self.is_store_operator:
            return target_store == self.store
        return False

class EmailVerificationCode(models.Model):
    """邮箱验证码模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name='邮箱')
    code = models.CharField(max_length=6, verbose_name='验证码')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    
    class Meta:
        verbose_name = '邮箱验证码'
        verbose_name_plural = '邮箱验证码'
        db_table = 'email_verification_codes'
    
    def is_expired(self):
        """检查验证码是否过期"""
        return datetime.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = datetime.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

class PasswordResetToken(models.Model):
    """密码重置令牌模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    token = models.CharField(max_length=100, unique=True, verbose_name='重置令牌')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    
    class Meta:
        verbose_name = '密码重置令牌'
        verbose_name_plural = '密码重置令牌'
        db_table = 'password_reset_tokens'
    
    def is_expired(self):
        """检查令牌是否过期"""
        return datetime.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = datetime.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
