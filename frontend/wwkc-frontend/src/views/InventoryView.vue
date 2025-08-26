<template>
  <div class="inventory-view">
    <!-- 页面标题 -->
    <div class="page-header fade-in-up">
      <h1>库存管理</h1>
      <p class="page-description">管理店铺商品库存、库存调整和预警设置</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid" v-loading="statisticsLoading">
      <div class="stat-card card fade-in-up" style="animation-delay: 0.1s">
        <div class="stat-icon">
          <el-icon><Box /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ totalItems }}</div>
          <div class="stat-label">总商品数</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.2s">
        <div class="stat-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ lowStockCount }}</div>
          <div class="stat-label">库存预警</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.3s">
        <div class="stat-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ formatNumber(totalValue) }}</div>
          <div class="stat-label">总库存数量</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.4s">
        <div class="stat-icon">
          <el-icon><Shop /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ selectedStore ? '1' : stores.length }}</div>
          <div class="stat-label">{{ selectedStore ? '当前店铺' : '店铺数量' }}</div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar card fade-in-up" style="animation-delay: 0.5s">
      <div class="action-left">
        <el-select 
          v-model="selectedStoreId" 
          placeholder="选择店铺" 
          clearable
          @change="handleStoreChange"
          style="width: 200px; margin-right: 12px;"
        >
          <el-option 
            v-for="store in stores" 
            :key="store.id" 
            :label="store.name" 
            :value="store.id" 
          />
        </el-select>
        
        <el-input
          v-model="searchQuery"
          placeholder="搜索商品名称、编码..."
          class="search-input"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-button 
          type="warning"
          @click="showLowStockItems"
          :disabled="!lowStockItems.length"
        >
          <el-icon><Warning /></el-icon>
          低库存预警 ({{ lowStockItems.length }})
        </el-button>
      </div>
      
      <div class="action-right">
        <el-button 
          type="primary" 
          class="btn-primary"
          @click="showCreateDialog = true"
          :disabled="!selectedStoreId"
        >
          <el-icon><Plus /></el-icon>
          添加商品
        </el-button>
        <el-button 
          class="btn-secondary"
          @click="exportData"
        >
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
      </div>
    </div>

    <!-- 商品列表 -->
    <div class="inventory-table card fade-in-up" style="animation-delay: 0.6s">
      <el-table 
        :data="inventories" 
        style="width: 100%" 
        stripe
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="商品信息" min-width="250">
          <template #default="scope">
            <div class="product-info">
              <el-avatar :size="40">{{ scope.row.product.name.charAt(0) }}</el-avatar>
              <div class="product-details">
                <div class="product-name">{{ scope.row.product.name }}</div>
                <div class="product-code">{{ scope.row.sku }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="所属店铺" width="150">
          <template #default="scope">
            {{ scope.row.store.name }}
          </template>
        </el-table-column>
        <el-table-column prop="current_stock" label="当前库存" width="120">
          <template #default="scope">
            <el-tag :type="getStockTagType(scope.row.current_stock, scope.row.min_stock)">
              {{ scope.row.current_stock }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="库存区间" width="120">
          <template #default="scope">
            <span class="stock-range">
              {{ scope.row.min_stock }} - {{ scope.row.max_stock }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="库存状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '激活' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="可用库存" width="120">
          <template #default="scope">
            <el-tag :type="getStockTagType(scope.row.available_stock, scope.row.min_stock)">
              {{ scope.row.available_stock }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_updated" label="最后更新" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.last_updated) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary" 
              text
              @click="handleEdit(scope.row)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="warning" 
              text
              @click="handleAdjustStock(scope.row)"
            >
              <el-icon><Sort /></el-icon>
              调整库存
            </el-button>
            <el-dropdown trigger="click">
              <el-button size="small" type="info" text>
                更多
                <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleView(scope.row)">
                    <el-icon><View /></el-icon>
                    查看详情
                  </el-dropdown-item>
                  <el-dropdown-item 
                    @click="handleDelete(scope.row)"
                    class="danger-item"
                  >
              <el-icon><Delete /></el-icon>
                    删除商品
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 创建/编辑商品对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEditing ? '编辑商品' : '添加商品'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="inventoryFormRef"
        :model="inventoryForm"
        :rules="inventoryFormRules"
        label-width="100px"
      >
        <el-form-item label="产品" prop="product_id">
          <el-select v-model="inventoryForm.product_id" placeholder="请选择产品" style="width: 100%">
            <el-option
              v-for="product in products"
              :key="product.id"
              :label="product.name"
              :value="product.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="SKU" prop="sku">
          <el-input v-model="inventoryForm.sku" placeholder="请输入SKU" />
        </el-form-item>
        <el-form-item label="所属店铺" prop="store_id" v-if="!isEditing">
          <el-select v-model="inventoryForm.store_id" placeholder="请选择店铺" style="width: 100%">
            <el-option
              v-for="store in stores"
              :key="store.id"
              :label="store.name"
              :value="store.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="库存数量" prop="current_stock">
          <el-input-number 
            v-model="inventoryForm.current_stock" 
            :min="0" 
            :precision="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="最低库存" prop="min_stock">
          <el-input-number 
            v-model="inventoryForm.min_stock" 
            :min="0" 
            :precision="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="最高库存" prop="max_stock">
          <el-input-number 
            v-model="inventoryForm.max_stock" 
            :min="0" 
            :precision="0"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="handleSaveInventory"
            :loading="submitLoading"
          >
            {{ isEditing ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 库存调整对话框 -->
    <el-dialog
      v-model="showAdjustDialog"
      title="库存调整"
      width="400px"
    >
      <div v-if="currentInventory">
        <p>商品：{{ currentInventory.product.name }}</p>
        <p>当前库存：{{ currentInventory.current_stock }}</p>
        <el-form>
          <el-form-item label="调整数量">
            <el-input-number 
              v-model="adjustmentAmount"
              :precision="0"
              style="width: 100%"
              placeholder="正数为增加，负数为减少"
            />
          </el-form-item>
          <el-form-item label="调整原因">
            <el-input 
              v-model="adjustmentReason"
              type="textarea"
              :rows="3"
              placeholder="请输入调整原因"
            />
          </el-form-item>
        </el-form>
        <div class="adjustment-preview">
          <p>调整后库存：{{ currentInventory.current_stock + (adjustmentAmount || 0) }}</p>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAdjustDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmStockAdjustment"
            :loading="adjustLoading"
          >
            确认调整
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 低库存预警对话框 -->
    <el-dialog
      v-model="showLowStockDialog"
      title="低库存预警"
      width="800px"
    >
      <el-table :data="lowStockItems" style="width: 100%">
        <el-table-column label="商品信息" min-width="200">
          <template #default="scope">
            <div class="product-info">
              <div class="product-details">
                <div class="product-name">{{ scope.row.product.name }}</div>
                <div class="product-code">{{ scope.row.sku }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="店铺" width="150">
          <template #default="scope">
            {{ scope.row.store.name }}
          </template>
        </el-table-column>
        <el-table-column prop="current_stock" label="当前库存" width="100">
          <template #default="scope">
            <el-tag type="danger">{{ scope.row.current_stock }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="min_stock" label="最低库存" width="100" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button 
              size="small" 
              type="warning"
              @click="quickAdjustStock(scope.row)"
            >
              补货
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { useInventoryStore } from '@/stores/inventory'
import { useStoreStore } from '@/stores/store'
import { productAPI } from '@/api/product'
import type { Inventory, InventoryCreate, InventoryUpdate, InventoryAdjustment } from '@/types/inventory'

// Store
const inventoryStore = useInventoryStore()
const storeStore = useStoreStore()

// 产品列表
const products = ref<any[]>([])

// 响应式数据
const searchQuery = ref('')
const selectedStoreId = ref('')
const selectedInventories = ref<Inventory[]>([])

// 对话框相关
const showCreateDialog = ref(false)
const showAdjustDialog = ref(false)
const showLowStockDialog = ref(false)
const isEditing = ref(false)
const submitLoading = ref(false)
const adjustLoading = ref(false)
const statisticsLoading = ref(false)

// 当前操作的库存
const currentInventory = ref<Inventory | null>(null)
const adjustmentAmount = ref(0)
const adjustmentReason = ref('')

// 表单相关
const inventoryFormRef = ref<FormInstance>()
const inventoryForm = ref<InventoryCreate>({
  store_id: '',
  product_id: '',
  sku: '',
  current_stock: 0,
  min_stock: 0,
  max_stock: 1000,
  is_active: true
})

const inventoryFormRules = {
  product_id: [
    { required: true, message: '请选择产品', trigger: 'change' }
  ],
  sku: [
    { required: true, message: '请输入SKU', trigger: 'blur' },
    { pattern: /^[A-Z0-9-_]+$/, message: 'SKU只能包含大写字母、数字、连字符和下划线', trigger: 'blur' }
  ],
  store_id: [
    { required: true, message: '请选择所属店铺', trigger: 'change' }
  ],
  current_stock: [
    { required: true, message: '请输入库存数量', trigger: 'blur' },
    { type: 'number', min: 0, message: '库存数量不能为负数', trigger: 'blur' }
  ],
  min_stock: [
    { required: true, message: '请输入最低库存', trigger: 'blur' },
    { type: 'number', min: 0, message: '最低库存不能为负数', trigger: 'blur' }
  ],
  max_stock: [
    { required: true, message: '请输入最高库存', trigger: 'blur' },
    { type: 'number', min: 0, message: '最高库存不能为负数', trigger: 'blur' }
  ]
}

// 计算属性
const inventories = computed(() => inventoryStore.inventories)
const loading = computed(() => inventoryStore.loading)
const pagination = computed(() => inventoryStore.pagination)
const lowStockItems = computed(() => inventoryStore.lowStockItems)
const stores = computed(() => storeStore.stores)
const selectedStore = computed(() => stores.value.find(s => s.id === selectedStoreId.value))

// 统计数据
const totalItems = computed(() => inventories.value.length)
const lowStockCount = computed(() => lowStockItems.value.length)
const totalValue = computed(() => {
  return inventories.value.reduce((total: number, item: Inventory) => {
    // 这里需要根据实际业务逻辑计算库存总值
    // 暂时返回库存数量作为示例
    return total + item.current_stock
  }, 0)
})

// 格式化数字
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

// 格式化日期
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 库存状态判断
const getStockTagType = (quantity: number, minStock: number) => {
  if (quantity <= minStock) return 'danger'
  if (quantity <= minStock * 2) return 'warning'
  return 'success'
}

// 搜索和过滤
const handleSearch = () => {
  // 实现搜索逻辑
}

// 店铺变更处理
const handleStoreChange = () => {
  if (selectedStoreId.value) {
    loadInventories()
  }
}

// 分页处理
const handleSizeChange = (val: number) => {
  pagination.value.pageSize = val
  pagination.value.current = 1
  loadInventories()
}

const handleCurrentChange = (val: number) => {
  pagination.value.current = val
  loadInventories()
}

// 表格选择
const handleSelectionChange = (selection: Inventory[]) => {
  selectedInventories.value = selection
}

// CRUD 操作
const handleEdit = (inventory: Inventory) => {
  isEditing.value = true
  currentInventory.value = inventory
  inventoryForm.value = {
    store_id: inventory.store.id,
    product_id: inventory.product.id,
    sku: inventory.sku,
    current_stock: inventory.current_stock,
    min_stock: inventory.min_stock,
    max_stock: inventory.max_stock,
    is_active: inventory.is_active
  }
  showCreateDialog.value = true
}

const handleView = (inventory: Inventory) => {
  ElMessage.info('商品详情页面开发中...')
}

const handleDelete = async (inventory: Inventory) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除商品"${inventory.product.name}"吗？此操作不可撤销。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await inventoryStore.deleteInventory(inventory.id)
    ElMessage.success('删除成功')
    loadInventories()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 库存调整
const handleAdjustStock = (inventory: Inventory) => {
  currentInventory.value = inventory
  adjustmentAmount.value = 0
  adjustmentReason.value = ''
  showAdjustDialog.value = true
}

const confirmStockAdjustment = async () => {
  if (!currentInventory.value || adjustmentAmount.value === 0) {
    ElMessage.warning('请输入调整数量')
    return
  }

  if (!adjustmentReason.value.trim()) {
    ElMessage.warning('请输入调整原因')
    return
  }

  try {
    adjustLoading.value = true
    await inventoryStore.adjustInventory(currentInventory.value.id, {
      adjustment_type: adjustmentAmount.value > 0 ? 'IN' : 'OUT',
      quantity: Math.abs(adjustmentAmount.value),
      notes: adjustmentReason.value
    })
    ElMessage.success('库存调整成功')
    showAdjustDialog.value = false
    loadInventories()
  } catch (error: any) {
    ElMessage.error(error.message || '库存调整失败')
  } finally {
    adjustLoading.value = false
  }
}

const quickAdjustStock = (inventory: Inventory) => {
  showLowStockDialog.value = false
  handleAdjustStock(inventory)
}

// 表单操作
const resetForm = () => {
  inventoryFormRef.value?.resetFields()
  inventoryForm.value = {
    store_id: selectedStoreId.value || '',
    product_id: '',
    sku: '',
    current_stock: 0,
    min_stock: 0,
    max_stock: 1000,
    is_active: true
  }
  isEditing.value = false
  currentInventory.value = null
}

const handleSaveInventory = async () => {
  try {
    await inventoryFormRef.value?.validate()
    submitLoading.value = true
    
    if (isEditing.value && currentInventory.value) {
      await inventoryStore.updateInventory(currentInventory.value.id, inventoryForm.value as InventoryUpdate)
      ElMessage.success('更新成功')
    } else {
      await inventoryStore.createInventory(inventoryForm.value)
      ElMessage.success('创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
    loadInventories()
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    submitLoading.value = false
  }
}

// 其他操作
const showLowStockItems = () => {
  showLowStockDialog.value = true
}

const exportData = () => {
  ElMessage.info('导出功能开发中...')
}

// 加载店铺列表
const loadStores = async () => {
  try {
    await storeStore.fetchStores()
  } catch (error: any) {
    ElMessage.error(error.message || '加载店铺列表失败')
  }
}

// 加载产品列表
const loadProducts = async () => {
  try {
    const response = await productAPI.getProducts()
    products.value = response.data.results || []
  } catch (error: any) {
    ElMessage.error(error.message || '加载产品列表失败')
  }
}

// 加载库存列表
const loadInventories = async () => {
  if (!selectedStoreId.value) return
  
  try {
    await inventoryStore.fetchInventories({
      store: selectedStoreId.value,
      search: searchQuery.value,
      page: pagination.value.current,
      page_size: pagination.value.pageSize
    })
  } catch (error: any) {
    ElMessage.error(error.message || '加载库存列表失败')
  }
}

// 加载低库存商品
const loadLowStockItems = async () => {
  try {
    await inventoryStore.fetchLowStock()
  } catch (error: any) {
    ElMessage.error(error.message || '加载低库存商品失败')
  }
}

// 监听搜索条件变化
watch([searchQuery, selectedStoreId], () => {
  // 延迟搜索，避免频繁请求
  const timer = setTimeout(() => {
    if (selectedStoreId.value) {
      loadInventories()
    }
    clearTimeout(timer)
  }, 500)
})

// 页面加载时获取数据
onMounted(async () => {
  try {
    await nextTick()
    await loadStores()
    await loadProducts()
    
    // 如果URL中有店铺参数，自动选择
    const urlParams = new URLSearchParams(window.location.search)
    const storeParam = urlParams.get('store')
    if (storeParam) {
      selectedStoreId.value = storeParam
    }
    
    // 等待店铺加载完成后再加载库存
    if (selectedStoreId.value) {
      await loadInventories()
      await loadLowStockItems()
    }
  } catch (error) {
    console.error('组件初始化失败:', error)
  }
})

// 组件卸载时清理
onUnmounted(() => {
  // 清理定时器和异步操作
  selectedStoreId.value = ''
  searchQuery.value = ''
})
</script>

<style scoped>
.inventory-view {
  max-width: 100%;
}

.page-header {
  margin-bottom: var(--spacing-xl);
  text-align: center;
}

.page-description {
  color: var(--text-secondary);
  font-size: 16px;
  margin-top: var(--spacing-sm);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: var(--spacing-xs);
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-lg);
}

.action-left {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.search-input {
  width: 300px;
}

.action-right {
  display: flex;
  gap: var(--spacing-md);
}

.inventory-table {
  padding: 0;
  overflow: hidden;
}

.product-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.product-details {
  display: flex;
  flex-direction: column;
}

.product-name {
  font-weight: 600;
  color: var(--text-primary);
}

.product-category {
  font-size: 12px;
  color: var(--text-secondary);
}

.pagination-wrapper {
  padding: var(--spacing-lg);
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--border-color);
}

/* 库存相关样式 */
.product-code {
  font-size: 12px;
  color: var(--text-secondary);
}

.stock-range {
  font-size: 12px;
  color: var(--text-secondary);
}

.adjustment-preview {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm);
  background-color: var(--el-color-primary-light-9);
  border-radius: var(--border-radius);
  border-left: 3px solid var(--el-color-primary);
}

.adjustment-preview p {
  margin: 0;
  font-weight: 600;
  color: var(--el-color-primary);
}

/* 对话框样式 */
.dialog-footer {
  text-align: right;
}

.danger-item {
  color: var(--el-color-danger);
}

.danger-item:hover {
  background-color: var(--el-color-danger-light-9);
}

/* 表格样式优化 */
.el-table .el-table__row:hover {
  background-color: var(--el-color-primary-light-9);
}

.el-table .el-table__header {
  font-weight: 600;
}

/* 操作按钮组样式 */
.el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 加载状态优化 */
.el-loading-mask {
  background-color: rgba(255, 255, 255, 0.9);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-bar {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .action-left {
    flex-direction: column;
  }
  
  .search-input {
    width: 100%;
  }
  
  .action-right {
    justify-content: center;
  }
}
</style>
