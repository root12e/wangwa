from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from ..models.User import User
from ..views.User import (
    UserSerializer, UserRegistrationSerializer, UserApprovalSerializer,
    UserProfileUpdateSerializer, ChangePasswordSerializer
)
from ..permissions.user_permissions import CanManageUser, CanApproveUser

class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, CanManageUser]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return User.objects.all()
        elif user.role == 'department_manager':
            return User.objects.filter(department=user.department)
        else:
            return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """获取待审批用户列表"""
        user = request.user
        if user.role == 'super_admin':
            queryset = User.objects.filter(status='pending')
        elif user.role == 'department_manager':
            queryset = User.objects.filter(status='pending', department=user.department)
        else:
            queryset = User.objects.none()
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
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
    
    @action(detail=False, methods=['get'])
    def check_super_admin(self, request):
        """检查是否已存在超级管理员"""
        exists = User.objects.filter(role='super_admin', status='approved').exists()
        return Response({'exists': exists})

class UserRegistrationView(generics.CreateAPIView):
    """用户注册视图"""
    serializer_class = UserRegistrationSerializer
    permission_classes = []
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 如果是第一个超级管理员，自动审批通过
        if user.role == 'super_admin' and user.status == 'approved':
            message = '注册成功，超级管理员账号已激活'
        else:
            message = '注册成功，等待审批'
        
        return Response({
            'message': message,
            'user_id': user.id,
            'status': user.status
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """用户资料视图"""
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    """修改密码视图"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 验证旧密码
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': '旧密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 设置新密码
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': '密码修改成功'})
