#!/usr/bin/env python
"""
测试认证系统修复的脚本
"""

import os
import sys
import django
from datetime import timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wwkc.settings')
django.setup()

from django.utils import timezone
from mk.models import EmailVerificationCode, User
from mk.serializers import UserRegistrationSerializer

def test_timezone_fix():
    """测试时区修复"""
    print("=== 测试时区修复 ===")
    
    # 创建测试验证码
    email = "test@example.com"
    code = "123456"
    
    # 使用timezone-aware datetime
    now = timezone.now()
    expires_at = now + timedelta(minutes=5)
    
    verification = EmailVerificationCode.objects.create(
        email=email,
        code=code,
        created_at=now,
        expires_at=expires_at
    )
    
    print(f"创建验证码: {verification.id}")
    print(f"创建时间: {verification.created_at}")
    print(f"过期时间: {verification.expires_at}")
    print(f"是否过期: {verification.is_expired()}")
    
    # 清理测试数据
    verification.delete()
    print("时区修复测试完成\n")

def test_verification_code_validation():
    """测试验证码验证逻辑"""
    print("=== 测试验证码验证逻辑 ===")
    
    # 创建测试验证码
    email = "test@example.com"
    code = "123456"
    
    now = timezone.now()
    expires_at = now + timedelta(minutes=5)
    
    verification = EmailVerificationCode.objects.create(
        email=email,
        code=code,
        created_at=now,
        expires_at=expires_at
    )
    
    # 测试序列化器验证
    test_data = {
        'username': 'testuser',
        'phone': '13800138000',
        'email': email,
        'password': 'testpassword123',
        'confirm_password': 'testpassword123',
        'email_verification_code': code,
        'role': 'staff'
    }
    
    serializer = UserRegistrationSerializer(data=test_data)
    is_valid = serializer.is_valid()
    
    print(f"序列化器验证结果: {is_valid}")
    if not is_valid:
        print(f"验证错误: {serializer.errors}")
    
    # 清理测试数据
    verification.delete()
    print("验证码验证测试完成\n")

def test_user_creation():
    """测试用户创建"""
    print("=== 测试用户创建 ===")
    
    # 创建测试验证码
    email = "test@example.com"
    code = "123456"
    
    now = timezone.now()
    expires_at = now + timedelta(minutes=5)
    
    verification = EmailVerificationCode.objects.create(
        email=email,
        code=code,
        created_at=now,
        expires_at=expires_at
    )
    
    # 测试数据
    test_data = {
        'username': 'testuser',
        'phone': '13800138000',
        'email': email,
        'password': 'testpassword123',
        'confirm_password': 'testpassword123',
        'email_verification_code': code,
        'role': 'staff'
    }
    
    serializer = UserRegistrationSerializer(data=test_data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            print(f"用户创建成功: {user.username}")
            print(f"用户ID: {user.id}")
            print(f"邮箱验证状态: {user.is_email_verified}")
            
            # 清理测试用户
            user.delete()
            print("测试用户已删除")
        except Exception as e:
            print(f"用户创建失败: {e}")
    else:
        print(f"数据验证失败: {serializer.errors}")
    
    # 清理测试验证码
    verification.delete()
    print("用户创建测试完成\n")

if __name__ == "__main__":
    print("开始测试认证系统修复...\n")
    
    try:
        test_timezone_fix()
        test_verification_code_validation()
        test_user_creation()
        print("所有测试完成！")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
