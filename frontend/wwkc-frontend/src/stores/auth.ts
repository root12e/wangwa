import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: number
  username: string
  email: string
  phone: string
  role: string
  role_display: string
  department?: any
  store?: any
}

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isAuthenticated = ref(false)

  // 计算属性
  const isSuperAdmin = computed(() => user.value?.role === 'super_admin')
  const isDepartmentManager = computed(() => user.value?.role === 'department_manager')
  const isStoreOperator = computed(() => user.value?.role === 'store_operator')
  const isStaff = computed(() => user.value?.role === 'staff')

  // 获取存储的认证信息
  const initAuth = () => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    
    if (storedToken && storedUser) {
      try {
        token.value = storedToken
        user.value = JSON.parse(storedUser)
        isAuthenticated.value = true
      } catch (error) {
        console.error('解析存储的用户信息失败:', error)
        clearAuth()
      }
    }
  }

  // 设置用户信息
  const setUser = (userData: User) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  // 设置token
  const setToken = (tokenValue: string) => {
    token.value = tokenValue
    localStorage.setItem('token', tokenValue)
    isAuthenticated.value = true
  }

  // 清除认证信息
  const clearAuth = () => {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('rememberMe')
  }

  // 登出
  const logout = () => {
    clearAuth()
  }

  // 检查权限
  const hasPermission = (requiredRole: string | string[]) => {
    if (!isAuthenticated.value || !user.value) {
      return false
    }

    if (Array.isArray(requiredRole)) {
      return requiredRole.includes(user.value.role)
    }

    return user.value.role === requiredRole
  }

  // 检查是否可以管理用户
  const canManageUser = (targetUser?: User) => {
    if (!isAuthenticated.value || !user.value) {
      return false
    }

    // 超级管理员可以管理所有用户
    if (user.value.role === 'super_admin') {
      return true
    }

    // 部门部长可以管理本部门用户
    if (user.value.role === 'department_manager' && user.value.department) {
      return targetUser?.department?.id === user.value.department.id
    }

    // 店铺运营可以管理本店铺用户
    if (user.value.role === 'store_operator' && user.value.store) {
      return targetUser?.store?.id === user.value.store.id
    }

    // 普通员工只能管理自己
    if (user.value.role === 'staff') {
      return targetUser?.id === user.value.id
    }

    return false
  }

  // 检查是否可以管理部门
  const canManageDepartment = (targetDepartment?: any) => {
    if (!isAuthenticated.value || !user.value) {
      return false
    }

    // 超级管理员可以管理所有部门
    if (user.value.role === 'super_admin') {
      return true
    }

    // 部门部长可以管理本部门
    if (user.value.role === 'department_manager' && user.value.department) {
      return targetDepartment?.id === user.value.department.id
    }

    return false
  }

  // 检查是否可以管理店铺
  const canManageStore = (targetStore?: any) => {
    if (!isAuthenticated.value || !user.value) {
      return false
    }

    // 超级管理员可以管理所有店铺
    if (user.value.role === 'super_admin') {
      return true
    }

    // 部门部长可以管理本部门店铺
    if (user.value.role === 'department_manager' && user.value.department) {
      return targetStore?.department?.id === user.value.department.id
    }

    // 店铺运营可以管理本店铺
    if (user.value.role === 'store_operator' && user.value.store) {
      return targetStore?.id === user.value.store.id
    }

    return false
  }

  // 获取用户头像
  const getUserAvatar = () => {
    if (user.value?.avatar) {
      return user.value.avatar
    }
    
    // 根据角色返回默认头像
    const roleAvatars = {
      'super_admin': 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
      'department_manager': 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
      'store_operator': 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
      'staff': 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
    }
    
    return roleAvatars[user.value?.role as keyof typeof roleAvatars] || roleAvatars.staff
  }

  // 获取用户显示名称
  const getUserDisplayName = () => {
    if (user.value?.username) {
      return user.value.username
    }
    return '用户'
  }

  // 获取角色显示名称
  const getRoleDisplayName = () => {
    if (user.value?.role_display) {
      return user.value.role_display
    }
    
    const roleNames = {
      'super_admin': '超级管理员',
      'department_manager': '部门部长',
      'store_operator': '店铺运营',
      'staff': '普通员工'
    }
    
    return roleNames[user.value?.role as keyof typeof roleNames] || '未知角色'
  }

  return {
    // 状态
    user,
    token,
    isAuthenticated,
    
    // 计算属性
    isSuperAdmin,
    isDepartmentManager,
    isStoreOperator,
    isStaff,
    
    // 方法
    initAuth,
    setUser,
    setToken,
    clearAuth,
    logout,
    hasPermission,
    canManageUser,
    canManageDepartment,
    canManageStore,
    getUserAvatar,
    getUserDisplayName,
    getRoleDisplayName
  }
})
