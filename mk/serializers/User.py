from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from ..models import User, EmailVerificationCode, PasswordResetToken, Department, Store
import re


class DepartmentSerializer(serializers.ModelSerializer):
    """部门序列化器"""
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StoreSerializer(serializers.ModelSerializer):
    """店铺序列化器"""
    department = DepartmentSerializer(read_only=True)
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'phone', 'department', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    confirm_password = serializers.CharField(write_only=True)
    email_verification_code = serializers.CharField(write_only=True, max_length=6)

    class Meta:
        model = User
        fields = ['username', 'phone', 'email', 'password', 'confirm_password', 'email_verification_code', 'role', 'department', 'store']

    def validate(self, attrs):
        # 验证密码确认
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("两次输入的密码不一致")

        # 验证密码强度
        try:
            validate_password(attrs['password'])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})

        # 验证手机号格式
        phone_pattern = re.compile(r'^1[3-9]\d{9}$')
        if not phone_pattern.match(attrs['phone']):
            raise serializers.ValidationError({'phone': '请输入正确的手机号格式'})

        # 验证邮箱验证码
        try:
            verification = EmailVerificationCode.objects.get(
                email=attrs['email'],
                code=attrs['email_verification_code'],
                is_used=False
            )
            if verification.is_expired():
                raise serializers.ValidationError({'email_verification_code': '验证码已过期'})
        except EmailVerificationCode.DoesNotExist:
            raise serializers.ValidationError({'email_verification_code': '验证码错误'})

        # 验证角色权限
        role = attrs.get('role', 'staff')
        if role not in ['staff', 'store_operator']:
            raise serializers.ValidationError({'role': '注册时只能选择普通员工或店铺运营角色'})

        return attrs

    def create(self, validated_data):
        # 移除不需要的字段
        validated_data.pop('confirm_password')
        validated_data.pop('email_verification_code')

        # 创建用户
        user = User.objects.create_user(
            username=validated_data['username'],
            phone=validated_data['phone'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'staff'),
            department=validated_data.get('department'),
            store=validated_data.get('store')
        )

        # 标记验证码为已使用
        EmailVerificationCode.objects.filter(
            email=validated_data['email'],
            code=validated_data['email_verification_code']
        ).update(is_used=True)

        # 标记邮箱为已验证
        user.is_email_verified = True
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username_or_phone = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        username_or_phone = attrs.get('username_or_phone')
        password = attrs.get('password')

        if username_or_phone and password:
            # 判断是用户名还是手机号
            if re.match(r'^1[3-9]\d{9}$', username_or_phone):
                # 手机号登录
                try:
                    user = User.objects.get(phone=username_or_phone)
                    username_or_phone = user.username
                except User.DoesNotExist:
                    raise serializers.ValidationError('手机号不存在')

            # 验证用户
            user = authenticate(username=username_or_phone, password=password)
            if not user:
                raise serializers.ValidationError('用户名或密码错误')

            if not user.is_active:
                raise serializers.ValidationError('用户账户已被禁用')

            attrs['user'] = user
        else:
            raise serializers.ValidationError('必须提供用户名/手机号和密码')

        return attrs


class SendEmailVerificationCodeSerializer(serializers.Serializer):
    """发送邮箱验证码序列化器"""
    email = serializers.EmailField()

    def validate_email(self, value):
        # 检查是否在60秒内已经发送过验证码
        from datetime import datetime, timedelta
        recent_code = EmailVerificationCode.objects.filter(
            email=value,
            created_at__gte=datetime.now() - timedelta(seconds=60)
        ).first()

        if recent_code:
            raise serializers.ValidationError('请等待60秒后再发送验证码')

        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """密码重置请求序列化器"""
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('该邮箱未注册')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """密码重置确认序列化器"""
    token = serializers.CharField(max_length=100)
    new_password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    confirm_password = serializers.CharField(min_length=8, max_length=128, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("两次输入的密码不一致")

        # 验证密码强度
        try:
            validate_password(attrs['new_password'])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({'new_password': e.messages})

        # 验证令牌
        try:
            reset_token = PasswordResetToken.objects.get(
                token=attrs['token'],
                is_used=False
            )
            if reset_token.is_expired():
                raise serializers.ValidationError({'token': '重置令牌已过期'})
            attrs['reset_token'] = reset_token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({'token': '无效的重置令牌'})

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    department = DepartmentSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'is_email_verified', 'role', 'role_display', 'department', 'store', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器"""
    department = DepartmentSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'role', 'role_display', 'department', 'store', 'is_active', 'created_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""
    
    class Meta:
        model = User
        fields = ['username', 'phone', 'email', 'role', 'department', 'store', 'is_active']
    
    def validate_role(self, value):
        """验证角色权限"""
        user = self.context['request'].user
        
        # 超级管理员可以设置任何角色
        if user.is_super_admin:
            return value
        
        # 部门部长只能设置自己部门内的角色，且不能设置为超级管理员
        if user.is_department_manager:
            if value == 'super_admin':
                raise serializers.ValidationError('部门部长不能设置超级管理员角色')
            return value
        
        # 其他用户不能修改角色
        if not user.is_super_admin and not user.is_department_manager:
            raise serializers.ValidationError('您没有权限修改用户角色')
        
        return value
    
    def validate_department(self, value):
        """验证部门权限"""
        user = self.context['request'].user
        
        # 超级管理员可以设置任何部门
        if user.is_super_admin:
            return value
        
        # 部门部长只能设置自己部门
        if user.is_department_manager:
            if value != user.department:
                raise serializers.ValidationError('部门部长只能管理自己部门的用户')
            return value
        
        # 其他用户不能修改部门
        if not user.is_super_admin and not user.is_department_manager:
            raise serializers.ValidationError('您没有权限修改用户部门')
        
        return value
    
    def validate_store(self, value):
        """验证店铺权限"""
        user = self.context['request'].user
        
        # 超级管理员可以设置任何店铺
        if user.is_super_admin:
            return value
        
        # 部门部长只能设置自己部门的店铺
        if user.is_department_manager:
            if value and value.department != user.department:
                raise serializers.ValidationError('部门部长只能管理自己部门的店铺')
            return value
        
        # 店铺运营只能设置自己店铺
        if user.is_store_operator:
            if value != user.store:
                raise serializers.ValidationError('店铺运营只能管理自己店铺的用户')
            return value
        
        # 其他用户不能修改店铺
        if not user.is_super_admin and not user.is_department_manager and not user.is_store_operator:
            raise serializers.ValidationError('您没有权限修改用户店铺')
        
        return value
