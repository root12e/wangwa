// API基础配置
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// API端点
export const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: '/api/auth/login/',
    REGISTER: '/api/auth/register/',
    LOGOUT: '/api/auth/logout/',
    SEND_VERIFICATION_CODE: '/api/auth/send-verification-code/',
    FORGOT_PASSWORD: '/api/auth/forgot-password/',
    RESET_PASSWORD: '/api/auth/reset-password/',
  },
  
  // 用户相关
  USERS: {
    LIST: '/api/users/',
    DETAIL: (id: string | number) => `/api/users/${id}/`,
    PROFILE: '/api/users/profile/',
    CHANGE_PASSWORD: '/api/users/change-password/',
  },
  
  // 部门相关
  DEPARTMENTS: {
    LIST: '/api/departments/',
    DETAIL: (id: string | number) => `/api/departments/${id}/`,
  },
  
  // 店铺相关
  STORES: {
    LIST: '/api/stores/',
    DETAIL: (id: string | number) => `/api/stores/${id}/`,
  },
  
  // 库存相关
  INVENTORY: {
    LIST: '/api/inventory/',
    DETAIL: (id: string | number) => `/api/inventory/${id}/`,
    CATEGORIES: '/api/inventory/categories/',
    SUPPLIERS: '/api/inventory/suppliers/',
  }
}

// 请求配置
export const REQUEST_CONFIG = {
  TIMEOUT: 10000,
  RETRY_TIMES: 3,
  RETRY_DELAY: 1000,
}

// HTTP状态码
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
}

// 错误消息
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  TIMEOUT_ERROR: '请求超时，请稍后重试',
  SERVER_ERROR: '服务器内部错误，请稍后重试',
  UNAUTHORIZED: '登录已过期，请重新登录',
  FORBIDDEN: '没有权限访问该资源',
  NOT_FOUND: '请求的资源不存在',
  VALIDATION_ERROR: '输入数据有误，请检查后重试',
  UNKNOWN_ERROR: '未知错误，请稍后重试',
}

// 请求拦截器配置
export const REQUEST_INTERCEPTORS = {
  // 添加认证头
  addAuthHeader: (config: any, token: string | null) => {
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  
  // 添加内容类型
  addContentType: (config: any) => {
    if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json'
    }
    return config
  },
  
  // 添加时间戳
  addTimestamp: (config: any) => {
    config.headers['X-Request-Time'] = Date.now().toString()
    return config
  }
}

// 响应拦截器配置
export const RESPONSE_INTERCEPTORS = {
  // 处理认证错误
  handleAuthError: (error: any) => {
    if (error.response?.status === HTTP_STATUS.UNAUTHORIZED) {
      // 清除本地认证信息
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // 跳转到登录页
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
  
  // 处理网络错误
  handleNetworkError: (error: any) => {
    if (!error.response) {
      error.message = ERROR_MESSAGES.NETWORK_ERROR
    }
    return Promise.reject(error)
  },
  
  // 处理超时错误
  handleTimeoutError: (error: any) => {
    if (error.code === 'ECONNABORTED') {
      error.message = ERROR_MESSAGES.TIMEOUT_ERROR
    }
    return Promise.reject(error)
  }
}

// 构建完整的API URL
export const buildApiUrl = (endpoint: string): string => {
  return `${API_BASE_URL}${endpoint}`
}

// 检查响应状态
export const checkResponseStatus = (response: Response): boolean => {
  return response.ok
}

// 解析响应数据
export const parseResponseData = async (response: Response): Promise<any> => {
  try {
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return await response.json()
    }
    return await response.text()
  } catch (error) {
    console.error('解析响应数据失败:', error)
    throw new Error('响应数据解析失败')
  }
}

// 处理API错误
export const handleApiError = (error: any): string => {
  if (error.response) {
    const { status, data } = error.response
    
    switch (status) {
      case HTTP_STATUS.BAD_REQUEST:
        return data?.message || ERROR_MESSAGES.VALIDATION_ERROR
      case HTTP_STATUS.UNAUTHORIZED:
        return ERROR_MESSAGES.UNAUTHORIZED
      case HTTP_STATUS.FORBIDDEN:
        return ERROR_MESSAGES.FORBIDDEN
      case HTTP_STATUS.NOT_FOUND:
        return ERROR_MESSAGES.NOT_FOUND
      case HTTP_STATUS.UNPROCESSABLE_ENTITY:
        return data?.message || ERROR_MESSAGES.VALIDATION_ERROR
      case HTTP_STATUS.INTERNAL_SERVER_ERROR:
        return ERROR_MESSAGES.SERVER_ERROR
      default:
        return data?.message || ERROR_MESSAGES.UNKNOWN_ERROR
    }
  }
  
  if (error.request) {
    return ERROR_MESSAGES.NETWORK_ERROR
  }
  
  return error.message || ERROR_MESSAGES.UNKNOWN_ERROR
}
