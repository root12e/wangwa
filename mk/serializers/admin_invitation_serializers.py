from rest_framework import serializers

from ..models import AdminInvitation
from ..models.Department import Department


class AdminInvitationSerializer(serializers.ModelSerializer):
    inviter = serializers.StringRelatedField(read_only=True)
    department = serializers.StringRelatedField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AdminInvitation
        fields = [
            'id', 'inviter', 'invitee_email', 'role', 'role_display',
            'department', 'status', 'status_display', 'created_at', 'expires_at'
        ]
        read_only_fields = ['inviter', 'token', 'status', 'created_at', 'expires_at']


class AdminInvitationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminInvitation
        fields = ['invitee_email', 'role', 'department']

    def validate(self, attrs):
        # 检查邀请人是否有权限邀请该角色
        request = self.context.get('request')
        if request and request.user:
            user = request.user
            if user.role == 'department_manager' and attrs['role'] in ['super_admin', 'department_manager']:
                raise serializers.ValidationError("部门管理员无法邀请超级管理员或部门管理员")
        return attrs


class AdminInvitationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminInvitation
        fields = ['status']
