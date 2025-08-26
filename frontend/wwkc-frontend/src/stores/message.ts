import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatRoom, Message, InventoryWarning, WarningNotification } from '@/api/message'
import {
  chatRoomApi,
  messageApi,
  inventoryWarningApi,
  warningNotificationApi
} from '@/api/message'
import { useAuthStore } from './auth'

export const useMessageStore = defineStore('message', () => {
  // 状态
  const chatRooms = ref<ChatRoom[]>([])
  const currentRoom = ref<ChatRoom | null>(null)
  const messages = ref<Message[]>([])
  const inventoryWarnings = ref<InventoryWarning[]>([])
  const warningNotifications = ref<WarningNotification[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const activeChatRooms = computed(() => 
    chatRooms.value.filter(room => room.is_active)
  )

  const systemMessages = computed(() => 
    messages.value.filter(msg => msg.message_type === 'system')
  )

  const warningMessages = computed(() => 
    messages.value.filter(msg => msg.message_type === 'warning')
  )

  const activeWarnings = computed(() => 
    inventoryWarnings.value.filter(warning => warning.status === 'active')
  )

  const unreadNotifications = computed(() => 
    warningNotifications.value.filter(notification => !notification.is_read)
  )

  // 获取聊天室列表
  const fetchChatRooms = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await chatRoomApi.getChatRooms()
      chatRooms.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取聊天室列表失败'
      console.error('获取聊天室列表失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 创建聊天室
  const createChatRoom = async (data: {
    name: string
    room_type: 'private' | 'group' | 'system'
    member_ids?: string[]
  }) => {
    try {
      loading.value = true
      error.value = null
      const response = await chatRoomApi.createChatRoom(data)
      chatRooms.value.unshift(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '创建聊天室失败'
      console.error('创建聊天室失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取聊天室详情
  const fetchChatRoom = async (id: string) => {
    try {
      loading.value = true
      error.value = null
      const response = await chatRoomApi.getChatRoom(id)
      currentRoom.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取聊天室详情失败'
      console.error('获取聊天室详情失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取消息列表
  const fetchMessages = async (roomId?: string) => {
    try {
      loading.value = true
      error.value = null
      const response = await messageApi.getMessages(roomId)
      messages.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取消息列表失败'
      console.error('获取消息列表失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 发送消息
  const sendMessage = async (data: {
    room: string
    message_type: 'text' | 'image' | 'file' | 'system' | 'warning'
    content: string
    file_url?: string
    file_name?: string
    file_size?: number
  }) => {
    try {
      loading.value = true
      error.value = null
      const response = await messageApi.sendMessage(data)
      messages.value.push(response.data)
      
      // 更新聊天室的最后消息
      const room = chatRooms.value.find(r => r.id === data.room)
      if (room) {
        room.last_message = {
          id: response.data.id,
          content: response.data.content,
          sender: response.data.sender.username,
          created_at: response.data.created_at
        }
        room.updated_at = response.data.created_at
      }
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '发送消息失败'
      console.error('发送消息失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 标记消息为已读
  const markMessageAsRead = async (messageId: string) => {
    try {
      await messageApi.markAsRead(messageId)
      const message = messages.value.find(m => m.id === messageId)
      if (message) {
        message.is_read = true
      }
    } catch (err: any) {
      console.error('标记消息为已读失败:', err)
    }
  }

  // 获取未读消息数量
  const fetchUnreadCount = async () => {
    try {
      const response = await messageApi.getUnreadCount()
      unreadCount.value = response.data.unread_count
    } catch (err: any) {
      console.error('获取未读消息数量失败:', err)
    }
  }

  // 获取库存预警列表
  const fetchInventoryWarnings = async (storeId?: string) => {
    try {
      loading.value = true
      error.value = null
      const response = await inventoryWarningApi.getWarnings(storeId)
      inventoryWarnings.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取库存预警列表失败'
      console.error('获取库存预警列表失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 解决库存预警
  const resolveWarning = async (warningId: string, resolutionNote?: string) => {
    try {
      loading.value = true
      error.value = null
      await inventoryWarningApi.resolveWarning(warningId, { resolution_note: resolutionNote })
      
      // 更新预警状态
      const warning = inventoryWarnings.value.find(w => w.id === warningId)
      if (warning) {
        warning.status = 'resolved'
        warning.resolved_at = new Date().toISOString()
        warning.resolved_by = useAuthStore().user
      }
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '解决预警失败'
      console.error('解决预警失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 手动检查预警
  const checkWarnings = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await inventoryWarningApi.checkWarnings()
      
      // 重新获取预警列表
      await fetchInventoryWarnings()
      
      return response.data.warnings_created
    } catch (err: any) {
      error.value = err.response?.data?.detail || '检查预警失败'
      console.error('检查预警失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取预警通知列表
  const fetchWarningNotifications = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await warningNotificationApi.getNotifications()
      warningNotifications.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取预警通知列表失败'
      console.error('获取预警通知列表失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 标记通知为已读
  const markNotificationAsRead = async (notificationId: string) => {
    try {
      await warningNotificationApi.markAsRead(notificationId)
      const notification = warningNotifications.value.find(n => n.id === notificationId)
      if (notification) {
        notification.is_read = true
        notification.read_at = new Date().toISOString()
      }
    } catch (err: any) {
      console.error('标记通知为已读失败:', err)
    }
  }

  // 标记所有通知为已读
  const markAllNotificationsAsRead = async () => {
    try {
      await warningNotificationApi.markAllAsRead()
      warningNotifications.value.forEach(notification => {
        notification.is_read = true
        notification.read_at = new Date().toISOString()
      })
    } catch (err: any) {
      console.error('标记所有通知为已读失败:', err)
    }
  }

  // 邀请成员加入聊天室
  const inviteMembers = async (roomId: string, data: { user_ids: string[], role: string }) => {
    try {
      loading.value = true
      error.value = null
      await chatRoomApi.inviteMembers(roomId, data)
      
      // 重新获取聊天室详情
      await fetchChatRoom(roomId)
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '邀请成员失败'
      console.error('邀请成员失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 离开聊天室
  const leaveRoom = async (roomId: string) => {
    try {
      loading.value = true
      error.value = null
      await chatRoomApi.leaveRoom(roomId)
      
      // 从列表中移除
      chatRooms.value = chatRooms.value.filter(room => room.id !== roomId)
      
      // 如果当前聊天室是离开的聊天室，清空当前聊天室
      if (currentRoom.value?.id === roomId) {
        currentRoom.value = null
      }
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '离开聊天室失败'
      console.error('离开聊天室失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 清空状态
  const clearState = () => {
    chatRooms.value = []
    currentRoom.value = null
    messages.value = []
    inventoryWarnings.value = []
    warningNotifications.value = []
    unreadCount.value = 0
    loading.value = false
    error.value = null
  }

  return {
    // 状态
    chatRooms,
    currentRoom,
    messages,
    inventoryWarnings,
    warningNotifications,
    unreadCount,
    loading,
    error,
    
    // 计算属性
    activeChatRooms,
    systemMessages,
    warningMessages,
    activeWarnings,
    unreadNotifications,
    
    // 方法
    fetchChatRooms,
    createChatRoom,
    fetchChatRoom,
    fetchMessages,
    sendMessage,
    markMessageAsRead,
    fetchUnreadCount,
    fetchInventoryWarnings,
    resolveWarning,
    checkWarnings,
    fetchWarningNotifications,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    inviteMembers,
    leaveRoom,
    clearState
  }
})
