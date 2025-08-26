from rest_framework import status, generics, permissions, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
import random
import string
import uuid
from django.db.models import Q

from ..models import User, EmailVerificationCode, PasswordResetToken
from ..models.Department import Department
from ..models.store_management import Store
from ..permissions import (
    IsSuperAdmin,
    IsDepartmentManager,
    IsStoreOperator,
    CanManageUser,
    CanManageDepartment,
    CanManageStore,
    UserManagementPermission
)

# 序列化器类
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at']

class StoreSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'phone', 'department', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    approved_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'role', 'status', 
            'department', 'store', 'approved_by', 'approval_date', 
            'rejection_reason', 'created_at', 'is_email_verified'
        ]
        read_only_fields = ['approved_by', 'approval_date', 'rejection_reason', 'created_at']
    
    def to_representation(self, instance):
        """自定义序列化输出"""
        data = super().to_representation(instance)
        
        # 确保状态字段有正确的值
        if not data.get('status'):
            data['status'] = getattr(instance, 'status', 'pending')
        
        # 确保角色字段有正确的值
        if not data.get('role'):
            data['role'] = getattr(instance, 'role', 'staff')
        
        # 格式化时间字段
        if data.get('created_at'):
            data['created_at'] = instance.created_at.isoformat()
        
        if data.get('approval_date') and instance.approval_date:
            data['approval_date'] = instance.approval_date.isoformat()
        
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'confirm_password', 'role', 'department']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("密码和确认密码不匹配")
        
        # 检查超级管理员数量限制
        if attrs['role'] == 'super_admin':
            existing_super_admin = User.objects.filter(role='super_admin', status='approved').exists()
            if existing_super_admin:
                raise serializers.ValidationError("超级管理员已存在，需要审批")
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.create_user(**validated_data)
        return user

class UserApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['status', 'rejection_reason']
    
    def validate(self, attrs):
        if attrs['status'] == 'rejected' and not attrs.get('rejection_reason'):
            raise serializers.ValidationError("拒绝时必须提供拒绝原因")
        return attrs

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'department', 'store']
        read_only_fields = ['role', 'status']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("新密码和确认密码不匹配")
        return attrs

# 导入序列化器
from ..serializers.User import (
    UserLoginSerializer,
    SendEmailVerificationCodeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

class UserProfileSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role', 'department', 'store', 'created_at']
        read_only_fields = ['id', 'role', 'created_at']

class UserListSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role', 'status', 'department', 'store', 'created_at']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'role', 'department', 'store']
        read_only_fields = ['id', 'created_at']


class UserRegistrationView(generics.CreateAPIView):
    """用户注册视图"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        print(f"=== 注册请求调试信息 ===")
        print(f"请求数据: {request.data}")
        print(f"请求方法: {request.method}")
        print(f"请求头: {dict(request.headers)}")
        
        serializer = self.get_serializer(data=request.data)
        
        # 详细验证
        if not serializer.is_valid():
            print(f"序列化器验证失败: {serializer.errors}")
            # 返回详细的错误信息
            error_details = {}
            for field, errors in serializer.errors.items():
                if isinstance(errors, list):
                    error_details[field] = errors[0] if errors else "验证失败"
                else:
                    error_details[field] = str(errors)
            
            return Response({
                'success': False,
                'error': '数据验证失败',
                'details': error_details,
                'message': '请检查输入信息'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print("序列化器验证成功")
        
        try:
            user = serializer.save()
            print(f"用户创建成功: {user.username}")
            
            return Response({
                'success': True,
                'message': '注册成功！请登录',
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"用户创建失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return Response({
                'success': False,
                'error': '用户创建失败',
                'details': str(e),
                'message': '注册失败，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    """用户登录视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': '数据验证失败',
                'details': serializer.errors,
                'message': '请检查用户名和密码'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        login(request, user)

        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)

        return Response({
            'success': True,
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
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': '数据验证失败',
                'details': serializer.errors,
                'message': '请检查邮箱格式'
            }, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']

        # 生成6位随机验证码
        code = ''.join(random.choices(string.digits, k=6))

        # 使用timezone-aware datetime
        now = timezone.now()
        expires_at = now + timedelta(minutes=5)

        # 创建验证码记录
        EmailVerificationCode.objects.create(
            email=email,
            code=code,
            created_at=now,
            expires_at=expires_at
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
                'success': True,
                'message': '验证码已发送到您的邮箱',
                'email': email
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # 如果发送失败，删除验证码记录
            EmailVerificationCode.objects.filter(email=email, code=code).delete()
            return Response({
                'success': False,
                'error': '邮件发送失败',
                'details': str(e),
                'message': '邮件发送失败，请稍后重试'
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

        # 使用timezone-aware datetime
        now = timezone.now()
        expires_at = now + timedelta(hours=1)

        # 创建重置令牌记录
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            created_at=now,
            expires_at=expires_at
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
                'message': '重置密码邮件已发送到您的邮箱',
                'email': email
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # 如果发送失败，删除重置令牌记录
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

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            # 查找并验证重置令牌
            reset_token = PasswordResetToken.objects.get(
                token=token,
                expires_at__gt=timezone.now()  # 使用timezone-aware比较
            )

            # 更新用户密码
            user = reset_token.user
            user.set_password(new_password)
            user.save()

            # 删除重置令牌
            reset_token.delete()

            return Response({
                'message': '密码重置成功'
            }, status=status.HTTP_200_OK)

        except PasswordResetToken.DoesNotExist:
            return Response({
                'error': '重置令牌无效或已过期'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """用户资料视图"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class CheckEmailVerificationView(APIView):
    """检查邮箱验证视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({
                'error': '请提供邮箱和验证码'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 查找验证码记录，使用timezone-aware比较
            verification = EmailVerificationCode.objects.get(
                email=email,
                code=code,
                expires_at__gt=timezone.now()  # 使用expires_at字段
            )

            # 验证成功后删除验证码
            verification.delete()

            return Response({
                'message': '邮箱验证成功',
                'email': email
            }, status=status.HTTP_200_OK)

        except EmailVerificationCode.DoesNotExist:
            return Response({
                'error': '验证码无效或已过期'
            }, status=status.HTTP_400_BAD_REQUEST)


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

        if not old_password or not new_password:
            return Response({
                'error': '请提供旧密码和新密码'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        # 验证旧密码
        if not user.check_password(old_password):
            return Response({
                'error': '旧密码不正确'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 更新密码
        user.set_password(new_password)
        user.save()

        return Response({
            'message': '密码修改成功'
        }, status=status.HTTP_200_OK)


class TokenRefreshView(APIView):
    """JWT令牌刷新视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'error': '请提供refresh token'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 验证refresh token
            refresh = RefreshToken(refresh_token)
            
            # 生成新的access token
            new_access_token = str(refresh.access_token)
            
            return Response({
                'access': new_access_token
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'refresh token无效或已过期'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserManagementView(generics.ListCreateAPIView):
    """用户管理视图 - 列表和创建"""
    serializer_class = UserSerializer
    permission_classes = [UserManagementPermission]
    pagination_class = None  # 暂时禁用分页，直接返回所有数据
    
    def get_queryset(self):
        user = self.request.user
        print(f"=== 用户管理视图调试 ===")
        print(f"当前用户: {user.username}, 角色: {getattr(user, 'role', 'unknown')}")
        print(f"用户ID: {user.id}")
        print(f"是否为超级用户: {user.is_superuser}")
        print(f"是否为员工: {getattr(user, 'is_staff', False)}")
        
        # 根据用户角色返回不同的查询集
        if hasattr(user, 'role') and user.role == 'super_admin':
            # 超级管理员可以看到所有用户
            queryset = User.objects.all()
            print("超级管理员权限：可以看到所有用户")
        elif hasattr(user, 'role') and user.role == 'department_manager':
            # 部门部长只能看到自己部门的用户
            if hasattr(user, 'department') and user.department:
                queryset = User.objects.filter(department=user.department)
                print(f"部门部长权限：只能看到部门 {user.department.name} 的用户")
            else:
                queryset = User.objects.none()
                print("部门部长权限：没有分配部门，无法查看用户")
        elif hasattr(user, 'role') and user.role == 'store_operator':
            # 店铺运营只能看到自己店铺的用户
            if hasattr(user, 'store') and user.store:
                queryset = User.objects.filter(store=user.store)
                print(f"店铺运营权限：只能看到店铺 {user.store.name} 的用户")
            else:
                queryset = User.objects.none()
                print("店铺运营权限：没有分配店铺，无法查看用户")
        else:
            # 普通员工只能看到自己
            queryset = User.objects.filter(id=user.id)
            print("普通员工权限：只能看到自己")
        
        # 应用搜索过滤
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
            print(f"应用搜索过滤: {search}")
        
        # 应用角色过滤
        role = self.request.query_params.get('role', '')
        if role:
            queryset = queryset.filter(role=role)
            print(f"应用角色过滤: {role}")
        
        # 应用部门过滤
        department = self.request.query_params.get('department', '')
        if department:
            queryset = queryset.filter(department_id=department)
            print(f"应用部门过滤: {department}")
        
        # 应用状态过滤
        status = self.request.query_params.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
            print(f"应用状态过滤: {status}")
        
        # 按创建时间倒序排列
        queryset = queryset.order_by('-created_at')
        
        print(f"最终查询集数量: {queryset.count()}")
        return queryset
    
    def list(self, request, *args, **kwargs):
        """重写list方法，返回标准格式的响应"""
        try:
            print(f"=== 用户列表请求 ===")
            print(f"请求用户: {request.user.username}")
            print(f"请求参数: {request.query_params}")
            
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            
            response_data = {
                'success': True,
                'results': serializer.data,
                'count': queryset.count(),
                'message': '用户列表获取成功'
            }
            
            print(f"返回数据: 成功={response_data['success']}, 用户数={response_data['count']}")
            return Response(response_data)
            
        except Exception as e:
            print(f"用户列表获取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return Response({
                'success': False,
                'error': '获取用户列表失败',
                'details': str(e),
                'message': '服务器内部错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """创建新用户"""
        print(f"=== 创建用户请求 ===")
        print(f"请求用户: {request.user.username}")
        print(f"请求数据: {request.data}")
        
        # 检查权限
        if not hasattr(request.user, 'can_manage_user') or not request.user.can_manage_user(None):
            print("权限检查失败：没有权限创建用户")
            return Response({
                'success': False,
                'error': '您没有权限创建用户',
                'message': '权限不足'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"数据验证失败: {serializer.errors}")
            return Response({
                'success': False,
                'error': '数据验证失败',
                'details': serializer.errors,
                'message': '请检查输入信息'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = serializer.save()
            print(f"用户创建成功: {user.username}")
            return Response({
                'success': True,
                'message': '用户创建成功',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"用户创建失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return Response({
                'success': False,
                'error': '用户创建失败',
                'details': str(e),
                'message': '创建失败，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDetailManagementView(generics.RetrieveUpdateDestroyAPIView):
    """用户详情管理视图 - 查看、更新、删除"""
    serializer_class = UserUpdateSerializer
    permission_classes = [UserManagementPermission]
    
    def get_queryset(self):
        user = self.request.user
        
        if hasattr(user, 'role') and user.role == 'super_admin':
            return User.objects.all()
        elif hasattr(user, 'role') and user.role == 'department_manager':
            return User.objects.filter(department=user.department)
        elif hasattr(user, 'role') and user.role == 'store_operator':
            return User.objects.filter(store=user.store)
        else:
            return User.objects.filter(id=user.id)
    
    def retrieve(self, request, *args, **kwargs):
        """获取用户详情"""
        user = self.get_object()
        serializer = UserSerializer(user)
        return Response({
            'success': True,
            'user': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """更新用户信息"""
        user = self.get_object()
        
        # 检查权限
        if not hasattr(request.user, 'can_manage_user') or not request.user.can_manage_user(user):
            return Response({
                'success': False,
                'error': '您没有权限更新此用户'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': '数据验证失败',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            updated_user = serializer.save()
            return Response({
                'success': True,
                'message': '用户信息更新成功',
                'user': UserSerializer(updated_user).data
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': '用户信息更新失败',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, *args, **kwargs):
        """部分更新用户信息（用于状态更新等）"""
        user = self.get_object()
        
        # 检查权限
        if not hasattr(request.user, 'can_manage_user') or not request.user.can_manage_user(user):
            return Response({
                'success': False,
                'error': '您没有权限更新此用户'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 如果是状态更新，使用UserSerializer
        if 'status' in request.data:
            serializer = UserSerializer(user, data=request.data, partial=True)
        else:
            serializer = self.get_serializer(user, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': '数据验证失败',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            updated_user = serializer.save()
            return Response({
                'success': True,
                'message': '用户信息更新成功',
                'user': UserSerializer(updated_user).data
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': '用户信息更新失败',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """删除用户"""
        user = self.get_object()
        
        # 检查权限
        if not hasattr(request.user, 'can_manage_user') or not request.user.can_manage_user(user):
            return Response({
                'success': False,
                'error': '您没有权限删除此用户'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 不能删除自己
        if user == request.user:
            return Response({
                'success': False,
                'error': '不能删除自己的账户'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 不能删除超级管理员（除非是另一个超级管理员）
        if hasattr(user, 'role') and user.role == 'super_admin' and (not hasattr(request.user, 'role') or request.user.role != 'super_admin'):
            return Response({
                'success': False,
                'error': '只有超级管理员才能删除超级管理员账户'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            username = user.username
            user.delete()
            return Response({
                'success': True,
                'message': f'用户 {username} 删除成功'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': '用户删除失败',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserBulkActionView(APIView):
    """用户批量操作视图"""
    permission_classes = [UserManagementPermission]
    
    def post(self, request):
        """批量操作用户"""
        action = request.data.get('action')
        user_ids = request.data.get('user_ids', [])
        
        if not action or not user_ids:
            return Response({
                'success': False,
                'error': '请提供操作类型和用户ID列表'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取用户列表
        user = request.user
        if hasattr(user, 'role') and user.role == 'super_admin':
            users = User.objects.filter(id__in=user_ids)
        elif hasattr(user, 'role') and user.role == 'department_manager':
            users = User.objects.filter(id__in=user_ids, department=user.department)
        elif hasattr(user, 'role') and user.role == 'store_operator':
            users = User.objects.filter(id__in=user_ids, store=user.store)
        else:
            return Response({
                'success': False,
                'error': '您没有权限进行批量操作'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not users.exists():
            return Response({
                'success': False,
                'error': '没有找到符合条件的用户'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success_count = 0
        failed_count = 0
        errors = []
        
        for user_obj in users:
            try:
                if action == 'activate':
                    if user_obj.status != 'active':
                        user_obj.status = 'active'
                        user_obj.save()
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f'用户 {user_obj.username} 已经是激活状态')
                
                elif action == 'deactivate':
                    if user_obj.status != 'inactive':
                        user_obj.status = 'inactive'
                        user_obj.save()
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f'用户 {user_obj.username} 已经是禁用状态')
                
                elif action == 'approve':
                    if user_obj.status == 'pending':
                        user_obj.status = 'approved'
                        user_obj.approved_by = request.user
                        user_obj.approval_date = timezone.now()
                        user_obj.save()
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f'用户 {user_obj.username} 不需要审批')
                
                elif action == 'reject':
                    reason = request.data.get('reason', '审批被拒绝')
                    if user_obj.status == 'pending':
                        user_obj.status = 'rejected'
                        user_obj.rejection_reason = reason
                        user_obj.save()
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f'用户 {user_obj.username} 不需要审批')
                
                else:
                    return Response({
                        'success': False,
                        'error': f'不支持的操作类型: {action}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                failed_count += 1
                errors.append(f'用户 {user_obj.username} 操作失败: {str(e)}')
        
        return Response({
            'success': True,
            'message': f'批量操作完成，成功: {success_count}，失败: {failed_count}',
            'success_count': success_count,
            'failed_count': failed_count,
            'errors': errors
        })


class UserStatisticsView(APIView):
    """用户统计视图"""
    permission_classes = [UserManagementPermission]
    
    def get(self, request):
        """获取用户统计信息"""
        try:
            print(f"=== 用户统计请求 ===")
            print(f"请求用户: {request.user.username}")
            print(f"用户角色: {getattr(request.user, 'role', 'unknown')}")
            
            user = request.user
            
            if hasattr(user, 'role') and user.role == 'super_admin':
                # 超级管理员可以看到所有统计
                print("超级管理员权限：查看所有统计")
                total_users = User.objects.count()
                active_users = User.objects.filter(status='active').count()
                pending_users = User.objects.filter(status='pending').count()
                inactive_users = User.objects.filter(status='inactive').count()
                rejected_users = User.objects.filter(status='rejected').count()
                
                role_stats = {
                    'super_admin': User.objects.filter(role='super_admin').count(),
                    'department_manager': User.objects.filter(role='department_manager').count(),
                    'store_operator': User.objects.filter(role='store_operator').count(),
                    'staff': User.objects.filter(role='staff').count()
                }
                
            elif hasattr(user, 'role') and user.role == 'department_manager':
                # 部门部长只能看到自己部门的统计
                print(f"部门部长权限：查看部门 {getattr(user, 'department', 'None')} 的统计")
                if hasattr(user, 'department') and user.department:
                    dept_users = User.objects.filter(department=user.department)
                    total_users = dept_users.count()
                    active_users = dept_users.filter(status='active').count()
                    pending_users = dept_users.filter(status='pending').count()
                    inactive_users = dept_users.filter(status='inactive').count()
                    rejected_users = dept_users.filter(status='rejected').count()
                    
                    role_stats = {
                        'department_manager': dept_users.filter(role='department_manager').count(),
                        'store_operator': dept_users.filter(role='store_operator').count(),
                        'staff': dept_users.filter(role='staff').count()
                    }
                else:
                    print("部门部长没有分配部门，返回空统计")
                    total_users = active_users = pending_users = inactive_users = rejected_users = 0
                    role_stats = {}
                
            elif hasattr(user, 'role') and user.role == 'store_operator':
                # 店铺运营只能看到自己店铺的统计
                print(f"店铺运营权限：查看店铺 {getattr(user, 'store', 'None')} 的统计")
                if hasattr(user, 'store') and user.store:
                    store_users = User.objects.filter(store=user.store)
                    total_users = store_users.count()
                    active_users = store_users.filter(status='active').count()
                    pending_users = store_users.filter(status='pending').count()
                    inactive_users = store_users.filter(status='inactive').count()
                    rejected_users = store_users.filter(status='rejected').count()
                    
                    role_stats = {
                        'store_operator': store_users.filter(role='store_operator').count(),
                        'staff': store_users.filter(role='staff').count()
                    }
                else:
                    print("店铺运营没有分配店铺，返回空统计")
                    total_users = active_users = pending_users = inactive_users = rejected_users = 0
                    role_stats = {}
                
            else:
                # 普通员工只能看到自己的信息
                print("普通员工权限：只能查看自己的统计")
                return Response({
                    'success': True,
                    'statistics': {
                        'total_users': 1,
                        'active_users': 1 if hasattr(user, 'status') and user.status == 'active' else 0,
                        'pending_users': 1 if hasattr(user, 'status') and user.status == 'pending' else 0,
                        'inactive_users': 1 if hasattr(user, 'status') and user.status == 'inactive' else 0,
                        'rejected_users': 1 if hasattr(user, 'status') and user.status == 'rejected' else 0,
                        'role_stats': {user.role: 1} if hasattr(user, 'role') else {}
                    }
                })
            
            statistics_data = {
                'total_users': total_users,
                'active_users': active_users,
                'pending_users': pending_users,
                'inactive_users': inactive_users,
                'rejected_users': rejected_users,
                'role_stats': role_stats
            }
            
            print(f"统计结果: {statistics_data}")
            
            return Response({
                'success': True,
                'statistics': statistics_data,
                'message': '统计信息获取成功'
            })
            
        except Exception as e:
            print(f"获取用户统计失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return Response({
                'success': False,
                'error': '获取统计信息失败',
                'details': str(e),
                'message': '服务器内部错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserApprovalManagementView(APIView):
    """用户审批管理视图"""
    permission_classes = [UserManagementPermission]
    
    def get(self, request):
        """获取待审批用户列表"""
        user = request.user
        
        if hasattr(user, 'role') and user.role == 'super_admin':
            pending_users = User.objects.filter(status='pending')
        elif hasattr(user, 'role') and user.role == 'department_manager':
            pending_users = User.objects.filter(status='pending', department=user.department)
        else:
            return Response({
                'success': False,
                'error': '您没有权限查看待审批用户'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(pending_users, many=True)
        return Response({
            'success': True,
            'pending_users': serializer.data,
            'count': pending_users.count()
        })
    
    def post(self, request):
        """审批用户"""
        user_id = request.data.get('user_id')
        action = request.data.get('action')  # 'approve' 或 'reject'
        reason = request.data.get('reason', '')
        
        if not user_id or not action:
            return Response({
                'success': False,
                'error': '请提供用户ID和操作类型'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_obj = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 检查权限
        if not request.user.can_manage_user(user_obj):
            return Response({
                'success': False,
                'error': '您没有权限审批此用户'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if action == 'approve':
            user_obj.status = 'approved'
            user_obj.approved_by = request.user
            user_obj.approval_date = timezone.now()
            user_obj.save()
            
            # 发送审批通过邮件
            try:
                send_mail(
                    '账号审批通过',
                    f'您的账号 {user_obj.username} 已通过审批，可以正常登录使用。',
                    settings.DEFAULT_FROM_EMAIL,
                    [user_obj.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"发送邮件失败: {e}")
            
            return Response({
                'success': True,
                'message': '用户审批通过'
            })
            
        elif action == 'reject':
            if not reason:
                return Response({
                    'success': False,
                    'error': '拒绝时必须提供原因'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user_obj.status = 'rejected'
            user_obj.rejection_reason = reason
            user_obj.save()
            
            # 发送拒绝邮件
            try:
                send_mail(
                    '账号审批被拒绝',
                    f'您的账号 {user_obj.username} 审批被拒绝，原因：{reason}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user_obj.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"发送邮件失败: {e}")
            
            return Response({
                'success': True,
                'message': '用户审批拒绝'
            })
        
        else:
            return Response({
                'success': False,
                'error': '不支持的操作类型'
            }, status=status.HTTP_400_BAD_REQUEST)
