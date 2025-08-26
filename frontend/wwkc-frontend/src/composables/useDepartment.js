import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { departmentAPI, departmentUtils } from '@/api/department'

/**
 * 部门管理组合式函数
 */
export function useDepartment() {
  // 状态管理
  const departments = ref([])
  const loading = ref(false)
  const searchQuery = ref('')
  const statusFilter = ref('')
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)

  // 对话框状态
  const dialogVisible = ref(false)
  const detailDialogVisible = ref(false)
  const isEditing = ref(false)
  const selectedDepartment = ref(null)
  const activeTab = ref('members')

  // 表单数据
  const departmentForm = reactive({
    name: '',
    description: '',
    status: 'active'
  })

  // 表单验证规则
  const departmentRules = {
    name: [
      { required: true, message: '请输入部门名称', trigger: 'blur' },
      { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
    ],
    description: [
      { required: true, message: '请输入部门描述', trigger: 'blur' },
      { min: 10, max: 200, message: '长度在 10 到 200 个字符', trigger: 'blur' }
    ],
    status: [
      { required: true, message: '请选择部门状态', trigger: 'change' }
    ]
  }

  // 计算属性
  const filteredDepartments = computed(() => {
    let filtered = departments.value
    
    if (searchQuery.value) {
      filtered = filtered.filter(dept => 
        dept.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        dept.description.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    }
    
    if (statusFilter.value) {
      filtered = filtered.filter(dept => dept.status === statusFilter.value)
    }
    
    return filtered
  })

  const departmentStats = computed(() => {
    return departmentUtils.calculateStats(departments.value)
  })

  // 方法
  const fetchDepartments = async (params = {}) => {
    try {
      loading.value = true
      const response = await departmentAPI.getDepartments({
        page: currentPage.value,
        page_size: pageSize.value,
        ...params
      })
      
      departments.value = response.data.results || response.data
      total.value = response.data.count || response.data.length
    } catch (error) {
      console.error('获取部门列表失败:', error)
      ElMessage.error('获取部门列表失败')
    } finally {
      loading.value = false
    }
  }

  const searchDepartments = async (query) => {
    if (!query.trim()) {
      await fetchDepartments()
      return
    }

    try {
      loading.value = true
      const response = await departmentAPI.searchDepartments(query, {
        page: currentPage.value,
        page_size: pageSize.value
      })
      
      departments.value = response.data.results || response.data
      total.value = response.data.count || response.data.length
    } catch (error) {
      console.error('搜索部门失败:', error)
      ElMessage.error('搜索部门失败')
    } finally {
      loading.value = false
    }
  }

  const handleSearch = () => {
    if (searchQuery.value.trim()) {
      searchDepartments(searchQuery.value)
    } else {
      fetchDepartments()
    }
  }

  const handleFilter = () => {
    fetchDepartments({ status: statusFilter.value })
  }

  const showCreateDialog = () => {
    isEditing.value = false
    resetForm()
    dialogVisible.value = true
  }

  const editDepartment = (department) => {
    isEditing.value = true
    Object.assign(departmentForm, department)
    dialogVisible.value = true
  }

  const deleteDepartment = async (department) => {
    try {
      await ElMessageBox.confirm(
        `确定要删除部门 "${department.name}" 吗？此操作不可恢复。`,
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      await departmentAPI.deleteDepartment(department.id)
      
      // 从本地列表中移除
      const index = departments.value.findIndex(d => d.id === department.id)
      if (index > -1) {
        departments.value.splice(index, 1)
      }
      
      ElMessage.success('部门删除成功')
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除部门失败:', error)
        ElMessage.error('删除部门失败')
      }
    }
  }

  const submitDepartment = async () => {
    try {
      if (isEditing.value) {
        // 更新部门
        await departmentAPI.updateDepartment(departmentForm.id, departmentForm)
        
        // 更新本地数据
        const index = departments.value.findIndex(d => d.id === departmentForm.id)
        if (index > -1) {
          Object.assign(departments.value[index], { ...departmentForm })
        }
        
        ElMessage.success('部门更新成功')
      } else {
        // 创建部门
        const response = await departmentAPI.createDepartment(departmentForm)
        const newDepartment = response.data
        
        // 添加到本地列表
        departments.value.unshift({
          ...newDepartment,
          member_count: 0,
          store_count: 0,
          members: [],
          stores: []
        })
        
        ElMessage.success('部门创建成功')
      }
      
      dialogVisible.value = false
      resetForm()
    } catch (error) {
      console.error('操作失败:', error)
      ElMessage.error('操作失败，请重试')
    }
  }

  const showDepartmentDetail = async (department) => {
    try {
      // 获取完整的部门信息
      const response = await departmentAPI.getDepartment(department.id)
      selectedDepartment.value = response.data
      detailDialogVisible.value = true
    } catch (error) {
      console.error('获取部门详情失败:', error)
      ElMessage.error('获取部门详情失败')
    }
  }

  const resetForm = () => {
    Object.assign(departmentForm, {
      name: '',
      description: '',
      status: 'active'
    })
  }

  const exportData = () => {
    // 实现导出功能
    ElMessage.info('导出功能开发中...')
  }

  const addMember = () => {
    ElMessage.info('添加成员功能开发中...')
  }

  const removeMember = (member) => {
    ElMessage.info('移除成员功能开发中...')
  }

  const addStore = () => {
    ElMessage.info('添加店铺功能开发中...')
  }

  const removeStore = (store) => {
    ElMessage.info('移除店铺功能开发中...')
  }

  const handlePageChange = (page) => {
    currentPage.value = page
    fetchDepartments()
  }

  const handlePageSizeChange = (size) => {
    pageSize.value = size
    currentPage.value = 1
    fetchDepartments()
  }

  // 初始化
  const init = () => {
    fetchDepartments()
  }

  return {
    // 状态
    departments,
    loading,
    searchQuery,
    statusFilter,
    currentPage,
    pageSize,
    total,
    dialogVisible,
    detailDialogVisible,
    isEditing,
    selectedDepartment,
    activeTab,
    departmentForm,
    departmentRules,
    
    // 计算属性
    filteredDepartments,
    departmentStats,
    
    // 方法
    fetchDepartments,
    searchDepartments,
    handleSearch,
    handleFilter,
    showCreateDialog,
    editDepartment,
    deleteDepartment,
    submitDepartment,
    showDepartmentDetail,
    resetForm,
    exportData,
    addMember,
    removeMember,
    addStore,
    removeStore,
    handlePageChange,
    handlePageSizeChange,
    init,
    
    // 工具函数
    formatStatus: departmentUtils.formatStatus,
    getStatusType: departmentUtils.getStatusType,
    formatDate: departmentUtils.formatDate
  }
}
