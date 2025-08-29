<template>
  <div class="data-table-container">
    <!-- 缓存状态指示器 -->
    <div class="cache-status-bar" v-if="showCacheStatus">
      <el-alert
        :title="cacheStatusTitle"
        :type="cacheStatusType"
        :description="cacheStatusDescription"
        show-icon
        :closable="false"
        class="cache-alert"
      >
        <template #default>
          <div class="cache-actions">
            <el-button 
              size="small" 
              type="primary" 
              @click="handleSyncData"
              :loading="syncing"
              :disabled="cacheStatus.sync_status === 'syncing'"
            >
              <el-icon><Refresh /></el-icon>
              同步数据
            </el-button>
            <el-button 
              size="small" 
              type="warning" 
              @click="handleClearCache"
              :disabled="cacheStatus.sync_status === 'syncing'"
            >
              <el-icon><Delete /></el-icon>
              清除缓存
            </el-button>
          </div>
        </template>
      </el-alert>
    </div>

    <!-- 表格工具栏 -->
    <div class="table-toolbar">
      <div class="toolbar-left">
        <slot name="toolbar-left">
          <el-button type="primary" @click="$emit('add')">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          <el-button @click="$emit('import')">
            <el-icon><Upload /></el-icon>
            批量导入
          </el-button>
          <el-button @click="$emit('export')">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </slot>
      </div>
      
      <div class="toolbar-right">
        <slot name="toolbar-right">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索..."
            clearable
            @keyup.enter="handleSearch"
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-button @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </slot>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="table-wrapper">
      <div class="table-scroll-container" ref="tableScrollContainer">
        <el-table
          :data="tableData"
          :height="tableHeight"
          :max-height="tableHeight"
          v-loading="loading"
          element-loading-text="加载中..."
          element-loading-spinner="el-icon-loading"
          element-loading-background="rgba(255, 255, 255, 0.8)"
          @selection-change="handleSelectionChange"
          @sort-change="handleSortChange"
          stripe
          border
          class="data-table"
          :show-header="true"
          :highlight-current-row="true"
          :row-class-name="getRowClassName"
        >
          <!-- 选择列 -->
          <el-table-column
            v-if="showSelection"
            type="selection"
            width="55"
            align="center"
            fixed="left"
          />
          
          <!-- 序号列 -->
          <el-table-column
            v-if="showIndex"
            type="index"
            label="序号"
            width="60"
            align="center"
            fixed="left"
          />
          
          <!-- 动态列 -->
          <el-table-column
            v-for="column in visibleColumns"
            :key="column.prop"
            :prop="column.prop"
            :label="column.label"
            :width="column.width"
            :min-width="column.minWidth"
            :align="column.align || 'left'"
            :sortable="column.sortable"
            :fixed="column.fixed"
            :show-overflow-tooltip="column.showOverflowTooltip !== false"
          >
            <template #default="scope" v-if="column.template">
              <component 
                :is="column.template" 
                :row="scope.row" 
                :column="column"
                :index="scope.$index"
              />
            </template>
          </el-table-column>
          
          <!-- 操作列 -->
          <el-table-column
            v-if="showActions"
            label="操作"
            width="150"
            align="center"
            fixed="right"
          >
            <template #default="scope">
              <el-button 
                size="small" 
                type="primary" 
                @click="handleEdit(scope.row)"
              >
                编辑
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="handleDelete(scope.row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 分页器 -->
      <div class="pagination-wrapper" v-if="showPagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100, 200, 500]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handleCurrentPageChange"
          background
          class="pagination"
        />
      </div>
    </div>

    <!-- 批量操作工具栏 -->
    <div class="batch-toolbar" v-if="showBatchActions && selectedRows.length > 0">
      <div class="batch-info">
        已选择 <span class="selected-count">{{ selectedRows.length }}</span> 项
      </div>
      <div class="batch-actions">
        <slot name="batch-actions" :selected-rows="selectedRows">
          <el-button size="small" type="danger" @click="$emit('batch-delete', selectedRows)">
            批量删除
          </el-button>
          <el-button size="small" type="warning" @click="$emit('batch-update', selectedRows)">
            批量更新
          </el-button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Upload, Download, Search, Delete } from '@element-plus/icons-vue'

// 定义组件属性
interface Props {
  // 表格数据
  data: any[]
  // 列配置
  columns: Array<{
    prop: string
    label: string
    width?: number | string
    minWidth?: number | string
    align?: 'left' | 'center' | 'right'
    sortable?: boolean
    fixed?: boolean | 'left' | 'right'
    showOverflowTooltip?: boolean
    render?: any
  }>
  // 分页相关
  total?: number
  currentPage?: number
  pageSize?: number
  pageSizes?: number[]
  // 表格高度
  height?: number | string
  // 是否显示选择列
  showSelection?: boolean
  // 是否显示序号列
  showIndex?: boolean
  // 是否显示操作列
  showActions?: boolean
  // 操作列宽度
  actionsWidth?: number | string
  // 是否显示分页
  showPagination?: boolean
  // 分页布局
  paginationLayout?: string
  // 是否显示批量操作
  showBatchActions?: boolean
  // 是否显示水平滚动条
  showHorizontalScroll?: boolean
  // 是否显示缓存状态
  showCacheStatus?: boolean
  // 缓存状态
  cacheStatus?: any
  // 加载状态
  loading?: boolean
}

// 定义事件
interface Emits {
  (e: 'update:currentPage', page: number): void
  (e: 'update:pageSize', size: number): void
  (e: 'selection-change', rows: any[]): void
  (e: 'sort-change', sort: any): void
  (e: 'search', keyword: string): void
  (e: 'refresh'): void
  (e: 'add'): void
  (e: 'edit', row: any): void
  (e: 'delete', row: any): void
  (e: 'import'): void
  (e: 'export'): void
  (e: 'batch-delete', rows: any[]): void
  (e: 'batch-update', rows: any[]): void
  (e: 'sync-data'): void
  (e: 'clear-cache'): void
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  columns: () => [],
  total: 0,
  currentPage: 1,
  pageSize: 20,
  pageSizes: () => [10, 20, 50, 100],
  height: 400,
  showSelection: false,
  showIndex: false,
  showActions: true,
  actionsWidth: 150,
  showPagination: true,
  paginationLayout: 'total, sizes, prev, pager, next, jumper',
  showBatchActions: false,
  showHorizontalScroll: true,
  showCacheStatus: false,
  cacheStatus: () => ({}),
  loading: false
})

const emit = defineEmits<Emits>()

// 响应式数据
const searchKeyword = ref('')
const selectedRows = ref<any[]>([])
const scrollPosition = ref(0)
const maxScrollPosition = ref(100)
const tableScrollContainer = ref<HTMLElement>()
const syncing = ref(false)

// 计算属性
const tableData = computed(() => props.data)
const tableHeight = computed(() => props.height)
const visibleColumns = computed(() => props.columns.filter(col => col.prop))

const cacheStatusTitle = computed(() => {
  const status = props.cacheStatus.sync_status
  switch (status) {
    case 'syncing':
      return '数据同步中...'
    case 'completed':
      return '数据已同步'
    case 'failed':
      return '数据同步失败'
    default:
      return '缓存状态'
  }
})

const cacheStatusType = computed(() => {
  const status = props.cacheStatus.sync_status
  switch (status) {
    case 'syncing':
      return 'info'
    case 'completed':
      return 'success'
    case 'failed':
      return 'error'
    default:
      return 'info'
  }
})

const cacheStatusDescription = computed(() => {
  const status = props.cacheStatus
  if (status.is_cached) {
    return `数据来自Redis缓存，TTL: ${status.cache_ttl}s，最后同步: ${status.last_sync}`
  } else {
    return '数据来自MySQL数据库，正在同步到Redis...'
  }
})

// 方法
const handleSearch = () => {
  emit('search', searchKeyword.value)
}

const handleRefresh = () => {
  emit('refresh')
}

const handleSelectionChange = (rows: any[]) => {
  selectedRows.value = rows
  emit('selection-change', rows)
}

const handleSortChange = (sort: any) => {
  emit('sort-change', sort)
}

const handleSizeChange = (size: number) => {
  emit('update:pageSize', size)
}

const handleCurrentChange = (page: number) => {
  emit('update:currentPage', page)
}

const handleScrollChange = (position: number) => {
  if (tableScrollContainer.value) {
    const container = tableScrollContainer.value
    const scrollWidth = container.scrollWidth - container.clientWidth
    const scrollLeft = (position / maxScrollPosition.value) * scrollWidth
    container.scrollLeft = scrollLeft
  }
}

const handleSyncData = async () => {
  try {
    syncing.value = true
    emit('sync-data')
    ElMessage.success('数据同步已启动')
  } catch (error) {
    ElMessage.error('数据同步失败')
  } finally {
    syncing.value = false
  }
}

const handleClearCache = async () => {
  try {
    await ElMessageBox.confirm('确定要清除缓存吗？这将重新从数据库加载数据。', '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    emit('clear-cache')
    ElMessage.success('缓存已清除')
  } catch (error) {
    // 用户取消操作
  }
}

// 监听滚动事件
const handleTableScroll = () => {
  if (tableScrollContainer.value) {
    const container = tableScrollContainer.value
    const scrollLeft = container.scrollLeft
    const scrollWidth = container.scrollWidth - container.clientWidth
    
    if (scrollWidth > 0) {
      const position = (scrollLeft / scrollWidth) * maxScrollPosition.value
      scrollPosition.value = Math.round(position)
    }
  }
}

// 生命周期
onMounted(async () => {
  await nextTick()
  
  if (tableScrollContainer.value && props.showHorizontalScroll) {
    tableScrollContainer.value.addEventListener('scroll', handleTableScroll)
    
    // 计算最大滚动位置
    const container = tableScrollContainer.value
    const scrollWidth = container.scrollWidth - container.clientWidth
    maxScrollPosition.value = Math.max(scrollWidth, 100)
  }
})

// 监听数据变化，重新计算滚动位置
watch(() => props.data, async () => {
  await nextTick()
  if (tableScrollContainer.value && props.showHorizontalScroll) {
    const container = tableScrollContainer.value
    const scrollWidth = container.scrollWidth - container.clientWidth
    maxScrollPosition.value = Math.max(scrollWidth, 100)
  }
}, { deep: true })

// 行样式类名
const getRowClassName = ({ row, rowIndex }: { row: any, rowIndex: number }) => {
  if (rowIndex % 2 === 0) {
    return 'even-row'
  }
  return 'odd-row'
}

// 编辑行
const handleEdit = (row: any) => {
  emit('edit', row)
}

// 删除行
const handleDelete = (row: any) => {
  emit('delete', row)
}

// 分页大小变化
const handlePageSizeChange = (size: number) => {
  emit('update:page-size', size)
}

// 当前页变化
const handleCurrentPageChange = (page: number) => {
  emit('update:current-page', page)
}
</script>

<style scoped>
.data-table-container {
  width: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.cache-status-bar {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.cache-alert {
  margin-bottom: 0;
}

.cache-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.toolbar-left {
  display: flex;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 250px;
}

.table-wrapper {
  position: relative;
}

.table-scroll-container {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 600px;
}

.data-table {
  width: 100%;
}

.data-table .even-row {
  background-color: #fafafa;
}

.data-table .odd-row {
  background-color: #ffffff;
}

.data-table .even-row:hover,
.data-table .odd-row:hover {
  background-color: #f0f9eb !important;
}
  overflow-y: hidden;
}

.data-table {
  width: 100%;
  min-width: 100%;
}

.horizontal-scrollbar {
  padding: 8px 16px;
  background: #f5f5f5;
  border-top: 1px solid #e0e0e0;
}

.scroll-slider {
  margin: 0;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 16px;
  border-top: 1px solid #f0f0f0;
}

.pagination {
  margin: 0;
}

.batch-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f0f9ff;
  border-top: 1px solid #e0f2fe;
}

.batch-info {
  color: #1890ff;
  font-weight: 500;
}

.selected-count {
  font-weight: bold;
  color: #1890ff;
}

.batch-actions {
  display: flex;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .table-toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .toolbar-left,
  .toolbar-right {
    justify-content: center;
  }
  
  .search-input {
    width: 100%;
  }
  
  .batch-toolbar {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
}
</style>
