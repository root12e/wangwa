import apiClient from './client'

// 用户注册
export function registerUser(data: any) {
  return apiClient.post('/api/auth/register/', data)
}

// 检查超级管理员是否存在
export function checkSuperAdmin() {
  return apiClient.get('/api/users/check-super_admin/')
}

// 获取部门列表
export function getDepartments() {
  return apiClient.get('/api/departments/')
}

// 用户登录
export function loginUser(data: any) {
  return apiClient.post('/api/auth/login/', data)
}

// 用户登出
export function logoutUser() {
  return apiClient.post('/api/auth/logout/')
}

// 刷新令牌
export function refreshToken() {
  return apiClient.post('/api/auth/refresh/')
}

// 获取用户资料
export function getUserProfile() {
  return apiClient.get('/api/user/profile/')
}

// 更新用户资料
export function updateUserProfile(data: any) {
  return apiClient.put('/api/user/profile/', data)
}

// 修改密码
export function changePassword(data: any) {
  return apiClient.put('/api/auth/change-password/', data)
}

// 发送邮箱验证码
export function sendVerificationCode(data: any) {
  return apiClient.post('/api/auth/send-verification-code/', data)
}

// 检查邮箱验证
export function checkEmailVerification(data: any) {
  return apiClient.post('/api/auth/check-email-verification/', data)
}

// 密码重置请求
export function passwordResetRequest(data: any) {
  return apiClient.post('/api/auth/password-reset-request/', data)
}

// 密码重置确认
export function passwordResetConfirm(data: any) {
  return apiClient.post('/api/auth/password-reset-confirm/', data)
}
