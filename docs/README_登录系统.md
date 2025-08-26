# 登录系统集成说明

## 概述

本文档描述了WWKC库存管理系统的登录前后端集成，包括用户认证、JWT令牌管理、验证码发送等功能。

## 系统架构

### 前端架构
- **Vue 3** + **TypeScript** + **Pinia** + **Vue Router**
- **Element Plus** UI组件库
- **Axios** HTTP客户端

### 后端架构
- **Django** + **Django REST Framework**
- **JWT** 认证系统
- **邮件服务** 验证码发送

## 功能特性

### 1. 用户认证
- 用户名/手机号 + 密码登录
- JWT令牌认证
- 自动令牌刷新
- 记住登录状态

### 2. 用户注册
- 邮箱验证码注册
- 角色选择（普通员工、店铺运营）
- 表单验证

### 3. 密码管理
- 忘记密码
- 邮箱重置密码
- 修改密码

### 4. 权限控制
- 基于角色的访问控制
- 路由级权限保护
- 组件级权限检查

## 文件结构

```
frontend/wwkc-frontend/src/
├── api/
│   ├── client.js              # API客户端配置
│   ├── auth.js                # 认证相关API
│   └── department.js          # 部门管理API
├── stores/
│   └── auth.ts                # 认证状态管理
├── views/
│   └── LoginView.vue          # 登录页面
├── router/
│   └── index.ts               # 路由配置
└── main.ts                    # 应用入口

backend/mk/
├── views/
│   └── User.py                # 用户认证视图
├── urls.py                    # URL路由配置
└── models/
    └── User.py                # 用户模型
```

## 安装和配置

### 1. 前端依赖安装

```bash
cd frontend/wwkc-frontend
npm install axios
```

### 2. 后端依赖安装

```bash
pip install djangorestframework-simplejwt
```

### 3. 环境配置

创建 `.env` 文件：

```bash
# API配置
VITE_API_BASE_URL=http://localhost:8000

# 应用配置
VITE_APP_TITLE=WWKC库存管理系统
VITE_APP_VERSION=1.0.0
```

### 4. Django设置

在 `settings.py` 中添加：

```python
INSTALLED_APPS = [
    # ...
    'rest_framework_simplejwt',
]

REST_FRAMERWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# JWT设置
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
}

# 邮件设置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # 或其他邮件服务
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

## API接口说明

### 1. 用户登录

```http
POST /api/auth/login/
Content-Type: application/json

{
  "username_or_phone": "admin",
  "password": "password123"
}
```

响应：
```json
{
  "message": "登录成功",
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "super_admin",
    "role_display": "超级管理员"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### 2. 发送验证码

```http
POST /api/auth/send-verification-code/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

响应：
```json
{
  "message": "验证码已发送到您的邮箱",
  "email": "user@example.com"
}
```

### 3. 用户注册

```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "phone": "13800138000",
  "email": "user@example.com",
  "email_verification_code": "123456",
  "password": "password123",
  "role": "staff"
}
```

### 4. 令牌刷新

```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "refresh_token_here"
}
```

## 使用示例

### 1. 前端登录调用

```javascript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 登录
const handleLogin = async () => {
  const result = await authStore.login({
    username_or_phone: 'admin',
    password: 'password123'
  })
  
  if (result.success) {
    console.log('登录成功')
    // 跳转到首页
    router.push('/')
  } else {
    console.error('登录失败:', result.error)
  }
}
```

### 2. 发送验证码

```javascript
// 发送验证码
const sendCode = async () => {
  const result = await authStore.sendVerificationCode('user@example.com')
  
  if (result.success) {
    ElMessage.success('验证码已发送')
    startCountdown()
  }
}
```

### 3. 权限检查

```javascript
// 检查用户权限
if (authStore.hasPermission(['super_admin', 'department_manager'])) {
  // 允许访问
}

// 检查特定权限
if (authStore.canManageDepartment(department)) {
  // 允许管理部门
}
```

## 安全特性

### 1. JWT令牌安全
- 访问令牌有效期：60分钟
- 刷新令牌有效期：1天
- 自动令牌刷新
- 令牌过期自动登出

### 2. 密码安全
- 密码强度验证
- 密码哈希存储
- 密码重置令牌

### 3. 权限控制
- 基于角色的访问控制
- 对象级权限检查
- 路由级权限保护

## 错误处理

### 1. 网络错误
- 自动重试机制
- 友好的错误提示
- 错误日志记录

### 2. 认证错误
- 401错误自动处理
- 令牌过期自动刷新
- 认证失败重定向

### 3. 权限错误
- 权限不足提示
- 自动重定向
- 权限检查日志

## 测试

### 1. 单元测试

```bash
# 前端测试
npm run test:unit

# 后端测试
python manage.py test
```

### 2. 集成测试

```bash
# 启动后端服务
python manage.py runserver

# 启动前端服务
npm run dev
```

### 3. API测试

使用Postman或curl测试API接口：

```bash
# 测试登录
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username_or_phone":"admin","password":"password123"}'
```

## 部署说明

### 1. 生产环境配置

```bash
# 前端构建
npm run build

# 后端收集静态文件
python manage.py collectstatic

# 使用Gunicorn部署
gunicorn wwkc.wsgi:application
```

### 2. 环境变量

```bash
# 生产环境
VITE_API_BASE_URL=https://api.wwkc.com
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
```

### 3. 安全配置

```python
# 生产环境安全设置
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
```

## 故障排除

### 1. 常见问题

**Q: 登录后立即跳转到登录页**
A: 检查JWT令牌配置和localStorage存储

**Q: 验证码发送失败**
A: 检查邮件服务配置和网络连接

**Q: 权限检查失败**
A: 检查用户角色设置和权限配置

### 2. 调试技巧

```javascript
// 前端调试
console.log('认证状态:', authStore.isAuthenticated)
console.log('用户信息:', authStore.user)
console.log('令牌:', authStore.token)

// 后端调试
print(f"用户: {request.user}")
print(f"权限: {request.user.get_all_permissions()}")
```

### 3. 日志查看

```bash
# 查看Django日志
tail -f logs/django.log

# 查看前端控制台
# 在浏览器开发者工具中查看
```

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础登录注册功能
- JWT认证系统
- 邮箱验证码

### v1.1.0 (计划中)
- 手机验证码
- 双因素认证
- OAuth第三方登录
- 会话管理

## 技术支持

如有问题或建议，请：
1. 查看本文档
2. 检查控制台错误
3. 查看后端日志
4. 联系开发团队

## 许可证

MIT License
