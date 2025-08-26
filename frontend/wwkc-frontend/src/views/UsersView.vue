<template>
  <div class="users-view">
    <!-- 页面标题 -->
    <div class="page-header fade-in-up">
      <h1>用户管理</h1>
      <p class="page-description">管理系统用户、角色和权限</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card card fade-in-up" style="animation-delay: 0.1s">
        <div class="stat-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.total_users || 0 }}</div>
          <div class="stat-label">总用户数</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.2s">
        <div class="stat-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.role_stats?.super_admin || 0 }}</div>
          <div class="stat-label">超级管理员</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.3s">
        <div class="stat-icon">
          <el-icon><OfficeBuilding /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.role_stats?.department_manager || 0 }}</div>
          <div class="stat-label">部门部长</div>
        </div>
      </div>

      <div class="stat-card card fade-in-up" style="animation-delay: 0.4s">
        <div class="stat-icon">
          <el-icon><Shop /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.role_stats?.store_operator || 0 }}</div>
          <div class="stat-label">店铺运营</div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar card fade-in-up" style="animation-delay: 0.5s">
      <div class="action-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户..."
          class="search-input"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="roleFilter" placeholder="选择角色" clearable @change="handleFilter">
          <el-option label="超级管理员" value="super_admin" />
          <el-option label="部门部长" value="department_manager" />
          <el-option label="店铺运营" value="store_operator" />
          <el-option label="普通员工" value="staff" />
        </el-select>
        
        <el-select v-model="departmentFilter" placeholder="选择部门" clearable @change="handleFilter">
          <el-option 
            v-for="dept in departments" 
            :key="dept.id" 
            :label="dept.name" 
            :value="dept.id" 
          />
        </el-select>

        <el-select v-model="statusFilter" placeholder="选择状态" clearable @change="handleFilter">
          <el-option label="激活" value="active" />
          <el-option label="已通过" value="approved" />
          <el-option label="待审批" value="pending" />
          <el-option label="禁用" value="inactive" />
          <el-option label="拒绝" value="rejected" />
        </el-select>
      </div>
      
      <div class="action-right">
        <el-button type="primary" class="btn-primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          添加用户
        </el-button>
        <el-button class="btn-secondary" @click="showBulkActionDialog">
          <el-icon><Setting /></el-icon>
          批量操作
        </el-button>
        <el-button class="btn-secondary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="users-table card fade-in-up" style="animation-delay: 0.6s">
      <div v-if="!Array.isArray(tableData)" class="error-message">
        <el-alert
          title="数据加载错误"
          description="用户数据格式异常，请刷新页面重试"
          type="error"
          show-icon
          :closable="false"
        />
      </div>
      <el-table 
        v-else
        :key="`users-table-${tableData.length}`"
        :data="tableData" 
        style="width: 100%" 
        stripe
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="scope">
            <el-tag :type="getRoleTagType(scope.row?.role || '')">
              {{ getRoleDisplayName(scope.row?.role || '') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="120">
          <template #default="scope">
            {{ scope.row.department?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="store" label="所属店铺" width="120">
          <template #default="scope">
            {{ scope.row.store?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusDisplayName(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row?.created_at || '') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" text @click="editUser(scope.row)" :disabled="!scope.row?.id">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="success" text @click="viewUser(scope.row)" :disabled="!scope.row?.id">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button 
              size="small" 
              :type="(scope.row?.status === 'active' || scope.row?.status === 'approved') ? 'warning' : 'success'"
              text
              @click="toggleUserStatus(scope.row)"
              :disabled="!scope.row?.id"
            >
              <el-icon><Lock v-if="scope.row?.status === 'active' || scope.row?.status === 'approved'" /><Unlock v-else /></el-icon>
              {{ (scope.row?.status === 'active' || scope.row?.status === 'approved') ? '禁用' : '激活' }}
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              text
              @click="deleteUserHandler(scope.row)"
              :disabled="!scope.row?.id || scope.row?.id === currentUser?.id"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 用户创建/编辑对话框 -->
    <el-dialog
      v-model="userDialogVisible"
      :title="isEdit ? '编辑用户' : '创建用户'"
      width="600px"
      @close="resetUserForm"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="超级管理员" value="super_admin" />
            <el-option label="部门部长" value="department_manager" />
            <el-option label="店铺运营" value="store_operator" />
            <el-option label="普通员工" value="staff" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="部门" prop="department">
          <el-select v-model="userForm.department" placeholder="请选择部门" clearable style="width: 100%">
            <el-option 
              v-for="dept in departments" 
              :key="dept.id" 
              :label="dept.name" 
              :value="dept.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="店铺" prop="store">
          <el-select v-model="userForm.store" placeholder="请选择店铺" clearable style="width: 100%">
            <el-option 
              v-for="store in stores" 
              :key="store.id" 
              :label="store.name" 
              :value="store.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="userDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUserForm" :loading="submitting">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 批量操作对话框 -->
    <el-dialog
      v-model="bulkActionDialogVisible"
      title="批量操作"
      width="500px"
    >
      <el-form :model="bulkActionForm" label-width="100px">
        <el-form-item label="操作类型">
          <el-select v-model="bulkActionForm.action" placeholder="请选择操作类型" style="width: 100%">
            <el-option label="激活用户" value="activate" />
            <el-option label="禁用用户" value="deactivate" />
            <el-option label="审批通过" value="approve" />
            <el-option label="审批拒绝" value="reject" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="bulkActionForm.action === 'reject'" label="拒绝原因">
          <el-input 
            v-model="bulkActionForm.reason" 
            type="textarea" 
            placeholder="请输入拒绝原因"
            :rows="3"
          />
        </el-form-item>
        
        <el-form-item label="选中用户">
          <div class="selected-users">
            已选择 {{ selectedUsers.length }} 个用户
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="bulkActionDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitBulkAction" 
            :loading="submitting"
            :disabled="selectedUsers.length === 0"
          >
            确认操作
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 用户详情对话框 -->
    <el-dialog
      v-model="userDetailDialogVisible"
      title="用户详情"
      width="600px"
    >
      <div v-if="selectedUserDetail" class="user-detail">
        <div class="detail-item">
          <label>用户名：</label>
          <span>{{ selectedUserDetail.username }}</span>
        </div>
        <div class="detail-item">
          <label>邮箱：</label>
          <span>{{ selectedUserDetail.email }}</span>
        </div>
        <div class="detail-item">
          <label>手机号：</label>
          <span>{{ selectedUserDetail.phone || '-' }}</span>
        </div>
        <div class="detail-item">
          <label>角色：</label>
          <el-tag :type="getRoleTagType(selectedUserDetail.role)">
            {{ getRoleDisplayName(selectedUserDetail.role) }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>部门：</label>
          <span>{{ selectedUserDetail.department?.name || '-' }}</span>
        </div>
        <div class="detail-item">
          <label>店铺：</label>
          <span>{{ selectedUserDetail.store?.name || '-' }}</span>
        </div>
        <div class="detail-item">
          <label>状态：</label>
          <el-tag :type="getStatusTagType(selectedUserDetail.status)">
            {{ getStatusDisplayName(selectedUserDetail.status) }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>创建时间：</label>
          <span>{{ formatDate(selectedUserDetail.created_at) }}</span>
        </div>
        <div v-if="selectedUserDetail.approval_date" class="detail-item">
          <label>审批时间：</label>
          <span>{{ formatDate(selectedUserDetail.approval_date) }}</span>
        </div>
        <div v-if="selectedUserDetail.approved_by" class="detail-item">
          <label>审批人：</label>
          <span>{{ selectedUserDetail.approved_by }}</span>
        </div>
        <div v-if="selectedUserDetail.rejection_reason" class="detail-item">
          <label>拒绝原因：</label>
          <span class="rejection-reason">{{ selectedUserDetail.rejection_reason }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  Star,
  OfficeBuilding,
  Shop,
  Search,
  Plus,
  Setting,
  Refresh,
  Edit,
  View,
  Lock,
  Unlock,
  Delete
} from '@element-plus/icons-vue'
import { 
  getUserList, 
  createUser, 
  updateUser, 
  deleteUser, 
  bulkActionUsers,
  getUserStatistics,
  getDepartmentsForUser,
  getStoresForUser,
  updateUserStatus,
  getUserDetail
} from '@/api/user'
import { useAuthStore } from '@/stores/auth'

// 响应式数据
const searchQuery = ref('')
const roleFilter = ref('')
const departmentFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const submitting = ref(false)
const isInitialized = ref(false) // 添加初始化状态标记

// 用户数据
const usersData = ref<any[]>([])
const statistics = ref<any>({
  total_users: 0,
  role_stats: {
    super_admin: 0,
    department_manager: 0,
    store_operator: 0
  }
})
const departments = ref<any[]>([])
const stores = ref<any[]>([])
const selectedUsers = ref<any[]>([])

// 确保表格数据始终是数组
const tableData = computed(() => {
  if (Array.isArray(usersData.value)) {
    return usersData.value
  }
  console.warn('usersData 不是数组，返回空数组')
  return []
})

// 对话框控制
const userDialogVisible = ref(false)
const bulkActionDialogVisible = ref(false)
const userDetailDialogVisible = ref(false)
const isEdit = ref(false)

// 表单数据
const userForm = ref({
  username: '',
  email: '',
  phone: '',
  role: '',
  department: null as number | null,
  store: null as number | null,
  password: ''
})

const bulkActionForm = ref({
  action: '' as 'activate' | 'deactivate' | 'approve' | 'reject',
  reason: ''
})

// 选中的用户详情
const selectedUserDetail = ref<any>(null)

// 表单引用
const userFormRef = ref()

// 权限存储
const authStore = useAuthStore()
const currentUser = computed(() => authStore.user)

// 防抖搜索
let searchTimeout: number | null = null

// 表单验证规则
const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

// 生命周期
onMounted(() => {
  // 只在组件挂载时初始化一次
  if (!isInitialized.value) {
    initializeData()
    isInitialized.value = true
  }
})

onUnmounted(() => {
  // 清理定时器
  if (searchTimeout) {
    clearTimeout(searchTimeout)
    searchTimeout = null
  }
})

// 初始化数据
const initializeData = async () => {
  try {
    console.log('开始初始化用户管理数据...')
    // 先加载基础数据，但单独处理每个错误
    const basePromises = [
      loadDepartments().catch(error => {
        console.error('加载部门数据失败:', error)
        return null
      }),
      loadStores().catch(error => {
        console.error('加载店铺数据失败:', error)
        return null
      })
    ]
    
    await Promise.all(basePromises)
    
    // 然后加载用户数据和统计信息，但单独处理每个错误
    const dataPromises = [
      loadData().catch(error => {
        console.error('加载用户数据失败:', error)
        return null
      }),
      loadStatistics().catch(error => {
        console.error('加载统计信息失败:', error)
        return null
      })
    ]
    
    await Promise.all(dataPromises)
    
    console.log('用户管理数据初始化完成')
  } catch (error) {
    console.error('初始化数据失败:', error)
    ElMessage.error('初始化数据失败，请刷新页面重试')
  }
}

// 加载数据
const loadData = async () => {
  // 防止重复调用
  if (loading.value) {
    console.log('数据正在加载中，跳过重复调用')
    return
  }
  
  console.log('开始加载用户数据...')
  loading.value = true
  
  try {
    const params = {
      search: searchQuery.value,
      role: roleFilter.value,
      department: departmentFilter.value,
      status: statusFilter.value,
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    console.log('加载用户数据，参数:', params)
    const response = await getUserList(params)
    console.log('用户数据响应:', response)
    
    // 统一处理响应数据
    if (response && response.data) {
      if (response.data.results && Array.isArray(response.data.results)) {
        // Django REST framework 标准格式：{results: [...], count: number}
        usersData.value = response.data.results
        total.value = response.data.count || 0
        console.log('使用Django格式处理数据，用户数:', usersData.value.length, '总数:', total.value)
      } else if (response.data.success && response.data.results && Array.isArray(response.data.results)) {
        // 标准格式：{success: true, results: [...], count: number}
        usersData.value = response.data.results
        total.value = response.data.count || 0
        console.log('使用标准格式处理数据，用户数:', usersData.value.length, '总数:', total.value)
      } else if (Array.isArray(response.data)) {
        // 直接返回数组格式
        usersData.value = response.data
        total.value = response.data.length
        console.log('使用数组格式处理数据，用户数:', response.data.length)
      } else if (response.data && typeof response.data === 'object') {
        // 尝试从对象中提取数据
        if (response.data.users && Array.isArray(response.data.users)) {
          usersData.value = response.data.users
          total.value = response.data.users.length
        } else if (response.data.data && Array.isArray(response.data.data)) {
          usersData.value = response.data.data
          total.value = response.data.data.length
        } else {
          // 如果都没有，设置为空数组
          usersData.value = []
          total.value = 0
          console.log('无法从对象中提取数组数据，设置空数据')
        }
        console.log('从对象中提取数据，用户数:', usersData.value.length)
      } else {
        // 兜底处理
        usersData.value = []
        total.value = 0
        console.log('使用兜底处理，设置空数据')
      }
    } else {
      // 响应为空的情况
      usersData.value = []
      total.value = 0
      console.log('响应为空，设置空数据')
    }
    
    // 确保 usersData 始终是数组
    if (!Array.isArray(usersData.value)) {
      console.warn('usersData 不是数组，强制转换为空数组')
      usersData.value = []
      total.value = 0
    }
    
    console.log('处理后的用户数据:', usersData.value)
    console.log('总数:', total.value)
    
    if (usersData.value.length === 0) {
      ElMessage.info('暂无用户数据')
    }
    
  } catch (error: any) {
    console.error('加载用户数据失败:', error)
    
    // 根据错误类型显示不同的错误信息
    if (error.response) {
      if (error.response.status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        // 跳转到登录页
        window.location.href = '/login'
        return
      } else if (error.response.status === 403) {
        ElMessage.error('没有权限访问用户管理功能')
      } else if (error.response.status === 404) {
        ElMessage.error('用户管理接口不存在')
      } else if (error.response.status >= 500) {
        ElMessage.error('服务器内部错误，请稍后重试')
      } else {
        ElMessage.error(`请求失败: ${error.response.status}`)
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络设置')
    } else {
      ElMessage.error('加载用户数据失败，请稍后重试')
    }
    
    // 设置默认值
    usersData.value = []
    total.value = 0
  } finally {
    loading.value = false
    console.log('加载状态设置为false')
    
    // 最终安全检查，确保数据是数组
    if (!Array.isArray(usersData.value)) {
      console.warn('最终检查：usersData 不是数组，强制转换为空数组')
      usersData.value = []
    }
  }
}

// 加载统计信息
const loadStatistics = async () => {
  try {
    console.log('开始加载用户统计信息...')
    const response = await getUserStatistics()
    console.log('统计信息响应:', response)
    
    if (response && response.data) {
      if (response.data.success && response.data.statistics) {
        statistics.value = response.data.statistics
        console.log('统计信息加载成功:', statistics.value)
      } else if (response.data.statistics) {
        statistics.value = response.data.statistics
        console.log('统计信息加载成功(直接格式):', statistics.value)
      } else {
        console.log('统计信息格式异常，使用默认值')
        statistics.value = {
          total_users: 0,
          role_stats: {}
        }
      }
    } else {
      console.log('统计信息响应为空，使用默认值')
      statistics.value = {
        total_users: 0,
        role_stats: {}
      }
    }
  } catch (error: any) {
    console.error('加载统计信息失败:', error)
    
    // 如果是404错误，说明统计接口不存在，使用默认值
    if (error.response && error.response.status === 404) {
      console.log('统计接口不存在，使用默认值')
      statistics.value = {
        total_users: total.value || 0,
        role_stats: {}
      }
    } else {
      // 其他错误，使用默认值
      statistics.value = {
        total_users: 0,
        role_stats: {}
      }
    }
  }
}

// 加载部门列表
const loadDepartments = async () => {
  try {
    console.log('开始加载部门列表...')
    const response = await getDepartmentsForUser()
    console.log('部门列表响应:', response)
    
    if (response && response.data) {
      if (Array.isArray(response.data)) {
        departments.value = response.data
      } else if (response.data.results) {
        departments.value = response.data.results
      } else if (response.data.departments) {
        departments.value = response.data.departments
      } else {
        departments.value = []
      }
    } else {
      departments.value = []
    }
    
    console.log('部门列表加载完成，数量:', departments.value.length)
  } catch (error) {
    console.error('加载部门列表失败:', error)
    departments.value = []
  }
}

// 加载店铺列表
const loadStores = async () => {
  try {
    console.log('开始加载店铺列表...')
    const response = await getStoresForUser()
    console.log('店铺列表响应:', response)
    
    if (response && response.data) {
      if (Array.isArray(response.data)) {
        stores.value = response.data
      } else if (response.data.results) {
        stores.value = response.data.results
      } else if (response.data.stores) {
        stores.value = response.data.stores
      } else {
        stores.value = []
      }
    } else {
      stores.value = []
    }
    
    console.log('店铺列表加载完成，数量:', stores.value.length)
  } catch (error) {
    console.error('加载店铺列表失败:', error)
    stores.value = []
  }
}

// 刷新数据
const refreshData = () => {
  if (loading.value) {
    console.log('数据正在加载中，跳过刷新')
    return
  }
  
  console.log('开始刷新数据...')
  // 重置分页
  currentPage.value = 1
  
  // 并行加载数据，但避免重复调用
  Promise.all([
    loadData(),
    loadStatistics()
  ]).catch(error => {
    console.error('刷新数据失败:', error)
  })
}

// 搜索处理
const handleSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadData()
  }, 500) // 500ms 防抖
}

// 过滤处理
const handleFilter = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadData()
  }, 300) // 300ms 防抖
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  if (isInitialized.value) {
    loadData()
  }
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  if (isInitialized.value) {
    loadData()
  }
}

// 选择处理
const handleSelectionChange = (selection: any[]) => {
  if (Array.isArray(selection)) {
    selectedUsers.value = selection
  } else {
    console.warn('selection 不是数组，重置为空数组')
    selectedUsers.value = []
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  userDialogVisible.value = true
}

// 编辑用户
const editUser = (user: any) => {
  isEdit.value = true
  userForm.value = {
    username: user.username,
    email: user.email,
    phone: user.phone || '',
    role: user.role,
    department: user.department?.id || null,
    store: user.store?.id || null,
    password: ''
  }
  // 保存当前编辑的用户ID
  selectedUsers.value = [user]
  userDialogVisible.value = true
}

// 查看用户
const viewUser = async (user: any) => {
  try {
    const response = await getUserDetail(user.id)
    if (response.data.success) {
      selectedUserDetail.value = response.data.user
      userDetailDialogVisible.value = true
    }
  } catch (error) {
    ElMessage.error('获取用户详情失败')
  }
}

// 切换用户状态
const toggleUserStatus = async (user: any) => {
  try {
    let newStatus: string
    let actionText: string
    
    // 根据当前状态决定新状态
    if (user.status === 'active' || user.status === 'approved') {
      newStatus = 'inactive'
      actionText = '禁用'
    } else if (user.status === 'inactive') {
      newStatus = 'active'
      actionText = '激活'
    } else if (user.status === 'pending') {
      newStatus = 'active'
      actionText = '激活'
    } else {
      // 对于rejected状态，先激活
      newStatus = 'active'
      actionText = '激活'
    }
    
    console.log(`开始${actionText}用户: ${user.username}, 从 ${user.status} 到 ${newStatus}`)
    
    await updateUserStatus(user.id, newStatus)
    ElMessage.success(`用户状态更新成功：${actionText}`)
    
    // 刷新数据
    await loadData()
  } catch (error: any) {
    console.error('更新用户状态失败:', error)
    
    let errorMessage = '更新用户状态失败'
    if (error.response?.data?.message) {
      errorMessage = error.response.data.message
    } else if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    }
    
    ElMessage.error(errorMessage)
  }
}

// 删除用户
const deleteUserHandler = async (user: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteUser(user.id)
    ElMessage.success('用户删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除用户失败')
    }
  }
}

// 显示批量操作对话框
const showBulkActionDialog = () => {
  if (selectedUsers.value.length === 0) {
    ElMessage.warning('请先选择要操作的用户')
    return
  }
  bulkActionDialogVisible.value = true
}

// 提交用户表单
const submitUserForm = async () => {
  if (!userFormRef.value) return
  
  try {
    await userFormRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      // 更新用户
      const updateData: any = { ...userForm.value }
      if (updateData.password !== undefined) {
        delete updateData.password
      }
      await updateUser(selectedUsers.value[0].id, updateData)
      ElMessage.success('用户信息更新成功')
    } else {
      // 创建用户
      const createData = {
        username: userForm.value.username,
        email: userForm.value.email,
        phone: userForm.value.phone,
        role: userForm.value.role,
        department: userForm.value.department || undefined,
        store: userForm.value.store || undefined,
        password: userForm.value.password
      }
      await createUser(createData)
      ElMessage.success('用户创建成功')
    }
    
    userDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新用户失败' : '创建用户失败')
  } finally {
    submitting.value = false
  }
}

// 提交批量操作
const submitBulkAction = async () => {
  if (selectedUsers.value.length === 0) {
    ElMessage.warning('请选择要操作的用户')
    return
  }
  
  try {
    submitting.value = true
    const userIds = selectedUsers.value.map(user => user.id)
    
    await bulkActionUsers({
      action: bulkActionForm.value.action,
      user_ids: userIds,
      reason: bulkActionForm.value.reason
    })
    
    ElMessage.success('批量操作完成')
    bulkActionDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('批量操作失败')
  } finally {
    submitting.value = false
  }
}

// 重置用户表单
const resetUserForm = () => {
  userForm.value = {
    username: '',
    email: '',
    phone: '',
    role: '',
    department: null,
    store: null,
    password: ''
  }
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
}

// 工具函数
const getRoleTagType = (role: string) => {
  if (!role || typeof role !== 'string') return 'info'
  const typeMap: Record<string, string> = {
    'super_admin': 'danger',
    'department_manager': 'warning',
    'store_operator': 'primary',
    'staff': 'info'
  }
  return typeMap[role] || 'info'
}

const getRoleDisplayName = (role: string) => {
  if (!role || typeof role !== 'string') return '未知角色'
  const nameMap: Record<string, string> = {
    'super_admin': '超级管理员',
    'department_manager': '部门部长',
    'store_operator': '店铺运营',
    'staff': '普通员工'
  }
  return nameMap[role] || role
}

const getStatusTagType = (status: string) => {
  if (!status || typeof status !== 'string') return 'info'
  const typeMap: Record<string, string> = {
    'active': 'success',
    'approved': 'success',
    'pending': 'warning',
    'inactive': 'danger',
    'rejected': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusDisplayName = (status: string) => {
  if (!status || typeof status !== 'string') return '未知状态'
  const nameMap: Record<string, string> = {
    'active': '激活',
    'approved': '已通过',
    'pending': '待审批',
    'inactive': '禁用',
    'rejected': '拒绝'
  }
  return nameMap[status] || status
}

const formatDate = (dateString: string) => {
  if (!dateString || typeof dateString !== 'string') return '-'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return '-'
    return date.toLocaleString('zh-CN')
  } catch (error) {
    console.warn('日期格式化失败:', dateString, error)
    return '-'
  }
}
</script>

<style scoped>
.users-view {
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

.users-table {
  padding: 0;
  overflow: hidden;
}

.error-message {
  padding: var(--spacing-lg);
  text-align: center;
}

.pagination-wrapper {
  padding: var(--spacing-lg);
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--border-color);
}

.selected-users {
  padding: var(--spacing-sm);
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  color: var(--text-secondary);
}

.user-detail {
  padding: var(--spacing-md);
}

.detail-item {
  display: flex;
  margin-bottom: var(--spacing-md);
  align-items: center;
}

.detail-item label {
  font-weight: 600;
  width: 100px;
  color: var(--text-secondary);
}

.detail-item span {
  flex: 1;
}

.rejection-reason {
  color: var(--danger-color);
  font-style: italic;
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
