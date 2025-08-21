# WWKC库存管理系统 - 登录系统说明

## 🚀 功能特性

### 1. 用户认证
- **登录功能**: 支持用户名或手机号登录
- **注册功能**: 完整的用户注册流程，包含邮箱验证码
- **密码管理**: 忘记密码、重置密码功能
- **记住我**: 支持记住登录状态

### 2. 权限控制
- **路由保护**: 所有页面都需要登录才能访问
- **角色权限**: 基于角色的访问控制（RBAC）
- **自动重定向**: 未登录用户自动跳转到登录页

### 3. 安全特性
- **JWT Token**: 使用JWT进行身份验证
- **表单验证**: 完整的客户端表单验证
- **错误处理**: 友好的错误提示和处理

## 🔧 技术实现

### 1. 前端架构
- **Vue 3**: 使用Composition API
- **TypeScript**: 完整的类型支持
- **Pinia**: 状态管理
- **Vue Router**: 路由管理和守卫
- **Element Plus**: UI组件库

### 2. 状态管理
```typescript
// 认证状态管理
const authStore = useAuthStore()

// 用户信息
authStore.user
authStore.token
authStore.isAuthenticated

// 权限检查
authStore.hasPermission('super_admin')
authStore.canManageUser(targetUser)
```

### 3. 路由守卫
```typescript
// 路由守卫配置
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})
```

## 📱 页面结构

### 1. 登录页面 (`/login`)
- 用户名/手机号登录
- 密码输入
- 记住我选项
- 忘记密码链接
- 注册账户链接

### 2. 注册页面 (登录页内切换)
- 用户名输入
- 手机号输入
- 邮箱地址
- 邮箱验证码
- 密码设置
- 角色选择
- 确认密码

### 3. 忘记密码
- 邮箱输入
- 发送重置邮件

## 🔐 权限系统

### 1. 用户角色
- **超级管理员** (`super_admin`): 可以管理所有信息
- **部门部长** (`department_manager`): 可以管理本部门信息
- **店铺运营** (`store_operator`): 可以管理本店铺信息
- **普通员工** (`staff`): 只能管理自己的信息

### 2. 权限检查
```typescript
// 检查角色权限
if (authStore.isSuperAdmin) {
  // 超级管理员权限
}

// 检查具体权限
if (authStore.canManageUser(targetUser)) {
  // 可以管理该用户
}
```

## 🌐 API接口

### 1. 认证接口
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/logout/` - 用户登出
- `POST /api/auth/send-verification-code/` - 发送验证码
- `POST /api/auth/forgot-password/` - 忘记密码

### 2. 请求格式
```typescript
// 登录请求
{
  "username_or_phone": "admin",
  "password": "password123"
}

// 注册请求
{
  "username": "newuser",
  "phone": "13800000000",
  "email": "user@example.com",
  "email_verification_code": "123456",
  "password": "password123",
  "confirm_password": "password123",
  "role": "staff"
}
```

### 3. 响应格式
```typescript
// 登录成功响应
{
  "message": "登录成功",
  "user": {
    "id": 1,
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

## 🚀 使用方法

### 1. 启动开发服务器
```bash
cd frontend/wwkc-frontend
npm run dev
```

### 2. 访问登录页面
- 打开浏览器访问: http://localhost:5174/login
- 或者直接访问: http://localhost:5174/ (会自动重定向到登录页)

### 3. 测试账户
根据后端初始化脚本，可以使用以下测试账户：

#### 超级管理员
- 用户名: `admin`
- 密码: `admin123`

#### 部门部长
- 用户名: `manager001`
- 密码: `manager123`

#### 店铺运营
- 用户名: `operator001`
- 密码: `operator123`

#### 普通员工
- 用户名: `staff001`
- 密码: `staff123`

## 🔧 配置说明

### 1. 环境变量
创建 `.env` 文件并配置：
```bash
# API基础URL
VITE_API_BASE_URL=http://localhost:8000

# 应用标题
VITE_APP_TITLE=WWKC库存管理系统
```

### 2. 后端配置
确保Django后端运行在 `http://localhost:8000`，并且：
- CORS已正确配置
- JWT认证已启用
- 数据库已初始化
- 测试用户已创建

## 🎨 样式定制

### 1. 主题色彩
```css
:root {
  --primary-color: #4A90E2;        /* 主色调 */
  --primary-light: #7BB3F0;        /* 浅色主调 */
  --primary-dark: #357ABD;         /* 深色主调 */
  --primary-ultra-light: #E8F4FD;  /* 超浅色主调 */
}
```

### 2. 动画效果
- 页面淡入动画
- 背景装饰浮动动画
- 按钮悬停效果
- 表单切换动画

## 🚨 注意事项

### 1. 安全提醒
- 生产环境请使用HTTPS
- 定期更新JWT密钥
- 设置合理的Token过期时间
- 启用密码强度验证

### 2. 性能优化
- 启用代码分割
- 使用懒加载
- 优化图片资源
- 启用Gzip压缩

### 3. 浏览器兼容
- Chrome >= 88
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 🔍 故障排除

### 1. 常见问题
- **登录失败**: 检查用户名密码是否正确
- **验证码错误**: 检查邮箱验证码是否有效
- **权限不足**: 检查用户角色和权限设置
- **网络错误**: 检查后端服务是否正常运行

### 2. 调试方法
- 打开浏览器开发者工具
- 查看Console错误信息
- 检查Network请求状态
- 验证Token是否有效

## 📚 相关文档

- [Vue 3 官方文档](https://vuejs.org/)
- [Element Plus 组件库](https://element-plus.org/)
- [Pinia 状态管理](https://pinia.vuejs.org/)
- [Vue Router 路由管理](https://router.vuejs.org/)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证
