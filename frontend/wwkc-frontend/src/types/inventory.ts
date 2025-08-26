// 库存相关类型定义

// 店铺信息
export interface Store {
  id: string
  name: string
  code: string
  description?: string
}

// 产品信息
export interface Product {
  id: string
  name: string
  sku: string
  description?: string
}

// 库存记录
export interface Inventory {
  id: string
  store: Store
  product: Product
  sku: string
  current_stock: number
  reserved_stock: number
  available_stock: number
  min_stock: number
  max_stock: number
  is_active: boolean
  last_updated: string
  created_at: string
  store_id?: string
  product_id?: string
}

// 库存创建
export interface InventoryCreate {
  store_id: string
  product_id: string
  sku: string
  current_stock: number
  min_stock: number
  max_stock: number
  is_active?: boolean
}

// 库存更新
export interface InventoryUpdate {
  current_stock?: number
  min_stock?: number
  max_stock?: number
  is_active?: boolean
}

// 库存调整
export interface InventoryAdjustment {
  adjustment_type: 'IN' | 'OUT' | 'ADJUST'
  quantity: number
  notes?: string
}

// 批量库存调整
export interface BulkInventoryAdjustment {
  adjustments: Array<{
    inventory_id: string
    adjustment_type: 'IN' | 'OUT' | 'ADJUST'
    quantity: number
    notes?: string
  }>
}

// 库存交易记录
export interface InventoryTransaction {
  id: string
  inventory: Inventory
  transaction_type: string
  transaction_type_display: string
  quantity: number
  order?: any
  before_stock: number
  after_stock: number
  notes?: string
  created_at: string
  created_by?: string
  inventory_id?: string
}

// 库存消耗统计
export interface InventoryConsumption {
  id: string
  store: Store
  sku: string
  total_consumed: number
  total_orders: number
  last_consumption_date?: string
  first_consumption_date?: string
  last_updated: string
  created_at: string
}

// 订单信息
export interface Order {
  id: string
  order_number: string
  country: string
  store_code: string
  sku: string
  detail: string
  n_quantity: number
  c1_value: string
  c2_value: string
  order_date: string
  label_status: string
  package_status: string
  combined_express_waybill: string
  yuntu_info: string
  last_mile: string
  store: Store
  store_name: string
  english_name: string
  first_sku: string
  last_update_time: string
  created_at: string
  page_token: string
  is_processed: boolean
  inventory_deducted: boolean
}

// 订单批次
export interface OrderBatch {
  id: string
  batch_id: string
  execution_time: string
  page_token: string
  orders_count: number
  is_completed: boolean
  error_message?: string
}

// 库存摘要
export interface InventorySummary {
  total_items: number
  total_value: number
  low_stock_count: number
  out_of_stock_count: number
  store_summary?: Array<{
    store_id: string
    store_name: string
    item_count: number
    total_value: number
    low_stock_count: number
  }>
}

// 交易统计
export interface TransactionStatistics {
  type_statistics: Record<string, {
    count: number
    total_quantity: number
  }>
  date_statistics: Array<{
    date: string
    count: number
    total_quantity: number
  }>
  total_transactions: number
}

// 工作流状态
export interface WorkflowStatus {
  is_running: boolean
  last_execution: string
  next_execution: string
  execution_count: number
  error_count: number
  last_error?: string
}

// 定时任务状态
export interface SchedulerStatus {
  is_active: boolean
  current_interval: number
  last_execution: string
  next_execution: string
  total_executions: number
}

// 库存过滤条件
export interface InventoryFilter {
  store_id?: string
  sku?: string
  is_active?: boolean
  low_stock?: boolean
}

// 交易记录过滤条件
export interface TransactionFilter {
  inventory_id?: string
  transaction_type?: string
  start_date?: string
  end_date?: string
}

// 订单过滤条件
export interface OrderFilter {
  store_id?: string
  is_processed?: boolean
  start_date?: string
  end_date?: string
  sku?: string
  order_number?: string
}

// 批次过滤条件
export interface BatchFilter {
  is_completed?: boolean
  start_date?: string
  end_date?: string
}

// 分页参数
export interface PaginationParams {
  page?: number
  page_size?: number
}

// API响应格式
export interface ApiResponse<T> {
  data: T
  message?: string
  success?: boolean
}

export interface PaginatedResponse<T> {
  count: number
  next?: string
  previous?: string
  results: T[]
}
