import apiClient from './client'

// 聊天室相关API
export const chatRoomApi = {
  // 获取聊天室列表
  getChatRooms: () => apiClient.get('/chat-rooms/'),
  
  // 创建聊天室
  createChatRoom: (data: {
    name: string
    room_type: 'private' | 'group' | 'system'
    member_ids?: string[]
  }) => apiClient.post('/chat-rooms/', data),
  
  // 获取聊天室详情
  getChatRoom: (id: string) => apiClient.get(`/chat-rooms/${id}/`),
  
  // 邀请成员
  inviteMembers: (id: string, data: { user_ids: string[], role: string }) =>
    apiClient.post(`/chat-rooms/${id}/invite_members/`, data),
  
  // 离开聊天室
  leaveRoom: (id: string) => apiClient.post(`/chat-rooms/${id}/leave_room/`),
  
  // 获取聊天室成员
  getMembers: (id: string) => apiClient.get(`/chat-rooms/${id}/members/`),
}

// 消息相关API
export const messageApi = {
  // 获取消息列表
  getMessages: (roomId?: string) => {
    const params = roomId ? { room: roomId } : {}
    return apiClient.get('/messages/', { params })
  },
  
  // 发送消息
  sendMessage: (data: {
    room: string
    message_type: 'text' | 'image' | 'file' | 'system' | 'warning'
    content: string
    file_url?: string
    file_name?: string
    file_size?: number
  }) => apiClient.post('/messages/', data),
  
  // 标记消息为已读
  markAsRead: (id: string) => apiClient.post(`/messages/${id}/mark_as_read/`),
  
  // 删除消息
  deleteMessage: (id: string) => apiClient.post(`/messages/${id}/delete_message/`),
  
  // 获取未读消息数量
  getUnreadCount: () => apiClient.get('/messages/unread_count/'),
}

// 库存预警相关API
export const inventoryWarningApi = {
  // 获取预警列表
  getWarnings: (storeId?: string) => {
    const params = storeId ? { store: storeId } : {}
    return apiClient.get('/inventory-warnings/', { params })
  },
  
  // 解决预警
  resolveWarning: (id: string, data: { resolution_note?: string }) =>
    apiClient.post(`/inventory-warnings/${id}/resolve/`, data),
  
  // 手动检查预警
  checkWarnings: () => apiClient.post('/inventory-warnings/check_warnings/'),
}

// 预警通知相关API
export const warningNotificationApi = {
  // 获取通知列表
  getNotifications: () => apiClient.get('/warning-notifications/'),
  
  // 标记通知为已读
  markAsRead: (id: string) => apiClient.post(`/warning-notifications/${id}/mark_as_read/`),
  
  // 标记所有通知为已读
  markAllAsRead: () => apiClient.post('/warning-notifications/mark_all_as_read/'),
}

// 文件上传相关API
export const fileUploadApi = {
  // 上传文件
  uploadFile: (data: FormData) => apiClient.post('/file-upload/upload_file/', data, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
}

// 类型定义
export interface ChatRoom {
  id: string
  name: string
  room_type: 'private' | 'group' | 'system'
  creator: {
    id: string
    username: string
    email: string
  }
  is_active: boolean
  created_at: string
  updated_at: string
  member_count: number
  last_message?: {
    id: string
    content: string
    sender: string
    created_at: string
  }
  unread_count: number
}

export interface Message {
  id: string
  room: ChatRoom
  sender: {
    id: string
    username: string
    email: string
  }
  message_type: 'text' | 'image' | 'file' | 'system' | 'warning'
  content: string
  file_url?: string
  file_name?: string
  file_size?: number
  is_read: boolean
  is_deleted: boolean
  created_at: string
  updated_at: string
  is_read_by_current_user: boolean
  file_info?: {
    url: string
    name: string
    size: number
    type: string
  }
}

export interface InventoryWarning {
  id: string
  store: {
    id: string
    name: string
    code: string
  }
  product: {
    id: string
    name: string
    sku: string
  }
  warning_level: 'low' | 'critical' | 'out_of_stock'
  current_stock: number
  threshold_stock: number
  status: 'active' | 'resolved' | 'ignored'
  email_sent: boolean
  email_sent_at?: string
  created_at: string
  resolved_at?: string
  resolved_by?: {
    id: string
    username: string
  }
  notification_count: number
}

export interface WarningNotification {
  id: string
  warning: InventoryWarning
  user: {
    id: string
    username: string
    email: string
  }
  notified_at: string
  is_read: boolean
  read_at?: string
}

export interface ChatRoomMember {
  id: string
  room: ChatRoom
  user: {
    id: string
    username: string
    email: string
  }
  role: 'admin' | 'member' | 'readonly'
  joined_at: string
  last_read_at?: string
  is_muted: boolean
}
