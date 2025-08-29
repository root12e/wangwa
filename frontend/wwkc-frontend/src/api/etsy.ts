import apiClient from './client'

// 分页参数接口
export interface PaginationParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
  filters?: Record<string, any>
}

// 分页响应接口
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
  page_info: {
    current_page: number
    total_pages: number
    page_size: number
    total_count: number
  }
}

// Redis缓存状态接口
export interface CacheStatus {
  is_cached: boolean
  cache_key: string
  cache_ttl: number
  last_sync: string
  sync_status: 'idle' | 'syncing' | 'completed' | 'failed'
}

// Etsy产品登记表API
export const etsyProductRegistrationAPI = {
  // 获取列表（支持分页和缓存）
  getList: (params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/product-registration/', { params }),
  
  // 获取详情
  getDetail: (id: number) => apiClient.get(`/api/etsy/product-registration/${id}/`),
  
  // 创建
  create: (data: any) => apiClient.post('/api/etsy/product-registration/', data),
  
  // 更新
  update: (id: number, data: any) => apiClient.put(`/api/etsy/product-registration/${id}/`, data),
  
  // 删除
  delete: (id: number) => apiClient.delete(`/api/etsy/product-registration/${id}/`),
  
  // 批量创建（优化版本）
  bulkCreate: (data: any) => apiClient.post('/api/etsy/product-registration/bulk_create/', data, {
    timeout: 30000, // 30秒超时
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  
  // 批量更新（优化版本）
  bulkUpdate: (data: any) => apiClient.post('/api/etsy/product-registration/bulk_update/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  
  // 批量删除（优化版本）
  bulkDelete: (data: any) => apiClient.post('/api/etsy/product-registration/bulk_delete/', data, {
    timeout: 15000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  
  // 下载模板
  downloadTemplate: () => apiClient.get('/api/etsy/product-registration/download_template/', { responseType: 'blob' }),
  
  // 导入数据（优化版本）
  importData: (file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/api/etsy/product-registration/import_data/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000, // 60秒超时
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    })
  },
  
  // 根据店铺筛选（支持分页）
  getByStore: (store: string, params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/product-registration/by_store/', { 
    params: { store, ...params } 
  }),
  
  // 获取统计信息（支持缓存）
  getStatistics: () => apiClient.get('/api/etsy/product-registration/statistics/'),
  
  // 获取库存预警（支持分页）
  getInventoryWarning: (params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/product-registration/inventory_warning/', { params }),
  
  // 导出Excel（优化版本）
  exportExcel: (params?: any) => apiClient.get('/api/etsy/product-registration/export_excel/', { 
    params, 
    responseType: 'blob',
    timeout: 60000
  }),
  
  // 手动同步数据
  syncData: () => apiClient.post('/api/etsy/product-registration/sync_data/'),
  
  // 获取缓存状态
  getCacheStatus: () => apiClient.get<CacheStatus>('/api/etsy/product-registration/cache_status/'),
  
  // 清除缓存
  clearCache: () => apiClient.post('/api/etsy/product-registration/clear_cache/')
}

// Etsy订单导入汇总表API
export const etsyOrderImportSummaryAPI = {
  getList: (params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/order-import-summary/', { params }),
  getDetail: (id: number) => apiClient.get(`/api/etsy/order-import-summary/${id}/`),
  create: (data: any) => apiClient.post('/api/etsy/order-import-summary/', data),
  update: (id: number, data: any) => apiClient.put(`/api/etsy/order-import-summary/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/api/etsy/order-import-summary/${id}/`),
  bulkCreate: (data: any) => apiClient.post('/api/etsy/order-import-summary/bulk_create/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkUpdate: (data: any) => apiClient.post('/api/etsy/order-import-summary/bulk_update/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkDelete: (data: any) => apiClient.post('/api/etsy/order-import-summary/bulk_delete/', data, {
    timeout: 15000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  getStatistics: () => apiClient.get('/api/etsy/order-import-summary/statistics/'),
  exportExcel: (params?: any) => apiClient.get('/api/etsy/order-import-summary/export_excel/', { 
    params, 
    responseType: 'blob',
    timeout: 60000
  }),
  syncData: () => apiClient.post('/api/etsy/order-import-summary/sync_data/'),
  getCacheStatus: () => apiClient.get<CacheStatus>('/api/etsy/order-import-summary/cache_status/'),
  clearCache: () => apiClient.post('/api/etsy/order-import-summary/clear_cache/')
}

// Etsy订单统计API
export const etsyOrderStatisticsAPI = {
  getList: (params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/order-statistics/', { params }),
  getDetail: (id: number) => apiClient.get(`/api/etsy/order-statistics/${id}/`),
  create: (data: any) => apiClient.post('/api/etsy/order-statistics/', data),
  update: (id: number, data: any) => apiClient.put(`/api/etsy/order-statistics/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/api/etsy/order-statistics/${id}/`),
  bulkCreate: (data: any) => apiClient.post('/api/etsy/order-statistics/bulk_create/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkUpdate: (data: any) => apiClient.post('/api/etsy/order-statistics/bulk_update/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkDelete: (data: any) => apiClient.post('/api/etsy/order-statistics/bulk_delete/', data, {
    timeout: 15000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  getStatistics: () => apiClient.get('/api/etsy/order-statistics/statistics/'),
  exportExcel: (params?: any) => apiClient.get('/api/etsy/order-statistics/export_excel/', { 
    params, 
    responseType: 'blob',
    timeout: 60000
  }),
  syncData: () => apiClient.post('/api/etsy/order-statistics/sync_data/'),
  getCacheStatus: () => apiClient.get<CacheStatus>('/api/etsy/order-statistics/cache_status/'),
  clearCache: () => apiClient.post('/api/etsy/order-statistics/clear_cache/')
}

// Etsy设计需求API
export const etsyDesignRequirementAPI = {
  getList: (params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/design-requirement/', { params }),
  getDetail: (id: number) => apiClient.get(`/api/etsy/design-requirement/${id}/`),
  create: (data: any) => apiClient.post('/api/etsy/design-requirement/', data),
  update: (id: number, data: any) => apiClient.put(`/api/etsy/design-requirement/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/api/etsy/design-requirement/${id}/`),
  bulkCreate: (data: any) => apiClient.post('/api/etsy/design-requirement/bulk_create/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkUpdate: (data: any) => apiClient.post('/api/etsy/design-requirement/bulk_update/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkDelete: (data: any) => apiClient.post('/api/etsy/design-requirement/bulk_delete/', data, {
    timeout: 15000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  getStatistics: () => apiClient.get('/api/etsy/design-requirement/statistics/'),
  exportExcel: (params?: any) => apiClient.get('/api/etsy/design-requirement/export_excel/', { 
    params, 
    responseType: 'blob',
    timeout: 60000
  }),
  syncData: () => apiClient.post('/api/etsy/design-requirement/sync_data/'),
  getCacheStatus: () => apiClient.get<CacheStatus>('/api/etsy/design-requirement/cache_status/'),
  clearCache: () => apiClient.post('/api/etsy/design-requirement/clear_cache/')
}

// Etsy采购需求API
export const etsyPurchaseRequirementAPI = {
  getList: (params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/purchase-requirement/', { params }),
  getDetail: (id: number) => apiClient.get(`/api/etsy/purchase-requirement/${id}/`),
  create: (data: any) => apiClient.post('/api/etsy/purchase-requirement/', data),
  update: (id: number, data: any) => apiClient.put(`/api/etsy/purchase-requirement/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/api/etsy/purchase-requirement/${id}/`),
  bulkCreate: (data: any) => apiClient.post('/api/etsy/purchase-requirement/bulk_create/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkUpdate: (data: any) => apiClient.post('/api/etsy/purchase-requirement/bulk_update/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkDelete: (data: any) => apiClient.post('/api/etsy/purchase-requirement/bulk_delete/', data, {
    timeout: 15000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  getStatistics: () => apiClient.get('/api/etsy/purchase-requirement/statistics/'),
  exportExcel: (params?: any) => apiClient.get('/api/etsy/purchase-requirement/export_excel/', { 
    params, 
    responseType: 'blob',
    timeout: 60000
  }),
  syncData: () => apiClient.post('/api/etsy/purchase-requirement/sync_data/'),
  getCacheStatus: () => apiClient.get<CacheStatus>('/api/etsy/purchase-requirement/cache_status/'),
  clearCache: () => apiClient.post('/api/etsy/purchase-requirement/clear_cache/')
}

// Etsy生产需求API
export const etsyProductionRequirementAPI = {
  getList: (params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/production-requirement/', { params }),
  getDetail: (id: number) => apiClient.get(`/api/etsy/production-requirement/${id}/`),
  create: (data: any) => apiClient.post('/api/etsy/production-requirement/', data),
  update: (id: number, data: any) => apiClient.put(`/api/etsy/production-requirement/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/api/etsy/production-requirement/${id}/`),
  bulkCreate: (data: any) => apiClient.post('/api/etsy/production-requirement/bulk_create/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkUpdate: (data: any) => apiClient.post('/api/etsy/production-requirement/bulk_update/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkDelete: (data: any) => apiClient.post('/api/etsy/production-requirement/bulk_delete/', data, {
    timeout: 15000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  getStatistics: () => apiClient.get('/api/etsy/production-requirement/statistics/'),
  exportExcel: (params?: any) => apiClient.get('/api/etsy/production-requirement/export_excel/', { 
    params, 
    responseType: 'blob',
    timeout: 60000
  }),
  syncData: () => apiClient.post('/api/etsy/production-requirement/sync_data/'),
  getCacheStatus: () => apiClient.get<CacheStatus>('/api/etsy/production-requirement/cache_status/'),
  clearCache: () => apiClient.post('/api/etsy/production-requirement/clear_cache/')
}

// Etsy配货发货API
export const etsyShippingDeliveryAPI = {
  getList: (params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/shipping-delivery/', { params }),
  getDetail: (id: number) => apiClient.get(`/api/etsy/shipping-delivery/${id}/`),
  create: (data: any) => apiClient.post('/api/etsy/shipping-delivery/', data),
  update: (id: number, data: any) => apiClient.put(`/api/etsy/shipping-delivery/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/api/etsy/shipping-delivery/${id}/`),
  bulkCreate: (data: any) => apiClient.post('/api/etsy/shipping-delivery/bulk_create/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkUpdate: (data: any) => apiClient.post('/api/etsy/shipping-delivery/bulk_update/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkDelete: (data: any) => apiClient.post('/api/etsy/shipping-delivery/bulk_delete/', data, {
    timeout: 15000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  getStatistics: () => apiClient.get('/api/etsy/shipping-delivery/statistics/'),
  exportExcel: (params?: any) => apiClient.get('/api/etsy/shipping-delivery/export_excel/', { 
    params, 
    responseType: 'blob',
    timeout: 60000
  }),
  syncData: () => apiClient.post('/api/etsy/shipping-delivery/sync_data/'),
  getCacheStatus: () => apiClient.get<CacheStatus>('/api/etsy/shipping-delivery/cache_status/'),
  clearCache: () => apiClient.post('/api/etsy/shipping-delivery/clear_cache/')
}

// Etsy二维码标签API
export const etsyQRCodeLabelAPI = {
  getList: (params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/qr-code-label/', { params }),
  getDetail: (id: number) => apiClient.get(`/api/etsy/qr-code-label/${id}/`),
  create: (data: any) => apiClient.post('/api/etsy/qr-code-label/', data),
  update: (id: number, data: any) => apiClient.put(`/api/etsy/qr-code-label/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/api/etsy/qr-code-label/${id}/`),
  bulkCreate: (data: any) => apiClient.post('/api/etsy/qr-code-label/bulk_create/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkUpdate: (data: any) => apiClient.post('/api/etsy/qr-code-label/bulk_update/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkDelete: (data: any) => apiClient.post('/api/etsy/qr-code-label/bulk_delete/', data, {
    timeout: 15000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  getStatistics: () => apiClient.get('/api/etsy/qr-code-label/statistics/'),
  exportExcel: (params?: any) => apiClient.get('/api/etsy/qr-code-label/export_excel/', { 
    params, 
    responseType: 'blob',
    timeout: 60000
  }),
  syncData: () => apiClient.post('/api/etsy/qr-code-label/sync_data/'),
  getCacheStatus: () => apiClient.get<CacheStatus>('/api/etsy/qr-code-label/cache_status/'),
  clearCache: () => apiClient.post('/api/etsy/qr-code-label/clear_cache/')
}

// Etsy云途导出API
export const etsyYunTuExportAPI = {
  getList: (params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/yuntu-export/', { params }),
  getDetail: (id: number) => apiClient.get(`/api/etsy/yuntu-export/${id}/`),
  create: (data: any) => apiClient.post('/api/etsy/yuntu-export/', data),
  update: (id: number, data: any) => apiClient.put(`/api/etsy/yuntu-export/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/api/etsy/yuntu-export/${id}/`),
  bulkCreate: (data: any) => apiClient.post('/api/etsy/yuntu-export/bulk_create/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkUpdate: (data: any) => apiClient.post('/api/etsy/yuntu-export/bulk_update/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkDelete: (data: any) => apiClient.post('/api/etsy/yuntu-export/bulk_delete/', data, {
    timeout: 15000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  getStatistics: () => apiClient.get('/api/etsy/yuntu-export/statistics/'),
  exportExcel: (params?: any) => apiClient.get('/api/etsy/yuntu-export/export_excel/', { 
    params, 
    responseType: 'blob',
    timeout: 60000
  }),
  syncData: () => apiClient.post('/api/etsy/yuntu-export/sync_data/'),
  getCacheStatus: () => apiClient.get<CacheStatus>('/api/etsy/yuntu-export/cache_status/'),
  clearCache: () => apiClient.post('/api/etsy/yuntu-export/clear_cache/')
}

// Etsy云途扣费API
export const etsyYunTuDeductionAPI = {
  getList: (params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/yuntu-deduction/', { params }),
  getDetail: (id: number) => apiClient.get(`/api/etsy/yuntu-deduction/${id}/`),
  create: (data: any) => apiClient.post('/api/etsy/yuntu-deduction/', data),
  update: (id: number, data: any) => apiClient.put(`/api/etsy/yuntu-deduction/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/api/etsy/yuntu-deduction/${id}/`),
  bulkCreate: (data: any) => apiClient.post('/api/etsy/yuntu-deduction/bulk_create/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkUpdate: (data: any) => apiClient.post('/api/etsy/yuntu-deduction/bulk_update/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkDelete: (data: any) => apiClient.post('/api/etsy/yuntu-deduction/bulk_delete/', data, {
    timeout: 15000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  getStatistics: () => apiClient.get('/api/etsy/yuntu-deduction/statistics/'),
  exportExcel: (params?: any) => apiClient.get('/api/etsy/yuntu-deduction/export_excel/', { 
    params, 
    responseType: 'blob',
    timeout: 60000
  }),
  syncData: () => apiClient.post('/api/etsy/yuntu-deduction/sync_data/'),
  getCacheStatus: () => apiClient.get<CacheStatus>('/api/etsy/yuntu-deduction/cache_status/'),
  clearCache: () => apiClient.post('/api/etsy/yuntu-deduction/clear_cache/')
}

// Etsy店铺信息API
export const etsyStoreInformationAPI = {
  getList: (params?: PaginationParams) => apiClient.get<PaginatedResponse<any>>('/api/etsy/store-information/', { params }),
  getDetail: (id: number) => apiClient.get(`/api/etsy/store-information/${id}/`),
  create: (data: any) => apiClient.post('/api/etsy/store-information/', data),
  update: (id: number, data: any) => apiClient.put(`/api/etsy/store-information/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/api/etsy/store-information/${id}/`),
  bulkCreate: (data: any) => apiClient.post('/api/etsy/store-information/bulk_create/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkUpdate: (data: any) => apiClient.post('/api/etsy/store-information/bulk_update/', data, {
    timeout: 30000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  bulkDelete: (data: any) => apiClient.post('/api/etsy/store-information/bulk_delete/', data, {
    timeout: 15000,
    headers: { 'X-Bulk-Operation': 'true' }
  }),
  getStatistics: () => apiClient.get('/api/etsy/store-information/statistics/'),
  exportExcel: (params?: any) => apiClient.get('/api/etsy/store-information/export_excel/', { 
    params, 
    responseType: 'blob',
    timeout: 60000
  }),
  syncData: () => apiClient.post('/api/etsy/store-information/sync_data/'),
  getCacheStatus: () => apiClient.get<CacheStatus>('/api/etsy/store-information/cache_status/'),
  clearCache: () => apiClient.post('/api/etsy/store-information/clear_cache/')
}

// Etsy同步管理API
export const etsySyncManagementAPI = {
  // 同步所有模型数据
  syncAll: () => apiClient.post('/api/etsy/sync-management/sync_all/'),
  
  // 获取同步状态
  getSyncStatus: () => apiClient.get('/api/etsy/sync-management/sync_status/'),
  
  // 获取缓存信息
  getCacheInfo: () => apiClient.get('/api/etsy/sync-management/cache_info/'),
  
  // 手动触发Redis同步
  triggerRedisSync: (model?: string) => apiClient.post('/api/etsy/sync-management/trigger_sync/', { model }),
  
  // 获取Redis缓存统计
  getRedisStats: () => apiClient.get('/api/etsy/sync-management/redis_stats/'),
  
  // 清除所有缓存
  clearAllCache: () => apiClient.post('/api/etsy/sync-management/clear_all_cache/')
}

// 导出所有API
export const etsyAPI = {
  productRegistration: etsyProductRegistrationAPI,
  orderImportSummary: etsyOrderImportSummaryAPI,
  orderStatistics: etsyOrderStatisticsAPI,
  designRequirement: etsyDesignRequirementAPI,
  purchaseRequirement: etsyPurchaseRequirementAPI,
  productionRequirement: etsyProductionRequirementAPI,
  shippingDelivery: etsyShippingDeliveryAPI,
  qrCodeLabel: etsyQRCodeLabelAPI,
  yunTuExport: etsyYunTuExportAPI,
  yunTuDeduction: etsyYunTuDeductionAPI,
  storeInformation: etsyStoreInformationAPI,
  syncManagement: etsySyncManagementAPI
}
