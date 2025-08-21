from django.urls import path
from . import views

app_name = 'mk'

urlpatterns = [
    # 用户认证相关
    path('api/auth/register/', views.UserRegistrationView.as_view(), name='user_register'),
    path('api/auth/login/', views.UserLoginView.as_view(), name='user_login'),
    path('api/auth/logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('api/auth/send-verification-code/', views.SendEmailVerificationCodeView.as_view(), name='send_verification_code'),
    path('api/auth/password-reset-request/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('api/auth/password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/auth/check-email-verification/', views.CheckEmailVerificationView.as_view(), name='check_email_verification'),
    path('api/auth/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # 用户资料
    path('api/user/profile/', views.UserProfileView.as_view(), name='user_profile'),
    
    # 用户管理
    path('api/users/', views.UserListView.as_view(), name='user_list'),
    path('api/users/<uuid:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # 部门管理
    path('api/departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('api/departments/<uuid:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    
    # 店铺管理
    path('api/stores/', views.StoreListView.as_view(), name='store_list'),
    path('api/stores/<uuid:pk>/', views.StoreDetailView.as_view(), name='store_detail'),
]