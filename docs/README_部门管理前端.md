# 部门管理前端页面

## 概述

部门管理前端页面是一个现代化的、响应式的Vue 3组件，提供了完整的部门管理功能，包括部门列表、创建、编辑、删除、详情查看等操作。

## 主要特性

### 🎨 现代化设计
- 采用淡蓝色商务风格主题
- 渐变背景和卡片式布局
- 流畅的动画效果和过渡
- 响应式设计，支持移动端

### 📊 数据展示
- 统计卡片显示关键指标
- 网格布局展示部门信息
- 搜索和过滤功能
- 分页支持

### 🔧 功能完整
- 部门CRUD操作
- 成员和店铺管理
- 状态管理
- 权限控制

## 文件结构

```
src/
├── views/
│   └── DepartmentView.vue          # 部门管理主页面
├── api/
│   └── department.js               # 部门管理API服务
├── composables/
│   └── useDepartment.js            # 部门管理组合式函数
└── router/
    └── index.ts                    # 路由配置
```

## 技术栈

- **Vue 3** - 使用Composition API
- **Element Plus** - UI组件库
- **Vue Router** - 路由管理
- **CSS Grid/Flexbox** - 布局系统
- **CSS Variables** - 主题系统

## 使用方法

### 1. 路由配置

页面已添加到路由系统中，访问路径：`/departments`

### 2. 组件引入

```vue
<template>
  <DepartmentView />
</template>

<script setup>
import DepartmentView from '@/views/DepartmentView.vue'
</script>
```

### 3. API集成

页面使用`useDepartment`组合式函数管理状态和逻辑：

```javascript
import { useDepartment } from '@/composables/useDepartment'

const {
  departments,
  loading,
  handleSearch,
  showCreateDialog,
  // ... 其他方法和状态
} = useDepartment()
```

## 功能详解

### 统计卡片

显示四个关键指标：
- 总部门数
- 总成员数
- 总店铺数
- 平均部门人数

### 操作栏

- **搜索框**：支持部门名称和描述搜索
- **状态过滤**：按部门状态筛选
- **创建按钮**：新建部门
- **导出按钮**：导出部门数据

### 部门卡片

每个部门卡片包含：
- 部门图标和状态标签
- 部门名称和描述
- 成员数量和店铺数量
- 创建时间
- 编辑和删除操作

### 部门详情

点击部门卡片可查看详细信息：
- **成员管理**：查看和管理部门成员
- **店铺管理**：查看和管理部门店铺
- **统计信息**：部门详细统计数据

## 状态管理

### 响应式状态

```javascript
// 部门列表
const departments = ref([])

// 加载状态
const loading = ref(false)

// 搜索和过滤
const searchQuery = ref('')
const statusFilter = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
```

### 计算属性

```javascript
// 过滤后的部门列表
const filteredDepartments = computed(() => {
  // 根据搜索和过滤条件过滤数据
})

// 部门统计信息
const departmentStats = computed(() => {
  // 计算统计数据
})
```

## API接口

### 主要接口

- `GET /api/departments/` - 获取部门列表
- `POST /api/departments/` - 创建部门
- `PUT /api/departments/{id}/` - 更新部门
- `DELETE /api/departments/{id}/` - 删除部门
- `GET /api/departments/{id}/` - 获取部门详情

### 扩展接口

- `GET /api/departments/{id}/members/` - 获取部门成员
- `GET /api/departments/{id}/stores/` - 获取部门店铺
- `GET /api/departments/{id}/statistics/` - 获取部门统计
- `GET /api/departments/search/` - 搜索部门

## 样式系统

### CSS变量

```css
:root {
  --primary-color: #4A90E2;
  --primary-light: #7BB3F0;
  --primary-dark: #357ABD;
  --primary-ultra-light: #E8F4FD;
  
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-xxl: 48px;
}
```

### 布局系统

- **Grid布局**：部门卡片使用CSS Grid自适应布局
- **Flexbox**：操作栏和卡片内部使用Flexbox布局
- **响应式**：支持不同屏幕尺寸

### 动画效果

```css
.fade-in-up {
  animation: fadeInUp 0.6s ease-out forwards;
  opacity: 0;
  transform: translateY(30px);
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

## 权限控制

### 用户角色

- **超级管理员**：可以管理所有部门
- **部门部长**：可以管理自己所在的部门
- **其他用户**：只能查看部门信息

### 操作权限

- 查看：所有认证用户
- 创建：超级管理员和部门部长
- 编辑：超级管理员和部门部长（仅自己部门）
- 删除：超级管理员和部门部长（仅自己部门）

## 响应式设计

### 断点设置

```css
@media (max-width: 768px) {
  .department-view {
    padding: var(--spacing-md);
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-bar {
    flex-direction: column;
  }
}
```

### 移动端适配

- 统计卡片垂直排列
- 操作栏垂直布局
- 部门卡片单列显示
- 触摸友好的交互

## 性能优化

### 懒加载

- 路由级别的代码分割
- 图片懒加载
- 分页加载数据

### 缓存策略

- 部门列表缓存
- 搜索结果缓存
- 详情数据缓存

## 错误处理

### 网络错误

- API调用失败提示
- 重试机制
- 离线状态处理

### 用户操作

- 表单验证
- 确认对话框
- 操作反馈

## 扩展功能

### 图表集成

可以集成图表库（如ECharts）来展示：
- 部门人员分布
- 部门业绩趋势
- 组织架构图

### 批量操作

- 批量删除部门
- 批量导入部门
- 批量分配成员

### 高级搜索

- 多条件组合搜索
- 搜索历史记录
- 搜索建议

## 开发指南

### 本地开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### 代码规范

- 使用ESLint进行代码检查
- 遵循Vue 3最佳实践
- 使用TypeScript类型注解（可选）

### 测试

- 单元测试：使用Vitest
- 组件测试：使用Vue Test Utils
- E2E测试：使用Playwright

## 部署说明

### 构建配置

```javascript
// vite.config.ts
export default defineConfig({
  build: {
    target: 'es2015',
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router'],
          elementPlus: ['element-plus']
        }
      }
    }
  }
})
```

### 环境配置

```bash
# 开发环境
VITE_API_BASE_URL=http://localhost:8000

# 生产环境
VITE_API_BASE_URL=https://api.example.com
```

## 常见问题

### Q: 如何修改主题颜色？
A: 修改CSS变量中的颜色值即可

### Q: 如何添加新的部门状态？
A: 在`departmentUtils.formatStatus`中添加新的状态映射

### Q: 如何集成后端API？
A: 修改`api/department.js`中的接口地址和参数

### Q: 如何添加新的统计指标？
A: 在`departmentUtils.calculateStats`中添加新的计算逻辑

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础CRUD功能
- 响应式设计
- 权限控制

### v1.1.0 (计划中)
- 图表集成
- 批量操作
- 高级搜索
- 性能优化

## 技术支持

如有问题或建议，请：
1. 查看本文档
2. 检查控制台错误
3. 联系开发团队

## 许可证

MIT License
