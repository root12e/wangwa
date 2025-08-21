from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import random
import string
import uuid

from ..models import User, EmailVerificationCode, PasswordResetToken, Department, Store
from ..serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    SendEmailVerificationCodeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserProfileSerializer,
    UserListSerializer,
    UserUpdateSerializer,
    DepartmentSerializer,
    StoreSerializer
)
from ..permissions import (
    IsSuperAdmin,
    IsDepartmentManager,
    IsStoreOperator,
    CanManageUser,
    CanManageDepartment,
    CanManageStore,
    UserManagementPermission
)


class UserRegistrationView(generics.CreateAPIView):
    """用户注册视图"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'message': '注册成功！请登录',
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """用户登录视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)

        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': '登录成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'role_display': user.get_role_display(),
                'department': DepartmentSerializer(user.department).data if user.department else None,
                'store': StoreSerializer(user.store).data if user.store else None
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    """用户登出视图"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({
            'message': '登出成功'
        }, status=status.HTTP_200_OK)


class SendEmailVerificationCodeView(APIView):
    """发送邮箱验证码视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SendEmailVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        # 生成6位随机验证码
        code = ''.join(random.choices(string.digits, k=6))

        # 创建验证码记录
        EmailVerificationCode.objects.create(
            email=email,
            code=code
        )

        # 发送邮件
        try:
            subject = 'WWKC库存管理系统 - 邮箱验证码'
            message = f'''
            您好！
            
            您的邮箱验证码是：{code}
            
            验证码有效期为5分钟，请尽快使用。
            
            如果这不是您的操作，请忽略此邮件。
            
            WWKC库存管理系统
            '''

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return Response({
                'message': '验证码已发送到您的邮箱',
                'email': email
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # 如果发送失败，删除验证码记录
            EmailVerificationCode.objects.filter(email=email, code=code).delete()
            return Response({
                'error': '邮件发送失败，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetRequestView(APIView):
    """密码重置请求视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        # 生成重置令牌
        token = str(uuid.uuid4())

        # 创建重置令牌记录
        PasswordResetToken.objects.create(
            user=user,
            token=token
        )

        # 发送重置邮件
        try:
            reset_url = f"{request.scheme}://{request.get_host()}/reset-password?token={token}"

            subject = 'WWKC库存管理系统 - 密码重置'
            message = f'''
            您好！
            
            您请求重置密码，请点击以下链接重置密码：
            {reset_url}
            
            此链接有效期为1小时，请尽快使用。
            
            如果这不是您的操作，请忽略此邮件。
            
            WWKC库存管理系统
            '''

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return Response({
                'message': '密码重置链接已发送到您的邮箱',
                'email': email
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # 如果发送失败，删除令牌记录
            PasswordResetToken.objects.filter(user=user, token=token).delete()
            return Response({
                'error': '邮件发送失败，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(APIView):
    """密码重置确认视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_token = serializer.validated_data['reset_token']
        new_password = serializer.validated_data['new_password']

        # 更新用户密码
        user = reset_token.user
        user.set_password(new_password)
        user.save()

        # 标记令牌为已使用
        reset_token.is_used = True
        reset_token.save()

        return Response({
            'message': '密码重置成功，请使用新密码登录'
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """用户资料视图"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CheckEmailVerificationView(APIView):
    """检查邮箱验证状态视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'error': '请提供邮箱地址'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            return Response({
                'is_verified': user.is_email_verified
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'error': '该邮箱未注册'
            }, status=status.HTTP_404_NOT_FOUND)


class UserListView(generics.ListAPIView):
    """用户列表视图"""
    serializer_class = UserListSerializer
    permission_classes = [UserManagementPermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_super_admin:
            # 超级管理员可以看到所有用户
            return User.objects.all()
        elif user.is_department_manager:
            # 部门部长只能看到自己部门的用户
            return User.objects.filter(department=user.department)
        elif user.is_store_operator:
            # 店铺运营只能看到自己店铺的用户
            return User.objects.filter(store=user.store)
        else:
            # 普通员工只能看到自己
            return User.objects.filter(id=user.id)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """用户详情视图"""
    serializer_class = UserUpdateSerializer
    permission_classes = [UserManagementPermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_super_admin:
            return User.objects.all()
        elif user.is_department_manager:
            return User.objects.filter(department=user.department)
        elif user.is_store_operator:
            return User.objects.filter(store=user.store)
        else:
            return User.objects.filter(id=user.id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        # 检查删除权限
        if not request.user.can_manage_user(user):
            return Response({
                'error': '您没有权限删除此用户'
            }, status=status.HTTP_403_FORBIDDEN)

        # 不能删除自己
        if user == request.user:
            return Response({
                'error': '不能删除自己的账户'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response({
            'message': '用户删除成功'
        }, status=status.HTTP_204_NO_CONTENT)


class DepartmentListView(generics.ListCreateAPIView):
    """部门列表视图"""
    serializer_class = DepartmentSerializer
    permission_classes = [IsSuperAdmin | IsDepartmentManager]

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return Department.objects.all()
        else:
            return Department.objects.filter(id=user.department.id)


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """部门详情视图"""
    serializer_class = DepartmentSerializer
    permission_classes = [CanManageDepartment]

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return Department.objects.all()
        else:
            return Department.objects.filter(id=user.department.id)


class StoreListView(generics.ListCreateAPIView):
    """店铺列表视图"""
    serializer_class = StoreSerializer
    permission_classes = [IsSuperAdmin | IsDepartmentManager | IsStoreOperator]

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return Store.objects.all()
        elif user.is_department_manager:
            return Store.objects.filter(department=user.department)
        else:
            return Store.objects.filter(id=user.store.id)


class StoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    """店铺详情视图"""
    serializer_class = StoreSerializer
    permission_classes = [CanManageStore]

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin:
            return Store.objects.all()
        elif user.is_department_manager:
            return Store.objects.filter(department=user.department)
        else:
            return Store.objects.filter(id=user.store.id)


class ChangePasswordView(APIView):
    """修改密码视图"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not all([old_password, new_password, confirm_password]):
            return Response({
                'error': '请提供所有必需的字段'
            }, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({
                'error': '两次输入的新密码不一致'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(old_password):
            return Response({
                'error': '原密码错误'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证新密码强度
        try:
            from django.contrib.auth.password_validation import validate_password
            validate_password(new_password)
        except Exception as e:
            return Response({
                'error': f'新密码不符合要求: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({
            'message': '密码修改成功，请重新登录'
        }, status=status.HTTP_200_OK)
