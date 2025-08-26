from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from ..models.User import AdminInvitation, User
from ..models.Department import Department
from ..serializers.admin_invitation_serializers import (
    AdminInvitationSerializer, AdminInvitationCreateSerializer, AdminInvitationResponseSerializer
)
from ..permissions.department_permissions import CanInviteAdmin

class AdminInvitationViewSet(viewsets.ModelViewSet):
    """管理员邀请视图集"""
    queryset = AdminInvitation.objects.all()
    serializer_class = AdminInvitationSerializer
    permission_classes = [IsAuthenticated, CanInviteAdmin]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AdminInvitationCreateSerializer
        elif self.action in ['accept', 'reject']:
            return AdminInvitationResponseSerializer
        return AdminInvitationSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return AdminInvitation.objects.all()
        elif user.role == 'department_manager':
            return AdminInvitation.objects.filter(department=user.department)
        else:
            return AdminInvitation.objects.none()
    
    def perform_create(self, serializer):
        """创建邀请时设置邀请人"""
        invitation = serializer.save(inviter=self.request.user)
        
        # 发送邀请邮件
        try:
            invitation_url = f"{settings.FRONTEND_URL}/admin-invitation/{invitation.token}"
            send_mail(
                '管理员邀请',
                f'您被邀请成为管理员，请点击链接接受邀请：{invitation_url}',
                settings.DEFAULT_FROM_EMAIL,
                [invitation.invitee_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"发送邮件失败: {e}")
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """接受邀请"""
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response({'error': '邀请已处理'}, status=status.HTTP_400_BAD_REQUEST)
        
        if invitation.is_expired():
            invitation.status = 'expired'
            invitation.save()
            return Response({'error': '邀请已过期'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建新用户或更新现有用户
        user, created = User.objects.get_or_create(
            email=invitation.invitee_email,
            defaults={
                'username': invitation.invitee_email.split('@')[0],
                'role': invitation.role,
                'department': invitation.department,
                'status': 'approved'
            }
        )
        
        if not created:
            user.role = invitation.role
            user.department = invitation.department
            user.status = 'approved'
            user.save()
        
        # 更新部门管理员
        if invitation.department and invitation.role == 'department_manager':
            invitation.department.admin = user
            invitation.department.save()
            
            # 原管理员降级为普通员工
            old_admin = invitation.department.admin
            if old_admin and old_admin != user:
                old_admin.role = 'staff'
                old_admin.save()
        
        invitation.status = 'accepted'
        invitation.save()
        
        return Response({'message': '邀请已接受'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝邀请"""
        invitation = self.get_object()
        invitation.status = 'rejected'
        invitation.save()
        return Response({'message': '邀请已拒绝'})
    
    @action(detail=False, methods=['get'])
    def my_invitations(self, request):
        """获取我发送的邀请"""
        invitations = AdminInvitation.objects.filter(inviter=request.user)
        serializer = self.get_serializer(invitations, many=True)
        return Response(serializer.data)

class AdminInvitationByTokenView(generics.RetrieveAPIView):
    """通过令牌获取邀请详情"""
    queryset = AdminInvitation.objects.all()
    serializer_class = AdminInvitationSerializer
    permission_classes = []
    lookup_field = 'token'
    
    def get_object(self):
        token = self.kwargs.get('token')
        try:
            return AdminInvitation.objects.get(token=token)
        except AdminInvitation.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        invitation = self.get_object()
        if not invitation:
            return Response({'error': '邀请不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        if invitation.is_expired():
            invitation.status = 'expired'
            invitation.save()
            return Response({'error': '邀请已过期'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(invitation)
        return Response(serializer.data)
