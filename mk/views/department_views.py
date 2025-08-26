from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from ..models.Department import Department
from ..models.User import User
from ..serializers.department_serializers import (
    DepartmentSerializer, DepartmentCreateSerializer, 
    DepartmentUpdateSerializer, DepartmentAdminChangeSerializer
)
from ..permissions.department_permissions import CanManageDepartment, CanInviteAdmin

class DepartmentViewSet(viewsets.ModelViewSet):
    """部门管理视图集"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, CanManageDepartment]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DepartmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DepartmentUpdateSerializer
        return DepartmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Department.objects.all()
        elif user.role == 'department_manager':
            return Department.objects.filter(id=user.department.id)
        else:
            return Department.objects.none()
    
    @action(detail=True, methods=['post'])
    def change_admin(self, request, pk=None):
        """更换部门管理员"""
        department = self.get_object()
        if not request.user.can_manage_department(department):
            return Response({'error': '没有权限管理该部门'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = DepartmentAdminChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_admin_email = serializer.validated_data['new_admin_email']
        new_admin = User.objects.filter(email=new_admin_email).first()
        
        if not new_admin:
            return Response({'error': '该邮箱未注册用户'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查新管理员是否属于该部门
        if new_admin.department != department:
            return Response({'error': '新管理员必须属于该部门'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 原管理员降级为普通员工
        old_admin = department.admin
        if old_admin and old_admin != new_admin:
            old_admin.role = 'staff'
            old_admin.save()
        
        # 新管理员升级为部门管理员
        new_admin.role = 'department_manager'
        new_admin.save()
        
        # 更新部门管理员
        department.admin = new_admin
        department.save()
        
        # 发送邮件通知
        try:
            # 通知新管理员
            send_mail(
                '部门管理员任命通知',
                f'您已被任命为 {department.name} 的部门管理员。',
                settings.DEFAULT_FROM_EMAIL,
                [new_admin.email],
                fail_silently=True,
            )
            
            # 通知原管理员
            if old_admin and old_admin != new_admin:
                send_mail(
                    '部门管理员变更通知',
                    f'您不再是 {department.name} 的部门管理员，已降级为普通员工。',
                    settings.DEFAULT_FROM_EMAIL,
                    [old_admin.email],
                    fail_silently=True,
                )
        except Exception as e:
            print(f"发送邮件失败: {e}")
        
        return Response({'message': '部门管理员更换成功'})
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """获取部门下的用户列表"""
        department = self.get_object()
        users = User.objects.filter(department=department)
        from ..views.User import UserSerializer
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """获取部门统计信息"""
        department = self.get_object()
        total_users = User.objects.filter(department=department).count()
        pending_users = User.objects.filter(department=department, status='pending').count()
        approved_users = User.objects.filter(department=department, status='approved').count()
        
        return Response({
            'total_users': total_users,
            'pending_users': pending_users,
            'approved_users': approved_users
        })
