<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { 
  House, 
  Box, 
  User, 
  Shop, 
  Setting, 
  Bell, 
  ArrowDown, 
  Fold, 
  Expand 
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

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 获取页面标题
const getPageTitle = () => {
  const titleMap: Record<string, string> = {
    'inventory': '库存管理',
    'users': '用户管理',
    'stores': '店铺管理',
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
          <router-link to="/" class="nav-item" active-class="active">
            <el-icon><House /></el-icon>
            <span v-if="!sidebarCollapsed">仪表盘</span>
          </router-link>
          
          <router-link to="/inventory" class="nav-item" active-class="active">
            <el-icon><Box /></el-icon>
            <span v-if="!sidebarCollapsed">库存管理</span>
          </router-link>
          
          <router-link to="/users" class="nav-item" active-class="active">
            <el-icon><User /></el-icon>
            <span v-if="!sidebarCollapsed">用户管理</span>
          </router-link>
          
          <router-link to="/stores" class="nav-item" active-class="active">
            <el-icon><Shop /></el-icon>
            <span v-if="!sidebarCollapsed">店铺管理</span>
          </router-link>
          
          <router-link to="/settings" class="nav-item" active-class="active">
            <el-icon><Setting /></el-icon>
            <span v-if="!sidebarCollapsed">系统设置</span>
          </router-link>
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
            <!-- 通知 -->
            <el-badge :value="3" class="notification-badge">
              <el-button type="text" class="header-btn">
                <el-icon><Bell /></el-icon>
              </el-button>
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
                    <el-icon><SwitchButton /></el-icon>
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
}

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
</style>
