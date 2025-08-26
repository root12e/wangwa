import apiClient from './client'

// 类型定义
export interface Department {
  id: string
  name: string
  description: string
  status: 'active' | 'inactive' | 'closed'
  created_at: string
  updated_at: string
  member_count?: number
  store_count?: number
  members?: any[]
  stores?: any[]
}

export interface DepartmentCreate {
  name: string
  description: string
  status?: 'active' | 'inactive' | 'closed'
}

export interface DepartmentUpdate {
  name?: string
  description?: string
  status?: 'active' | 'inactive' | 'closed'
}

export interface DepartmentListResponse {
  count: number
  next: string | null
  previous: string | null
  results: Department[]
}

/**
 * 部门管理API服务
 */
export const departmentAPI = {
  /**
   * 获取部门列表
   * @param params - 查询参数
   * @returns API响应
   */
  getDepartments(params: any = {}): Promise<{ data: DepartmentListResponse | Department[] }> {
    return apiClient.get('/api/departments/', { params })
  },

  /**
   * 获取部门详情
   * @param id - 部门ID
   * @returns API响应
   */
  getDepartment(id: string): Promise<{ data: Department }> {
    return apiClient.get(`/api/departments/${id}/`)
  },

  /**
   * 创建部门
   * @param data - 部门数据
   * @returns API响应
   */
  createDepartment(data: DepartmentCreate): Promise<{ data: Department }> {
    return apiClient.post('/api/departments/', data)
  },

  /**
   * 更新部门
   * @param id - 部门ID
   * @param data - 更新数据
   * @returns API响应
   */
  updateDepartment(id: string, data: DepartmentUpdate): Promise<{ data: Department }> {
    return apiClient.put(`/api/departments/${id}/`, data)
  },

  /**
   * 删除部门
   * @param id - 部门ID
   * @returns API响应
   */
  deleteDepartment(id: string): Promise<any> {
    return apiClient.delete(`/api/departments/${id}/`)
  },

  /**
   * 获取部门成员
   * @param id - 部门ID
   * @param params - 查询参数
   * @returns API响应
   */
  getDepartmentMembers(id: string, params: any = {}): Promise<any> {
    return apiClient.get(`/api/departments/${id}/members/`, { params })
  },

  /**
   * 获取部门店铺
   * @param id - 部门ID
   * @param params - 查询参数
   * @returns API响应
   */
  getDepartmentStores(id: string, params: any = {}): Promise<any> {
    return apiClient.get(`/api/departments/${id}/stores/`, { params })
  },

  /**
   * 获取部门统计信息
   * @param id - 部门ID
   * @returns API响应
   */
  getDepartmentStatistics(id: string): Promise<any> {
    return apiClient.get(`/departments/${id}/statistics/`)
  },

  /**
   * 获取我的部门
   * @returns API响应
   */
  getMyDepartment(): Promise<{ data: Department }> {
    return apiClient.get('/departments/my_department/')
  },

  /**
   * 搜索部门
   * @param query - 搜索关键词
   * @param params - 其他查询参数
   * @returns API响应
   */
  searchDepartments(query: string, params: any = {}): Promise<{ data: DepartmentListResponse | Department[] }> {
    return apiClient.get('/departments/search/', {
      params: { q: query, ...params }
    })
  }
}

/**
 * 部门管理工具函数
 */
export const departmentUtils = {
  /**
   * 格式化状态显示
   */
  formatStatus(status: string): string {
    const statusMap: Record<string, string> = {
      'active': '活跃',
      'inactive': '非活跃',
      'closed': '已关闭'
    }
    return statusMap[status] || status
  },

  /**
   * 获取状态标签类型
   */
  getStatusType(status: string): string {
    const typeMap: Record<string, string> = {
      'active': 'success',
      'inactive': 'warning',
      'closed': 'danger'
    }
    return typeMap[status] || 'info'
  },

  /**
   * 格式化日期
   */
  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('zh-CN')
  },

  /**
   * 计算部门统计信息
   */
  calculateStats(departments: Department[]) {
    return {
      total: departments.length,
      active: departments.filter(d => d.status === 'active').length,
      inactive: departments.filter(d => d.status === 'inactive').length,
      closed: departments.filter(d => d.status === 'closed').length
    }
  }
}
