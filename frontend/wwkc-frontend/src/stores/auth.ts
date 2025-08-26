import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI, authUtils } from '@/api/auth.js'

export interface User {
  id: string
  username: string
  email: string
  phone: string
  role: string
  role_display: string
  department?: any
  store?: any
  avatar?: string
}

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isAuthenticated = ref(false)
  const loading = ref(false)

  // 计算属性
  const isSuperAdmin = computed(() => user.value?.role === 'super_admin')
  const isDepartmentManager = computed(() => user.value?.role === 'department_manager')
  const isStoreOperator = computed(() => user.value?.role === 'store_operator')
  const isStaff = computed(() => user.value?.role === 'staff')

  // 获取存储的认证信息
  const initAuth = () => {
    const { accessToken, userInfo } = authUtils.getAuthData()
    
    if (accessToken && userInfo && !authUtils.isTokenExpired(accessToken)) {
      token.value = accessToken
      user.value = userInfo
      isAuthenticated.value = true
    } else {
      clearAuth()
    }
  }

  // 设置用户信息
  const setUser = (userData: User) => {
    user.value = userData
  }

  // 更新用户信息
  const updateUserInfo = (updateData: Partial<User>) => {
    if (user.value) {
      user.value = { ...user.value, ...updateData }
      // 同时更新本地存储
      const { accessToken } = authUtils.getAuthData()
      if (accessToken) {
        authUtils.saveAuthData({ user: user.value, tokens: { access: accessToken } })
      }
    }
  }

  // 设置token
  const setToken = (tokenValue: string) => {
    token.value = tokenValue
    isAuthenticated.value = true
  }

  // 清除认证信息
  const clearAuth = () => {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    authUtils.clearAuthData()
  }

  // 登录
  const login = async (credentials: { username_or_phone: string; password: string }) => {
    try {
      loading.value = true
      const response = await authAPI.login(credentials)
      if (response.data) {
        const { user: userData, tokens } = response.data
        authUtils.saveAuthData({ user: userData, tokens })
        setUser(userData)
        setToken(tokens.access)
        return { success: true, data: response.data }
      }
    } catch (error: any) {
      console.error('登录失败:', error)
      // 提取错误信息
      if (error.response?.data) {
        return { 
          success: false, 
          error: error.response.data.error || '登录失败',
          details: error.response.data.details || {},
          message: error.response.data.message || '登录失败，请重试'
        }
      }
      return { 
        success: false, 
        error: error.message || '登录失败',
        details: {},
        message: '登录失败，请重试'
      }
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (userData: any) => {
    try {
      loading.value = true
      const response = await authAPI.register(userData)
      return { success: true, data: response.data }
    } catch (error: any) {
      console.error('注册失败:', error)
      // 提取错误信息
      if (error.response?.data) {
        return { 
          success: false, 
          error: error.response.data.error || '注册失败',
          details: error.response.data.details || {},
          message: error.response.data.message || '注册失败，请重试'
        }
      }
      return { 
        success: false, 
        error: error.message || '注册失败',
        details: {},
        message: '注册失败，请重试'
      }
    } finally {
      loading.value = false
    }
  }

  // 发送验证码
  const sendVerificationCode = async (email: string) => {
    try {
      loading.value = true
      const response = await authAPI.sendVerificationCode({ email })
      return { success: true, data: response.data }
    } catch (error: any) {
      console.error('发送验证码失败:', error)
      // 提取错误信息
      if (error.response?.data) {
        return { 
          success: false, 
          error: error.response.data.error || '发送失败',
          details: error.response.data.details || {},
          message: error.response.data.message || '发送失败，请重试'
        }
      }
      return { 
        success: false, 
        error: error.message || '发送失败',
        details: {},
        message: '发送失败，请重试'
      }
    } finally {
      loading.value = false
    }
  }

  // 忘记密码
  const forgotPassword = async (email: string) => {
    try {
      loading.value = true
      const response = await authAPI.forgotPassword({ email })
      return { success: true, data: response.data }
    } catch (error: any) {
      console.error('忘记密码处理失败:', error)
      // 提取错误信息
      if (error.response?.data) {
        return { 
          success: false, 
          error: error.response.data.error || '发送失败',
          details: error.response.data.details || {},
          message: error.response.data.message || '发送失败，请重试'
        }
      }
      return { 
        success: false, 
        error: error.message || '发送失败',
        details: {},
        message: '发送失败，请重试'
      }
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      if (isAuthenticated.value) {
        await authAPI.logout()
      }
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      clearAuth()
    }
  }

  // 刷新用户信息
  const refreshUserInfo = async () => {
    try {
      if (!isAuthenticated.value) return
      
      const response = await authAPI.getUserProfile()
      if (response.data) {
        setUser(response.data)
        // 更新localStorage中的用户信息
        localStorage.setItem('user_info', JSON.stringify(response.data))
      }
    } catch (error) {
      console.error('刷新用户信息失败:', error)
      // 如果获取用户信息失败，可能是token过期，清除认证信息
      clearAuth()
    }
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
    loading,
    
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
    login,
    register,
    sendVerificationCode,
    forgotPassword,
    logout,
    refreshUserInfo,
    updateUserInfo,
    hasPermission,
    canManageUser,
    canManageDepartment,
    canManageStore,
    getUserAvatar,
    getUserDisplayName,
    getRoleDisplayName
  }
})
