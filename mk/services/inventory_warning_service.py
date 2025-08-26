import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from ..models.message_system import InventoryWarning, WarningNotification, ChatRoom, Message
from ..models.inventory_management import Inventory
from ..models.User import User

logger = logging.getLogger(__name__)


class InventoryWarningService:
    """库存预警服务"""
    
    @staticmethod
    def check_inventory_warnings():
        """检查所有库存是否需要预警"""
        try:
            # 获取所有活跃的库存记录
            inventories = Inventory.objects.filter(is_active=True)
            warnings_created = 0
            
            for inventory in inventories:
                if InventoryWarningService._should_create_warning(inventory):
                    warning = InventoryWarningService._create_warning(inventory)
                    if warning:
                        warnings_created += 1
                        # 发送邮件通知
                        InventoryWarningService._send_email_notification(warning)
                        # 创建系统消息
                        InventoryWarningService._create_system_message(warning)
            
            logger.info(f"库存预警检查完成，创建了 {warnings_created} 个预警")
            return warnings_created
            
        except Exception as e:
            logger.error(f"检查库存预警时发生错误: {str(e)}")
            return 0
    
    @staticmethod
    def _should_create_warning(inventory):
        """判断是否需要创建预警"""
        # 检查是否已有活跃的预警
        existing_warning = InventoryWarning.objects.filter(
            inventory=inventory,
            status='active'
        ).first()
        
        if existing_warning:
            return False
        
        # 检查库存是否低于阈值
        if inventory.current_stock <= inventory.min_stock:
            return True
        
        return False
    
    @staticmethod
    def _create_warning(inventory):
        """创建库存预警"""
        try:
            # 确定预警级别
            if inventory.current_stock == 0:
                warning_level = 'out_of_stock'
            elif inventory.current_stock <= inventory.min_stock * 0.5:
                warning_level = 'critical'
            else:
                warning_level = 'low'
            
            # 创建预警记录
            warning = InventoryWarning.objects.create(
                store=inventory.store,
                product=inventory.product,
                inventory=inventory,
                warning_level=warning_level,
                current_stock=inventory.current_stock,
                threshold_stock=inventory.min_stock,
                status='active'
            )
            
            # 通知相关用户
            InventoryWarningService._notify_users(warning)
            
            logger.info(f"创建库存预警: {warning}")
            return warning
            
        except Exception as e:
            logger.error(f"创建库存预警失败: {str(e)}")
            return None
    
    @staticmethod
    def _notify_users(warning):
        """通知相关用户"""
        try:
            # 获取店铺的运营人员
            store_operators = User.objects.filter(
                store=warning.store,
                role='store_operator',
                is_active=True
            )
            
            # 获取店铺经理
            store_managers = User.objects.filter(
                store=warning.store,
                role='department_manager',
                is_active=True
            )
            
            # 合并需要通知的用户
            users_to_notify = list(store_operators) + list(store_managers)
            
            # 创建通知记录
            notifications = []
            for user in users_to_notify:
                notification = WarningNotification(
                    warning=warning,
                    user=user
                )
                notifications.append(notification)
            
            WarningNotification.objects.bulk_create(notifications)
            
            logger.info(f"已通知 {len(users_to_notify)} 个用户关于库存预警")
            
        except Exception as e:
            logger.error(f"通知用户失败: {str(e)}")
    
    @staticmethod
    def _send_email_notification(warning):
        """发送邮件通知"""
        try:
            # 获取店铺运营人员的邮箱
            store_operators = User.objects.filter(
                store=warning.store,
                role='store_operator',
                is_active=True
            )
            
            if not store_operators.exists():
                logger.warning(f"店铺 {warning.store.name} 没有运营人员")
                return
            
            # 构建邮件内容
            subject = f"库存预警通知 - {warning.store.name}"
            
            if warning.warning_level == 'out_of_stock':
                level_text = "无库存"
            elif warning.warning_level == 'critical':
                level_text = "严重缺货"
            else:
                level_text = "低库存"
            
            message = f"""
            您好！
            
            您的店铺 {warning.store.name} 出现库存预警：
            
            产品名称：{warning.product.name}
            产品SKU：{warning.product.sku}
            预警级别：{level_text}
            当前库存：{warning.current_stock}
            预警阈值：{warning.threshold_stock}
            
            请及时处理库存问题，避免影响销售。
            
            此邮件由系统自动发送，请勿回复。
            """
            
            # 发送邮件
            recipient_list = [user.email for user in store_operators]
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            
            # 更新预警状态
            warning.email_sent = True
            warning.email_sent_at = timezone.now()
            warning.save()
            
            logger.info(f"库存预警邮件已发送给 {len(recipient_list)} 个用户")
            
        except Exception as e:
            logger.error(f"发送库存预警邮件失败: {str(e)}")
    
    @staticmethod
    def _create_system_message(warning):
        """创建系统消息"""
        try:
            # 获取或创建系统聊天室
            system_room, created = ChatRoom.objects.get_or_create(
                room_type='system',
                defaults={
                    'name': '系统通知',
                    'creator': User.objects.filter(is_superuser=True).first()
                }
            )
            
            # 构建消息内容
            if warning.warning_level == 'out_of_stock':
                level_text = "无库存"
            elif warning.warning_level == 'critical':
                level_text = "严重缺货"
            else:
                level_text = "低库存"
            
            content = f"""
            🚨 库存预警通知
            
            店铺：{warning.store.name}
            产品：{warning.product.name} ({warning.product.sku})
            预警级别：{level_text}
            当前库存：{warning.current_stock}
            预警阈值：{warning.threshold_stock}
            
            请相关运营人员及时处理！
            """
            
            # 创建系统消息
            system_user = User.objects.filter(is_superuser=True).first()
            if system_user:
                message = Message.objects.create(
                    room=system_room,
                    sender=system_user,
                    message_type='warning',
                    content=content,
                    inventory_warning=warning
                )
                
                logger.info(f"库存预警系统消息已创建: {message.id}")
            
        except Exception as e:
            logger.error(f"创建库存预警系统消息失败: {str(e)}")
    
    @staticmethod
    def resolve_warning(warning_id, resolved_by, resolution_note=""):
        """解决库存预警"""
        try:
            with transaction.atomic():
                warning = InventoryWarning.objects.get(id=warning_id)
                
                if warning.status != 'active':
                    return False, "预警已经解决或忽略"
                
                # 更新预警状态
                warning.status = 'resolved'
                warning.resolved_at = timezone.now()
                warning.resolved_by = resolved_by
                warning.save()
                
                # 创建解决通知消息
                InventoryWarningService._create_resolution_message(warning, resolved_by, resolution_note)
                
                logger.info(f"库存预警已解决: {warning.id}")
                return True, "预警已成功解决"
                
        except InventoryWarning.objects.DoesNotExist:
            return False, "预警不存在"
        except Exception as e:
            logger.error(f"解决库存预警失败: {str(e)}")
            return False, f"解决预警时发生错误: {str(e)}"
    
    @staticmethod
    def _create_resolution_message(warning, resolved_by, resolution_note):
        """创建解决通知消息"""
        try:
            # 获取系统聊天室
            system_room = ChatRoom.objects.filter(room_type='system').first()
            if not system_room:
                return
            
            content = f"""
            ✅ 库存预警已解决
            
            店铺：{warning.store.name}
            产品：{warning.product.name} ({warning.product.sku})
            解决人：{resolved_by.username}
            解决时间：{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            {f'备注：{resolution_note}' if resolution_note else ''}
            """
            
            # 创建解决通知消息
            message = Message.objects.create(
                room=system_room,
                sender=resolved_by,
                message_type='system',
                content=content
            )
            
            logger.info(f"库存预警解决通知已创建: {message.id}")
            
        except Exception as e:
            logger.error(f"创建库存预警解决通知失败: {str(e)}")
    
    @staticmethod
    def get_active_warnings(store=None, user=None):
        """获取活跃的预警"""
        try:
            queryset = InventoryWarning.objects.filter(status='active')
            
            if store:
                queryset = queryset.filter(store=store)
            
            if user:
                # 获取用户有权限查看的预警
                if user.is_superuser:
                    pass  # 超级管理员可以查看所有预警
                elif user.role == 'department_manager':
                    # 部门管理员可以查看本部门的预警
                    queryset = queryset.filter(store__department=user.department)
                elif user.role == 'store_operator':
                    # 店铺运营只能查看自己店铺的预警
                    queryset = queryset.filter(store=user.store)
                else:
                    # 普通员工只能查看自己店铺的预警
                    queryset = queryset.filter(store=user.store)
            
            return queryset.order_by('-created_at')
            
        except Exception as e:
            logger.error(f"获取库存预警失败: {str(e)}")
            return InventoryWarning.objects.none()
    
    @staticmethod
    def get_user_warning_notifications(user):
        """获取用户的预警通知"""
        try:
            return WarningNotification.objects.filter(
                user=user,
                is_read=False
            ).select_related('warning', 'warning__store', 'warning__product').order_by('-notified_at')
            
        except Exception as e:
            logger.error(f"获取用户预警通知失败: {str(e)}")
            return WarningNotification.objects.none()
