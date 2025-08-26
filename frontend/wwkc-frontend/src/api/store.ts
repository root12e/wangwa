import apiClient from './client'

// 店铺相关接口
export interface Store {
  id: string
  name: string
  code: string
  address: string
  phone: string
  email?: string
  manager?: {
    id: string
    username: string
    phone: string
    email: string
  }
  department: {
    id: string
    name: string
  }
  status: 'active' | 'inactive' | 'closed' | 'maintenance'
  description?: string
  business_hours?: string
  employee_count: number
  active_employee_count: number
  created_at: string
  updated_at: string
}

export interface StoreCreate {
  name: string
  code: string
  address: string
  phone: string
  email?: string
  manager_id?: string
  department_id: string
  status?: 'active' | 'inactive' | 'closed' | 'maintenance'
  description?: string
  business_hours?: string
}

export interface StoreUpdate {
  name?: string
  code?: string
  address?: string
  phone?: string
  email?: string
  manager_id?: string
  department_id?: string
  status?: 'active' | 'inactive' | 'closed' | 'maintenance'
  description?: string
  business_hours?: string
}

export interface StoreStatistics {
  total_stores: number
  active_stores: number
  total_employees: number
  total_inventory_items: number
  total_transactions: number
  total_transaction_amount: number
}

// 库存相关接口
export interface StoreInventory {
  id: string
  store: Store
  product_name: string
  product_code: string
  quantity: number
  unit_price: number
  min_stock: number
  max_stock: number
  created_at: string
  updated_at: string
}

export interface InventoryCreate {
  store_id: string
  product_name: string
  product_code: string
  quantity: number
  unit_price: number
  min_stock?: number
  max_stock?: number
}

export interface InventoryUpdate {
  product_name?: string
  product_code?: string
  quantity?: number
  unit_price?: number
  min_stock?: number
  max_stock?: number
}

export interface StockAdjustment {
  adjustment: number
  reason?: string
}

// 交易记录相关接口
export interface StoreTransaction {
  id: string
  store: Store
  transaction_type: 'sale' | 'purchase' | 'return' | 'adjustment'
  amount: number
  description?: string
  operator?: {
    id: string
    username: string
    phone: string
    email: string
  }
  created_at: string
}

export interface TransactionCreate {
  store_id: string
  transaction_type: 'sale' | 'purchase' | 'return' | 'adjustment'
  amount: number
  description?: string
  operator_id?: string
}

export interface DailySummary {
  date: string
  summary: Array<{
    transaction_type: string
    count: number
    total_amount: number
  }>
  total_count: number
  total_amount: number
}

export interface MonthlyReport {
  year: number
  month: number
  daily_summary: Array<{
    day: string
    count: number
    total_amount: number
  }>
  total_count: number
  total_amount: number
}

// 店铺管理API
export const storeApi = {
  // 获取店铺列表
  getStores: (params?: {
    page?: number
    page_size?: number
    search?: string
    status?: string
    department?: string
    manager?: string
  }) => {
    return apiClient.get<{
      count: number
      next: string | null
      previous: string | null
      results: Store[]
    }>('/api/stores/', { params })
  },

  // 获取店铺详情
  getStore: (id: string) => {
    return apiClient.get<Store>(`/api/stores/${id}/`)
  },

  // 创建店铺
  createStore: (data: StoreCreate) => {
    return apiClient.post<Store>('/api/stores/', data)
  },

  // 更新店铺
  updateStore: (id: string, data: StoreUpdate) => {
    return apiClient.patch<Store>(`/api/stores/${id}/`, data)
  },

  // 删除店铺
  deleteStore: (id: string) => {
    return apiClient.delete(`/api/stores/${id}/`)
  },

  // 获取我的店铺
  getMyStores: () => {
    return apiClient.get<Store | Store[]>('/api/stores/my_stores/')
  },

  // 更改店铺状态
  changeStoreStatus: (id: string, status: string) => {
    return apiClient.post<Store>(`/api/stores/${id}/change_status/`, { status })
  },

  // 获取店铺统计
  getStoreStatistics: () => {
    return apiClient.get<StoreStatistics>('/api/stores/statistics/')
  }
}

// 库存管理API
export const inventoryApi = {
  // 获取库存列表
  getInventories: (params?: {
    page?: number
    page_size?: number
    search?: string
    store?: string
    product_code?: string
  }) => {
    return apiClient.get<{
      count: number
      next: string | null
      previous: string | null
      results: StoreInventory[]
    }>('/api/store-inventory/', { params })
  },

  // 获取库存详情
  getInventory: (id: string) => {
    return apiClient.get<StoreInventory>(`/api/store-inventory/${id}/`)
  },

  // 创建库存记录
  createInventory: (data: InventoryCreate) => {
    return apiClient.post<StoreInventory>('/api/store-inventory/', data)
  },

  // 更新库存
  updateInventory: (id: string, data: InventoryUpdate) => {
    return apiClient.patch<StoreInventory>(`/api/store-inventory/${id}/`, data)
  },

  // 删除库存记录
  deleteInventory: (id: string) => {
    return apiClient.delete(`/api/store-inventory/${id}/`)
  },

  // 调整库存数量
  adjustStock: (id: string, data: StockAdjustment) => {
    return apiClient.post<StoreInventory>(`/api/store-inventory/${id}/adjust_stock/`, data)
  },

  // 获取低库存商品
  getLowStock: () => {
    return apiClient.get<StoreInventory[]>('/api/store-inventory/low_stock/')
  }
}

// 交易记录API
export const transactionApi = {
  // 获取交易记录列表
  getTransactions: (params?: {
    page?: number
    page_size?: number
    search?: string
    store?: string
    transaction_type?: string
    operator?: string
  }) => {
    return apiClient.get<{
      count: number
      next: string | null
      previous: string | null
      results: StoreTransaction[]
    }>('/api/store-transactions/', { params })
  },

  // 获取交易记录详情
  getTransaction: (id: string) => {
    return apiClient.get<StoreTransaction>(`/api/store-transactions/${id}/`)
  },

  // 创建交易记录
  createTransaction: (data: TransactionCreate) => {
    return apiClient.post<StoreTransaction>('/api/store-transactions/', data)
  },

  // 删除交易记录
  deleteTransaction: (id: string) => {
    return apiClient.delete(`/api/store-transactions/${id}/`)
  },

  // 获取每日汇总
  getDailySummary: (date?: string) => {
    const params = date ? { date } : {}
    return apiClient.get<DailySummary>('/api/store-transactions/daily_summary/', { params })
  },

  // 获取月度报告
  getMonthlyReport: (year?: number, month?: number) => {
    const params: Record<string, number> = {}
    if (year) params.year = year
    if (month) params.month = month
    return apiClient.get<MonthlyReport>('/api/store-transactions/monthly_report/', { params })
  }
}

// 导出常用的店铺管理函数
export const getStores = storeApi.getStores
export const getStore = storeApi.getStore
export const createStore = storeApi.createStore
export const updateStore = storeApi.updateStore
export const deleteStore = storeApi.deleteStore
export const getStoreStatistics = storeApi.getStoreStatistics
