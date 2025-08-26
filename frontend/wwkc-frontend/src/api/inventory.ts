import apiClient from './client'

// 库存管理API
export const inventoryAPI = {
  // 获取库存列表
  getInventories: (params = {}) => {
    return apiClient.get('/api/inventory/', { params })
  },

  // 获取库存详情
  getInventory: (id: string) => {
    return apiClient.get(`/api/inventory/${id}/`)
  },

  // 创建库存记录
  createInventory: (data: any) => {
    return apiClient.post('/api/inventory/', data)
  },

  // 更新库存记录
  updateInventory: (id: string, data: any) => {
    return apiClient.put(`/api/inventory/${id}/`, data)
  },

  // 删除库存记录
  deleteInventory: (id: string) => {
    return apiClient.delete(`/api/inventory/${id}/`)
  },

  // 调整库存
  adjustInventory: (id: string, data: any) => {
    return apiClient.post(`/api/inventory/${id}/adjust/`, data)
  },

  // 批量调整库存
  bulkAdjustInventory: (data: any) => {
    return apiClient.post('/api/inventory/bulk_adjust/', data)
  },

  // 获取库存摘要
  getInventorySummary: (params = {}) => {
    return apiClient.get('/api/inventory/summary/', { params })
  },

  // 获取库存交易记录
  getInventoryTransactions: (params = {}) => {
    return apiClient.get('/api/inventory-transactions/', { params })
  },

  // 获取交易统计
  getTransactionStatistics: (params = {}) => {
    return apiClient.get('/api/inventory-transactions/statistics/', { params })
  },

  // 获取库存消耗统计
  getInventoryConsumption: (params = {}) => {
    return apiClient.get('/api/inventory-consumption/', { params })
  },

  // 获取订单列表
  getOrders: (params = {}) => {
    return apiClient.get('/api/orders/', { params })
  },

  // 处理订单库存
  processOrderInventory: (data: any) => {
    return apiClient.post('/api/orders/process_inventory/', data)
  },

  // 处理所有未处理订单
  processAllUnprocessedOrders: () => {
    return apiClient.post('/api/orders/process_all_unprocessed/')
  },

  // 获取订单批次
  getOrderBatches: (params = {}) => {
    return apiClient.get('/api/order-batches/', { params })
  },

  // 获取工作流状态
  getWorkflowStatus: () => {
    return apiClient.get('/api/workflow/status/')
  },

  // 执行工作流
  executeWorkflow: () => {
    return apiClient.post('/api/workflow/execute/')
  },

  // 获取定时任务状态
  getSchedulerStatus: () => {
    return apiClient.get('/api/workflow/scheduler_status/')
  },

  // 强制执行工作流
  forceExecuteWorkflow: () => {
    return apiClient.post('/api/workflow/force_execute/')
  },

  // 更新执行间隔
  updateExecutionInterval: (data: any) => {
    return apiClient.post('/api/workflow/update_interval/', data)
  }
}

// 导出所有API函数
export const {
  getInventories,
  getInventory,
  createInventory,
  updateInventory,
  deleteInventory,
  adjustInventory,
  bulkAdjustInventory,
  getInventorySummary,
  getInventoryTransactions,
  getTransactionStatistics,
  getInventoryConsumption,
  getOrders,
  processOrderInventory,
  processAllUnprocessedOrders,
  getOrderBatches,
  getWorkflowStatus,
  executeWorkflow,
  getSchedulerStatus,
  forceExecuteWorkflow,
  updateExecutionInterval
} = inventoryAPI
