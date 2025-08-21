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
      meta: { requiresAuth: true }
    },
    {
      path: '/stores',
      name: 'stores',
      component: () => import('../views/StoresView.vue'),
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
  
  // 初始化认证状态
  if (!authStore.isAuthenticated) {
    authStore.initAuth()
  }
  
  // 检查路由是否需要认证
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // 未登录，重定向到登录页
      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }
    
    // 已登录，检查权限（这里可以根据需要添加更详细的权限检查）
    next()
  } else {
    // 不需要认证的路由
    if (to.name === 'login' && authStore.isAuthenticated) {
      // 已登录用户访问登录页，重定向到首页
      next({ name: 'home' })
      return
    }
    
    next()
  }
})

export default router
