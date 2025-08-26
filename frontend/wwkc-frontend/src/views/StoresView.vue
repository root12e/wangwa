<template>
  <div class="stores-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>店铺管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateStoreDialog" v-if="canCreateStore">
          <el-icon>
            <Plus />
          </el-icon>
          新增店铺
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ storeStats?.totalStores || 0 }}</div>
          <div class="stat-label">总店铺数</div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ storeStats?.activeStores || 0 }}</div>
          <div class="stat-label">营业中</div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ storeStats?.totalProducts || 0 }}</div>
          <div class="stat-label">总产品数</div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ storeStats?.totalValue || 0 }}</div>
          <div class="stat-label">总库存价值</div>
        </div>
      </el-card>
    </div>

    <!-- 店铺列表 -->
    <el-card class="stores-list">
      <template #header>
        <div class="card-header">
          <span>店铺列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索店铺名称或编码"
              style="width: 300px; margin-right: 16px;"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="handleSearch">
              <el-option label="全部状态" value="" />
              <el-option label="营业中" value="active" />
              <el-option label="暂停营业" value="inactive" />
              <el-option label="已关闭" value="closed" />
              <el-option label="维护中" value="maintenance" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="filteredStores" v-loading="loading" stripe>
        <el-table-column prop="name" label="店铺名称" min-width="150" />
        <el-table-column prop="code" label="店铺编码" width="120" />
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="phone" label="电话" width="120" />
        <el-table-column prop="manager" label="经理" width="100">
          <template #default="{ row }">
            {{ row.manager?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="department" label="所属部门" width="120">
          <template #default="{ row }">
            {{ row.department?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewStore(row)">查看</el-button>
            <el-button size="small" type="primary" @click="manageProducts(row)">
              产品管理
            </el-button>
            <el-button 
              size="small" 
              type="warning" 
              @click="editStore(row)"
              v-if="canEditStore(row)"
            >
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="handleDeleteStore(row)"
              v-if="canDeleteStore(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalStores"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑店铺对话框 -->
    <el-dialog
      v-model="storeDialogVisible"
      :title="isEdit ? '编辑店铺' : '新增店铺'"
      width="600px"
    >
      <el-form
        ref="storeFormRef"
        :model="storeForm"
        :rules="storeRules"
        label-width="100px"
      >
        <el-form-item label="店铺名称" prop="name">
          <el-input v-model="storeForm.name" placeholder="请输入店铺名称" />
        </el-form-item>
        <el-form-item label="店铺编码" prop="code">
          <el-input v-model="storeForm.code" placeholder="请输入店铺编码" />
        </el-form-item>
        <el-form-item label="店铺地址" prop="address">
          <el-input v-model="storeForm.address" type="textarea" placeholder="请输入店铺地址" />
        </el-form-item>
        <el-form-item label="店铺电话" prop="phone">
          <el-input v-model="storeForm.phone" placeholder="请输入店铺电话" />
        </el-form-item>
        <el-form-item label="店铺邮箱" prop="email">
          <el-input v-model="storeForm.email" placeholder="请输入店铺邮箱" />
        </el-form-item>
        <el-form-item label="所属部门" prop="department">
          <el-select v-model="storeForm.department" placeholder="请选择部门" style="width: 100%">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="店铺状态" prop="status">
          <el-select v-model="storeForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="营业中" value="active" />
            <el-option label="暂停营业" value="inactive" />
            <el-option label="已关闭" value="closed" />
            <el-option label="维护中" value="maintenance" />
          </el-select>
        </el-form-item>
        <el-form-item label="营业时间" prop="business_hours">
          <el-input v-model="storeForm.business_hours" placeholder="请输入营业时间" />
        </el-form-item>
        <el-form-item label="店铺描述" prop="description">
          <el-input v-model="storeForm.description" type="textarea" placeholder="请输入店铺描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="storeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitStore" :loading="submitting">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 产品管理对话框 -->
    <el-dialog
      v-model="productDialogVisible"
      title="产品管理"
      width="90%"
      top="5vh"
    >
      <StoreProducts :store="selectedStore" @close="productDialogVisible = false" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useDepartmentStore } from '@/stores/department'
import StoreProducts from '@/components/StoreProducts.vue'
import { getStores, createStore, updateStore, deleteStore } from '@/api/store'

// 状态管理
const authStore = useAuthStore()
const departmentStore = useDepartmentStore()

// 响应式数据
const loading = ref(false)
const stores = ref([])
const departments = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const totalStores = ref(0)
const searchKeyword = ref('')
const statusFilter = ref('')

// 对话框状态
const storeDialogVisible = ref(false)
const productDialogVisible = ref(false)
const isEdit = ref(false)
const selectedStore = ref(null)
const submitting = ref(false)

// 表单数据
const storeFormRef = ref()
const storeForm = reactive({
  name: '',
  code: '',
  address: '',
  phone: '',
  email: '',
  department: '',
  status: 'active',
  business_hours: '',
  description: ''
})

// 表单验证规则
const storeRules = {
  name: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入店铺编码', trigger: 'blur' }],
  address: [{ required: true, message: '请输入店铺地址', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入店铺电话', trigger: 'blur' }],
  department: [{ required: true, message: '请选择所属部门', trigger: 'change' }],
  status: [{ required: true, message: '请选择店铺状态', trigger: 'change' }]
}

// 统计信息
const storeStats = reactive({
  totalStores: 0,
  activeStores: 0,
  totalProducts: 0,
  totalValue: 0
})

// 确保 storeStats 始终可用的计算属性
const safeStoreStats = computed(() => ({
  totalStores: storeStats?.totalStores || 0,
  activeStores: storeStats?.activeStores || 0,
  totalProducts: storeStats?.totalProducts || 0,
  totalValue: storeStats?.totalValue || 0
}))

// 计算属性
const filteredStores = computed(() => {
  // 确保stores.value是数组
  if (!Array.isArray(stores.value)) {
    return []
  }
  
  let result = stores.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(store => 
      store.name?.toLowerCase().includes(keyword) ||
      store.code?.toLowerCase().includes(keyword)
    )
  }

  if (statusFilter.value) {
    result = result.filter(store => store.status === statusFilter.value)
  }

  return result
})

// 权限检查
const canCreateStore = computed(() => {
  return authStore.user?.role === 'super_admin' || authStore.user?.role === 'department_manager'
})

const canEditStore = (store) => {
  if (!store || !authStore.user) return false
  
  if (authStore.user.role === 'super_admin') return true
  if (authStore.user.role === 'department_manager' && store.department?.id === authStore.user.department?.id) return true
  return false
}

const canDeleteStore = (store) => {
  if (!store || !authStore.user) return false
  
  if (authStore.user.role === 'super_admin') return true
  if (authStore.user.role === 'department_manager' && store.department?.id === authStore.user.department?.id) return true
  return false
}

// 方法
const loadStores = async () => {
  try {
    loading.value = true
    const response = await getStores({
      page: currentPage.value,
      page_size: pageSize.value
    })
    
    // 确保正确提取数据
    if (response && response.data) {
      stores.value = response.data.results || response.data
      totalStores.value = response.data.count || (Array.isArray(response.data) ? response.data.length : 0)
    } else {
      stores.value = []
      totalStores.value = 0
    }
    
    // 更新统计信息
    updateStats()
  } catch (error) {
    ElMessage.error('加载店铺列表失败')
    console.error('加载店铺列表失败:', error)
    stores.value = []
    totalStores.value = 0
  } finally {
    loading.value = false
  }
}

const loadDepartments = async () => {
  try {
    await departmentStore.fetchDepartments()
    // 确保departments是数组
    if (Array.isArray(departmentStore.departments)) {
      departments.value = departmentStore.departments
    } else {
      departments.value = []
    }
  } catch (error) {
    console.error('加载部门列表失败:', error)
    departments.value = []
  }
}

const updateStats = () => {
  // 确保stores.value是数组
  if (Array.isArray(stores.value)) {
    storeStats.totalStores = stores.value.length
    storeStats.activeStores = stores.value.filter(store => store.status === 'active').length
  } else {
    storeStats.totalStores = 0
    storeStats.activeStores = 0
  }
  // 这里可以添加产品数量和库存价值的统计
}

const handleSearch = () => {
  currentPage.value = 1
  loadStores()
}

const handleSizeChange = (val) => {
  if (typeof val === 'number' && val > 0) {
    pageSize.value = val
    currentPage.value = 1
    loadStores()
  }
}

const handleCurrentChange = (val) => {
  if (typeof val === 'number' && val > 0) {
    currentPage.value = val
    loadStores()
  }
}

const showCreateStoreDialog = () => {
  isEdit.value = false
  resetStoreForm()
  storeDialogVisible.value = true
}

const editStore = (store) => {
  isEdit.value = true
  selectedStore.value = store
  
  // 重置表单并填充数据
  resetStoreForm()
  Object.assign(storeForm, {
    name: store.name,
    code: store.code,
    address: store.address,
    phone: store.phone,
    email: store.email,
    department: store.department?.id || '',
    status: store.status,
    business_hours: store.business_hours,
    description: store.description
  })
  
  storeDialogVisible.value = true
}

const resetStoreForm = () => {
  // 重置表单数据
  Object.assign(storeForm, {
    name: '',
    code: '',
    address: '',
    phone: '',
    email: '',
    department: '',
    status: 'active',
    business_hours: '',
    description: ''
  })
  
  // 重置表单验证状态
  if (storeFormRef.value) {
    storeFormRef.value.resetFields()
  }
}

const submitStore = async () => {
  try {
    await storeFormRef.value.validate()
    submitting.value = true

    // 准备提交数据
    const submitData = {
      name: storeForm.name,
      code: storeForm.code,
      address: storeForm.address,
      phone: storeForm.phone,
      email: storeForm.email,
      department_id: storeForm.department,
      status: storeForm.status,
      business_hours: storeForm.business_hours,
      description: storeForm.description
    }

    if (isEdit.value) {
      await updateStore(selectedStore.value.id, submitData)
      ElMessage.success('店铺更新成功')
    } else {
      await createStore(submitData)
      ElMessage.success('店铺创建成功')
    }

    storeDialogVisible.value = false
    loadStores()
  } catch (error) {
    ElMessage.error(isEdit.value ? '店铺更新失败' : '店铺创建失败')
    console.error('提交店铺信息失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleDeleteStore = async (store) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除店铺 "${store.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteStore(store.id)
    ElMessage.success('店铺删除成功')
    loadStores()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('店铺删除失败')
      console.error('删除店铺失败:', error)
    }
  }
}

const viewStore = (store) => {
  if (store && store.id) {
    selectedStore.value = store
    // 这里可以显示店铺详情
  }
}

const manageProducts = (store) => {
  if (store && store.id) {
    selectedStore.value = store
    productDialogVisible.value = true
  }
}

const getStatusType = (status) => {
  if (!status) return 'info'
  
  const statusMap = {
    active: 'success',
    inactive: 'warning',
    closed: 'danger',
    maintenance: 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  if (!status) return '未知'
  
  const statusMap = {
    active: '营业中',
    inactive: '暂停营业',
    closed: '已关闭',
    maintenance: '维护中'
  }
  return statusMap[status] || '未知'
}

const formatDate = (date) => {
  if (!date) return '-'
  try {
    return new Date(date).toLocaleString('zh-CN')
  } catch (error) {
    return '-'
  }
}

// 生命周期
onMounted(async () => {
  try {
    await Promise.all([
      loadStores(),
      loadDepartments()
    ])
  } catch (error) {
    console.error('初始化数据失败:', error)
  }
})
</script>

<style scoped>
.stores-container {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 16px;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stores-list {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-table) {
  margin-top: 16px;
}

:deep(.el-card__header) {
  padding: 16px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>
