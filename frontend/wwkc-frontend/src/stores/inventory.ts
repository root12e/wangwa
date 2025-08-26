import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  inventoryAPI,
  type Inventory, 
  type InventoryCreate, 
  type InventoryUpdate,
  type InventoryAdjustment,
  type BulkInventoryAdjustment,
  type InventoryTransaction,
  type InventoryConsumption,
  type Order,
  type OrderBatch,
  type InventorySummary,
  type TransactionStatistics,
  type WorkflowStatus,
  type SchedulerStatus,
  type InventoryFilter,
  type TransactionFilter,
  type OrderFilter,
  type BatchFilter,
  type PaginationParams,
  type PaginatedResponse
} from '@/api/inventory'

export const useInventoryStore = defineStore('inventory', () => {
  // 状态
  const inventories = ref<Inventory[]>([])
  const currentInventory = ref<Inventory | null>(null)
  const lowStockItems = ref<Inventory[]>([])
  const transactions = ref<InventoryTransaction[]>([])
  const consumption = ref<InventoryConsumption[]>([])
  const orders = ref<Order[]>([])
  const orderBatches = ref<OrderBatch[]>([])
  const summary = ref<InventorySummary | null>(null)
  const workflowStatus = ref<WorkflowStatus | null>(null)
  const schedulerStatus = ref<SchedulerStatus | null>(null)
  
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 分页相关
  const pagination = ref({
    current: 1,
    pageSize: 20,
    total: 0
  })

  // 过滤条件
  const filters = ref<InventoryFilter>({
    store_id: '',
    sku: '',
    is_active: true,
    low_stock: false
  })

  // 计算属性
  const activeInventories = computed(() => 
    inventories.value.filter(item => item.is_active)
  )

  const lowStockInventories = computed(() => 
    inventories.value.filter(item => item.current_stock <= item.min_stock)
  )

  const outOfStockInventories = computed(() => 
    inventories.value.filter(item => item.current_stock === 0)
  )

  // Actions
  const fetchInventories = async (params?: InventoryFilter & PaginationParams) => {
    loading.value = true
    error.value = null
    
    try {
      const queryParams = {
        page: pagination.value.current,
        page_size: pagination.value.pageSize,
        ...filters.value,
        ...params
      }

      const response = await inventoryAPI.getInventories(queryParams)
      inventories.value = response.data.results
      pagination.value.total = response.data.count
    } catch (err: any) {
      error.value = err.message || '获取库存列表失败'
      console.error('获取库存列表失败:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchInventoryById = async (id: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.getInventory(id)
      currentInventory.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.message || '获取库存详情失败'
      console.error('获取库存详情失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const createInventory = async (data: InventoryCreate) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.createInventory(data)
      inventories.value.unshift(response.data)
      pagination.value.total += 1
      return response.data
    } catch (err: any) {
      error.value = err.message || '创建库存记录失败'
      console.error('创建库存记录失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateInventory = async (id: string, data: InventoryUpdate) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.updateInventory(id, data)
      const index = inventories.value.findIndex(item => item.id === id)
      if (index !== -1) {
        inventories.value[index] = response.data
      }
      if (currentInventory.value?.id === id) {
        currentInventory.value = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.message || '更新库存失败'
      console.error('更新库存失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteInventory = async (id: string) => {
    loading.value = true
    error.value = null
    
    try {
      await inventoryAPI.deleteInventory(id)
      inventories.value = inventories.value.filter(item => item.id !== id)
      pagination.value.total -= 1
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

  const adjustInventory = async (id: string, data: InventoryAdjustment) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.adjustInventory(id, data)
      const index = inventories.value.findIndex(item => item.id === id)
      if (index !== -1) {
        inventories.value[index] = response.data
      }
      if (currentInventory.value?.id === id) {
        currentInventory.value = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.message || '调整库存失败'
      console.error('调整库存失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const bulkAdjustInventory = async (data: BulkInventoryAdjustment) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.bulkAdjustInventory(data)
      // 刷新库存列表
      await fetchInventories()
      return response.data
    } catch (err: any) {
      error.value = err.message || '批量调整库存失败'
      console.error('批量调整库存失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchInventorySummary = async (params?: { store_id?: string }) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.getInventorySummary(params)
      summary.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.message || '获取库存摘要失败'
      console.error('获取库存摘要失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchTransactions = async (params?: TransactionFilter & PaginationParams) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.getInventoryTransactions(params)
      transactions.value = response.data.results
      return response.data
    } catch (err: any) {
      error.value = err.message || '获取交易记录失败'
      console.error('获取交易记录失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchTransactionStatistics = async (params?: TransactionFilter) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.getTransactionStatistics(params)
      return response.data
    } catch (err: any) {
      error.value = err.message || '获取交易统计失败'
      console.error('获取交易统计失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchConsumption = async (params?: { store_id?: string }) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.getInventoryConsumption(params)
      consumption.value = response.data.results
      return response.data
    } catch (err: any) {
      error.value = err.message || '获取消耗统计失败'
      console.error('获取消耗统计失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchOrders = async (params?: OrderFilter & PaginationParams) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.getOrders(params)
      orders.value = response.data.results
      return response.data
    } catch (err: any) {
      error.value = err.message || '获取订单列表失败'
      console.error('获取订单列表失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const processOrderInventory = async (orderIds: string[]) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.processOrderInventory({ order_ids: orderIds })
      return response.data
    } catch (err: any) {
      error.value = err.message || '处理订单库存失败'
      console.error('处理订单库存失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const processAllUnprocessedOrders = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.processAllUnprocessedOrders()
      return response.data
    } catch (err: any) {
      error.value = err.message || '处理所有未处理订单失败'
      console.error('处理所有未处理订单失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchOrderBatches = async (params?: BatchFilter & PaginationParams) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.getOrderBatches(params)
      orderBatches.value = response.data.results
      return response.data
    } catch (err: any) {
      error.value = err.message || '获取订单批次失败'
      console.error('获取订单批次失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchWorkflowStatus = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.getWorkflowStatus()
      workflowStatus.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.message || '获取工作流状态失败'
      console.error('获取工作流状态失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const executeWorkflow = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.executeWorkflow()
      return response.data
    } catch (err: any) {
      error.value = err.message || '执行工作流失败'
      console.error('执行工作流失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchSchedulerStatus = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.getSchedulerStatus()
      schedulerStatus.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.message || '获取定时任务状态失败'
      console.error('获取定时任务状态失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const forceExecuteWorkflow = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.forceExecuteWorkflow()
      return response.data
    } catch (err: any) {
      error.value = err.message || '强制执行工作流失败'
      console.error('强制执行工作流失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateExecutionInterval = async (interval: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await inventoryAPI.updateExecutionInterval({ interval })
      return response.data
    } catch (err: any) {
      error.value = err.message || '更新执行间隔失败'
      console.error('更新执行间隔失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 设置过滤条件
  const setFilters = (newFilters: Partial<InventoryFilter>) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  // 设置分页
  const setPagination = (newPagination: Partial<typeof pagination.value>) => {
    pagination.value = { ...pagination.value, ...newPagination }
  }

  // 清除当前库存
  const clearCurrentInventory = () => {
    currentInventory.value = null
  }

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  return {
    // 状态
    inventories,
    currentInventory,
    lowStockItems,
    transactions,
    consumption,
    orders,
    orderBatches,
    summary,
    workflowStatus,
    schedulerStatus,
    loading,
    error,
    pagination,
    filters,
    
    // 计算属性
    activeInventories,
    lowStockInventories,
    outOfStockInventories,
    
    // Actions
    fetchInventories,
    fetchInventoryById,
    createInventory,
    updateInventory,
    deleteInventory,
    adjustInventory,
    bulkAdjustInventory,
    fetchInventorySummary,
    fetchTransactions,
    fetchTransactionStatistics,
    fetchConsumption,
    fetchOrders,
    processOrderInventory,
    processAllUnprocessedOrders,
    fetchOrderBatches,
    fetchWorkflowStatus,
    executeWorkflow,
    fetchSchedulerStatus,
    forceExecuteWorkflow,
    updateExecutionInterval,
    setFilters,
    setPagination,
    clearCurrentInventory,
    clearError
  }
})
