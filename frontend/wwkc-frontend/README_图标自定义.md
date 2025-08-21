# 图标和名称自定义说明

## 🎯 已完成的修改

### 1. 浏览器标题
- 已将浏览器标签页标题从 "Vite App" 改为 "智能库存管理系统"
- 修改位置：`index.html` 文件中的 `<title>` 标签

### 2. 网站图标 (Favicon)
- 已创建新的SVG格式图标：`public/favicon.svg`
- 图标设计：蓝色圆形背景 + 白色库存箱子图案
- 支持现代浏览器的SVG格式

### 3. Meta标签优化
- 添加了网站描述、关键词和作者信息
- 改善了搜索引擎优化和社交媒体分享效果

## 🔧 如何进一步自定义

### 1. 修改系统名称
如果您想修改系统名称，需要更新以下文件：

#### 登录页面名称
```vue
<!-- 文件：src/views/LoginView.vue -->
<h1 class="system-title">您的系统名称</h1>
<p class="system-subtitle">您的系统描述</p>
```

#### 侧边栏名称
```vue
<!-- 文件：src/App.vue -->
<h1 class="logo-text">您的系统简称</h1>
```

#### 浏览器标题
```html
<!-- 文件：index.html -->
<title>您的系统名称</title>
```

### 2. 自定义图标

#### 方法1：使用SVG图标（推荐）
- 修改 `public/favicon.svg` 文件
- 支持任意尺寸，清晰度高
- 现代浏览器完全支持

#### 方法2：使用ICO图标
- 创建 `public/favicon.ico` 文件
- 传统格式，兼容性最好
- 建议尺寸：16x16, 32x32, 48x48

#### 方法3：使用PNG图标
- 创建 `public/favicon.png` 文件
- 现代格式，支持透明背景
- 建议尺寸：32x32 或 64x64

### 3. 图标设计建议

#### 颜色搭配
```css
/* 主色调 */
--primary-color: #4A90E2;        /* 蓝色 */
--primary-light: #7BB3F0;        /* 浅蓝色 */
--primary-dark: #357ABD;         /* 深蓝色 */

/* 背景色 */
--background-color: #F5F7FA;     /* 浅灰蓝 */
--card-background: #FFFFFF;      /* 白色 */
```

#### 图标元素
- **库存管理**：箱子、货架、标签
- **数据分析**：图表、趋势线、仪表盘
- **商务风格**：简洁、现代、专业

## 🚀 快速修改步骤

### 1. 修改系统名称
```bash
# 1. 修改浏览器标题
sed -i 's/智能库存管理系统/您的系统名称/g' index.html

# 2. 修改登录页面标题
sed -i 's/智能库存管理系统/您的系统名称/g' src/views/LoginView.vue

# 3. 修改侧边栏名称
sed -i 's/WWKC/您的简称/g' src/App.vue
```

### 2. 替换图标
```bash
# 1. 备份原图标
cp public/favicon.svg public/favicon.svg.backup

# 2. 替换为新图标
cp 您的图标.svg public/favicon.svg

# 3. 如果需要ICO格式
# 使用在线工具将SVG转换为ICO
```

## 📱 多平台支持

### 1. iOS设备
```html
<!-- 添加到index.html的head部分 -->
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="apple-mobile-web-app-title" content="智能库存管理系统">
```

### 2. Android设备
```html
<!-- 添加到index.html的head部分 -->
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#4A90E2">
```

### 3. Windows设备
```html
<!-- 添加到index.html的head部分 -->
<meta name="msapplication-TileColor" content="#4A90E2">
<meta name="msapplication-TileImage" content="/mstile-144x144.png">
```

## 🎨 图标设计工具推荐

### 1. 在线工具
- **Favicon.io**: 生成各种格式的favicon
- **RealFaviconGenerator**: 专业的favicon生成器
- **SVGOMG**: SVG优化工具

### 2. 设计软件
- **Figma**: 免费在线设计工具
- **Adobe Illustrator**: 专业矢量图形设计
- **Inkscape**: 免费开源矢量图形编辑器

### 3. 图标资源
- **Feather Icons**: 简洁的图标集合
- **Heroicons**: 精美的SVG图标
- **Material Icons**: Google Material Design图标

## 🔍 测试验证

### 1. 本地测试
```bash
# 启动开发服务器
npm run dev

# 在浏览器中检查
# 1. 标签页标题是否正确
# 2. 图标是否显示
# 3. 收藏夹图标是否正确
```

### 2. 浏览器兼容性
- **Chrome**: 完全支持SVG和现代格式
- **Firefox**: 完全支持SVG和现代格式
- **Safari**: 完全支持SVG和现代格式
- **Edge**: 完全支持SVG和现代格式

### 3. 移动设备测试
- 在手机浏览器中测试图标显示
- 检查添加到主屏幕的效果
- 验证不同尺寸下的显示效果

## 📝 注意事项

1. **图标尺寸**: 建议提供多种尺寸的图标
2. **文件大小**: SVG图标通常比ICO小
3. **缓存问题**: 修改图标后可能需要清除浏览器缓存
4. **CDN部署**: 生产环境建议使用CDN加速图标加载

## 🤝 需要帮助？

如果您在自定义过程中遇到问题，可以：

1. 检查浏览器控制台是否有错误
2. 验证文件路径是否正确
3. 确认文件格式是否支持
4. 清除浏览器缓存后重试
