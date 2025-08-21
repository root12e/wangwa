# WWKC库存管理系统 - 前端

## 项目概述

这是一个基于Vue3 + TypeScript + Element Plus的现代化库存管理系统前端，采用淡蓝色商务风格设计，具有高级感和可玩性。

## 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript超集
- **Element Plus** - 基于Vue 3的组件库
- **Vue Router** - 官方路由管理器
- **Pinia** - Vue的状态管理库
- **Vite** - 下一代前端构建工具
- **ESLint + Prettier** - 代码质量和格式化

## 设计特色

### 🎨 视觉设计
- **淡蓝色商务风格** - 专业、现代、优雅
- **渐变色彩** - 丰富的视觉层次
- **卡片式布局** - 清晰的信息组织
- **响应式设计** - 支持各种设备尺寸

### ✨ 交互体验
- **流畅动画** - 淡入、滑入、脉冲等动画效果
- **悬停效果** - 卡片提升、按钮变换等
- **状态指示** - 清晰的状态标签和图标
- **加载状态** - 优雅的加载动画

### 🚀 功能特性
- **权限管理** - 基于角色的访问控制
- **数据可视化** - 统计卡片和图表展示
- **搜索过滤** - 强大的数据筛选功能
- **分页导航** - 高效的数据浏览体验

## 项目结构

```
src/
├── assets/          # 静态资源
│   ├── main.css     # 主样式文件
│   └── base.css     # 基础样式
├── components/      # 公共组件
├── router/          # 路由配置
├── stores/          # 状态管理
├── views/           # 页面组件
│   ├── HomeView.vue         # 仪表盘
│   ├── InventoryView.vue    # 库存管理
│   ├── UsersView.vue        # 用户管理
│   ├── StoresView.vue       # 店铺管理
│   └── SettingsView.vue     # 系统设置
├── App.vue          # 根组件
└── main.ts          # 入口文件
```

## 页面说明

### 1. 仪表盘 (HomeView)
- 系统概览和关键指标
- 快速访问常用功能
- 实时数据展示

### 2. 库存管理 (InventoryView)
- 商品列表和详情
- 库存统计和预警
- 分类管理和搜索
- 供应商信息

### 3. 用户管理 (UsersView)
- 用户列表和角色管理
- 权限分配和状态控制
- 部门和店铺关联

### 4. 店铺管理 (StoresView)
- 店铺信息和状态
- 业绩统计和分析
- 地理位置展示
- 员工管理

### 5. 系统设置 (SettingsView)
- 基本配置管理
- 安全策略设置
- 通知配置
- 备份管理

## 安装和运行

### 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 代码格式化
```bash
npm run format
```

### 代码检查
```bash
npm run lint
```

## 开发指南

### 添加新页面
1. 在 `src/views/` 目录下创建新的 `.vue` 文件
2. 在 `src/router/index.ts` 中添加路由配置
3. 在 `src/App.vue` 中添加导航菜单项

### 样式规范
- 使用CSS变量定义主题色彩
- 遵循BEM命名规范
- 响应式设计优先
- 动画效果适度

### 组件开发
- 使用Composition API
- TypeScript类型定义
- Props和事件规范
- 插槽和具名插槽

## 自定义主题

### 颜色变量
```css
:root {
  --primary-color: #4A90E2;        /* 主色调 */
  --primary-light: #7BB3F0;        /* 浅色主调 */
  --primary-dark: #357ABD;         /* 深色主调 */
  --primary-ultra-light: #E8F4FD;  /* 超浅色主调 */
  --accent-color: #00B4D8;         /* 强调色 */
  --success-color: #52C41A;        /* 成功色 */
  --warning-color: #FAAD14;        /* 警告色 */
  --error-color: #FF4D4F;          /* 错误色 */
}
```

### 间距系统
```css
:root {
  --spacing-xs: 4px;    /* 超小间距 */
  --spacing-sm: 8px;    /* 小间距 */
  --spacing-md: 16px;   /* 中等间距 */
  --spacing-lg: 24px;   /* 大间距 */
  --spacing-xl: 32px;   /* 超大间距 */
  --spacing-xxl: 48px;  /* 超超大间距 */
}
```

### 阴影系统
```css
:root {
  --shadow-light: 0 2px 8px rgba(74, 144, 226, 0.1);
  --shadow-medium: 0 4px 16px rgba(74, 144, 226, 0.15);
  --shadow-heavy: 0 8px 32px rgba(74, 144, 226, 0.2);
}
```

## 性能优化

### 代码分割
- 路由级别的代码分割
- 组件懒加载
- 第三方库按需引入

### 资源优化
- 图片压缩和格式优化
- CSS和JavaScript压缩
- 静态资源CDN部署

### 缓存策略
- 浏览器缓存配置
- 静态资源版本控制
- API响应缓存

## 部署说明

### 开发环境
```bash
npm run dev
# 访问 http://localhost:5173
```

### 生产环境
```bash
npm run build
# 将 dist/ 目录部署到Web服务器
```

### Docker部署
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 80
CMD ["npm", "run", "preview"]
```

## 浏览器支持

- Chrome >= 88
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者: WWKC团队
- 邮箱: admin@wwkc.com
- 项目地址: [GitHub Repository](https://github.com/wwkc/inventory-system)

## 更新日志

### v1.0.0 (2024-01-15)
- ✨ 初始版本发布
- 🎨 淡蓝色商务风格设计
- 📱 响应式布局支持
- 🔐 基于角色的权限管理
- 📊 数据统计和可视化
- ⚙️ 完整的系统设置功能
