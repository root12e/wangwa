import apiClient from './client'

// 获取邀请详情（通过令牌）
export function getInvitationByToken(token: string) {
  return apiClient.get(`/api/admin-invitation/${token}/`)
}

// 接受邀请
export function acceptInvitation(invitationId: string) {
  return apiClient.post(`/api/admin-invitations/${invitationId}/accept/`)
}

// 拒绝邀请
export function rejectInvitation(invitationId: string) {
  return apiClient.post(`/api/admin-invitations/${invitationId}/reject/`)
}

// 创建邀请
export function createInvitation(data: any) {
  return apiClient.post('/api/admin-invitations/', data)
}

// 获取我发送的邀请
export function getMyInvitations() {
  return apiClient.get('/api/admin-invitations/my_invitations/')
}

// 获取邀请列表
export function getInvitations(params?: any) {
  return apiClient.get('/api/admin-invitations/', { params })
}

// 获取邀请详情
export function getInvitation(invitationId: string) {
  return apiClient.get(`/api/admin-invitations/${invitationId}/`)
}

// 更新邀请
export function updateInvitation(invitationId: string, data: any) {
  return apiClient.put(`/api/admin-invitations/${invitationId}/`, data)
}

// 删除邀请
export function deleteInvitation(invitationId: string) {
  return apiClient.delete(`/api/admin-invitations/${invitationId}/`)
}
