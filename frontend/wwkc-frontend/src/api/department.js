import apiClient from './client'

// 部门管理API
export const departmentAPI = {
  // 获取部门列表
  getDepartments: (params = {}) => {
    return apiClient.get('/api/departments/', { params })
  },

  // 获取部门详情
  getDepartment: (id) => {
    return apiClient.get(`/api/departments/${id}/`)
  },

  // 创建部门
  createDepartment: (data) => {
    return apiClient.post('/api/departments/', data)
  },

  // 更新部门
  updateDepartment: (id, data) => {
    return apiClient.put(`/api/departments/${id}/`, data)
  },

  // 删除部门
  deleteDepartment: (id) => {
    return apiClient.delete(`/api/departments/${id}/`)
  },

  // 获取部门成员
  getDepartmentMembers: (id, params = {}) => {
    return apiClient.get(`/api/departments/${id}/members/`, { params })
  },

  // 添加部门成员
  addDepartmentMember: (id, data) => {
    return apiClient.post(`/api/departments/${id}/members/`, data)
  },

  // 移除部门成员
  removeDepartmentMember: (id, memberId) => {
    return apiClient.delete(`/api/departments/${id}/members/${memberId}/`)
  },

  // 获取部门店铺
  getDepartmentStores: (id, params = {}) => {
    return apiClient.get(`/api/departments/${id}/stores/`, { params })
  },

  // 添加部门店铺
  addDepartmentStore: (id, data) => {
    return apiClient.post(`/api/departments/${id}/stores/`, data)
  },

  // 移除部门店铺
  removeDepartmentStore: (id, storeId) => {
    return apiClient.delete(`/api/departments/${id}/stores/${storeId}/`)
  },

  // 获取部门统计信息
  getDepartmentStatistics: (id) => {
    return apiClient.get(`/api/departments/${id}/statistics/`)
  },

  // 部门搜索
  searchDepartments: (params = {}) => {
    return apiClient.get('/api/departments/search/', { params })
  },

  // 获取部门层级结构
  getDepartmentHierarchy: () => {
    return apiClient.get('/api/departments/hierarchy/')
  },

  // 移动部门位置
  moveDepartment: (id, data) => {
    return apiClient.post(`/api/departments/${id}/move/`, data)
  },

  // 获取部门权限
  getDepartmentPermissions: (id) => {
    return apiClient.get(`/api/departments/${id}/permissions/`)
  },

  // 设置部门权限
  setDepartmentPermissions: (id, data) => {
    return apiClient.post(`/api/departments/${id}/permissions/`, data)
  },

  // 部门导入
  importDepartments: (data) => {
    return apiClient.post('/api/departments/import/', data)
  },

  // 部门导出
  exportDepartments: (params = {}) => {
    return apiClient.get('/api/departments/export/', { params })
  }
}

// 导出所有API函数
export const {
  getDepartments,
  getDepartment,
  createDepartment,
  updateDepartment,
  deleteDepartment,
  getDepartmentMembers,
  addDepartmentMember,
  removeDepartmentMember,
  getDepartmentStores,
  addDepartmentStore,
  removeDepartmentStore,
  getDepartmentStatistics,
  searchDepartments,
  getDepartmentHierarchy,
  moveDepartment,
  getDepartmentPermissions,
  setDepartmentPermissions,
  importDepartments,
  exportDepartments
} = departmentAPI
