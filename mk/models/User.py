from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

# 导入部门相关模型
from .Department import Department
from .store_management import Store

class User(AbstractUser):
    """自定义用户模型"""
    ROLE_CHOICES = [
        ('super_admin', '超级管理员'),
        ('department_manager', '部门管理员'),
        ('store_operator', '店铺运营'),
        ('staff', '普通员工'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '审批中'),
        ('approved', '已通过'),
        ('active', '激活'),
        ('inactive', '禁用'),
        ('rejected', '已拒绝'),
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
    
    # 审批相关字段
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='审批状态')
    approved_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='审批人')
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    rejection_reason = models.TextField(blank=True, verbose_name='拒绝原因')
    
    # AbstractUser 的必需字段，设置默认值
    is_staff = models.BooleanField(default=False, verbose_name='是否为员工')
    is_superuser = models.BooleanField(default=False, verbose_name='是否为超级用户')
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
        """是否为部门管理员"""
        return self.role == 'department_manager'
    
    @property
    def is_store_operator(self):
        """是否为店铺运营"""
        return self.role == 'store_operator'
    
    @property
    def is_staff_member(self):
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

    @classmethod
    def normalize_email(cls, email):
        """标准化邮箱地址"""
        if email:
            email = email.strip().lower()
        return email

    @classmethod
    def create_user(cls, username, email, password, **extra_fields):
        """创建用户的自定义方法"""
        if not username:
            raise ValueError('用户名是必需的')
        if not email:
            raise ValueError('邮箱是必需的')
        if not password:
            raise ValueError('密码是必需的')
        
        # 标准化邮箱
        email = cls.normalize_email(email)
        
        # 设置默认值
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        
        # 设置默认状态
        if 'status' not in extra_fields:
            extra_fields['status'] = 'pending'
        
        # 创建用户实例
        user = cls(
            username=username,
            email=email,
            **extra_fields
        )
        
        # 设置密码
        user.set_password(password)
        
        # 如果是第一个超级管理员，自动审批通过并激活
        if user.role == 'super_admin' and not cls.objects.filter(role='super_admin', status__in=['approved', 'active']).exists():
            user.status = 'active'
            user.is_staff = True
            user.is_superuser = True
            print(f"自动激活第一个超级管理员: {username}")
        
        # 保存用户
        user.save()
        
        return user

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批通过用户"""
        user = self.get_object()
        if not request.user.can_approve_user(user):
            return Response({'error': '没有权限审批该用户'}, status=status.HTTP_403_FORBIDDEN)
        
        user.status = 'approved'
        user.approved_by = request.user
        user.approval_date = timezone.now()
        user.save()
        
        # 发送审批通过邮件
        try:
            send_mail(
                '账号审批通过',
                f'您的账号 {user.username} 已通过审批，可以正常登录使用。',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"发送邮件失败: {e}")
        
        return Response({'message': '审批通过'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """审批拒绝用户"""
        user = self.get_object()
        if not request.user.can_approve_user(user):
            return Response({'error': '没有权限审批该用户'}, status=status.HTTP_403_FORBIDDEN)
        
        reason = request.data.get('reason', '')
        if not reason:
            return Response({'error': '拒绝时必须提供原因'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.status = 'rejected'
        user.rejection_reason = reason
        user.save()
        
        # 发送拒绝邮件
        try:
            send_mail(
                '账号审批被拒绝',
                f'您的账号 {user.username} 审批被拒绝，原因：{reason}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"发送邮件失败: {e}")
        
        return Response({'message': '审批拒绝'})

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
        """检查验证码是否过期 - 使用timezone-aware datetime"""
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
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
        """检查令牌是否过期 - 使用timezone-aware datetime"""
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

class AdminInvitation(models.Model):
    """管理员邀请模型"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('accepted', '已接受'),
        ('rejected', '已拒绝'),
        ('expired', '已过期'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations', verbose_name='邀请人')
    invitee_email = models.EmailField(verbose_name='被邀请人邮箱')
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES, verbose_name='邀请角色')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, verbose_name='所属部门')
    token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='邀请令牌')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='邀请状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    
    class Meta:
        verbose_name = '管理员邀请'
        verbose_name_plural = '管理员邀请'
        db_table = 'admin_invitations'
    
    def __str__(self):
        return f"{self.inviter.username} 邀请 {self.invitee_email} 成为 {self.get_role_display()}"
    
    def is_expired(self):
        """检查邀请是否过期"""
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)
