from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    user_views, department_views, store_management, admin_invitation_views,
    product_management, inventory_management, message_system, etsy_views
)
from .views.User import (
    UserLoginView, UserRegistrationView, UserLogoutView,
    SendEmailVerificationCodeView, CheckEmailVerificationView,
    PasswordResetRequestView, PasswordResetConfirmView,
    ChangePasswordView, TokenRefreshView, UserProfileView,
    UserManagementView, UserDetailManagementView, UserBulkActionView,
    UserStatisticsView, UserApprovalManagementView
)

# 创建路由器
router = DefaultRouter()

# 用户管理路由
router.register(r'users', user_views.UserViewSet)

# 部门管理路由
router.register(r'departments', department_views.DepartmentViewSet)

# 店铺管理路由
router.register(r'stores', store_management.StoreViewSet)
router.register(r'store-inventory', store_management.StoreInventoryViewSet)
router.register(r'store-transactions', store_management.StoreTransactionViewSet)

# 产品管理路由
router.register(r'products', product_management.ProductViewSet)
router.register(r'product-categories', product_management.ProductCategoryViewSet)
router.register(r'product-images', product_management.ProductImageViewSet)
router.register(r'product-transactions', product_management.ProductTransactionViewSet)

# 库存管理路由
router.register(r'inventory', inventory_management.InventoryViewSet)
router.register(r'inventory-transactions', inventory_management.InventoryTransactionViewSet)
router.register(r'inventory-consumption', inventory_management.InventoryConsumptionViewSet)
router.register(r'orders', inventory_management.OrderViewSet)
router.register(r'order-batches', inventory_management.OrderBatchViewSet)
router.register(r'workflow', inventory_management.WorkflowManagementViewSet, basename='workflow')

# 消息系统路由
router.register(r'chat-rooms', message_system.ChatRoomViewSet)
router.register(r'messages', message_system.MessageViewSet)
router.register(r'inventory-warnings', message_system.InventoryWarningViewSet)
router.register(r'warning-notifications', message_system.WarningNotificationViewSet)
router.register(r'file-upload', message_system.FileUploadViewSet, basename='file-upload')

# Etsy模块路由
router.register(r'etsy/product-registration', etsy_views.EtsyProductRegistrationViewSet)
router.register(r'etsy/order-import-summary', etsy_views.EtsyOrderImportSummaryViewSet)
router.register(r'etsy/order-statistics', etsy_views.EtsyOrderStatisticsViewSet)
router.register(r'etsy/design-requirement', etsy_views.EtsyDesignRequirementViewSet)
router.register(r'etsy/purchase-requirement', etsy_views.EtsyPurchaseRequirementViewSet)
router.register(r'etsy/production-requirement', etsy_views.EtsyProductionRequirementViewSet)
router.register(r'etsy/shipping-delivery', etsy_views.EtsyShippingDeliveryViewSet)
router.register(r'etsy/qr-code-label', etsy_views.EtsyQRCodeLabelViewSet)
router.register(r'etsy/yuntu-export', etsy_views.EtsyYunTuExportViewSet)
router.register(r'etsy/yuntu-deduction', etsy_views.EtsyYunTuDeductionViewSet)
router.register(r'etsy/store-information', etsy_views.EtsyStoreInformationViewSet)

# Etsy同步管理路由
router.register(r'etsy/sync-management', etsy_views.EtsySyncManagementViewSet, basename='etsy-sync-management')

# 管理员邀请路由
router.register(r'admin-invitations', admin_invitation_views.AdminInvitationViewSet)

urlpatterns = [
    # API路由
    path('api/', include(router.urls)),
    
    # 店铺产品路由（嵌套路由）
    path('api/stores/<uuid:store_id>/products/', 
         product_management.StoreProductViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/stores/<uuid:store_id>/products/<uuid:pk>/', 
         product_management.StoreProductViewSet.as_view({
             'get': 'retrieve', 
             'put': 'update', 
             'patch': 'partial_update', 
             'delete': 'destroy'
         })),
    path('api/stores/<uuid:store_id>/products/inventory/', 
         product_management.StoreProductViewSet.as_view({'get': 'store_inventory'})),
    path('api/stores/<uuid:store_id>/products/statistics/', 
         product_management.StoreProductViewSet.as_view({'get': 'store_statistics'})),
    
    # 认证相关路由
    path('api/auth/login/', UserLoginView.as_view(), name='user_login'),
    path('api/auth/register/', UserRegistrationView.as_view(), name='user_register'),
    path('api/auth/logout/', UserLogoutView.as_view(), name='user_logout'),
    path('api/auth/send-verification-code/', SendEmailVerificationCodeView.as_view(), name='send_verification_code'),
    path('api/auth/check-email-verification/', CheckEmailVerificationView.as_view(), name='check_email_verification'),
    path('api/auth/password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('api/auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    
    # 用户相关路由
    path('api/user/profile/', UserProfileView.as_view(), name='user_profile'),
    
    # 用户管理路由
    path('api/users/', UserManagementView.as_view(), name='user_management'),
    path('api/users/<int:pk>/', UserDetailManagementView.as_view(), name='user_detail_management'),
    path('api/users/bulk-action/', UserBulkActionView.as_view(), name='user_bulk_action'),
    path('api/users/statistics/', UserStatisticsView.as_view(), name='user_statistics'),
    path('api/users/approvals/', UserApprovalManagementView.as_view(), name='user_approval_management'),
]