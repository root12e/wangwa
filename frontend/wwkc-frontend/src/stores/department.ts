import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { departmentAPI } from '@/api/department'
import type { Department } from '@/api/department'

export const useDepartmentStore = defineStore('department', () => {
  // 状态
  const departments = ref<Department[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const activeDepartments = computed(() => 
    departments.value.filter(dept => dept.status === 'active')
  )

  const departmentOptions = computed(() => 
    departments.value.map(dept => ({
      id: dept.id,
      name: dept.name
    }))
  )

  // 获取部门列表
  const fetchDepartments = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await departmentAPI.getDepartments()
      
      // 确保正确提取数据
      if (response && response.data) {
        if (response.data.results) {
          departments.value = response.data.results
        } else if (Array.isArray(response.data)) {
          departments.value = response.data
        } else {
          departments.value = []
        }
      } else {
        departments.value = []
      }
    } catch (err: any) {
      error.value = err.message || '获取部门列表失败'
      console.error('获取部门列表失败:', err)
      departments.value = []
    } finally {
      loading.value = false
    }
  }

  // 根据ID获取部门
  const getDepartmentById = (id: string) => {
    return departments.value.find(dept => dept.id === id)
  }

  // 添加部门
  const addDepartment = async (department: Partial<Department>) => {
    try {
      loading.value = true
      error.value = null
      const response = await departmentAPI.createDepartment(department)
      departments.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.message || '创建部门失败'
      console.error('创建部门失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新部门
  const updateDepartment = async (id: string, updates: Partial<Department>) => {
    try {
      loading.value = true
      error.value = null
      const response = await departmentAPI.updateDepartment(id, updates)
      const index = departments.value.findIndex(dept => dept.id === id)
      if (index !== -1) {
        departments.value[index] = { ...departments.value[index], ...response.data }
      }
      return response.data
    } catch (err: any) {
      error.value = err.message || '更新部门失败'
      console.error('更新部门失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除部门
  const deleteDepartment = async (id: string) => {
    try {
      loading.value = true
      error.value = null
      await departmentAPI.deleteDepartment(id)
      const index = departments.value.findIndex(dept => dept.id === id)
      if (index !== -1) {
        departments.value.splice(index, 1)
      }
    } catch (err: any) {
      error.value = err.message || '删除部门失败'
      console.error('删除部门失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 搜索部门
  const searchDepartments = async (query: string) => {
    try {
      loading.value = true
      error.value = null
      const response = await departmentAPI.searchDepartments(query)
      departments.value = response.data.results || response.data
    } catch (err: any) {
      error.value = err.message || '搜索部门失败'
      console.error('搜索部门失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 重置状态
  const reset = () => {
    departments.value = []
    loading.value = false
    error.value = null
  }

  return {
    // 状态
    departments,
    loading,
    error,
    
    // 计算属性
    activeDepartments,
    departmentOptions,
    
    // 方法
    fetchDepartments,
    getDepartmentById,
    addDepartment,
    updateDepartment,
    deleteDepartment,
    searchDepartments,
    reset
  }
})
