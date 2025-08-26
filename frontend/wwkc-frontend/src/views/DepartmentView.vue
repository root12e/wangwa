<template>
  <div class="department-management">
    
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">
            <el-icon class="title-icon"><OfficeBuilding /></el-icon>
            部门管理
          </h1>
          <p class="page-subtitle">管理系统组织架构，分配人员与店铺</p>
        </div>
        <div class="header-right">
          <el-button 
            type="primary" 
            size="large" 
            @click="showCreateDialog = true"
            :disabled="!canCreate"
            class="create-btn"
          >
            <el-icon><Plus /></el-icon>
            新建部门
          </el-button>
        </div>
      </div>
    </div>
  
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-icon">
          <el-icon><OfficeBuilding /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ totalDepartments }}</div>
          <div class="stat-label">总部门数</div>
        </div>
      </div>
      
      <div class="stat-card card">
        <div class="stat-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ totalMembers }}</div>
          <div class="stat-label">总成员数</div>
        </div>
      </div>
      
      <div class="stat-card card">
        <div class="stat-icon">
          <el-icon><Shop /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ totalStores }}</div>
          <div class="stat-label">总店铺数</div>
        </div>
      </div>
      
      <div class="stat-card card">
        <div class="stat-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ avgMembersPerDept }}</div>
          <div class="stat-label">平均成员/部门</div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar card">
      <div class="action-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索部门名称或描述..."
          class="search-input"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select 
          v-model="filterStatus" 
          placeholder="筛选状态" 
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option label="有成员" value="has_members" />
          <el-option label="无成员" value="no_members" />
          <el-option label="有店铺" value="has_stores" />
          <el-option label="无店铺" value="no_stores" />
        </el-select>
      </div>
      
      <div class="action-right">
        <el-button @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="exportData" :disabled="departments.length === 0">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 部门列表 -->
    <div class="department-table card">
      <el-table
        :data="filteredDepartments"
        v-loading="loading"
        stripe
        class="table"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="name" label="部门名称" sortable="custom" min-width="150">
          <template #default="{ row }">
            <div class="department-name">
              <el-icon class="dept-icon"><OfficeBuilding /></el-icon>
              <span class="name-text">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="description-text">{{ row.description || '暂无描述' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="member_count" label="成员数" sortable="custom" width="100" align="center">
          <template #default="{ row }">
            <el-tag 
              :type="row.member_count > 0 ? 'success' : 'info'"
              size="small"
            >
              {{ row.member_count }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="store_count" label="店铺数" sortable="custom" width="100" align="center">
          <template #default="{ row }">
            <el-tag 
              :type="row.store_count > 0 ? 'primary' : 'info'"
              size="small"
            >
              {{ row.store_count }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" sortable="custom" width="180">
          <template #default="{ row }">
            <span class="time-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button 
                size="small" 
                @click="viewDetails(row)"
                class="action-btn view-btn"
              >
                <el-icon><View /></el-icon>
                查看
              </el-button>
              
              <el-button 
                size="small" 
                type="primary" 
                @click="editDepartment(row)"
                :disabled="!canEdit(row)"
                class="action-btn edit-btn"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteDepartment(row)"
                :disabled="!canDelete(row)"
                class="action-btn delete-btn"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
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

    <!-- 创建/编辑部门对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEditing ? '编辑部门' : '新建部门'"
      width="500px"
      :close-on-click-modal="false"
      @close="resetForm"
    >
      <el-form
        ref="departmentFormRef"
        :model="departmentForm"
        :rules="departmentRules"
        label-width="80px"
        class="department-form"
      >
        <el-form-item label="部门名称" prop="name">
          <el-input
            v-model="departmentForm.name"
            placeholder="请输入部门名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="部门描述" prop="description">
          <el-input
            v-model="departmentForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入部门描述"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitForm"
            :loading="submitting"
          >
            {{ isEditing ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 部门详情对话框 -->
    <el-dialog
      v-model="showDetailsDialog"
      title="部门详情"
      width="800px"
      class="details-dialog"
    >
      <div v-if="selectedDepartment" class="department-details">
        <div class="detail-header">
          <div class="detail-title">
            <el-icon class="title-icon"><OfficeBuilding /></el-icon>
            <h3>{{ selectedDepartment.name }}</h3>
          </div>
          <div class="detail-meta">
            <el-tag type="info">创建于 {{ formatDate(selectedDepartment.created_at) }}</el-tag>
          </div>
        </div>
        
        <div class="detail-description">
          <h4>部门描述</h4>
          <p>{{ selectedDepartment.description || '暂无描述' }}</p>
        </div>
        
        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="成员列表" name="members">
            <div class="members-section">
              <div class="section-header">
                <h4>部门成员 ({{ selectedDepartment.members?.length || 0 }})</h4>
                <el-button size="small" type="primary" @click="addMember">
                  <el-icon><Plus /></el-icon>
                  添加成员
                </el-button>
              </div>
              
              <el-table :data="selectedDepartment.members || []" stripe>
                <el-table-column prop="username" label="用户名" />
                <el-table-column prop="role_display" label="角色" />
                <el-table-column prop="phone" label="手机号" />
                <el-table-column prop="email" label="邮箱" />
                <el-table-column prop="store_name" label="所属店铺" />
                <el-table-column label="操作" width="120">
                  <template #default="{ row }">
                    <el-button size="small" type="danger" @click="removeMember(row)">
                      移除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="店铺列表" name="stores">
            <div class="stores-section">
              <div class="section-header">
                <h4>部门店铺 ({{ selectedDepartment.stores?.length || 0 }})</h4>
                <el-button size="small" type="primary" @click="addStore">
                  <el-icon><Plus /></el-icon>
                  添加店铺
                </el-button>
              </div>
              
              <el-table :data="selectedDepartment.stores || []" stripe>
                <el-table-column prop="name" label="店铺名称" />
                <el-table-column prop="address" label="地址" show-overflow-tooltip />
                <el-table-column prop="phone" label="电话" />
                <el-table-column label="操作" width="120">
                  <template #default="{ row }">
                    <el-button size="small" type="danger" @click="removeStore(row)">
                      移除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>
  
  <script setup lang="ts">
  import { ref, reactive, computed, onMounted, nextTick } from 'vue'
  import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
  import { 
    OfficeBuilding, 
    Plus, 
    Search, 
    Refresh, 
    Download, 
    View, 
    Edit, 
    Delete,
    User,
    Shop,
    TrendCharts
  } from '@element-plus/icons-vue'
  import { useAuthStore } from '@/stores/auth'
  import { departmentAPI } from '@/api/department'
  
  // 认证状态
  const authStore = useAuthStore()
  
  // 响应式数据
  const loading = ref(false)
  const submitting = ref(false)
  const searchQuery = ref('')
  const filterStatus = ref('')
  const currentPage = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  const departments = ref([])
  const showCreateDialog = ref(false)
  const showDetailsDialog = ref(false)
  const isEditing = ref(false)
  const selectedDepartment = ref(null)
  const activeTab = ref('members')
  
  // 调试信息
  console.log('🔍 部门管理页面加载状态:', {
    isAuthenticated: authStore.isAuthenticated,
    userRole: authStore.user?.role,
    isSuperAdmin: authStore.isSuperAdmin,
    isDepartmentManager: authStore.isDepartmentManager
  })
  
  // 表单数据
  const departmentFormRef = ref()
  const departmentForm = reactive({
    id: '',
    name: '',
    description: ''
  })
  
  // 表单验证规则
  const departmentRules = {
    name: [
      { required: true, message: '请输入部门名称', trigger: 'blur' },
      { min: 2, max: 100, message: '部门名称长度在 2 到 100 个字符', trigger: 'blur' }
    ],
    description: [
      { max: 500, message: '描述长度不能超过 500 个字符', trigger: 'blur' }
    ]
  }
  
  // 计算属性
  const canCreate = computed(() => {
    return authStore.isSuperAdmin || authStore.isDepartmentManager
  })
  
  const canEdit = computed(() => (department: any) => {
    return authStore.isSuperAdmin || 
           (authStore.isDepartmentManager && department.id === authStore.user?.department?.id)
  })
  
  const canDelete = computed(() => (department: any) => {
    return authStore.isSuperAdmin || 
           (authStore.isDepartmentManager && department.id === authStore.user?.department?.id)
  })
  
  const filteredDepartments = computed(() => {
    let filtered = departments.value
  
    // 搜索过滤
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(dept => 
        dept.name.toLowerCase().includes(query) || 
        (dept.description && dept.description.toLowerCase().includes(query))
      )
    }
  
    // 状态过滤
    if (filterStatus.value) {
      switch (filterStatus.value) {
        case 'has_members':
          filtered = filtered.filter(dept => dept.member_count > 0)
          break
        case 'no_members':
          filtered = filtered.filter(dept => dept.member_count === 0)
          break
        case 'has_stores':
          filtered = filtered.filter(dept => dept.store_count > 0)
          break
        case 'no_stores':
          filtered = filtered.filter(dept => dept.store_count === 0)
          break
      }
    }
  
    return filtered
  })
  
  const totalDepartments = computed(() => departments.value.length)
  const totalMembers = computed(() => departments.value.reduce((sum, dept) => sum + dept.member_count, 0))
  const totalStores = computed(() => departments.value.reduce((sum, dept) => sum + dept.store_count, 0))
  const avgMembersPerDept = computed(() => {
    if (totalDepartments.value === 0) return 0
    return Math.round(totalMembers.value / totalDepartments.value)
  })
  
  // 方法
  const fetchDepartments = async () => {
    try {
      loading.value = true
      const response = await departmentAPI.getDepartments({
        page: currentPage.value,
        page_size: pageSize.value
      })
      
      if (response.data) {
        departments.value = response.data.results || response.data
        total.value = response.data.count || response.data.length
      }
    } catch (error) {
      console.error('获取部门列表失败:', error)
      ElMessage.error('获取部门列表失败')
    } finally {
      loading.value = false
    }
  }
  
  const handleSearch = () => {
    currentPage.value = 1
  }
  
  const handleFilter = () => {
    currentPage.value = 1
  }
  
  const handleSortChange = ({ prop, order }) => {
    // 实现排序逻辑
    console.log('排序:', prop, order)
  }
  
  const handleSizeChange = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    fetchDepartments()
  }
  
  const handleCurrentChange = (page: number) => {
    currentPage.value = page
    fetchDepartments()
  }
  
  const refreshData = () => {
    fetchDepartments()
  }
  
  const exportData = () => {
    ElMessage.success('导出功能开发中...')
  }
  
  const viewDetails = async (department: any) => {
    try {
      const response = await departmentAPI.getDepartmentDetail(department.id)
      if (response.data) {
        selectedDepartment.value = response.data
        showDetailsDialog.value = true
      }
    } catch (error) {
      console.error('获取部门详情失败:', error)
      ElMessage.error('获取部门详情失败')
    }
  }
  
  const editDepartment = (department: any) => {
    isEditing.value = true
    departmentForm.id = department.id
    departmentForm.name = department.name
    departmentForm.description = department.description || ''
    showCreateDialog.value = true
  }
  
  const deleteDepartment = async (department: any) => {
    try {
      await ElMessageBox.confirm(
        `确定要删除部门 "${department.name}" 吗？此操作不可恢复。`,
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
  
      await departmentAPI.deleteDepartment(department.id)
      ElMessage.success('部门删除成功')
      fetchDepartments()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除部门失败:', error)
        ElMessage.error('删除部门失败')
      }
    }
  }
  
  const submitForm = async () => {
    try {
      await departmentFormRef.value.validate()
      submitting.value = true
  
      if (isEditing.value) {
        await departmentAPI.updateDepartment(departmentForm.id, departmentForm)
        ElMessage.success('部门更新成功')
      } else {
        await departmentAPI.createDepartment(departmentForm)
        ElMessage.success('部门创建成功')
      }
  
      showCreateDialog.value = false
      fetchDepartments()
    } catch (error) {
      console.error('提交表单失败:', error)
      ElMessage.error('操作失败，请重试')
    } finally {
      submitting.value = false
    }
  }
  
  const resetForm = () => {
    departmentForm.id = ''
    departmentForm.name = ''
    departmentForm.description = ''
    isEditing.value = false
    departmentFormRef.value?.clearValidate()
  }
  
  const formatDate = (dateString: string) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  const addMember = () => {
    ElMessage.info('添加成员功能开发中...')
  }
  
  const removeMember = (member: any) => {
    ElMessage.info('移除成员功能开发中...')
  }
  
  const addStore = () => {
    ElMessage.info('添加店铺功能开发中...')
  }
  
  const removeStore = (store: any) => {
    ElMessage.info('移除店铺功能开发中...')
  }
  
  // 生命周期
  onMounted(() => {
    fetchDepartments()
  })
  </script>
  
  <style scoped>
  .department-management {
    padding: var(--spacing-lg);
    min-height: 100vh;
  }
  
  /* 页面头部 */
  .page-header {
    margin-bottom: var(--spacing-xl);
  }
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .header-left {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .page-title {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin: 0;
    font-size: 28px;
    font-weight: 600;
    color: var(--text-primary);
  }
  
  .title-icon {
    font-size: 32px;
    color: var(--primary-color);
  }
  
  .page-subtitle {
    margin: 0;
    color: var(--text-secondary);
    font-size: 16px;
  }
  
  .create-btn {
    padding: var(--spacing-md) var(--spacing-lg);
    font-size: 16px;
    font-weight: 500;
  }
  
  /* 统计卡片 */
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
    transition: all 0.3s ease;
  }
  
  .stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-heavy);
  }
  
  .stat-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
    color: white;
    font-size: 24px;
  }
  
  .stat-content {
    flex: 1;
  }
  
  .stat-number {
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: var(--spacing-xs);
  }
  
  .stat-label {
    color: var(--text-secondary);
    font-size: 14px;
  }
  
  /* 操作栏 */
  .action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
  }
  
  .action-left {
    display: flex;
    gap: var(--spacing-md);
    align-items: center;
  }
  
  .search-input {
    width: 300px;
  }
  
  .filter-select {
    width: 150px;
  }
  
  .action-right {
    display: flex;
    gap: var(--spacing-md);
  }
  
  /* 部门表格 */
  .department-table {
    padding: 0;
    overflow: hidden;
  }
  
  .table {
    width: 100%;
  }
  
  .department-name {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
  }
  
  .dept-icon {
    color: var(--primary-color);
    font-size: 16px;
  }
  
  .name-text {
    font-weight: 500;
    color: var(--text-primary);
  }
  
  .description-text {
    color: var(--text-secondary);
    line-height: 1.4;
  }
  
  .time-text {
    color: var(--text-secondary);
    font-size: 13px;
  }
  
  .action-buttons {
    display: flex;
    gap: var(--spacing-xs);
  }
  
  .action-btn {
    padding: var(--spacing-xs) var(--spacing-sm);
  }
  
  /* 分页 */
  .pagination-wrapper {
    display: flex;
    justify-content: center;
    padding: var(--spacing-lg);
    border-top: 1px solid var(--border-color);
  }
  
  /* 表单 */
  .department-form {
    padding: var(--spacing-md) 0;
  }
  
  /* 详情对话框 */
  .details-dialog {
    max-height: 80vh;
  }
  
  .department-details {
    padding: var(--spacing-md) 0;
  }
  
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
    padding-bottom: var(--spacing-md);
    border-bottom: 1px solid var(--border-color);
  }
  
  .detail-title {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
  }
  
  .detail-title h3 {
    margin: 0;
    color: var(--text-primary);
  }
  
  .detail-meta {
    display: flex;
    gap: var(--spacing-sm);
  }
  
  .detail-description {
    margin-bottom: var(--spacing-lg);
  }
  
  .detail-description h4 {
    margin: 0 0 var(--spacing-sm) 0;
    color: var(--text-primary);
    font-size: 16px;
  }
  
  .detail-description p {
    margin: 0;
    color: var(--text-secondary);
    line-height: 1.6;
  }
  
  .detail-tabs {
    margin-top: var(--spacing-lg);
  }
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
  }
  
  .section-header h4 {
    margin: 0;
    color: var(--text-primary);
    font-size: 16px;
  }
  
  /* 响应式设计 */
  @media (max-width: 768px) {
    .department-management {
      padding: var(--spacing-md);
    }
    
    .header-content {
      flex-direction: column;
      gap: var(--spacing-md);
      align-items: flex-start;
    }
    
    .stats-grid {
      grid-template-columns: 1fr;
      gap: var(--spacing-md);
    }
    
    .action-bar {
      flex-direction: column;
      gap: var(--spacing-md);
      align-items: stretch;
    }
    
    .action-left {
      flex-direction: column;
      width: 100%;
    }
    
    .search-input,
    .filter-select {
      width: 100%;
    }
    
    .action-right {
      justify-content: center;
    }
    
    .department-table {
      overflow-x: auto;
    }
    
    .action-buttons {
      flex-direction: column;
      gap: var(--spacing-xs);
    }
    
    .action-btn {
      width: 100%;
    }
  }
  
  @media (max-width: 480px) {
    .department-management {
      padding: var(--spacing-sm);
    }
    
    .page-title {
      font-size: 24px;
    }
    
    .title-icon {
      font-size: 28px;
    }
    
    .stat-card {
      padding: var(--spacing-lg);
    }
    
    .stat-icon {
      width: 50px;
      height: 50px;
      font-size: 20px;
    }
    
    .stat-number {
      font-size: 28px;
    }
  }
</style>