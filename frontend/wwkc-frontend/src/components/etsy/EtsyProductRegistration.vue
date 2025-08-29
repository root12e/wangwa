<template>
  <div class="etsy-product-registration">
    <!-- Redis缓存状态监控 -->
    <RedisStatusMonitor 
      @sync-data="handleSyncData"
      @clear-all-cache="handleClearAllCache"
      @stats-updated="handleStatsUpdated"
    />

    <!-- 统计卡片 -->
    <div class="statistics-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.total_count }}</div>
              <div class="stat-label">总产品数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.today_count }}</div>
              <div class="stat-label">今日新增</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.low_inventory_count }}</div>
              <div class="stat-label">库存不足</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.avg_profit_margin }}%</div>
              <div class="stat-label">平均毛利率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 高级筛选 -->
    <div class="advanced-filter-section">
      <el-collapse v-model="activeCollapse">
        <el-collapse-item title="高级筛选" name="1">
          <el-form :model="filterForm" inline class="filter-form">
            <el-form-item label="搜索关键词">
              <el-input
                v-model="filterForm.search"
                placeholder="SKU、店铺名、产品名"
                clearable
                @keyup.enter="handleSearch"
              />
            </el-form-item>
            <el-form-item label="店铺筛选">
              <el-select v-model="filterForm.store" placeholder="选择店铺" clearable>
                <el-option 
                  v-for="store in storeOptions" 
                  :key="store" 
                  :label="store" 
                  :value="store" 
                />
              </el-select>
            </el-form-item>
            <el-form-item label="库存状态">
              <el-select v-model="filterForm.inventory_status" placeholder="选择状态" clearable>
                <el-option label="充足" value="sufficient" />
                <el-option label="不足" value="insufficient" />
                <el-option label="告警" value="warning" />
              </el-select>
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
          </el-form>
          
          <!-- 滑动条筛选 -->
          <div class="slider-filters">
            <div class="slider-group">
              <label>单位成本范围 (¥)</label>
              <el-slider
                v-model="filterForm.cost_range"
                range
                :min="0"
                :max="1000"
                :step="10"
                show-input
                show-input-controls
                @change="handleCostRangeChange"
              />
            </div>
            
            <div class="slider-group">
              <label>预估售价范围 (¥)</label>
              <el-slider
                v-model="filterForm.price_range"
                range
                :min="0"
                :max="2000"
                :step="20"
                show-input
                show-input-controls
                @change="handlePriceRangeChange"
              />
            </div>
            
            <div class="slider-group">
              <label>库存范围</label>
              <el-slider
                v-model="filterForm.inventory_range"
                range
                :min="0"
                :max="1000"
                :step="10"
                show-input
                show-input-controls
                @change="handleInventoryRangeChange"
              />
            </div>
            
            <div class="slider-group">
              <label>预估毛利率范围 (%)</label>
              <el-slider
                v-model="filterForm.profit_margin_range"
                range
                :min="0"
                :max="100"
                :step="5"
                show-input
                show-input-controls
                @change="handleProfitMarginRangeChange"
              />
            </div>
          </div>
          
          <div class="filter-actions">
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetFilters">重置筛选</el-button>
            <el-button type="success" @click="applyFilters">应用筛选</el-button>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

    <!-- 数据表格 -->
    <DataTable
      :data="tableData"
      :columns="tableColumns"
      :total="pagination.total"
      :current-page="pagination.currentPage"
      :page-size="pagination.pageSize"
      :loading="loading"
      :show-selection="true"
      :show-index="true"
      :show-batch-actions="true"
      :show-horizontal-scroll="true"
      :show-cache-status="true"
      :cache-status="cacheStatus"
      height="600"
      @update:current-page="handlePageChange"
      @update:page-size="handlePageSizeChange"
      @selection-change="handleSelectionChange"
      @search="handleTableSearch"
      @refresh="fetchData"
      @add="showCreateDialog = true"
      @import="showImportDialog = true"
      @export="exportData"
      @edit="handleEdit"
      @delete="handleDelete"
      @batch-delete="handleBatchDelete"
      @batch-update="handleBatchUpdate"
      @sync-data="handleSyncData"
      @clear-cache="handleClearCache"
    >
      <template #toolbar-left>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新增产品
        </el-button>
        <el-button @click="showImportDialog = true">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button @click="downloadTemplate">
          <el-icon><Download /></el-icon>
          下载模板
        </el-button>
        <el-button type="success" @click="showProductAnalysisView = true">
          <el-icon><TrendCharts /></el-icon>
          产品分析
        </el-button>
        <el-button type="warning" @click="showBulkRegistrationView = true">
          <el-icon><Edit /></el-icon>
          批量注册
        </el-button>
        <el-button type="info" @click="exportData">
          <el-icon><Document /></el-icon>
          导出数据
        </el-button>
        <el-button 
          :type="showVirtualTable ? 'success' : 'warning'" 
          @click="toggleVirtualTable"
        >
          <el-icon><View /></el-icon>
          {{ showVirtualTable ? '标准视图' : '高性能视图' }}
        </el-button>
      </template>
      
      <template #toolbar-right>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索产品..."
          clearable
          @keyup.enter="handleSearch"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-button @click="fetchData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </template>
      
      <template #batch-actions="{ selectedRows }">
        <el-button size="small" type="danger" @click="handleBatchDelete(selectedRows)">
          批量删除
        </el-button>
        <el-button size="small" type="warning" @click="handleBatchUpdate(selectedRows)">
          批量更新
        </el-button>
        <el-button size="small" type="success" @click="handleBatchExport(selectedRows)">
          批量导出
        </el-button>
      </template>
    </DataTable>

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
                <div class="row-cell" style="width: 200px;">
                  <el-image
                    v-if="item.product_image"
                    :src="item.product_image"
                    :preview-src-list="[item.product_image]"
                    fit="cover"
                    class="product-thumbnail"
                  />
                  <span v-else class="no-image">无图片</span>
                </div>
                <div class="row-cell" style="width: 150px;">{{ item.product_name }}</div>
                <div class="row-cell" style="width: 120px;">{{ item.store_sku }}</div>
                <div class="row-cell" style="width: 120px;">{{ item.listing_store }}</div>
                <div class="row-cell" style="width: 100px;">{{ item.inventory }}</div>
                <div class="row-cell" style="width: 100px;">¥{{ item.unit_cost }}</div>
                <div class="row-cell" style="width: 100px;">{{ item.estimated_gross_profit_margin }}%</div>
                <div class="row-cell" style="width: 150px;">
                  <el-tag 
                    :type="getInventoryStatusType(item.inventory, item.inventory_warning_line)"
                    size="small"
                  >
                    {{ getInventoryStatusText(item.inventory, item.inventory_warning_line) }}
                  </el-tag>
                </div>
                <div class="row-cell" style="width: 120px;">
                  <el-button size="small" @click="handleQuickEdit(item)">快速编辑</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingItem ? '编辑产品' : '新增产品'"
      width="80%"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        class="product-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="产品名称" prop="product_name">
              <el-input v-model="formData.product_name" placeholder="请输入产品名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开发者" prop="developer">
              <el-input v-model="formData.developer" placeholder="请输入开发者" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上架店铺" prop="listing_store">
              <el-select v-model="formData.listing_store" placeholder="选择店铺" filterable>
                <el-option 
                  v-for="store in storeOptions" 
                  :key="store" 
                  :label="store" 
                  :value="store" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="店铺SKU" prop="store_sku">
              <el-input v-model="formData.store_sku" placeholder="请输入店铺SKU" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="1688 SKU" prop="sku_1688">
              <el-input v-model="formData.sku_1688" placeholder="请输入1688 SKU" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位成本" prop="unit_cost">
              <el-input-number 
                v-model="formData.unit_cost" 
                :precision="2" 
                :min="0" 
                placeholder="请输入单位成本"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预估售价" prop="estimated_price">
              <el-input-number 
                v-model="formData.estimated_price" 
                :precision="2" 
                :min="0" 
                placeholder="请输入预估售价"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="库存数量" prop="inventory">
              <el-input-number 
                v-model="formData.inventory" 
                :min="0" 
                placeholder="请输入库存数量"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="库存标准线" prop="inventory_standard_line">
              <el-input-number 
                v-model="formData.inventory_standard_line" 
                :min="0" 
                placeholder="请输入库存标准线"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="库存告警线" prop="inventory_warning_line">
              <el-input-number 
                v-model="formData.inventory_warning_line" 
                :min="0" 
                placeholder="请输入库存告警线"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="申报中文名" prop="declaration_chinese_name">
              <el-input v-model="formData.declaration_chinese_name" placeholder="请输入申报中文名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="申报英文名" prop="declaration_english_name">
              <el-input v-model="formData.declaration_english_name" placeholder="请输入申报英文名" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="生产方式" prop="production_method">
              <el-input v-model="formData.production_method" placeholder="请输入生产方式" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工艺" prop="craft_technology">
              <el-input v-model="formData.craft_technology" placeholder="请输入工艺" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="采购链接" prop="purchase_link">
              <el-input v-model="formData.purchase_link" placeholder="请输入采购链接" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位重量" prop="unit_weight">
              <el-input-number 
                v-model="formData.unit_weight" 
                :precision="3" 
                :min="0" 
                placeholder="请输入单位重量"
                style="width: 100%"
              />
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

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="批量导入产品"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-upload
        ref="uploadRef"
        :action="uploadAction"
        :headers="uploadHeaders"
        :data="uploadData"
        :before-upload="beforeUpload"
        :on-success="onUploadSuccess"
        :on-error="onUploadError"
        :on-progress="onUploadProgress"
        :show-file-list="true"
        :multiple="false"
        accept=".xlsx,.xls,.csv"
        drag
        class="upload-area"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 xlsx/xls/csv 文件，且不超过 10MB
          </div>
        </template>
      </el-upload>
      
      <div v-if="uploadProgress > 0" class="upload-progress">
        <el-progress :percentage="uploadProgress" />
      </div>
      
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="downloadTemplate">下载模板</el-button>
      </template>
    </el-dialog>

    <!-- 批量注册对话框 -->
    <el-dialog
      v-model="showBulkRegistrationView"
      title="批量产品注册"
      width="80%"
      :close-on-click-modal="false"
    >
      <div class="bulk-registration-content">
        <el-alert
          title="批量注册说明"
          type="info"
          :closable="false"
          show-icon
        >
          <p>1. 请先下载模板文件，按照格式填写产品信息</p>
          <p>2. 支持批量导入产品基本信息、价格、库存等</p>
          <p>3. 系统会自动验证数据格式和必填字段</p>
        </el-alert>
        
        <div class="bulk-actions">
          <el-button type="primary" @click="downloadTemplate">
            <el-icon><Download /></el-icon>
            下载模板
          </el-button>
          <el-button @click="showImportDialog = true">
            <el-icon><Upload /></el-icon>
            选择文件
          </el-button>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showBulkRegistrationView = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 产品分析对话框 -->
    <el-dialog
      v-model="showProductAnalysisView"
      title="产品分析"
      width="90%"
      :close-on-click-modal="false"
    >
      <div class="product-analysis-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="analysis-chart">
              <h4>产品分类分布</h4>
              <div class="chart-placeholder">产品分类分布图表</div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="analysis-chart">
              <h4>价格区间分布</h4>
              <div class="chart-placeholder">价格区间分布图表</div>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="24">
            <div class="analysis-chart">
              <h4>库存趋势分析</h4>
              <div class="chart-placeholder">库存趋势分析图表</div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <template #footer>
        <el-button @click="showProductAnalysisView = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Upload, Download, TrendCharts, Edit, Document, 
  Search, Refresh, UploadFilled, View 
} from '@element-plus/icons-vue'
import { etsyAPI, PaginationParams, PaginatedResponse, CacheStatus } from '@/api/etsy'
import DataTable from '@/components/common/DataTable.vue'
import RedisStatusMonitor from '@/components/common/RedisStatusMonitor.vue'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const uploadProgress = ref(0)
const searchKeyword = ref('')
const activeCollapse = ref(['1'])
const showCreateDialog = ref(false)
const showImportDialog = ref(false)
const showBulkRegistrationView = ref(false)
const showProductAnalysisView = ref(false)
const showVirtualTable = ref(false) // 控制虚拟滚动表格的显示

// 分页数据
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 表格数据
const tableData = ref<any[]>([])
const selectedRows = ref<any[]>([])

// 虚拟滚动数据
const virtualTableData = ref<any[]>([])
const virtualRowHeight = ref(60) // 每行的高度
const virtualTableHeight = ref(500) // 虚拟表格的容器高度
const virtualTableWrapper = ref<HTMLElement | null>(null)
const virtualScrollTop = ref(0)
const visibleVirtualItems = ref<any[]>([])
const totalVirtualHeight = ref(0)
const virtualBufferSize = ref(20) // 缓冲区大小，用于优化滚动性能

// 筛选表单
const filterForm = reactive({
  search: '',
  store: '',
  inventory_status: '',
  start_date: '',
  end_date: '',
  cost_range: [0, 1000],
  price_range: [0, 2000],
  inventory_range: [0, 1000],
  profit_margin_range: [0, 100]
})

// 表单数据
const formData = reactive({
  product_name: '',
  developer: '',
  listing_store: '',
  store_sku: '',
  sku_1688: '',
  unit_cost: 0,
  declaration_chinese_name: '',
  declaration_english_name: '',
  production_method: '',
  craft_technology: '',
  purchase_link: '',
  remarks: '',
  estimated_price: 0,
  unit_weight: 0,
  inventory: 0,
  inventory_standard_line: 0,
  inventory_warning_line: 0
})

// 编辑项
const editingItem = ref<any>(null)

// 统计信息
const statistics = ref({
  total_count: 0,
  today_count: 0,
  low_inventory_count: 0,
  avg_profit_margin: 0
})

// 缓存状态
const cacheStatus = ref<CacheStatus>({
  is_cached: false,
  cache_key: '',
  cache_ttl: 0,
  last_sync: '',
  sync_status: 'idle'
})

// 店铺选项
const storeOptions = ref<string[]>([])

// 表单引用
const formRef = ref()
const uploadRef = ref()

// 表单验证规则
const formRules = {
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  listing_store: [{ required: true, message: '请选择上架店铺', trigger: 'change' }],
  store_sku: [{ required: true, message: '请输入店铺SKU', trigger: 'blur' }],
  unit_cost: [{ required: true, message: '请输入单位成本', trigger: 'blur' }],
  estimated_price: [{ required: true, message: '请输入预估售价', trigger: 'blur' }]
}

// 表格列配置
const tableColumns = [
  { prop: 'product_name', label: '产品名称', minWidth: 150, showOverflowTooltip: true },
  { prop: 'developer', label: '开发者', width: 100 },
  { prop: 'listing_store', label: '上架店铺', width: 120 },
  { prop: 'store_sku', label: '店铺SKU', width: 120, fixed: 'left' },
  { prop: 'sku_1688', label: '1688 SKU', width: 120 },
  { prop: 'unit_cost', label: '单位成本', width: 100, sortable: true },
  { prop: 'estimated_price', label: '预估售价', width: 100, sortable: true },
  { prop: 'inventory', label: '库存', width: 80, sortable: true },
  { prop: 'inventory_warning_line', label: '告警线', width: 80 },
  { prop: 'estimated_gross_profit_margin', label: '预估毛利率', width: 100, sortable: true },
  { prop: 'declaration_chinese_name', label: '申报中文名', minWidth: 150, showOverflowTooltip: true },
  { prop: 'declaration_english_name', label: '申报英文名', minWidth: 150, showOverflowTooltip: true },
  { prop: 'production_method', label: '生产方式', width: 100 },
  { prop: 'craft_technology', label: '工艺', width: 100 },
  { prop: 'unit_weight', label: '单位重量', width: 100 },
  { prop: 'created_at', label: '创建时间', width: 150, sortable: true },
  { prop: 'updated_at', label: '更新时间', width: 150, sortable: true }
]

// 上传配置
const uploadAction = '/api/etsy/product-registration/import_data/'
const uploadHeaders = { 'X-Requested-With': 'XMLHttpRequest' }
const uploadData = { type: 'bulk_import' }

// 计算属性
const hasSelectedRows = computed(() => selectedRows.value.length > 0)

// 方法
const fetchData = async (params?: PaginationParams) => {
  try {
    loading.value = true
    
    const requestParams: PaginationParams = {
      page: pagination.currentPage,
      page_size: pagination.pageSize,
      search: searchKeyword.value,
      filters: filterForm,
      ...params
    }
    
    const response = await etsyAPI.productRegistration.getList(requestParams)
    const data = response.data as PaginatedResponse<any>
    
    tableData.value = data.results
    pagination.total = data.count
    pagination.currentPage = data.page_info.current_page
    pagination.pageSize = data.page_info.page_size
    
    // 同时更新虚拟表格数据
    if (showVirtualTable.value) {
      // 如果是虚拟表格模式，获取所有数据
      await fetchAllDataForVirtualTable()
    }
    
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 为虚拟表格获取所有数据
const fetchAllDataForVirtualTable = async () => {
  try {
    const requestParams: PaginationParams = {
      page: 1,
      page_size: 10000, // 获取大量数据
      search: searchKeyword.value,
      filters: filterForm
    }
    
    const response = await etsyAPI.productRegistration.getList(requestParams)
    const data = response.data as PaginatedResponse<any>
    virtualTableData.value = data.results
    
    // 更新虚拟表格
    nextTick(() => {
      updateVirtualTable()
    })
  } catch (error) {
    console.error('获取虚拟表格数据失败:', error)
    ElMessage.error('获取虚拟表格数据失败')
  }
}

const fetchStatistics = async () => {
  try {
    const response = await etsyAPI.productRegistration.getStatistics()
    statistics.value = response.data
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

const fetchCacheStatus = async () => {
  try {
    const response = await etsyAPI.productRegistration.getCacheStatus()
    cacheStatus.value = response.data
  } catch (error) {
    console.error('获取缓存状态失败:', error)
  }
}

const fetchStoreOptions = async () => {
  try {
    const response = await etsyAPI.storeInformation.getList()
    const stores = response.data.results || []
    storeOptions.value = [...new Set(stores.map(store => store.store))]
  } catch (error) {
    console.error('获取店铺选项失败:', error)
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  fetchData()
}

const handleTableSearch = (keyword: string) => {
  searchKeyword.value = keyword
  handleSearch()
}

const handlePageChange = (page: number) => {
  pagination.currentPage = page
  fetchData()
}

const handlePageSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  fetchData()
}

const handleSelectionChange = (rows: any[]) => {
  selectedRows.value = rows
}

const handleEdit = (row: any) => {
  editingItem.value = row
  Object.assign(formData, row)
  showCreateDialog.value = true
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除产品 "${row.product_name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await etsyAPI.productRegistration.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDelete = async (rows: any[]) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${rows.length} 个产品吗？`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const ids = rows.map(row => row.id)
    await etsyAPI.productRegistration.bulkDelete({ ids })
    ElMessage.success('批量删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

const handleBatchUpdate = async (rows: any[]) => {
  try {
    await ElMessageBox.prompt(
      '请输入要更新的字段和值（JSON格式）',
      '批量更新',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '{"field": "value"}'
      }
    )
    
    const updates = JSON.parse(ElMessageBox.prompt)
    const data = rows.map(row => ({ id: row.id, ...updates }))
    
    await etsyAPI.productRegistration.bulkUpdate({ data })
    ElMessage.success('批量更新成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量更新失败:', error)
      ElMessage.error('批量更新失败')
    }
  }
}

const handleBatchExport = async (rows: any[]) => {
  try {
    const ids = rows.map(row => row.id)
    const response = await etsyAPI.productRegistration.exportExcel({ ids })
    
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `Etsy产品登记表_选中项目_${new Date().toISOString().slice(0, 10)}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (editingItem.value) {
      await etsyAPI.productRegistration.update(editingItem.value.id, formData)
      ElMessage.success('更新成功')
    } else {
      await etsyAPI.productRegistration.create(formData)
      ElMessage.success('创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
    fetchData()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  editingItem.value = null
  Object.keys(formData).forEach(key => {
    if (typeof formData[key] === 'number') {
      formData[key] = 0
    } else {
      formData[key] = ''
    }
  })
  formRef.value?.resetFields()
}

const resetFilters = () => {
  Object.keys(filterForm).forEach(key => {
    if (Array.isArray(filterForm[key])) {
      filterForm[key] = [0, 1000]
    } else {
      filterForm[key] = ''
    }
  })
  handleSearch()
}

const applyFilters = () => {
  handleSearch()
}

const handleCostRangeChange = () => {
  // 成本范围变化处理
}

const handlePriceRangeChange = () => {
  // 价格范围变化处理
}

const handleInventoryRangeChange = () => {
  // 库存范围变化处理
}

const handleProfitMarginRangeChange = () => {
  // 毛利率范围变化处理
}

const downloadTemplate = async () => {
  try {
    const response = await etsyAPI.productRegistration.downloadTemplate()
    
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'Etsy产品登记表模板.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error('模板下载失败:', error)
    ElMessage.error('模板下载失败')
  }
}

const exportData = async () => {
  try {
    const params = {
      search: searchKeyword.value,
      filters: filterForm
    }
    
    const response = await etsyAPI.productRegistration.exportExcel(params)
    
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `Etsy产品登记表_${new Date().toISOString().slice(0, 10)}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const handleSyncData = async () => {
  try {
    await etsyAPI.productRegistration.syncData()
    ElMessage.success('数据同步已启动')
    
    // 等待同步完成后刷新数据
    setTimeout(() => {
      fetchData()
      fetchCacheStatus()
    }, 3000)
  } catch (error) {
    console.error('数据同步失败:', error)
    ElMessage.error('数据同步失败')
  }
}

const handleClearCache = async () => {
  try {
    await etsyAPI.productRegistration.clearCache()
    ElMessage.success('缓存已清除')
    
    // 刷新缓存状态
    fetchCacheStatus()
  } catch (error) {
    console.error('清除缓存失败:', error)
    ElMessage.error('清除缓存失败')
  }
}

const handleStatsUpdated = (stats: any) => {
  // 处理统计信息更新
  console.log('统计信息已更新:', stats)
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

// 获取库存状态类型
const getInventoryStatusType = (inventory: number, warningLine: number) => {
  if (inventory <= 0) return 'danger'
  if (inventory <= warningLine) return 'warning'
  return 'success'
}

// 获取库存状态文本
const getInventoryStatusText = (inventory: number, warningLine: number) => {
  if (inventory <= 0) return '无库存'
  if (inventory <= warningLine) return '库存不足'
  return '库存充足'
}

// 上传相关方法
const beforeUpload = (file: File) => {
  const isValidType = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                       'application/vnd.ms-excel', 'text/csv'].includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10
  
  if (!isValidType) {
    ElMessage.error('只能上传 Excel 或 CSV 文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

const onUploadSuccess = (response: any, file: File) => {
  ElMessage.success('文件上传成功')
  showImportDialog.value = false
  fetchData()
  uploadProgress.value = 0
}

const onUploadError = (error: any, file: File) => {
  ElMessage.error('文件上传失败')
  uploadProgress.value = 0
}

const onUploadProgress = (event: any, file: File) => {
  uploadProgress.value = Math.round((event.loaded * 100) / event.total)
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    fetchData(),
    fetchStatistics(),
    fetchCacheStatus(),
    fetchStoreOptions()
  ])
  updateVirtualTable() // 初始化虚拟表格
})
</script>

<style scoped>
.etsy-product-registration {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.statistics-cards {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-content {
  text-align: center;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.advanced-filter-section {
  margin-bottom: 20px;
}

.filter-form {
  margin-bottom: 20px;
}

.slider-filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.slider-group {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 6px;
}

.slider-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.filter-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.product-form {
  max-height: 60vh;
  overflow-y: auto;
}

.upload-area {
  text-align: center;
}

.upload-progress {
  margin-top: 16px;
}

.bulk-registration-content {
  padding: 20px 0;
}

.bulk-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}

.product-analysis-content {
  padding: 20px 0;
}

.analysis-chart {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.analysis-chart h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
}

.chart-placeholder {
  height: 200px;
  background: #e9ecef;
  border: 2px dashed #dee2e6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  font-size: 14px;
}

.search-input {
  width: 250px;
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
  -webkit-overflow-scrolling: touch; /* 优化移动端滚动 */
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
  background-color: #f0f9eb; /* 悬停效果 */
}

.virtual-table-row:nth-child(even) {
  background-color: #fafafa; /* 偶数行背景 */
}

.virtual-table-row:nth-child(even):hover {
  background-color: #f0f9eb; /* 偶数行悬停效果 */
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

.product-thumbnail {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  object-fit: cover;
}

.no-image {
  color: #909399;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .etsy-product-registration {
    padding: 10px;
  }
  
  .slider-filters {
    grid-template-columns: 1fr;
  }
  
  .filter-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .bulk-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
