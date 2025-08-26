import apiClient from './client'

// 产品管理API
export const productAPI = {
  // 获取产品列表
  getProducts: (params = {}) => {
    return apiClient.get('/api/products/', { params })
  },

  // 获取产品详情
  getProduct: (id) => {
    return apiClient.get(`/api/products/${id}/`)
  },

  // 创建产品
  createProduct: (data) => {
    return apiClient.post('/api/products/', data)
  },

  // 更新产品
  updateProduct: (id, data) => {
    return apiClient.put(`/api/products/${id}/`, data)
  },

  // 删除产品
  deleteProduct: (id) => {
    return apiClient.delete(`/api/products/${id}/`)
  },

  // 获取产品分类
  getProductCategories: (params = {}) => {
    return apiClient.get('/api/product-categories/', { params })
  },

  // 创建产品分类
  createProductCategory: (data) => {
    return apiClient.post('/api/product-categories/', data)
  },

  // 更新产品分类
  updateProductCategory: (id, data) => {
    return apiClient.put(`/api/product-categories/${id}/`, data)
  },

  // 删除产品分类
  deleteProductCategory: (id) => {
    return apiClient.delete(`/api/product-categories/${id}/`)
  },

  // 产品搜索
  searchProducts: (params = {}) => {
    return apiClient.get('/api/products/search/', { params })
  },

  // 批量导入产品
  importProducts: (data) => {
    return apiClient.post('/api/products/import/', data)
  },

  // 导出产品
  exportProducts: (params = {}) => {
    return apiClient.get('/api/products/export/', { params })
  },

  // 获取产品库存
  getProductInventory: (productId, params = {}) => {
    return apiClient.get(`/api/products/${productId}/inventory/`, { params })
  },

  // 更新产品库存
  updateProductInventory: (productId, data) => {
    return apiClient.post(`/api/products/${productId}/inventory/`, data)
  },

  // 获取产品价格历史
  getProductPriceHistory: (productId, params = {}) => {
    return apiClient.get(`/api/products/${productId}/price-history/`, { params })
  },

  // 设置产品价格
  setProductPrice: (productId, data) => {
    return apiClient.post(`/api/products/${productId}/price/`, data)
  }
}

// 导出所有API函数
export const {
  getProducts,
  getProduct,
  createProduct,
  updateProduct,
  deleteProduct,
  getProductCategories,
  createProductCategory,
  updateProductCategory,
  deleteProductCategory,
  searchProducts,
  importProducts,
  exportProducts,
  getProductInventory,
  updateProductInventory,
  getProductPriceHistory,
  setProductPrice
} = productAPI
