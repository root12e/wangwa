from django.db import models
from django.utils import timezone
import uuid
from .User import User


class ChatRoom(models.Model):
    """聊天室模型"""
    ROOM_TYPES = [
        ('private', '私聊'),
        ('group', '群聊'),
        ('system', '系统消息'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='聊天室名称')
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='group', verbose_name='聊天室类型')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者', related_name='created_rooms')
    members = models.ManyToManyField(User, through='ChatRoomMember', verbose_name='成员')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '聊天室'
        verbose_name_plural = '聊天室'
        db_table = 'chat_rooms'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"


class ChatRoomMember(models.Model):
    """聊天室成员模型"""
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('member', '普通成员'),
        ('readonly', '只读成员'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, verbose_name='聊天室')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name='角色')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')
    last_read_at = models.DateTimeField(null=True, blank=True, verbose_name='最后阅读时间')
    is_muted = models.BooleanField(default=False, verbose_name='是否静音')
    
    class Meta:
        verbose_name = '聊天室成员'
        verbose_name_plural = '聊天室成员'
        db_table = 'chat_room_members'
        unique_together = ['room', 'user']
        ordering = ['joined_at']


class Message(models.Model):
    """消息模型"""
    MESSAGE_TYPES = [
        ('text', '文本'),
        ('image', '图片'),
        ('file', '文件'),
        ('system', '系统消息'),
        ('warning', '预警消息'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, verbose_name='聊天室')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发送者', related_name='sent_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text', verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    file_url = models.URLField(blank=True, null=True, verbose_name='文件链接')
    file_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='文件名')
    file_size = models.BigIntegerField(blank=True, null=True, verbose_name='文件大小(字节)')
    
    # 消息状态
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    is_deleted = models.BooleanField(default=False, verbose_name='是否已删除')
    
    # 关联预警（如果是预警消息）
    inventory_warning = models.ForeignKey('InventoryWarning', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联库存预警')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '消息'
        verbose_name_plural = '消息'
        db_table = 'messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['message_type']),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class MessageReadStatus(models.Model):
    """消息阅读状态模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='消息')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    read_at = models.DateTimeField(auto_now_add=True, verbose_name='阅读时间')
    
    class Meta:
        verbose_name = '消息阅读状态'
        verbose_name_plural = '消息阅读状态'
        db_table = 'message_read_status'
        unique_together = ['message', 'user']


class InventoryWarning(models.Model):
    """库存预警模型"""
    WARNING_LEVELS = [
        ('low', '低库存'),
        ('critical', '严重缺货'),
        ('out_of_stock', '无库存'),
    ]
    
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('resolved', '已解决'),
        ('ignored', '已忽略'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, verbose_name='店铺')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='产品')
    inventory = models.ForeignKey('Inventory', on_delete=models.CASCADE, verbose_name='库存记录')
    
    warning_level = models.CharField(max_length=20, choices=WARNING_LEVELS, verbose_name='预警级别')
    current_stock = models.IntegerField(verbose_name='当前库存')
    threshold_stock = models.IntegerField(verbose_name='预警阈值')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    
    # 通知相关
    notified_users = models.ManyToManyField(User, through='WarningNotification', verbose_name='已通知用户', related_name='received_warnings')
    email_sent = models.BooleanField(default=False, verbose_name='邮件是否已发送')
    email_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='邮件发送时间')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='解决时间')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='解决人', related_name='resolved_warnings')
    
    class Meta:
        verbose_name = '库存预警'
        verbose_name_plural = '库存预警'
        db_table = 'inventory_warnings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['warning_level', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.store.name} - {self.product.name} ({self.get_warning_level_display()})"


class WarningNotification(models.Model):
    """预警通知模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warning = models.ForeignKey(InventoryWarning, on_delete=models.CASCADE, verbose_name='预警')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    notified_at = models.DateTimeField(auto_now_add=True, verbose_name='通知时间')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='阅读时间')
    
    class Meta:
        verbose_name = '预警通知'
        verbose_name_plural = '预警通知'
        db_table = 'warning_notifications'
        unique_together = ['warning', 'user']
