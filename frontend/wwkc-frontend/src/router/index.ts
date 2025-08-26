import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/admin-invitation/:token',
      name: 'admin-invitation',
      component: () => import('../views/AdminInvitationView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/inventory',
      name: 'inventory',
      component: () => import('../views/InventoryView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('../views/UsersView.vue'),
      meta: { requiresAuth: true, roles: ['super_admin', 'department_manager'] }
    },
    {
      path: '/stores',
      name: 'stores',
      component: () => import('../views/StoresView.vue'),
      meta: { requiresAuth: true, roles: ['super_admin', 'department_manager', 'store_operator'] }
    },
    {
      path: '/departments',
      name: 'departments',
      component: () => import('../views/DepartmentView.vue'),
      meta: { requiresAuth: true, roles: ['super_admin', 'department_manager'] }
    },
    {
      path: '/messages',
      name: 'messages',
      component: () => import('../views/MessageView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
      meta: { requiresAuth: true }
    },
    // 捕获所有未匹配的路由，重定向到首页
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ],
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 只在开发环境下显示详细调试信息
  if (import.meta.env.DEV) {
    console.log('🔍 路由守卫:', {
      to: to.path,
      from: from.path,
      auth: authStore.isAuthenticated,
      userRole: authStore.user?.role,
      meta: to.meta
    })
  }
  
  // 初始化认证状态
  if (!authStore.isAuthenticated) {
    authStore.initAuth()
  }
  
  // 检查路由是否需要认证
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      console.log('❌ 未登录，重定向到登录页')
      // 未登录，重定向到登录页
      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }
    
    // 检查角色权限
    if (to.meta.roles && Array.isArray(to.meta.roles)) {
      const userRole = authStore.user?.role
      
      if (!userRole || !to.meta.roles.includes(userRole)) {
        console.log(`❌ 权限不足: 用户角色 ${userRole}，需要角色 ${to.meta.roles.join(' 或 ')}`)
        
        // 权限不足，重定向到首页
        next({ name: 'home' })
        return
      }
      
      if (import.meta.env.DEV) {
        console.log(`✅ 权限检查通过: ${userRole} -> ${to.meta.roles.join(' 或 ')}`)
      }
    } else {
      if (import.meta.env.DEV) {
        console.log('✅ 基础认证通过，无需角色检查')
      }
    }
    
    // 已登录且权限足够，允许访问
    next()
  } else {
    // 不需要认证的路由
    if (to.name === 'login' && authStore.isAuthenticated) {
      console.log('❌ 已登录用户访问登录页，重定向到首页')
      // 已登录用户访问登录页，重定向到首页
      next({ name: 'home' })
      return
    }
    
    if (import.meta.env.DEV) {
      console.log('✅ 无需认证，允许访问')
    }
    next()
  }
})

export default router
