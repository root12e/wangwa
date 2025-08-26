import apiClient from './client'

// 用户管理接口

// 获取用户列表
export function getUserList(params?: {
  search?: string
  role?: string
  department?: string
  status?: string
  page?: number
  page_size?: number
}) {
  return apiClient.get('/api/users/', { params })
}

// 获取用户详情
export function getUserDetail(userId: number) {
  return apiClient.get(`/api/users/${userId}/`)
}

// 创建用户
export function createUser(data: {
  username: string
  email: string
  phone?: string
  role: string
  department?: number
  store?: number
  password: string
}) {
  return apiClient.post('/api/users/', data)
}

// 更新用户信息
export function updateUser(userId: number, data: {
  username?: string
  email?: string
  phone?: string
  role?: string
  department?: number
  store?: number
}) {
  return apiClient.put(`/api/users/${userId}/`, data)
}

// 删除用户
export function deleteUser(userId: number) {
  return apiClient.delete(`/api/users/${userId}/`)
}

// 批量操作用户
export function bulkActionUsers(data: {
  action: 'activate' | 'deactivate' | 'approve' | 'reject'
  user_ids: number[]
  reason?: string
}) {
  return apiClient.post('/api/users/bulk-action/', data)
}

// 获取用户统计信息
export function getUserStatistics() {
  return apiClient.get('/api/users/statistics/')
}

// 获取待审批用户列表
export function getPendingApprovals() {
  return apiClient.get('/api/users/approvals/')
}

// 审批用户
export function approveUser(data: {
  user_id: number
  action: 'approve' | 'reject'
  reason?: string
}) {
  return apiClient.post('/api/users/approvals/', data)
}

// 用户资料相关接口

// 获取当前用户资料
export function getCurrentUserProfile() {
  return apiClient.get('/api/user/profile/')
}

// 更新当前用户资料
export function updateCurrentUserProfile(data: {
  username?: string
  email?: string
  phone?: string
  department?: number
  store?: number
}) {
  return apiClient.put('/api/user/profile/', data)
}

// 修改密码
export function changePassword(data: {
  old_password: string
  new_password: string
  confirm_password: string
}) {
  return apiClient.post('/api/auth/change-password/', data)
}

// 获取部门列表（用于用户管理）
export function getDepartmentsForUser() {
  return apiClient.get('/api/departments/')
}

// 获取店铺列表（用于用户管理）
export function getStoresForUser() {
  return apiClient.get('/api/stores/')
}

// 用户状态管理
export function updateUserStatus(userId: number, status: string) {
  return apiClient.patch(`/api/users/${userId}/`, { status })
}

// 用户角色管理
export function updateUserRole(userId: number, role: string) {
  return apiClient.patch(`/api/users/${userId}/`, { role })
}

// 用户部门管理
export function updateUserDepartment(userId: number, department: number) {
  return apiClient.patch(`/api/users/${userId}/`, { department })
}

// 用户店铺管理
export function updateUserStore(userId: number, store: number) {
  return apiClient.patch(`/api/users/${userId}/`, { store })
}

// 搜索用户
export function searchUsers(query: string) {
  return apiClient.get('/api/users/', { params: { search: query } })
}

// 按角色筛选用户
export function filterUsersByRole(role: string) {
  return apiClient.get('/api/users/', { params: { role } })
}

// 按部门筛选用户
export function filterUsersByDepartment(departmentId: number) {
  return apiClient.get('/api/users/', { params: { department: departmentId } })
}

// 按状态筛选用户
export function filterUsersByStatus(status: string) {
  return apiClient.get('/api/users/', { params: { status } })
}

// 导出用户数据
export function exportUsers(params?: {
  search?: string
  role?: string
  department?: string
  status?: string
  format?: 'csv' | 'excel'
}) {
  return apiClient.get('/api/users/export/', { 
    params,
    responseType: 'blob'
  })
}

// 导入用户数据
export function importUsers(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post('/api/users/import/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 用户活动日志
export function getUserActivityLog(userId: number, params?: {
  start_date?: string
  end_date?: string
  action?: string
  page?: number
  page_size?: number
}) {
  return apiClient.get(`/api/users/${userId}/activity-log/`, { params })
}

// 重置用户密码
export function resetUserPassword(userId: number, newPassword: string) {
  return apiClient.post(`/api/users/${userId}/reset-password/`, {
    new_password: newPassword
  })
}

// 锁定/解锁用户账户
export function toggleUserLock(userId: number, locked: boolean) {
  return apiClient.post(`/api/users/${userId}/toggle-lock/`, {
    locked
  })
}

// 获取用户权限
export function getUserPermissions(userId: number) {
  return apiClient.get(`/api/users/${userId}/permissions/`)
}

// 更新用户权限
export function updateUserPermissions(userId: number, permissions: string[]) {
  return apiClient.put(`/api/users/${userId}/permissions/`, {
    permissions
  })
}
