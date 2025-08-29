<script setup lang="ts">
import { ref, computed, onMounted, onErrorCaptured } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { 
  House, 
  Box, 
  User, 
  Shop, 
  Setting, 
  Bell, 
  ArrowDown, 
  Fold, 
  Expand,
  OfficeBuilding,
  ArrowRight,
  Document,
  Edit,
  ShoppingCart,
  Tools,
  Van,
  Picture,
  Upload,
  Money,
  Switch
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import LoadingPage from '@/components/LoadingPage.vue'

// 路由和状态管理
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 响应式数据
const sidebarCollapsed = ref(false)
const showLoading = ref(true)
const expandedMenus = ref<Set<string>>(new Set(['etsy'])) // 默认展开Etsy菜单

// 菜单配置
const menuConfig = [
  {
    key: 'dashboard',
    icon: House,
    label: '仪表盘',
    path: '/',
    type: 'link'
  },
  {
    key: 'inventory',
    icon: Box,
    label: '库存管理',
    path: '/inventory',
    type: 'link'
  },
  {
    key: 'users',
    icon: User,
    label: '用户管理',
    path: '/users',
    type: 'link'
  },
  {
    key: 'stores',
    icon: Shop,
    label: '店铺管理',
    path: '/stores',
    type: 'link'
  },
  {
    key: 'departments',
    icon: OfficeBuilding,
    label: '部门管理',
    path: '/departments',
    type: 'link'
  },
  {
    key: 'etsy',
    icon: Shop,
    label: 'Etsy管理',
    type: 'group',
    children: [
      {
        key: 'product-management',
        label: '产品管理',
        type: 'subgroup',
        children: [
          {
            key: 'product-registration',
            icon: Document,
            label: '产品登记表',
            path: '/etsy/product-registration'
          },
          {
            key: 'design-requirement',
            icon: Edit,
            label: '设计需求表',
            path: '/etsy/design-requirement'
          }
        ]
      },
      {
        key: 'order-management',
        label: '订单管理',
        type: 'subgroup',
        children: [
          {
            key: 'order-import-summary',
            icon: Document,
            label: '订单导入汇总表',
            path: '/etsy/order-import-summary'
          },
          {
            key: 'order-statistics',
            icon: Document,
            label: '订单统计表',
            path: '/etsy/order-statistics'
          }
        ]
      },
      {
        key: 'production-management',
        label: '生产管理',
        type: 'subgroup',
        children: [
          {
            key: 'purchase-requirement',
            icon: ShoppingCart,
            label: '采购需求表',
            path: '/etsy/purchase-requirement'
          },
          {
            key: 'production-requirement',
            icon: Tools,
            label: '生产需求表',
            path: '/etsy/production-requirement'
          }
        ]
      },
      {
        key: 'logistics',
        label: '物流管理',
        type: 'subgroup',
        children: [
          {
            key: 'shipping-delivery',
            icon: Van,
            label: '配货发货表',
            path: '/etsy/shipping-delivery'
          },
          {
            key: 'qr-code-label',
            icon: Picture,
            label: '二维码标签表',
            path: '/etsy/qr-code-label'
          }
        ]
      },
      {
        key: 'financial',
        label: '财务管理',
        type: 'subgroup',
        children: [
          {
            key: 'yuntu-export',
            icon: Upload,
            label: '云途导出表',
            path: '/etsy/yuntu-export'
          },
          {
            key: 'yuntu-deduction',
            icon: Money,
            label: '云途扣费表',
            path: '/etsy/yuntu-deduction'
          }
        ]
      },
      {
        key: 'store-info',
        label: '店铺信息',
        type: 'subgroup',
        children: [
          {
            key: 'store-information',
            icon: Shop,
            label: '店铺信息表',
            path: '/etsy/store-information'
          }
        ]
      }
    ]
  },
  {
    key: 'messages',
    icon: Bell,
    label: '消息和聊天室',
    path: '/messages',
    type: 'link'
  },
  {
    key: 'settings',
    icon: Setting,
    label: '系统设置',
    path: '/settings',
    type: 'link'
  }
]

// 全局错误处理
onErrorCaptured((error, instance, info) => {
  console.error('全局错误捕获:', error)
  console.error('错误信息:', info)
  
  // 如果是DOM引用错误，尝试重新渲染
  if (error.message?.includes('parentNode') || error.message?.includes('Cannot read properties of null')) {
    console.warn('检测到DOM引用错误，尝试恢复...')
    // 延迟重新渲染，避免无限循环
    setTimeout(() => {
      window.location.reload()
    }, 1000)
    return false // 阻止错误继续传播
  }
  
  // 其他错误显示用户友好的消息
  ElMessage.error('页面出现错误，请刷新重试')
  return false
})

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 切换菜单展开状态
const toggleMenu = (menuKey: string) => {
  if (expandedMenus.value.has(menuKey)) {
    expandedMenus.value.delete(menuKey)
  } else {
    expandedMenus.value.add(menuKey)
  }
}

// 检查菜单是否展开
const isMenuExpanded = (menuKey: string) => {
  return expandedMenus.value.has(menuKey)
}

// 检查路由是否激活
const isRouteActive = (path: string) => {
  return route.path.startsWith(path)
}

// 获取页面标题
const getPageTitle = () => {
  const titleMap: Record<string, string> = {
    'inventory': '库存管理',
    'users': '用户管理',
    'stores': '店铺管理',
    'departments': '部门管理',
    'etsy': 'Etsy管理',
    'etsy-product-registration': '产品登记表',
    'etsy-design-requirement': '设计需求表',
    'etsy-order-import-summary': '订单导入汇总表',
    'etsy-order-statistics': '订单统计表',
    'etsy-purchase-requirement': '采购需求表',
    'etsy-production-requirement': '生产需求表',
    'etsy-shipping-delivery': '配货发货表',
    'etsy-qr-code-label': '二维码标签表',
    'etsy-yuntu-export': '云途导出表',
    'etsy-yuntu-deduction': '云途扣费表',
    'etsy-store-information': '店铺信息表',
    'messages': '消息和聊天室',
    'settings': '系统设置'
  }
  return titleMap[route.name as string] || '页面'
}

// 处理用户命令
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      // 跳转到个人资料页面
      router.push('/profile')
      break
    case 'settings':
      // 跳转到设置页面
      router.push('/settings')
      break
    case 'logout':
      // 确认登出
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 调用后端登出接口
        try {
          await fetch('/api/auth/logout/', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${authStore.token}`,
              'Content-Type': 'application/json'
            }
          })
        } catch (error) {
          console.error('登出接口调用失败:', error)
        }
        
        // 清除本地认证信息
        authStore.logout()
        
        // 跳转到登录页
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}

// 加载完成事件处理
const onLoadingComplete = () => {
  showLoading.value = false
}

// 页面加载时的处理
onMounted(() => {
  // 初始化认证状态
  authStore.initAuth()
  
  // 检查是否已登录
  if (!authStore.isAuthenticated && route.name !== 'login') {
    router.push('/login')
  }
  
  // 模拟加载时间，实际项目中可以根据需要调整
  setTimeout(() => {
    showLoading.value = false
  }, 3000)
})
</script>

<template>
  <div id="app">
    <!-- 加载页面 -->
    <LoadingPage 
      v-if="showLoading" 
      :show="showLoading" 
      :duration="3000"
      @loading-complete="onLoadingComplete"
    />
    
    <!-- 登录页面不显示导航栏 -->
    <router-view v-if="$route.name === 'login' && !showLoading" />
    
    <!-- 其他页面显示完整布局 -->
    <div v-else-if="$route.name !== 'login' && !showLoading" class="app-layout">
      <!-- 侧边栏 -->
      <div class="sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
        <div class="sidebar-header">
          <div class="logo-container">
            <div class="logo-icon">
              <el-icon><Shop /></el-icon>
            </div>
            <h1 class="logo-text" v-if="!sidebarCollapsed">WWKC</h1>
          </div>
          <el-button
            type="text"
            class="collapse-btn"
            @click="toggleSidebar"
          >
            <el-icon><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
          </el-button>
        </div>
        
        <nav class="sidebar-nav">
          <!-- 渲染菜单 -->
          <template v-for="menu in menuConfig" :key="menu.key">
            <!-- 普通链接菜单 -->
            <router-link 
              v-if="menu.type === 'link'" 
              :to="menu.path" 
              class="nav-item" 
              active-class="active"
            >
              <el-icon><component :is="menu.icon" /></el-icon>
              <span v-if="!sidebarCollapsed">{{ menu.label }}</span>
            </router-link>
            
            <!-- 分组菜单 -->
            <div v-else-if="menu.type === 'group'" class="menu-group">
              <div 
                class="menu-header"
                :class="{ 'active': isRouteActive('/etsy') }"
                @click="toggleMenu(menu.key)"
              >
                <el-icon><component :is="menu.icon" /></el-icon>
                <span v-if="!sidebarCollapsed" class="menu-title">{{ menu.label }}</span>
                <el-icon 
                  v-if="!sidebarCollapsed" 
                  class="expand-arrow"
                  :class="{ 'expanded': isMenuExpanded(menu.key) }"
                >
                  <ArrowRight />
                </el-icon>
              </div>
              
              <!-- 二级菜单 -->
              <div 
                v-if="!sidebarCollapsed && isMenuExpanded(menu.key)" 
                class="submenu"
              >
                <template v-for="subMenu in menu.children" :key="subMenu.key">
                  <!-- 二级分组 -->
                  <div v-if="subMenu.type === 'subgroup'" class="submenu-group">
                    <div class="submenu-header">
                      <span class="submenu-title">{{ subMenu.label }}</span>
                    </div>
                    
                    <!-- 三级菜单项 -->
                    <div class="submenu-items">
                      <router-link 
                        v-for="item in subMenu.children"
                        :key="item.key"
                        :to="item.path"
                        class="submenu-item"
                        :class="{ 'active': isRouteActive(item.path) }"
                      >
                        <el-icon><component :is="item.icon" /></el-icon>
                        <span>{{ item.label }}</span>
                      </router-link>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </template>
        </nav>
      </div>

      <!-- 主内容区 -->
      <div class="main-content">
        <!-- 顶部导航栏 -->
        <header class="top-header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="$route.name !== 'home'">
                {{ getPageTitle() }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          
          <div class="header-right">
            <!-- 消息和聊天室 -->
            <el-badge :value="3" class="notification-badge">
              <router-link to="/messages" class="header-btn notification-link">
                <el-icon><Bell /></el-icon>
              </router-link>
            </el-badge>
            
            <!-- 用户信息 -->
            <el-dropdown @command="handleUserCommand" trigger="click">
              <div class="user-info">
                <el-avatar :size="32" :src="authStore.getUserAvatar()" />
                <div class="user-details" v-if="!sidebarCollapsed">
                  <div class="username">{{ authStore.getUserDisplayName() }}</div>
                  <div class="role">{{ authStore.getRoleDisplayName() }}</div>
                </div>
                <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人资料
                  </el-dropdown-item>
                  <el-dropdown-item command="settings">
                    <el-icon><Setting /></el-icon>
                    设置
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><Switch /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </header>

        <!-- 页面内容 -->
        <main class="page-content">
          <router-view />
        </main>
      </div>
    </div>
  </div>
</template>

<style scoped>
#app {
  height: 100vh;
  overflow: hidden;
}

.app-layout {
  display: flex;
  height: 100vh;
}

/* 侧边栏样式 */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: white;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-heavy);
}

.sidebar-collapsed {
  width: 80px;
}

.sidebar-header {
  padding: var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: white;
}

.collapse-btn {
  color: white;
  padding: 4px;
}

.sidebar-nav {
  flex: 1;
  padding: var(--spacing-lg) 0;
  overflow-y: auto;
}

/* 导航项样式 */
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border-left-color: white;
}

.nav-item .el-icon {
  font-size: 18px;
  min-width: 20px;
}

/* 菜单组样式 */
.menu-group {
  margin: var(--spacing-xs) 0;
}

.menu-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  position: relative;
}

.menu-header:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.menu-header.active {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border-left-color: white;
}

.menu-title {
  flex: 1;
  font-weight: 500;
}

.expand-arrow {
  transition: transform 0.3s ease;
  font-size: 12px;
}

.expand-arrow.expanded {
  transform: rotate(90deg);
}

/* 子菜单样式 */
.submenu {
  background: rgba(0, 0, 0, 0.1);
  margin-left: var(--spacing-md);
}

.submenu-group {
  margin: var(--spacing-xs) 0;
}

.submenu-header {
  padding: var(--spacing-sm) var(--spacing-lg);
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.submenu-items {
  margin-left: var(--spacing-md);
}

.submenu-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 13px;
  border-left: 2px solid transparent;
}

.submenu-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: white;
}

.submenu-item.active {
  background: rgba(255, 255, 255, 0.12);
  color: white;
  border-left-color: rgba(255, 255, 255, 0.8);
}

.submenu-item .el-icon {
  font-size: 14px;
  min-width: 16px;
}

/* 三级菜单的缩进和样式优化 */
.submenu-group .submenu-items {
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  margin-left: var(--spacing-md);
}

.submenu-group .submenu-item {
  padding-left: var(--spacing-xl);
  font-size: 12px;
  min-height: 32px;
}

.submenu-group .submenu-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(2px);
}

/* 菜单组之间的分隔 */
.menu-group + .menu-group {
  margin-top: var(--spacing-xs);
}

/* 滚动条样式 */
.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* 主内容区样式 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--background-color);
}

.top-header {
  height: 64px;
  background: white;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-xl);
  box-shadow: var(--shadow-light);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.notification-badge {
  margin-right: var(--spacing-sm);
}

.header-btn {
  color: var(--text-secondary);
  font-size: 18px;
}

.notification-link {
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.notification-link:hover {
  color: var(--primary-color);
  transform: scale(1.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  cursor: pointer;
  padding: var(--spacing-sm);
  border-radius: var(--border-radius);
  transition: all 0.3s ease;
}

.user-info:hover {
  background: var(--primary-ultra-light);
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.username {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.2;
}

.role {
  color: var(--text-secondary);
  font-size: 12px;
  line-height: 1.2;
}

.dropdown-arrow {
  color: var(--text-secondary);
  font-size: 12px;
}

.page-content {
  flex: 1;
  padding: var(--spacing-xl);
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar.show {
    transform: translateX(0);
  }
  
  .sidebar-collapsed {
    width: 260px;
  }
  
  .page-content {
    padding: var(--spacing-md);
  }
}

/* 动画效果 */
.sidebar {
  animation: slideInLeft 0.3s ease-out;
}

@keyframes slideInLeft {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

/* 面包屑样式 */
.el-breadcrumb {
  font-size: 14px;
}

/* 下拉菜单样式 */
.el-dropdown-menu {
  min-width: 160px;
}

.el-dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.el-dropdown-item .el-icon {
  font-size: 16px;
}

/* 滚动条样式 */
.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>
