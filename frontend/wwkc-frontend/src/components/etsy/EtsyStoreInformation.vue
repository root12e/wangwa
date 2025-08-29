<template>
  <div class="etsy-store-information">
    <!-- Redis缓存状态监控 -->
    <RedisStatusMonitor 
      @sync-data="handleSyncData"
      @clear-all-cache="handleClearAllCache"
      @stats-updated="handleStatsUpdated"
    />

    <div class="component-header">
      <h2>店铺信息管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新增店铺
        </el-button>
        <el-button @click="showImportDialog = true">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button @click="downloadTemplate">
          <el-icon><Download /></el-icon>
          下载模板
        </el-button>
        <el-button type="success" @click="showAnalyticsView = true">
          <el-icon><TrendCharts /></el-icon>
          店铺分析
        </el-button>
        <el-button 
          :type="showVirtualTable ? 'success' : 'warning'" 
          @click="toggleVirtualTable"
        >
          <el-icon><View /></el-icon>
          {{ showVirtualTable ? '标准视图' : '高性能视图' }}
        </el-button>
      </div>
    </div>

    <!-- 筛选和排序 -->
    <div class="filter-section">
      <el-form :model="filterForm" inline>
        <el-form-item label="搜索关键词">
          <el-input
            v-model="filterForm.search"
            placeholder="店铺名、店铺ID、产品类型"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="店铺状态">
          <el-select v-model="filterForm.store_status" placeholder="选择状态" clearable>
            <el-option label="正常运营" value="正常运营" />
            <el-option label="暂停运营" value="暂停运营" />
            <el-option label="已关闭" value="已关闭" />
            <el-option label="待审核" value="待审核" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品类型">
          <el-select v-model="filterForm.product_type" placeholder="选择产品类型" clearable>
            <el-option label="服装" value="服装" />
            <el-option label="家居" value="家居" />
            <el-option label="数码" value="数码" />
            <el-option label="美妆" value="美妆" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="运营人员">
          <el-input
            v-model="filterForm.operation_personnel"
            placeholder="运营人员姓名"
            clearable
          />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="filterForm.start_date"
            type="date"
            placeholder="开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="filterForm.end_date"
            type="date"
            placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 批量操作 -->
    <div class="bulk-actions" v-if="selectedRows.length > 0">
      <el-button type="danger" @click="handleBulkDelete">
        批量删除 ({{ selectedRows.length }})
      </el-button>
      <el-button @click="handleBulkUpdate">
        批量更新 ({{ selectedRows.length }})
      </el-button>
    </div>

    <!-- 标准数据表格 -->
    <el-table
      v-if="!showVirtualTable"
      :data="tableData"
      v-loading="loading"
      @selection-change="handleSelectionChange"
      border
      stripe
      style="width: 100%"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="store_id" label="店铺ID" width="120" />
      <el-table-column prop="store_name" label="店铺名称" min-width="150" />
      <el-table-column prop="store_status" label="店铺状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStoreStatusType(row.store_status)">
            {{ row.store_status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="product_type" label="产品类型" width="100" />
      <el-table-column prop="operation_personnel" label="运营人员" width="100" />
      <el-table-column prop="product_count" label="产品数量" width="100" />
      <el-table-column prop="sales_amount" label="销售额" width="120">
        <template #default="{ row }">
          ¥{{ row.sales_amount }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="150" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 高性能虚拟滚动表格 -->
    <div class="virtual-table-container" v-if="showVirtualTable">
      <div class="virtual-table-header">
        <h3>高性能数据视图 ({{ virtualTableData.length }} 条记录)</h3>
        <div class="virtual-table-controls">
          <el-button size="small" @click="toggleVirtualTable">
            <el-icon><View /></el-icon>
            切换视图
          </el-button>
          <el-button size="small" @click="refreshVirtualTable">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
      
      <div class="virtual-table-wrapper" ref="virtualTableWrapper">
        <div 
          class="virtual-table-content"
          :style="{ height: virtualTableHeight + 'px' }"
          @scroll="handleVirtualTableScroll"
        >
          <div 
            class="virtual-table-inner"
            :style="{ height: totalVirtualHeight + 'px' }"
          >
            <div
              v-for="(item, index) in visibleVirtualItems"
              :key="item.id || index"
              class="virtual-table-row"
              :style="{ 
                position: 'absolute',
                top: (index * virtualRowHeight) + 'px',
                height: virtualRowHeight + 'px',
                width: '100%'
              }"
            >
              <div class="virtual-row-content">
                <div class="row-cell" style="width: 120px;">{{ item.store_id }}</div>
                <div class="row-cell" style="width: 150px;">{{ item.store_name }}</div>
                <div class="row-cell" style="width: 100px;">
                  <el-tag :type="getStoreStatusType(item.store_status)">
                    {{ item.store_status }}
                  </el-tag>
                </div>
                <div class="row-cell" style="width: 100px;">{{ item.product_type }}</div>
                <div class="row-cell" style="width: 100px;">{{ item.operation_personnel }}</div>
                <div class="row-cell" style="width: 100px;">{{ item.product_count }}</div>
                <div class="row-cell" style="width: 120px;">
                  <el-button size="small" @click="handleQuickEdit(item)">快速编辑</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="!showVirtualTable">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingItem ? '编辑店铺信息' : '新增店铺信息'"
      width="800px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="店铺ID" prop="store_id">
              <el-input v-model="formData.store_id" placeholder="请输入店铺ID" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="店铺名称" prop="store_name">
              <el-input v-model="formData.store_name" placeholder="请输入店铺名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="店铺状态" prop="store_status">
              <el-select v-model="formData.store_status" placeholder="选择状态" style="width: 100%">
                <el-option label="正常运营" value="正常运营" />
                <el-option label="暂停运营" value="暂停运营" />
                <el-option label="已关闭" value="已关闭" />
                <el-option label="待审核" value="待审核" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产品类型" prop="product_type">
              <el-select v-model="formData.product_type" placeholder="选择产品类型" style="width: 100%">
                <el-option label="服装" value="服装" />
                <el-option label="家居" value="家居" />
                <el-option label="数码" value="数码" />
                <el-option label="美妆" value="美妆" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="运营人员" prop="operation_personnel">
              <el-input v-model="formData.operation_personnel" placeholder="请输入运营人员姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产品数量" prop="product_count">
              <el-input-number v-model="formData.product_count" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="销售额" prop="sales_amount">
              <el-input-number 
                v-model="formData.sales_amount" 
                :precision="2" 
                :min="0" 
                placeholder="请输入销售额"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="店铺地址" prop="store_address">
              <el-input v-model="formData.store_address" placeholder="请输入店铺地址" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="formData.remarks"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingItem ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量更新对话框 -->
    <el-dialog v-model="showBulkUpdateDialog" title="批量更新" width="600px">
      <el-form :model="bulkUpdateForm" label-width="120px">
        <el-form-item label="更新字段">
          <el-select v-model="bulkUpdateForm.field" placeholder="选择要更新的字段" style="width: 100%">
            <el-option label="店铺状态" value="store_status" />
            <el-option label="产品类型" value="product_type" />
            <el-option label="运营人员" value="operation_personnel" />
            <el-option label="备注" value="remarks" />
          </el-select>
        </el-form-item>
        <el-form-item label="更新值">
          <el-input v-model="bulkUpdateForm.value" placeholder="请输入新的值" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBulkUpdateDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmBulkUpdate" :loading="submitting">
          确认更新
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="批量导入" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="fileList"
        accept=".xlsx,.csv"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 xlsx/csv 文件，且不超过 10MB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importing">
          开始导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 店铺分析视图对话框 -->
    <el-dialog v-model="showAnalyticsView" title="店铺分析" width="1200px">
      <div class="analytics-view">
        <div class="view-header">
          <el-alert
            title="店铺运营数据分析，包含销售趋势、产品分布、状态统计等信息"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
        
        <!-- 统计卡片 -->
        <div class="stats-cards">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-number">{{ analyticsData.totalStores }}</div>
                  <div class="stat-label">总店铺数</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-number">{{ analyticsData.activeStores }}</div>
                  <div class="stat-label">活跃店铺</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-number">{{ analyticsData.totalProducts }}</div>
                  <div class="stat-label">总产品数</div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-number">${{ formatCurrency(analyticsData.totalSales) }}</div>
                  <div class="stat-label">总销售额</div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <!-- 状态分布图表 -->
        <div class="chart-section">
          <el-card>
            <template #header>
              <span>店铺状态分布</span>
            </template>
            <div class="chart-container">
              <div class="chart-placeholder">
                图表区域 - 可集成 ECharts 等图表库
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, UploadFilled, View, Refresh, TrendCharts } from '@element-plus/icons-vue'
import { etsyStoreInformationAPI } from '@/api/etsy'
import RedisStatusMonitor from '@/components/common/RedisStatusMonitor.vue'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const importing = ref(false)
const showCreateDialog = ref(false)
const showImportDialog = ref(false)
const showBulkUpdateDialog = ref(false)
const editingItem = ref(null)
const selectedRows = ref([])
const fileList = ref([])
const showVirtualTable = ref(false) // 控制虚拟滚动表格的显示

// 表格数据
const tableData = ref([])

// 虚拟滚动数据
const virtualTableData = ref([])
const virtualRowHeight = ref(50) // 每行的高度
const virtualTableHeight = ref(400) // 虚拟表格的容器高度
const virtualTableWrapper = ref<HTMLElement | null>(null)
const virtualScrollTop = ref(0)
const visibleVirtualItems = ref([])
const totalVirtualHeight = ref(0)
const virtualBufferSize = ref(20) // 缓冲区大小，用于优化滚动性能

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 筛选表单
const filterForm = reactive({
  search: '',
  store_status: '',
  product_type: '',
  operation_personnel: '',
  start_date: '',
  end_date: ''
})

// 表单数据
const formData = reactive({
  store_id: '',
  store_name: '',
  store_status: '',
  product_type: '',
  operation_personnel: '',
  product_count: 0,
  sales_amount: 0,
  store_address: '',
  remarks: ''
})

// 批量更新表单
const bulkUpdateForm = reactive({
  field: '',
  value: ''
})

// 分析数据
const analyticsData = reactive({
  totalStores: 0,
  activeStores: 0,
  totalProducts: 0,
  totalSales: 0
})

// 表单验证规则
const formRules = {
  store_id: [{ required: true, message: '请输入店铺ID', trigger: 'blur' }],
  store_name: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }],
  store_status: [{ required: true, message: '请选择店铺状态', trigger: 'change' }],
  product_type: [{ required: true, message: '请选择产品类型', trigger: 'change' }],
  operation_personnel: [{ required: true, message: '请输入运营人员姓名', trigger: 'blur' }]
}

// 表单引用
const formRef = ref()

// 初始化
onMounted(() => {
  fetchData()
})

// 获取数据
const fetchData = async () => {
  try {
    loading.value = true
    const params = {
      ...filterForm,
      page: pagination.page,
      page_size: pagination.page_size
    }
    
    const response = await etsyStoreInformationAPI.getList(params)
    tableData.value = response.data.results || response.data
    pagination.total = response.data.count || response.data.length
    
    // 同时更新虚拟表格数据
    if (showVirtualTable.value) {
      await fetchAllDataForVirtualTable()
    }
  } catch (error) {
    ElMessage.error('获取数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 为虚拟表格获取所有数据
const fetchAllDataForVirtualTable = async () => {
  try {
    const params = {
      ...filterForm,
      page: 1,
      page_size: 10000 // 获取大量数据
    }
    
    const response = await etsyStoreInformationAPI.getList(params)
    virtualTableData.value = response.data.results || response.data
    
    // 更新虚拟表格
    nextTick(() => {
      updateVirtualTable()
    })
  } catch (error) {
    console.error('获取虚拟表格数据失败:', error)
    ElMessage.error('获取虚拟表格数据失败')
  }
}

// 虚拟滚动相关方法
const updateVirtualTable = () => {
  if (!virtualTableWrapper.value || virtualTableData.value.length === 0) return

  const scrollTop = virtualScrollTop.value
  const containerHeight = virtualTableHeight.value

  // 计算可见区域的起始和结束索引
  const start = Math.max(0, Math.floor(scrollTop / virtualRowHeight.value) - virtualBufferSize.value)
  const end = Math.min(
    virtualTableData.value.length,
    Math.ceil((scrollTop + containerHeight) / virtualRowHeight.value) + virtualBufferSize.value
  )

  // 更新可见项目
  visibleVirtualItems.value = virtualTableData.value.slice(start, end)
  
  // 计算总高度
  totalVirtualHeight.value = virtualTableData.value.length * virtualRowHeight.value
}

// 优化滚动性能
const handleVirtualTableScroll = (event: Event) => {
  const target = event.target as HTMLElement
  virtualScrollTop.value = target.scrollTop
  
  // 使用 requestAnimationFrame 优化滚动性能
  requestAnimationFrame(() => {
    updateVirtualTable()
  })
}

const refreshVirtualTable = () => {
  fetchData() // 重新从后端获取所有数据
  updateVirtualTable() // 更新虚拟表格
}

const toggleVirtualTable = () => {
  showVirtualTable.value = !showVirtualTable.value
  if (showVirtualTable.value) {
    fetchData() // 切换到虚拟表格时，重新获取所有数据
    updateVirtualTable() // 更新虚拟表格
  }
}

const handleQuickEdit = (row: any) => {
  editingItem.value = row
  Object.assign(formData, row)
  showCreateDialog.value = true
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

// 重置筛选
const resetFilter = () => {
  Object.assign(filterForm, {
    search: '',
    store_status: '',
    product_type: '',
    operation_personnel: '',
    start_date: '',
    end_date: ''
  })
  pagination.page = 1
  fetchData()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.page_size = size
  pagination.page = 1
  fetchData()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchData()
}

// 选择行
const handleSelectionChange = (rows: any[]) => {
  selectedRows.value = rows
}

// 新增
const handleCreate = () => {
  editingItem.value = null
  Object.assign(formData, {
    store_id: '',
    store_name: '',
    store_status: '',
    product_type: '',
    operation_personnel: '',
    product_count: 0,
    sales_amount: 0,
    store_address: '',
    remarks: ''
  })
  showCreateDialog.value = true
}

// 编辑
const handleEdit = (row: any) => {
  editingItem.value = row
  Object.assign(formData, row)
  showCreateDialog.value = true
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个店铺信息吗？', '提示', {
      type: 'warning'
    })
    
    await etsyStoreInformationAPI.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (editingItem.value) {
      await etsyStoreInformationAPI.update(editingItem.value.id, formData)
      ElMessage.success('更新成功')
    } else {
      await etsyStoreInformationAPI.create(formData)
      ElMessage.success('创建成功')
    }
    
    showCreateDialog.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

// 批量删除
const handleBulkDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 个店铺信息吗？`, '提示', {
      type: 'warning'
    })
    
    const ids = selectedRows.value.map(row => row.id)
    await etsyStoreInformationAPI.bulkDelete({ ids })
    ElMessage.success('批量删除成功')
    selectedRows.value = []
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
      console.error(error)
    }
  }
}

// 批量更新
const handleBulkUpdate = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要更新的店铺信息')
    return
  }
  showBulkUpdateDialog.value = true
}

// 确认批量更新
const confirmBulkUpdate = async () => {
  try {
    if (!bulkUpdateForm.field || !bulkUpdateForm.value) {
      ElMessage.warning('请填写完整的更新信息')
      return
    }
    
    submitting.value = true
    const ids = selectedRows.value.map(row => row.id)
    const updates = { [bulkUpdateForm.field]: bulkUpdateForm.value }
    
    await etsyStoreInformationAPI.bulkUpdate({ ids, updates })
    ElMessage.success('批量更新成功')
    
    showBulkUpdateDialog.value = false
    selectedRows.value = []
    fetchData()
  } catch (error) {
    ElMessage.error('批量更新失败')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

// 下载模板
const downloadTemplate = async () => {
  try {
    const response = await etsyStoreInformationAPI.downloadTemplate()
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '店铺信息表模板.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载模板失败')
    console.error(error)
  }
}

// 文件选择
const handleFileChange = (file: any) => {
  fileList.value = [file]
}

// 导入数据
const handleImport = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择要导入的文件')
    return
  }
  
  try {
    importing.value = true
    const file = fileList.value[0].raw
    
    await etsyStoreInformationAPI.importData(file)
    ElMessage.success('导入成功')
    
    showImportDialog.value = false
    fileList.value = []
    fetchData()
  } catch (error) {
    ElMessage.error('导入失败')
    console.error(error)
  } finally {
    importing.value = false
  }
}

// 获取店铺状态标签类型
const getStoreStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '正常运营': 'success',
    '暂停运营': 'warning',
    '已关闭': 'danger',
    '待审核': 'info'
  }
  return statusMap[status] || 'info'
}

// 格式化货币
const formatCurrency = (amount: number) => {
  return amount.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// Redis缓存相关方法
const handleSyncData = async () => {
  try {
    await etsyStoreInformationAPI.syncData()
    ElMessage.success('数据同步已启动')
    
    // 等待同步完成后刷新数据
    setTimeout(() => {
      fetchData()
    }, 3000)
  } catch (error) {
    console.error('数据同步失败:', error)
    ElMessage.error('数据同步失败')
  }
}

const handleClearAllCache = async () => {
  try {
    await etsyStoreInformationAPI.clearCache()
    ElMessage.success('缓存已清除')
    
    // 刷新数据
    fetchData()
  } catch (error) {
    console.error('清除缓存失败:', error)
    ElMessage.error('清除缓存失败')
  }
}

const handleStatsUpdated = (stats: any) => {
  // 处理统计信息更新
  console.log('统计信息已更新:', stats)
}
</script>

<style scoped>
.etsy-store-information {
  padding: 20px;
}

.component-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.component-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.bulk-actions {
  margin-bottom: 16px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

.virtual-table-container {
  margin-top: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.virtual-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  background-color: #f8f9fa;
}

.virtual-table-header h3 {
  margin: 0;
  color: #333;
  font-size: 16px;
}

.virtual-table-controls {
  display: flex;
  gap: 10px;
}

.virtual-table-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.virtual-table-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.virtual-table-inner {
  position: relative;
  width: 100%;
  height: 100%;
}

.virtual-table-row {
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fff;
  transition: background-color 0.2s ease;
}

.virtual-table-row:hover {
  background-color: #f0f9eb;
}

.virtual-table-row:nth-child(even) {
  background-color: #fafafa;
}

.virtual-table-row:nth-child(even):hover {
  background-color: #f0f9eb;
}

.virtual-row-content {
  display: flex;
  align-items: center;
  width: 100%;
  height: 100%;
}

.row-cell {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
