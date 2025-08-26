import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  storeApi, 
  inventoryApi, 
  transactionApi,
  type Store, 
  type StoreCreate, 
  type StoreUpdate,
  type StoreStatistics,
  type StoreInventory,
  type InventoryCreate,
  type InventoryUpdate,
  type StockAdjustment,
  type StoreTransaction,
  type TransactionCreate,
  type DailySummary,
  type MonthlyReport
} from '@/api/store.ts'

export const useStoreStore = defineStore('store', () => {
  // 状态
  const stores = ref<Store[]>([])
  const currentStore = ref<Store | null>(null)
  const statistics = ref<StoreStatistics | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 分页相关
  const pagination = ref({
    current: 1,
    pageSize: 20,
    total: 0
  })

  // 过滤条件
  const filters = ref({
    search: '',
    status: '',
    department: '',
    manager: ''
  })

  // 计算属性
  const activeStores = computed(() => 
    stores.value.filter(store => store.status === 'active')
  )

  const inactiveStores = computed(() =>
    stores.value.filter(store => store.status === 'inactive')
  )

  // Actions
  const fetchStores = async (params?: any) => {
    loading.value = true
    error.value = null
    
    try {
      const queryParams = {
        page: pagination.value.current,
        page_size: pagination.value.pageSize,
        ...filters.value,
        ...params
      }

      const response = await storeApi.getStores(queryParams)
      
      // 确保正确提取数据
      if (response && response.data) {
        stores.value = response.data.results || []
        pagination.value.total = response.data.count || 0
      } else {
        stores.value = []
        pagination.value.total = 0
      }
    } catch (err: any) {
      error.value = err.message || '获取店铺列表失败'
      console.error('获取店铺列表失败:', err)
      stores.value = []
      pagination.value.total = 0
    } finally {
      loading.value = false
    }
  }

  const fetchStoreById = async (id: string) => {
    if (!id) {
      error.value = '店铺ID不能为空'
      return null
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await storeApi.getStore(id)
      if (response && response.data) {
        currentStore.value = response.data
        return response.data
      } else {
        error.value = '获取店铺详情失败：响应数据为空'
        return null
      }
    } catch (err: any) {
      error.value = err.message || '获取店铺详情失败'
      console.error('获取店铺详情失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const createStore = async (data: StoreCreate) => {
    if (!data || !data.name || !data.code) {
      error.value = '店铺名称和编码不能为空'
      throw new Error('店铺名称和编码不能为空')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await storeApi.createStore(data)
      if (response && response.data) {
        stores.value.unshift(response.data)
        pagination.value.total += 1
        return response.data
      } else {
        error.value = '创建店铺失败：响应数据为空'
        throw new Error('创建店铺失败：响应数据为空')
      }
    } catch (err: any) {
      error.value = err.message || '创建店铺失败'
      console.error('创建店铺失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateStore = async (id: string, data: StoreUpdate) => {
    if (!id) {
      error.value = '店铺ID不能为空'
      throw new Error('店铺ID不能为空')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await storeApi.updateStore(id, data)
      if (response && response.data) {
        const index = stores.value.findIndex(store => store.id === id)
        if (index !== -1) {
          stores.value[index] = response.data
        }
        if (currentStore.value?.id === id) {
          currentStore.value = response.data
        }
        return response.data
      } else {
        error.value = '更新店铺失败：响应数据为空'
        throw new Error('更新店铺失败：响应数据为空')
      }
    } catch (err: any) {
      error.value = err.message || '更新店铺失败'
      console.error('更新店铺失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteStore = async (id: string) => {
    if (!id) {
      error.value = '店铺ID不能为空'
      throw new Error('店铺ID不能为空')
    }
    
    loading.value = true
    error.value = null
    
    try {
      await storeApi.deleteStore(id)
      stores.value = stores.value.filter(store => store.id !== id)
      pagination.value.total = Math.max(0, pagination.value.total - 1)
      if (currentStore.value?.id === id) {
        currentStore.value = null
      }
    } catch (err: any) {
      error.value = err.message || '删除店铺失败'
      console.error('删除店铺失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const changeStoreStatus = async (id: string, status: string) => {
    if (!id) {
      error.value = '店铺ID不能为空'
      throw new Error('店铺ID不能为空')
    }
    
    if (!status) {
      error.value = '店铺状态不能为空'
      throw new Error('店铺状态不能为空')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await storeApi.changeStoreStatus(id, status)
      if (response && response.data) {
        const index = stores.value.findIndex(store => store.id === id)
        if (index !== -1) {
          stores.value[index] = response.data
        }
        if (currentStore.value?.id === id) {
          currentStore.value = response.data
        }
        return response.data
      } else {
        error.value = '更改店铺状态失败：响应数据为空'
        throw new Error('更改店铺状态失败：响应数据为空')
      }
    } catch (err: any) {
      error.value = err.message || '更改店铺状态失败'
      console.error('更改店铺状态失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchMyStores = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await storeApi.getMyStores()
      if (response && response.data) {
        // 处理返回的数据（可能是单个店铺或店铺数组）
        if (Array.isArray(response.data)) {
          stores.value = response.data
        } else {
          stores.value = [response.data]
          currentStore.value = response.data
        }
        return response.data
      } else {
        error.value = '获取我的店铺失败：响应数据为空'
        throw new Error('获取我的店铺失败：响应数据为空')
      }
    } catch (err: any) {
      error.value = err.message || '获取我的店铺失败'
      console.error('获取我的店铺失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchStatistics = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await storeApi.getStoreStatistics()
      if (response && response.data) {
        statistics.value = response.data
        return response.data
      } else {
        error.value = '获取统计信息失败：响应数据为空'
        throw new Error('获取统计信息失败：响应数据为空')
      }
    } catch (err: any) {
      error.value = err.message || '获取统计信息失败'
      console.error('获取统计信息失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 设置过滤条件
  const setFilters = (newFilters: Partial<typeof filters.value>) => {
    if (newFilters && typeof newFilters === 'object') {
      filters.value = { ...filters.value, ...newFilters }
    }
  }

  // 设置分页
  const setPagination = (newPagination: Partial<typeof pagination.value>) => {
    if (newPagination && typeof newPagination === 'object') {
      pagination.value = { ...pagination.value, ...newPagination }
    }
  }

  // 清除当前店铺
  const clearCurrentStore = () => {
    currentStore.value = null
  }

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  return {
    // 状态
    stores,
    currentStore,
    statistics,
    loading,
    error,
    pagination,
    filters,
    
    // 计算属性
    activeStores,
    inactiveStores,
    
    // Actions
    fetchStores,
    fetchStoreById,
    createStore,
    updateStore,
    deleteStore,
    changeStoreStatus,
    fetchMyStores,
    fetchStatistics,
    setFilters,
    setPagination,
    clearCurrentStore,
    clearError
  }
})

// 库存管理 Store
export const useInventoryStore = defineStore('inventory', () => {
  // 状态
  const inventories = ref<StoreInventory[]>([])
  const currentInventory = ref<StoreInventory | null>(null)
  const lowStockItems = ref<StoreInventory[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 分页相关
  const pagination = ref({
    current: 1,
    pageSize: 20,
    total: 0
  })

  // 过滤条件
  const filters = ref({
    search: '',
    store: '',
    product_code: ''
  })

  // Actions
  const fetchInventories = async (params?: any) => {
    loading.value = true
    error.value = null
    
    try {
      const queryParams = {
        page: pagination.value.current,
        page_size: pagination.value.pageSize,
        ...filters.value,
        ...params
      }

      const response = await inventoryApi.getInventories(queryParams)
      if (response && response.data) {
        inventories.value = response.data.results || []
        pagination.value.total = response.data.count || 0
      } else {
        inventories.value = []
        pagination.value.total = 0
      }
    } catch (err: any) {
      error.value = err.message || '获取库存列表失败'
      console.error('获取库存列表失败:', err)
      inventories.value = []
      pagination.value.total = 0
    } finally {
      loading.value = false
    }
  }

  const fetchInventoryById = async (id: string) => {
    if (!id) {
      error.value = '库存ID不能为空'
      return null
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryApi.getInventory(id)
      if (response && response.data) {
        currentInventory.value = response.data
        return response.data
      } else {
        error.value = '获取库存详情失败：响应数据为空'
        return null
      }
    } catch (err: any) {
      error.value = err.message || '获取库存详情失败'
      console.error('获取库存详情失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const createInventory = async (data: InventoryCreate) => {
    if (!data || !data.store_id || !data.product_name) {
      error.value = '店铺ID和产品名称不能为空'
      throw new Error('店铺ID和产品名称不能为空')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryApi.createInventory(data)
      if (response && response.data) {
        inventories.value.unshift(response.data)
        pagination.value.total += 1
        return response.data
      } else {
        error.value = '创建库存记录失败：响应数据为空'
        throw new Error('创建库存记录失败：响应数据为空')
      }
    } catch (err: any) {
      error.value = err.message || '创建库存记录失败'
      console.error('创建库存记录失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateInventory = async (id: string, data: InventoryUpdate) => {
    if (!id) {
      error.value = '库存ID不能为空'
      throw new Error('库存ID不能为空')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryApi.updateInventory(id, data)
      if (response && response.data) {
        const index = inventories.value.findIndex(item => item.id === id)
        if (index !== -1) {
          inventories.value[index] = response.data
        }
        if (currentInventory.value?.id === id) {
          currentInventory.value = response.data
        }
        return response.data
      } else {
        error.value = '更新库存失败：响应数据为空'
        throw new Error('更新库存失败：响应数据为空')
      }
    } catch (err: any) {
      error.value = err.message || '更新库存失败'
      console.error('更新库存失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteInventory = async (id: string) => {
    if (!id) {
      error.value = '库存ID不能为空'
      throw new Error('库存ID不能为空')
    }
    
    loading.value = true
    error.value = null
    
    try {
      await inventoryApi.deleteInventory(id)
      inventories.value = inventories.value.filter(item => item.id !== id)
      pagination.value.total = Math.max(0, pagination.value.total - 1)
      if (currentInventory.value?.id === id) {
        currentInventory.value = null
      }
    } catch (err: any) {
      error.value = err.message || '删除库存记录失败'
      console.error('删除库存记录失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const adjustStock = async (id: string, data: StockAdjustment) => {
    if (!id) {
      error.value = '库存ID不能为空'
      throw new Error('库存ID不能为空')
    }
    
    if (typeof data.adjustment !== 'number') {
      error.value = '调整数量必须是数字'
      throw new Error('调整数量必须是数字')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryApi.adjustStock(id, data)
      if (response && response.data) {
        const index = inventories.value.findIndex(item => item.id === id)
        if (index !== -1) {
          inventories.value[index] = response.data
        }
        if (currentInventory.value?.id === id) {
          currentInventory.value = response.data
        }
        return response.data
      } else {
        error.value = '调整库存失败：响应数据为空'
        throw new Error('调整库存失败：响应数据为空')
      }
    } catch (err: any) {
      error.value = err.message || '调整库存失败'
      console.error('调整库存失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchLowStock = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryApi.getLowStock()
      if (response && response.data) {
        lowStockItems.value = response.data
        return response.data
      } else {
        error.value = '获取低库存商品失败：响应数据为空'
        throw new Error('获取低库存商品失败：响应数据为空')
      }
    } catch (err: any) {
      error.value = err.message || '获取低库存商品失败'
      console.error('获取低库存商品失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    inventories,
    currentInventory,
    lowStockItems,
    loading,
    error,
    pagination,
    filters,
    
    // Actions
    fetchInventories,
    fetchInventoryById,
    createInventory,
    updateInventory,
    deleteInventory,
    adjustStock,
    fetchLowStock
  }
})

// 交易记录 Store
export const useTransactionStore = defineStore('transaction', () => {
  // 状态
  const transactions = ref<StoreTransaction[]>([])
  const currentTransaction = ref<StoreTransaction | null>(null)
  const dailySummary = ref<DailySummary | null>(null)
  const monthlyReport = ref<MonthlyReport | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 分页相关
  const pagination = ref({
    current: 1,
    pageSize: 20,
    total: 0
  })

  // 过滤条件
  const filters = ref({
    search: '',
    store: '',
    transaction_type: '',
    operator: ''
  })

  // Actions
  const fetchTransactions = async (params?: any) => {
    loading.value = true
    error.value = null
    
    try {
      const queryParams = {
        page: pagination.value.current,
        page_size: pagination.value.pageSize,
        ...filters.value,
        ...params
      }

      const response = await transactionApi.getTransactions(queryParams)
      if (response && response.data) {
        transactions.value = response.data.results || []
        pagination.value.total = response.data.count || 0
      } else {
        transactions.value = []
        pagination.value.total = 0
      }
    } catch (err: any) {
      error.value = err.message || '获取交易记录失败'
      console.error('获取交易记录失败:', err)
      transactions.value = []
      pagination.value.total = 0
    } finally {
      loading.value = false
    }
  }

  const createTransaction = async (data: TransactionCreate) => {
    if (!data || !data.store_id || !data.transaction_type) {
      error.value = '店铺ID和交易类型不能为空'
      throw new Error('店铺ID和交易类型不能为空')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await transactionApi.createTransaction(data)
      if (response && response.data) {
        transactions.value.unshift(response.data)
        pagination.value.total += 1
        return response.data
      } else {
        error.value = '创建交易记录失败：响应数据为空'
        throw new Error('创建交易记录失败：响应数据为空')
      }
    } catch (err: any) {
      error.value = err.message || '创建交易记录失败'
      console.error('创建交易记录失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchDailySummary = async (date?: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await transactionApi.getDailySummary(date)
      if (response && response.data) {
        dailySummary.value = response.data
        return response.data
      } else {
        error.value = '获取每日汇总失败：响应数据为空'
        throw new Error('获取每日汇总失败：响应数据为空')
      }
    } catch (err: any) {
      error.value = err.message || '获取每日汇总失败'
      console.error('获取每日汇总失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchMonthlyReport = async (year?: number, month?: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await transactionApi.getMonthlyReport(year, month)
      if (response && response.data) {
        monthlyReport.value = response.data
        return response.data
      } else {
        error.value = '获取月度报告失败：响应数据为空'
        throw new Error('获取月度报告失败：响应数据为空')
      }
    } catch (err: any) {
      error.value = err.message || '获取月度报告失败'
      console.error('获取月度报告失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    transactions,
    currentTransaction,
    dailySummary,
    monthlyReport,
    loading,
    error,
    pagination,
    filters,
    
    // Actions
    fetchTransactions,
    createTransaction,
    fetchDailySummary,
    fetchMonthlyReport
  }
})
