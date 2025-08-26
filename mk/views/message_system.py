from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from ..models.message_system import (
    ChatRoom, ChatRoomMember, Message, MessageReadStatus,
    InventoryWarning, WarningNotification
)
from ..serializers.message_system import (
    ChatRoomSerializer, ChatRoomMemberSerializer, MessageSerializer,
    MessageCreateSerializer, InventoryWarningSerializer,
    WarningNotificationSerializer, ChatRoomCreateSerializer,
    InventoryWarningResolveSerializer, ChatRoomInviteSerializer,
    FileUploadSerializer
)
from ..services.inventory_warning_service import InventoryWarningService
from ..permissions.base import IsAuthenticated


class ChatRoomViewSet(viewsets.ModelViewSet):
    """聊天室视图集"""
    queryset = ChatRoom.objects.filter(is_active=True)
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取用户有权限访问的聊天室"""
        user = self.request.user
        if user.is_superuser:
            return ChatRoom.objects.filter(is_active=True)
        
        # 获取用户所在的聊天室
        return ChatRoom.objects.filter(
            is_active=True,
            chatroommember__user=user
        ).distinct()
    
    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer
    
    @action(detail=True, methods=['post'])
    def invite_members(self, request, pk=None):
        """邀请成员加入聊天室"""
        chat_room = self.get_object()
        serializer = ChatRoomInviteSerializer(data=request.data)
        
        if serializer.is_valid():
            user_ids = serializer.validated_data['user_ids']
            role = serializer.validated_data['role']
            
            # 检查权限
            if not self._can_manage_room(request.user, chat_room):
                return Response(
                    {"detail": "您没有权限管理此聊天室"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 添加成员
            added_count = 0
            for user_id in user_ids:
                try:
                    from ..models.User import User
                    user = User.objects.get(id=user_id, is_active=True)
                    
                    # 检查是否已经是成员
                    if not ChatRoomMember.objects.filter(room=chat_room, user=user).exists():
                        ChatRoomMember.objects.create(
                            room=chat_room,
                            user=user,
                            role=role
                        )
                        added_count += 1
                except User.DoesNotExist:
                    continue
            
            return Response({
                "detail": f"成功邀请 {added_count} 个成员",
                "added_count": added_count
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def leave_room(self, request, pk=None):
        """离开聊天室"""
        chat_room = self.get_object()
        user = request.user
        
        try:
            member = ChatRoomMember.objects.get(room=chat_room, user=user)
            member.delete()
            return Response({"detail": "已成功离开聊天室"})
        except ChatRoomMember.DoesNotExist:
            return Response(
                {"detail": "您不是此聊天室的成员"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """获取聊天室成员列表"""
        chat_room = self.get_object()
        members = ChatRoomMember.objects.filter(room=chat_room).select_related('user')
        serializer = ChatRoomMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    def _can_manage_room(self, user, chat_room):
        """检查用户是否可以管理聊天室"""
        if user.is_superuser:
            return True
        
        member = ChatRoomMember.objects.filter(room=chat_room, user=user).first()
        return member and member.role == 'admin'


class MessageViewSet(viewsets.ModelViewSet):
    """消息视图集"""
    queryset = Message.objects.filter(is_deleted=False)
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取用户有权限查看的消息"""
        user = self.request.user
        room_id = self.request.query_params.get('room')
        
        if room_id:
            # 检查用户是否有权限访问该聊天室
            if not ChatRoomMember.objects.filter(
                room_id=room_id,
                user=user
            ).exists():
                return Message.objects.none()
            
            return Message.objects.filter(
                room_id=room_id,
                is_deleted=False
            ).select_related('sender', 'room')
        
        # 获取用户所在聊天室的所有消息
        user_rooms = ChatRoom.objects.filter(
            chatroommember__user=user
        ).values_list('id', flat=True)
        
        return Message.objects.filter(
            room_id__in=user_rooms,
            is_deleted=False
        ).select_related('sender', 'room')
    
    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        """创建消息时设置发送者"""
        serializer.save(sender=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """标记消息为已读"""
        message = self.get_object()
        user = request.user
        
        # 创建或更新阅读状态
        MessageReadStatus.objects.update_or_create(
            message=message,
            user=user,
            defaults={'read_at': timezone.now()}
        )
        
        return Response({"detail": "消息已标记为已读"})
    
    @action(detail=True, methods=['post'])
    def delete_message(self, request, pk=None):
        """删除消息（软删除）"""
        message = self.get_object()
        user = request.user
        
        # 检查权限：只能删除自己的消息或管理员可以删除任何消息
        if message.sender != user and not user.is_superuser:
            return Response(
                {"detail": "您没有权限删除此消息"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.is_deleted = True
        message.save()
        
        return Response({"detail": "消息已删除"})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读消息数量"""
        user = request.user
        
        # 获取用户所在的所有聊天室
        user_rooms = ChatRoom.objects.filter(
            chatroommember__user=user
        ).values_list('id', flat=True)
        
        # 计算未读消息数量
        unread_count = Message.objects.filter(
            room_id__in=user_rooms,
            is_deleted=False,
            created_at__gt=user.last_login or user.date_joined
        ).exclude(
            messagereadstatus__user=user
        ).count()
        
        return Response({"unread_count": unread_count})


class InventoryWarningViewSet(viewsets.ReadOnlyModelViewSet):
    """库存预警视图集"""
    queryset = InventoryWarning.objects.all()
    serializer_class = InventoryWarningSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取用户有权限查看的预警"""
        user = self.request.user
        store_id = self.request.query_params.get('store')
        
        if store_id:
            return InventoryWarningService.get_active_warnings(store_id=store_id, user=user)
        
        return InventoryWarningService.get_active_warnings(user=user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """解决库存预警"""
        warning = self.get_object()
        serializer = InventoryWarningResolveSerializer(data=request.data)
        
        if serializer.is_valid():
            resolution_note = serializer.validated_data.get('resolution_note', '')
            success, message = InventoryWarningService.resolve_warning(
                warning.id,
                request.user,
                resolution_note
            )
            
            if success:
                return Response({"detail": message})
            else:
                return Response(
                    {"detail": message},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def check_warnings(self, request):
        """手动检查库存预警"""
        if not request.user.is_superuser:
            return Response(
                {"detail": "只有超级管理员可以手动检查预警"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        warnings_created = InventoryWarningService.check_inventory_warnings()
        return Response({
            "detail": f"检查完成，创建了 {warnings_created} 个预警",
            "warnings_created": warnings_created
        })


class WarningNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """预警通知视图集"""
    queryset = WarningNotification.objects.all()
    serializer_class = WarningNotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的预警通知"""
        return InventoryWarningService.get_user_warning_notifications(self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """标记通知为已读"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return Response({"detail": "通知已标记为已读"})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """标记所有通知为已读"""
        user = request.user
        unread_notifications = WarningNotification.objects.filter(
            user=user,
            is_read=False
        )
        
        count = unread_notifications.count()
        unread_notifications.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            "detail": f"已标记 {count} 个通知为已读",
            "marked_count": count
        })


class FileUploadViewSet(viewsets.ViewSet):
    """文件上传视图集"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    @action(detail=False, methods=['post'])
    def upload_file(self, request):
        """上传文件"""
        serializer = FileUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            file_obj = serializer.validated_data['file']
            message_type = serializer.validated_data['message_type']
            room_id = serializer.validated_data['room_id']
            
            # 检查用户是否有权限访问该聊天室
            if not ChatRoomMember.objects.filter(
                room_id=room_id,
                user=request.user
            ).exists():
                return Response(
                    {"detail": "您没有权限访问此聊天室"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 这里应该实现文件上传到存储服务的逻辑
            # 暂时返回模拟的文件URL
            file_url = f"/media/files/{file_obj.name}"
            
            # 创建文件消息
            try:
                room = ChatRoom.objects.get(id=room_id)
                message = Message.objects.create(
                    room=room,
                    sender=request.user,
                    message_type=message_type,
                    content=f"文件：{file_obj.name}",
                    file_url=file_url,
                    file_name=file_obj.name,
                    file_size=file_obj.size
                )
                
                return Response({
                    "detail": "文件上传成功",
                    "message": MessageSerializer(message, context={'request': request}).data
                })
                
            except ChatRoom.DoesNotExist:
                return Response(
                    {"detail": "聊天室不存在"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
