from rest_framework import serializers
from ..models.message_system import (
    ChatRoom, ChatRoomMember, Message, MessageReadStatus,
    InventoryWarning, WarningNotification
)
from ..serializers.User import UserSerializer
from ..serializers.store_management import StoreSerializer
from ..serializers.product_management import ProductSerializer


class ChatRoomSerializer(serializers.ModelSerializer):
    """聊天室序列化器"""
    creator = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'room_type', 'creator', 'is_active',
            'created_at', 'updated_at', 'member_count', 'last_message', 'unread_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        """获取成员数量"""
        return obj.members.count()
    
    def get_last_message(self, obj):
        """获取最后一条消息"""
        last_message = obj.message_set.filter(is_deleted=False).order_by('-created_at').first()
        if last_message:
            return {
                'id': str(last_message.id),
                'content': last_message.content[:100],
                'sender': last_message.sender.username,
                'created_at': last_message.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        """获取未读消息数量"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.message_set.filter(
                is_deleted=False,
                created_at__gt=request.user.last_login or request.user.date_joined
            ).count()
        return 0


class ChatRoomMemberSerializer(serializers.ModelSerializer):
    """聊天室成员序列化器"""
    user = UserSerializer(read_only=True)
    room = ChatRoomSerializer(read_only=True)
    
    class Meta:
        model = ChatRoomMember
        fields = [
            'id', 'room', 'user', 'role', 'joined_at',
            'last_read_at', 'is_muted'
        ]
        read_only_fields = ['id', 'joined_at']


class MessageSerializer(serializers.ModelSerializer):
    """消息序列化器"""
    sender = UserSerializer(read_only=True)
    room = ChatRoomSerializer(read_only=True)
    is_read_by_current_user = serializers.SerializerMethodField()
    file_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'room', 'sender', 'message_type', 'content',
            'file_url', 'file_name', 'file_size', 'is_read',
            'is_deleted', 'created_at', 'updated_at',
            'is_read_by_current_user', 'file_info'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_read_by_current_user(self, obj):
        """获取当前用户是否已读"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return MessageReadStatus.objects.filter(
                message=obj,
                user=request.user
            ).exists()
        return False
    
    def get_file_info(self, obj):
        """获取文件信息"""
        if obj.file_url and obj.message_type in ['file', 'image']:
            return {
                'url': obj.file_url,
                'name': obj.file_name,
                'size': obj.file_size,
                'type': obj.message_type
            }
        return None


class MessageCreateSerializer(serializers.ModelSerializer):
    """消息创建序列化器"""
    class Meta:
        model = Message
        fields = ['room', 'message_type', 'content', 'file_url', 'file_name', 'file_size']
    
    def validate(self, attrs):
        """验证消息内容"""
        if attrs.get('message_type') == 'text' and not attrs.get('content'):
            raise serializers.ValidationError("文本消息不能为空")
        
        if attrs.get('message_type') in ['file', 'image'] and not attrs.get('file_url'):
            raise serializers.ValidationError("文件消息必须包含文件链接")
        
        return attrs


class InventoryWarningSerializer(serializers.ModelSerializer):
    """库存预警序列化器"""
    store = StoreSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    resolved_by = UserSerializer(read_only=True)
    notification_count = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryWarning
        fields = [
            'id', 'store', 'product', 'warning_level', 'current_stock',
            'threshold_stock', 'status', 'email_sent', 'email_sent_at',
            'created_at', 'resolved_at', 'resolved_by', 'notification_count'
        ]
        read_only_fields = ['id', 'created_at', 'email_sent', 'email_sent_at']
    
    def get_notification_count(self, obj):
        """获取通知用户数量"""
        return obj.notified_users.count()


class WarningNotificationSerializer(serializers.ModelSerializer):
    """预警通知序列化器"""
    warning = InventoryWarningSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = WarningNotification
        fields = [
            'id', 'warning', 'user', 'notified_at',
            'is_read', 'read_at'
        ]
        read_only_fields = ['id', 'notified_at']


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """聊天室创建序列化器"""
    member_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ChatRoom
        fields = ['name', 'room_type', 'member_ids']
    
    def create(self, validated_data):
        """创建聊天室并添加成员"""
        member_ids = validated_data.pop('member_ids', [])
        request = self.context.get('request')
        
        # 设置创建者
        if request and request.user.is_authenticated:
            validated_data['creator'] = request.user
        
        # 创建聊天室
        chat_room = ChatRoom.objects.create(**validated_data)
        
        # 添加创建者为成员
        if request and request.user.is_authenticated:
            ChatRoomMember.objects.create(
                room=chat_room,
                user=request.user,
                role='admin'
            )
        
        # 添加其他成员
        for user_id in member_ids:
            try:
                from ..models.User import User
                user = User.objects.get(id=user_id)
                ChatRoomMember.objects.create(
                    room=chat_room,
                    user=user,
                    role='member'
                )
            except User.DoesNotExist:
                continue
        
        return chat_room


class MessageReadStatusSerializer(serializers.ModelSerializer):
    """消息阅读状态序列化器"""
    message = MessageSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MessageReadStatus
        fields = ['id', 'message', 'user', 'read_at']
        read_only_fields = ['id', 'read_at']


class InventoryWarningResolveSerializer(serializers.Serializer):
    """库存预警解决序列化器"""
    resolution_note = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_resolution_note(self, value):
        """验证解决备注"""
        if value and len(value.strip()) > 500:
            raise serializers.ValidationError("解决备注不能超过500个字符")
        return value.strip() if value else ""


class ChatRoomInviteSerializer(serializers.Serializer):
    """聊天室邀请序列化器"""
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="要邀请的用户ID列表"
    )
    role = serializers.ChoiceField(
        choices=ChatRoomMember.ROLE_CHOICES,
        default='member',
        help_text="成员角色"
    )
    
    def validate_user_ids(self, value):
        """验证用户ID列表"""
        if not value:
            raise serializers.ValidationError("用户ID列表不能为空")
        
        # 检查用户是否存在
        from ..models.User import User
        existing_users = User.objects.filter(id__in=value, is_active=True)
        if len(existing_users) != len(value):
            raise serializers.ValidationError("部分用户不存在或已被禁用")
        
        return value


class FileUploadSerializer(serializers.Serializer):
    """文件上传序列化器"""
    file = serializers.FileField(help_text="要上传的文件")
    message_type = serializers.ChoiceField(
        choices=[('file', '文件'), ('image', '图片')],
        help_text="消息类型"
    )
    room_id = serializers.UUIDField(help_text="聊天室ID")
    
    def validate_file(self, value):
        """验证文件"""
        # 检查文件大小（限制为10MB）
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("文件大小不能超过10MB")
        
        # 检查文件类型
        allowed_types = {
            'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            'file': ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'text/plain', 'application/zip', 'application/x-rar-compressed']
        }
        
        if value.content_type not in allowed_types.get(self.initial_data.get('message_type', 'file'), []):
            raise serializers.ValidationError("不支持的文件类型")
        
        return value
