import apiClient from './client'

// 产品管理API
export const productAPI = {
  // 获取产品列表
  getProducts: (params = {}) => {
    return apiClient.get('/api/products/', { params })
  },

  // 获取产品详情
  getProduct: (id: string) => {
    return apiClient.get(`/api/products/${id}/`)
  },

  // 创建产品
  createProduct: (data: any) => {
    return apiClient.post('/api/products/', data)
  },

  // 更新产品
  updateProduct: (id: string, data: any) => {
    return apiClient.put(`/api/products/${id}/`, data)
  },

  // 删除产品
  deleteProduct: (id: string) => {
    return apiClient.delete(`/api/products/${id}/`)
  }
}

// 导出所有API函数
export const {
  getProducts,
  getProduct,
  createProduct,
  updateProduct,
  deleteProduct
} = productAPI
