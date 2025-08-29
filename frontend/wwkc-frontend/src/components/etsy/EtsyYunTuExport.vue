<template>
  <div class="etsy-yuntu-export">
    <!-- Redis缓存状态监控 -->
    <RedisStatusMonitor 
      @sync-data="handleSyncData"
      @clear-all-cache="handleClearAllCache"
      @stats-updated="handleStatsUpdated"
    />

    <div class="component-header">
      <h2>云图导出管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新增导出
        </el-button>
        <el-button @click="showImportDialog = true">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button @click="downloadTemplate">
          <el-icon><Download /></el-icon>
          下载模板
        </el-button>
        <el-button type="success" @click="showExportAnalysisView = true">
          <el-icon><TrendCharts /></el-icon>
          导出分析
        </el-button>
        <el-button type="warning" @click="showQualityControlView = true">
          <el-icon><Setting /></el-icon>
          质量控制
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
            placeholder="SKU、产品名、导出编号"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="导出状态">
          <el-select v-model="filterForm.status" placeholder="选择状态" clearable>
            <el-option label="待导出" value="待导出" />
            <el-option label="导出中" value="导出中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="导出失败" value="导出失败" />
          </el-select>
        </el-form-item>
        <el-form-item label="导出类型">
          <el-select v-model="filterForm.export_type" placeholder="选择类型" clearable>
            <el-option label="产品图片" value="产品图片" />
            <el-option label="产品视频" value="产品视频" />
            <el-option label="产品描述" value="产品描述" />
          </el-select>
        </el-form-item>
        <el-form-item label="店铺">
          <el-input
            v-model="filterForm.store"
            placeholder="店铺名称"
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
      <el-button @click="handleBulkExport">
        批量导出 ({{ selectedRows.length }})
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
      <el-table-column prop="export_number" label="导出编号" width="150" />
      <el-table-column prop="sku" label="SKU" width="120" />
      <el-table-column prop="product_name" label="产品名称" min-width="150" />
      <el-table-column prop="store" label="店铺" width="120" />
      <el-table-column prop="status" label="导出状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="export_type" label="导出类型" width="100">
        <template #default="{ row }">
          <el-tag :type="getExportTypeType(row.export_type)">
            {{ row.export_type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="file_size" label="文件大小" width="100" />
      <el-table-column prop="export_date" label="导出日期" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="150" />
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="success" @click="handleExport(row)">导出</el-button>
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
                <div class="row-cell" style="width: 150px;">{{ item.export_number }}</div>
                <div class="row-cell" style="width: 120px;">{{ item.sku }}</div>
                <div class="row-cell" style="width: 150px;">{{ item.product_name }}</div>
                <div class="row-cell" style="width: 120px;">{{ item.store }}</div>
                <div class="row-cell" style="width: 100px;">
                  <el-tag :type="getStatusType(item.status)">
                    {{ item.status }}
                  </el-tag>
                </div>
                <div class="row-cell" style="width: 100px;">
                  <el-tag :type="getExportTypeType(item.export_type)">
                    {{ item.export_type }}
                  </el-tag>
                </div>
                <div class="row-cell" style="width: 100px;">{{ item.file_size }}</div>
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
      :title="editingItem ? '编辑云图导出' : '新增云图导出'"
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
            <el-form-item label="SKU" prop="sku">
              <el-input v-model="formData.sku" placeholder="请输入SKU" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产品名称" prop="product_name">
              <el-input v-model="formData.product_name" placeholder="请输入产品名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="店铺" prop="store">
              <el-input v-model="formData.store" placeholder="请输入店铺名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="导出类型" prop="export_type">
              <el-select v-model="formData.export_type" placeholder="选择导出类型" style="width: 100%">
                <el-option label="产品图片" value="产品图片" />
                <el-option label="产品视频" value="产品视频" />
                <el-option label="产品描述" value="产品描述" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="导出状态" prop="status">
              <el-select v-model="formData.status" placeholder="选择状态" style="width: 100%">
                <el-option label="待导出" value="待导出" />
                <el-option label="导出中" value="导出中" />
                <el-option label="已完成" value="已完成" />
                <el-option label="导出失败" value="导出失败" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="文件格式" prop="file_format">
              <el-select v-model="formData.file_format" placeholder="选择文件格式" style="width: 100%">
                <el-option label="JPG" value="JPG" />
                <el-option label="PNG" value="PNG" />
                <el-option label="MP4" value="MP4" />
                <el-option label="TXT" value="TXT" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="导出日期" prop="export_date">
              <el-date-picker
                v-model="formData.export_date"
                type="date"
                placeholder="选择导出日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="文件大小" prop="file_size">
              <el-input v-model="formData.file_size" placeholder="请输入文件大小" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="导出路径" prop="export_path">
          <el-input v-model="formData.export_path" placeholder="请输入导出路径" />
        </el-form-item>
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
            <el-option label="导出状态" value="status" />
            <el-option label="导出类型" value="export_type" />
            <el-option label="店铺" value="store" />
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, UploadFilled, View, Refresh, TrendCharts, Setting } from '@element-plus/icons-vue'
import { etsyYunTuExportAPI } from '@/api/etsy'
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
  status: '',
  export_type: '',
  store: '',
  start_date: '',
  end_date: ''
})

// 表单数据
const formData = reactive({
  sku: '',
  product_name: '',
  store: '',
  export_type: '',
  status: '',
  file_format: '',
  export_date: '',
  file_size: '',
  export_path: '',
  remarks: ''
})

// 批量更新表单
const bulkUpdateForm = reactive({
  field: '',
  value: ''
})

// 表单验证规则
const formRules = {
  sku: [{ required: true, message: '请输入SKU', trigger: 'blur' }],
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  store: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }],
  export_type: [{ required: true, message: '请选择导出类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择导出状态', trigger: 'change' }],
  file_format: [{ required: true, message: '请选择文件格式', trigger: 'change' }]
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
    
    const response = await etsyYunTuExportAPI.getList(params)
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
    
    const response = await etsyYunTuExportAPI.getList(params)
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
    status: '',
    export_type: '',
    store: '',
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
    sku: '',
    product_name: '',
    store: '',
    export_type: '',
    status: '',
    file_format: '',
    export_date: '',
    file_size: '',
    export_path: '',
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
    await ElMessageBox.confirm('确定要删除这个云图导出记录吗？', '提示', {
      type: 'warning'
    })
    
    await etsyYunTuExportAPI.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

// 导出
const handleExport = async (row: any) => {
  try {
    await etsyYunTuExportAPI.export(row.id)
    ElMessage.success('导出任务已启动')
    fetchData()
  } catch (error) {
    ElMessage.error('导出失败')
    console.error(error)
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (editingItem.value) {
      await etsyYunTuExportAPI.update(editingItem.value.id, formData)
      ElMessage.success('更新成功')
    } else {
      await etsyYunTuExportAPI.create(formData)
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
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 个云图导出记录吗？`, '提示', {
      type: 'warning'
    })
    
    const ids = selectedRows.value.map(row => row.id)
    await etsyYunTuExportAPI.bulkDelete({ ids })
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

// 批量导出
const handleBulkExport = async () => {
  try {
    const ids = selectedRows.value.map(row => row.id)
    await etsyYunTuExportAPI.bulkExport({ ids })
    ElMessage.success('批量导出任务已启动')
    selectedRows.value = []
    fetchData()
  } catch (error) {
    ElMessage.error('批量导出失败')
    console.error(error)
  }
}

// 批量更新
const handleBulkUpdate = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要更新的云图导出记录')
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
    
    await etsyYunTuExportAPI.bulkUpdate({ ids, updates })
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
    const response = await etsyYunTuExportAPI.downloadTemplate()
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '云图导出表模板.xlsx'
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
    
    await etsyYunTuExportAPI.importData(file)
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

// 获取状态标签类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '待导出': 'warning',
    '导出中': 'info',
    '已完成': 'success',
    '导出失败': 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取导出类型标签类型
const getExportTypeType = (exportType: string) => {
  const exportTypeMap: Record<string, string> = {
    '产品图片': 'primary',
    '产品视频': 'success',
    '产品描述': 'warning'
  }
  return exportTypeMap[exportType] || 'info'
}

// Redis缓存相关方法
const handleSyncData = async () => {
  try {
    await etsyYunTuExportAPI.syncData()
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
    await etsyYunTuExportAPI.clearCache()
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
.etsy-yuntu-export {
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
