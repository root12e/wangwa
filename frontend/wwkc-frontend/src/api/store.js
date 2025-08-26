import apiClient from './client'

// 店铺管理API
export const storeAPI = {
  // 获取店铺列表
  getStores: (params = {}) => {
    return apiClient.get('/api/stores/', { params })
  },

  // 获取店铺详情
  getStore: (id) => {
    return apiClient.get(`/api/stores/${id}/`)
  },

  // 创建店铺
  createStore: (data) => {
    return apiClient.post('/api/stores/', data)
  },

  // 更新店铺
  updateStore: (id, data) => {
    return apiClient.put(`/api/stores/${id}/`, data)
  },

  // 删除店铺
  deleteStore: (id) => {
    return apiClient.delete(`/api/stores/${id}/`)
  },

  // 获取店铺库存
  getStoreInventory: (storeId, params = {}) => {
    return apiClient.get(`/api/stores/${storeId}/inventory/`, { params })
  },

  // 获取店铺交易记录
  getStoreTransactions: (storeId, params = {}) => {
    return apiClient.get(`/api/stores/${storeId}/transactions/`, { params })
  },

  // 创建店铺交易记录
  createStoreTransaction: (storeId, data) => {
    return apiClient.post(`/api/stores/${storeId}/transactions/`, data)
  },

  // 获取店铺统计信息
  getStoreStatistics: (storeId) => {
    return apiClient.get(`/api/stores/${storeId}/statistics/`)
  },

  // 获取店铺员工
  getStoreEmployees: (storeId, params = {}) => {
    return apiClient.get(`/api/stores/${storeId}/employees/`, { params })
  },

  // 添加店铺员工
  addStoreEmployee: (storeId, data) => {
    return apiClient.post(`/api/stores/${storeId}/employees/`, data)
  },

  // 移除店铺员工
  removeStoreEmployee: (storeId, employeeId) => {
    return apiClient.delete(`/api/stores/${storeId}/employees/${employeeId}/`)
  },

  // 店铺状态变更
  changeStoreStatus: (storeId, status) => {
    return apiClient.patch(`/api/stores/${storeId}/`, { status })
  },

  // 店铺搜索
  searchStores: (params = {}) => {
    return apiClient.get('/api/stores/search/', { params })
  },

  // 获取部门店铺
  getDepartmentStores: (departmentId, params = {}) => {
    return apiClient.get(`/api/departments/${departmentId}/stores/`, { params })
  },

  // 店铺导入
  importStores: (data) => {
    return apiClient.post('/api/stores/import/', data)
  },

  // 店铺导出
  exportStores: (params = {}) => {
    return apiClient.get('/api/stores/export/', { params })
  }
}

// 导出所有API函数
export const {
  getStores,
  getStore,
  createStore,
  updateStore,
  deleteStore,
  getStoreInventory,
  getStoreTransactions,
  createStoreTransaction,
  getStoreStatistics,
  getStoreEmployees,
  addStoreEmployee,
  removeStoreEmployee,
  changeStoreStatus,
  searchStores,
  getDepartmentStores,
  importStores,
  exportStores
} = storeAPI
