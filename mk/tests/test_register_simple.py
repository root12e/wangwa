#!/usr/bin/env python
"""
简化的注册测试脚本
"""

import os
import sys
import django
from datetime import timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wwkc.settings')
django.setup()

from django.utils import timezone
from mk.models import EmailVerificationCode, User, Department, Store
from mk.serializers.User import UserRegistrationSerializer

def test_simple_registration():
    """测试简单注册流程"""
    print("=== 测试简单注册流程 ===")
    
    # 1. 创建测试部门
    try:
        dept = Department.objects.create(
            name="测试部门",
            description="用于测试的部门"
        )
        print(f"创建测试部门: {dept.name}")
    except Exception as e:
        print(f"创建部门失败: {e}")
        return
    
    # 2. 创建测试店铺
    try:
        store = Store.objects.create(
            name="测试店铺",
            address="测试地址",
            phone="13800138000",
            department=dept
        )
        print(f"创建测试店铺: {store.name}")
    except Exception as e:
        print(f"创建店铺失败: {e}")
        return
    
    # 3. 创建验证码
    try:
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
        print(f"创建验证码: {verification.id}")
    except Exception as e:
        print(f"创建验证码失败: {e}")
        return
    
    # 4. 测试注册数据
    test_data = {
        'username': 'testuser',
        'phone': '13800138001',
        'email': email,
        'password': 'testpassword123',
        'confirm_password': 'testpassword123',
        'email_verification_code': code,
        'role': 'staff',
        'department': dept.id,
        'store': store.id
    }
    
    print(f"测试数据: {test_data}")
    
    # 5. 验证序列化器
    serializer = UserRegistrationSerializer(data=test_data)
    print(f"序列化器验证结果: {serializer.is_valid()}")
    
    if not serializer.is_valid():
        print(f"验证错误详情:")
        for field, errors in serializer.errors.items():
            print(f"  {field}: {errors}")
        return
    
    # 6. 创建用户
    try:
        user = serializer.save()
        print(f"用户创建成功: {user.username}")
        print(f"用户ID: {user.id}")
        print(f"邮箱验证状态: {user.is_email_verified}")
        print(f"用户角色: {user.role}")
        print(f"所属部门: {user.department.name if user.department else '无'}")
        print(f"所属店铺: {user.store.name if user.store else '无'}")
        
        # 清理测试用户
        user.delete()
        print("测试用户已删除")
        
    except Exception as e:
        print(f"用户创建失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. 清理测试数据
    try:
        verification.delete()
        store.delete()
        dept.delete()
        print("测试数据已清理")
    except Exception as e:
        print(f"清理测试数据失败: {e}")
    
    print("简单注册测试完成\n")

if __name__ == "__main__":
    print("开始测试简单注册流程...\n")
    
    try:
        test_simple_registration()
        print("所有测试完成！")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
