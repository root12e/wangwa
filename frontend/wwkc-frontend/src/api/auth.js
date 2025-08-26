import apiClient from './client'

// 认证工具函数
export const authUtils = {
  // 保存认证数据到localStorage
  saveAuthData: ({ user, tokens }) => {
    if (tokens?.access) {
      localStorage.setItem('access_token', tokens.access)
    }
    if (tokens?.refresh) {
      localStorage.setItem('refresh_token', tokens.refresh)
    }
    if (user) {
      localStorage.setItem('user_info', JSON.stringify(user))
    }
  },

  // 从localStorage获取认证数据
  getAuthData: () => {
    const accessToken = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')
    const userInfo = localStorage.getItem('user_info')
    
    return {
      accessToken,
      refreshToken,
      userInfo: userInfo ? JSON.parse(userInfo) : null
    }
  },

  // 清除认证数据
  clearAuthData: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
  },

  // 检查token是否过期
  isTokenExpired: (token) => {
    if (!token) return true
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const currentTime = Date.now() / 1000
      return payload.exp < currentTime
    } catch (error) {
      return true
    }
  },

  // 获取token过期时间
  getTokenExpirationTime: (token) => {
    if (!token) return null
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.exp * 1000 // 转换为毫秒
    } catch (error) {
      return null
    }
  },

  // 检查token是否即将过期（默认5分钟内）
  isTokenExpiringSoon: (token, minutes = 5) => {
    if (!token) return true
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const currentTime = Date.now() / 1000
      const timeUntilExpiry = payload.exp - currentTime
      return timeUntilExpiry < (minutes * 60)
    } catch (error) {
      return true
    }
  },

  // 获取用户角色
  getUserRole: () => {
    const userInfo = localStorage.getItem('user_info')
    if (userInfo) {
      try {
        const user = JSON.parse(userInfo)
        return user.role
      } catch (error) {
        return null
      }
    }
    return null
  },

  // 检查用户是否有特定角色
  hasRole: (role) => {
    const userRole = authUtils.getUserRole()
    return userRole === role
  },

  // 检查用户是否有权限
  hasPermission: (permission) => {
    const userInfo = localStorage.getItem('user_info')
    if (userInfo) {
      try {
        const user = JSON.parse(userInfo)
        return user.permissions && user.permissions.includes(permission)
      } catch (error) {
        return false
      }
    }
    return false
  }
}

// 认证相关API
export const authAPI = {
  // 用户登录
  login: (credentials) => {
    return apiClient.post('/api/auth/login/', credentials)
  },

  // 用户注册
  register: (userData) => {
    return apiClient.post('/api/users/register/', userData)
  },

  // 刷新token
  refreshToken: (refreshToken) => {
    return apiClient.post('/api/auth/refresh/', { refresh: refreshToken })
  },

  // 用户登出
  logout: () => {
    return apiClient.post('/api/users/logout/')
  },

  // 获取当前用户信息
  getCurrentUser: () => {
    return apiClient.get('/api/users/me/')
  },

  // 更新用户信息
  updateProfile: (userData) => {
    return apiClient.put('/api/users/me/', userData)
  },

  // 修改密码
  changePassword: (passwordData) => {
    return apiClient.post('/api/users/change-password/', passwordData)
  },

  // 重置密码
  resetPassword: (email) => {
    return apiClient.post('/api/users/reset-password/', { email })
  },

  // 确认重置密码
  confirmResetPassword: (token, newPassword) => {
    return apiClient.post('/api/users/confirm-reset-password/', {
      token,
      new_password: newPassword
    })
  },

  // 验证邮箱
  verifyEmail: (token) => {
    return apiClient.post('/api/users/verify-email/', { token })
  },

  // 重新发送验证邮件
  resendVerificationEmail: (email) => {
    return apiClient.post('/api/users/resend-verification-email/', { email })
  },

  // 获取用户权限
  getUserPermissions: () => {
    return apiClient.get('/api/users/permissions/')
  },

  // 获取用户角色
  getUserRoles: () => {
    return apiClient.get('/api/users/roles/')
  },

  // 检查用户是否有特定权限
  checkPermission: (permission) => {
    return apiClient.post('/api/users/check-permission/', { permission })
  },

  // 获取登录历史
  getLoginHistory: (params = {}) => {
    return apiClient.get('/api/users/login-history/', { params })
  },

  // 获取活跃会话
  getActiveSessions: () => {
    return apiClient.get('/api/users/active-sessions/')
  },

  // 终止会话
  terminateSession: (sessionId) => {
    return apiClient.delete(`/api/users/sessions/${sessionId}/`)
  },

  // 终止所有会话
  terminateAllSessions: () => {
    return apiClient.delete('/api/users/sessions/')
  }
}

// 导出所有API函数
export const {
  login,
  register,
  refreshToken,
  logout,
  getCurrentUser,
  updateProfile,
  changePassword,
  resetPassword,
  confirmResetPassword,
  verifyEmail,
  resendVerificationEmail,
  getUserPermissions,
  getUserRoles,
  checkPermission,
  getLoginHistory,
  getActiveSessions,
  terminateSession,
  terminateAllSessions
} = authAPI
